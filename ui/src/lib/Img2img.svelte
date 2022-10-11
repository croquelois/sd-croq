<script>
  import Prompt from './Prompt.svelte';
  import ParametersCard from './ParametersCard.svelte';
  import ParametersCardImg2Img from './ParametersCardImg2Img.svelte';
  import JobStatus from './JobStatus.svelte';
  import Images from './Images.svelte';
  import { historyStore } from './historyStore.js';
  import { paramsImg2Img, paramsCanvas } from './paramsStore.js';
  import {generate, cancelRequest} from './backendLogic.js'
  import {shallowCopy} from './utils.js';
  import {getDetailFromUrl} from './detailMgmtUtils.js';
  
  let prompt = "";
  let negativePrompt = "";
  let width = 512;
  let height = 512;
  let classifierStrength = 12;
  let subseedStrength = 0.0;
  let seed = null;
  let subseed = null;
  let nbImages = 1;
  let samplingSteps = 20;
  let samplingMethod = "DDIM";
  let restoreFaces = false;
  let tiling = false;
  
  let denoiserStrength = 0.63;
  
  let inputImageUrl = null;
  let details = [];
  
  let actionText = "Generate";
  let actionDisabled = false;
  let waitImage = null;
  let jobStatus = null;
  
  function feedback(status){
    jobStatus = status;
  }
  
  function getAllParams(){
    return {prompt, negativePrompt, width, height, classifierStrength, seed, subseed, subseedStrength, nbImages, samplingSteps, samplingMethod, restoreFaces, tiling, denoiserStrength};
  }
  
  function setAllParams(p){
    if(p.prompt)
      prompt = p.prompt;
    if(p.negativePrompt)
      negativePrompt = p.negativePrompt;
    if(p.width)
      width = p.width;
    if(p.height)
      height = p.height;
    if(p.classifierStrength)
      classifierStrength = p.classifierStrength;
    if(p.seed)
      seed = p.seed;
    if(p.subseed)
      subseed = p.subseed;
    if(p.subseedStrength)
      subseedStrength = p.subseedStrength;
    if(p.nbImages)
      nbImages = p.nbImages;
    if(p.samplingSteps)
      samplingSteps = p.samplingSteps;
    if(p.samplingMethod)
      samplingMethod = p.samplingMethod;
    if(p.restoreFaces)
      restoreFaces = p.restoreFaces;
    if(p.tiling)
      tiling = p.tiling;
    if(p.denoiserStrength)
      denoiserStrength = p.denoiserStrength;
    if(p.inputImageUrl)
      inputImageUrl = p.inputImageUrl;
  }
  paramsImg2Img.subscribe(setAllParams);
  
  async function action(){
    if (actionText == "Generate") {
      jobStatus = {status:"Starting"};
      waitImage = "working.png";
      actionText = "Cancel";
      let params = getAllParams();
      details = [];
      let resImage = await fetch(inputImageUrl);
      let image = await resImage.blob();
      let res = await generate(params, image, null, feedback);
      if(res.images){
        let initSeed = (res.opt && res.opt.seed);
        details = res.images.map((image,i) => {
          let p = shallowCopy(params);
          if(initSeed != null)
            p.seed = initSeed + i;
          return {params: p, image};
        });
      }
      waitImage = res.status == "error" ? "error.png" : null;
      actionDisabled = false;
      actionText = "Generate";
      jobStatus = null;
    } else if(actionText == "Cancel") {
      waitImage = "cancelling.png";
      actionDisabled = true;
      actionText = "Cancelling...";
      await cancelRequest();
    }
  }
  
  function isOkExt(name, whitelist){
    let ext = name.split(".").slice(-1)[0].toLowerCase();
    return whitelist.some(w => w == ext);
  }
  
  async function handleFile(ev){
    ev.preventDefault();
    console.log(ev);
    let files = [];
    if (ev.dataTransfer.items) {
      files = [...ev.dataTransfer.items].filter(item => item.kind == "file").map(item => item.getAsFile());
    } else {
      files = [...ev.dataTransfer.files];
    }
    let imgFiles = files.filter(file => isOkExt(file.name, ["jpg", "jpeg", "png", "gif"]));
    console.log("number of files: ", imgFiles.length);
    inputImageUrl = URL.createObjectURL(imgFiles[0]);
  }
  function allowDrop(ev) {
    ev.preventDefault();
  }
  function onDelete(){
    inputImageUrl = null;
  }
  
  function send(event, where){
    let url = (typeof event == "string" ? event : event.detail.image);
    where = where || event.detail.where;
    if(where == "img2img"){
      inputImageUrl = url;
      return;
    }
    let detail = getDetailFromUrl(details, url);
    let p = shallowCopy(detail.params);
    p.inputImageUrl = url;
    paramsCanvas.set(p);
    window.location.hash = where;
  }
  
  function save(event){
    let url = (typeof event == "string" ? event : event.detail.image);
    let detail = getDetailFromUrl(details, url);
    let p = shallowCopy(detail.params);
    p.url = url;
    historyStore.append(p);
    window.location.hash = "history";
  }
</script>

<div class="container text-center">
  <Prompt 
    bind:prompt={prompt} 
    bind:negativePrompt={negativePrompt}
    bind:actionText={actionText} actionDisabled={actionDisabled|| !inputImageUrl} on:action={action} 
  />
  <div class="row align-items-start g-0">
    <div class="col">
      <div class="card">
        <div class="card-body">
          {#if inputImageUrl}
            <div class="input_image" style="background-image: url({inputImageUrl})">
              <div class="float-end">
                <div class="btn-group m-2">
                  <button type="button" on:click={onDelete} class="btn btn-sm btn-danger"><i class="bi-trash"></i></button>
                </div>
              </div>
            </div>
          {:else}
            <div class="drop_file_zone" on:drop={handleFile} on:dragover={allowDrop}>
              <div>
                  <p>Drop file here</p>
              </div>
            </div>
          {/if}
        </div>
      </div>
    </div>
    
    <div class="col">
      <div class="card">
        <div class="card-body">
          {#if waitImage}
            <img src={waitImage}>
          {:else}
            <Images details={details} on:send={send} on:save={save} 
              actions={["copy seed", "to img2img", "to canvas", "history"]}
            />
          {/if}
        </div>
      </div>
    </div>
  </div>
    
  <div class="row align-items-start g-0">
    <div class="col">
      <ParametersCard 
        bind:width={width} 
        bind:height={height} 
        bind:classifierStrength={classifierStrength} 
        bind:seed={seed}
        bind:subseed={subseed}
        bind:subseedStrength={subseedStrength}
        bind:nbImages={nbImages}
        bind:samplingSteps={samplingSteps} 
        bind:samplingMethod={samplingMethod}
        bind:restoreFaces={restoreFaces}
        bind:tiling={tiling}
      />
    </div>
    
    <div class="col">
      <ParametersCardImg2Img
        bind:denoiserStrength={denoiserStrength}
      />
      <JobStatus status={jobStatus} />
    </div>
  </div>
</div>

<style>
  .card {
    align-items: center;
  }
  .input_image {
    width: 512px;
    height: 512px;
    background-repeat: no-repeat;
    background-size: contain;
    background-position: center;
  }
  .drop_file_zone {
    background-color: #EEE;
    border: #999 2px dashed;
    width: 512px;
    height: 512px;
    padding: 8px;
    font-size: 18px;
  }
  .drop_file_zone div {
    width:50%;
    margin:0 auto;
  }
  .drop_file_zone div {
    text-align: center;
  }
</style>
