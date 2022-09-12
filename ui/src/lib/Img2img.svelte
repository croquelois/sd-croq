<script>
  import ParametersCard1 from './ParametersCard1.svelte';
  import ParametersCard2 from './ParametersCard2.svelte';
  import JobStatus from './JobStatus.svelte';
  import Images from './Images.svelte';
  import { params } from './paramsStore.js';
  import {generate, cancelRequest} from './backendLogic.js'
  
  let prompt = "";
  let width = 512;
  let height = 512;
  let classifierStrength = 7.5;
  let seed = null;
  let nbImages = 1;
  
  let samplingSteps = 20;
  let samplingMethod = "DDIM";
  let denoiserStrength = 0.63;
  let denoiserStrengthFactor = 0.50;
  let nbLoopback = 0;
  let saveLoopback = false;
  
  let inputImageUrl = null;
  let images = [];
  let seeds = null;
  
  let actionText = "Generate";
  let actionDisabled = false;
  let waitImage = null;
  let jobStatus = null;
  
  function feedback(status){
    console.log("feedback", status);
    jobStatus = status;
  }
  
  function getAllParams(){
    return {prompt, width, height, classifierStrength, seed, nbImages, samplingSteps, samplingMethod, denoiserStrength, denoiserStrengthFactor, nbLoopback, saveLoopback};
  }
  
  function setAllParams(p){
    if(p.prompt)
      prompt = p.prompt;
    if(p.width)
      width = p.width;
    if(p.height)
      height = p.height;
    if(p.classifierStrength)
      classifierStrength = p.classifierStrength;
    if(p.seed)
      seed = p.seed;
    if(p.nbImages)
      nbImages = p.nbImages;
    if(p.samplingSteps)
      samplingSteps = p.samplingSteps;
    if(p.samplingMethod)
      samplingMethod = p.samplingMethod;
    if(p.denoiserStrength)
      denoiserStrength = p.denoiserStrength;
    if(p.denoiserStrengthFactor)
      denoiserStrengthFactor = p.denoiserStrengthFactor;
    if(p.inputImageUrl)
      inputImageUrl = p.inputImageUrl;
    if(p.nbLoopback)
      nbLoopback = p.nbLoopback;
    if(p.saveLoopback)
      saveLoopback = p.saveLoopback;
  }
  params.subscribe(setAllParams);
  
  async function action(){
    if (actionText == "Generate") {
      jobStatus = {status:"Starting"};
      waitImage = "working.png";
      actionText = "Cancel";
      let resImage = await fetch(inputImageUrl);
      let image = await resImage.blob();
      let res = await generate(getAllParams(), image, feedback);
      images = res.images || [];
      if (res.opt && res.opt.seed !== undefined && res.opt.seed !== null) {
        if (res.opt.nbLoopback > 0 && res.opt.saveLoopback == true) {
          seeds = images.map((img,i) => res.opt.seed + Math.floor(i/res.opt.nbLoopback));
        } else {
          seeds = images.map((img,i) => res.opt.seed + i);
        }
      } else {
        seeds = null;
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
</script>

<div class="container text-center">
  <div class="row align-items-start g-0">
    <div class="card" style="align-items: normal">
      <div class="card-body">
        <div class="input-group mb-3">
          <input type="text" class="form-control" placeholder="Enter your prompt here" bind:value={prompt}>
          <button class="btn btn-primary" type="button" disabled={actionDisabled || !inputImageUrl} on:click={action}>{actionText}</button>
        </div>
      </div>
    </div>
  </div>
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
            <Images images={images} seeds={seeds}/>
          {/if}
        </div>
        <JobStatus status={jobStatus} />
      </div>
    </div>
  </div>
    
  <div class="row align-items-start g-0">
    <div class="col">
      <ParametersCard1 
        bind:width={width} 
        bind:height={height} 
        bind:classifierStrength={classifierStrength} 
        bind:seed={seed}
        bind:nbImages={nbImages}
      />
    </div>
    
    <div class="col">
      <ParametersCard2 
        bind:samplingSteps={samplingSteps} 
        bind:samplingMethod={samplingMethod} 
        bind:denoiserStrength={denoiserStrength} 
        bind:denoiserStrengthFactor={denoiserStrengthFactor}
        bind:nbLoopback={nbLoopback}
        bind:saveLoopback={saveLoopback}
      />
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
