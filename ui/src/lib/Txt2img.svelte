<script>
  import Prompt from './Prompt.svelte';
  import ParametersCard from './ParametersCard.svelte';
  import JobStatus from './JobStatus.svelte';
  import Images from './Images.svelte';
  import { paramsCanvas, paramsImg2Img, paramsTxt2Img } from './paramsStore.js';
  import { historyStore } from './historyStore.js';
  import {generate, interpolateRequest, cancelRequest} from './backendLogic.js'
  import InputText from './InputText.svelte';
  import InputRange from './InputRange.svelte';
  import ButtonOptions from './ButtonOptions.svelte';
  import {shallowCopy} from './utils.js';
  import {getDetailFromUrl, getAndlockDetail, unlockAndUpdateDetail} from './detailMgmtUtils.js';
  
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
  
  // Experimental
  let experimental = false
  let perlinStrength = 0.0;
  let perlinOctave = 6.0;
  let perlinScale = 5.0;
  // ************
  
  let details = [];
  
  let actionText = "Generate";
  let actionDisabled = false;
  let waitImage = null;
  let jobStatus = null;
  
  function feedback(status){
    jobStatus = status;
  }
  
  function getAllParams(){
    let p = {prompt, negativePrompt, width, height, classifierStrength, seed, subseed, subseedStrength, nbImages, samplingSteps, samplingMethod, restoreFaces, tiling};
    if(experimental){
      p.perlinStrength = perlinStrength;
      p.perlinOctave = perlinOctave;
      p.perlinScale = perlinScale;
    }
    return p;
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
  }
  paramsTxt2Img.subscribe(setAllParams);
  
  async function action(){
    if (actionText == "Generate") {
      jobStatus = {status:"Starting"};
      waitImage = "working.png";
      actionText = "Cancel";
      let params = getAllParams();
      details = [];
      let res = await generate(params, null, null, feedback);
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
  
  function send(event, where){
    let url = (typeof event == "string" ? event : event.detail.image);
    where = where || event.detail.where;
    let detail = getDetailFromUrl(details, url);
    let p = shallowCopy(detail.params);
    p.inputImageUrl = url;
    if(where == "img2img")
      paramsImg2Img.set(p);
    else if(where == "canvas")
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
  
  let nbQueued = 0;
  
  async function regenerateImage(event){
    if (actionText != "Generate")
      return;
    let url = (typeof event == "string" ? event : event.detail.image);
    let detail = getAndlockDetail(details, url);
    if (!detail)
      return;
    let p = getAllParams();
    p.seed = detail.params.seed;
    p.nbImages = 1;
    if(!jobStatus)
      jobStatus = {status:"Starting"};
    waitImage = "working.png";
    nbQueued++;
    let res = await generate(p, null, null, feedback);
    if(res.images && res.images.length == 1){
      details = unlockAndUpdateDetail(details, url, p, res.images[0]);
    }else{
      details = unlockAndUpdateDetail(details, url, null, null, "error");
    }
    nbQueued--;
    if(nbQueued == 0){
      waitImage = res.status == "error" ? "error.png" : null;
      jobStatus = null;
    }
  }
  
  let viewModeName = "Carousel";
  function onViewMode(){
    if(viewModeName == "Carousel")
      viewModeName = "Grid";
    else
      viewModeName = "Carousel";
  }
  
  let optionsGridAction = ["Regenerate", "Fullscreen", "Send to img2img", "Send to history"];
  let currentGridAction = optionsGridAction[0];
  
  function onGridAction(event){
    let url = (event.target && event.target.dataset.url) || (event.detail && event.detail.image) || event;
    if(currentGridAction == "Regenerate")
      return regenerateImage(url);
    if(currentGridAction == "Send to img2img")
      return send(url, "img2img");
    if(currentGridAction == "Send to history")
      return save(url);
  }
  
</script>

<div class="container text-center">
  <Prompt 
    bind:prompt={prompt} 
    bind:negativePrompt={negativePrompt}
    bind:actionText={actionText} actionDisabled={actionDisabled || nbQueued} on:action={action} 
  />
          
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
      {#if experimental}
        <InputNumber title="perlin strength" bind:value={perlinStrength} />
        <InputNumber title="perlin octave" bind:value={perlinOctave} />
        <InputNumber title="perlin scale" bind:value={perlinOctave} />
      {/if}
      <JobStatus status={jobStatus} nbQueued={nbQueued} />
    </div>
    
    <div class="col">
      <div class="card">
        <div class="card-body">
          {#if waitImage || viewModeName == "Grid"}
            <img src={waitImage || "success.png"}>
          {:else}
            <Images details={details} on:send={send} on:save={save} on:regenerate={regenerateImage}
              actions={["copy seed", "regenerate", "to img2img", "to canvas", "history"]}
            />
          {/if}
          
        </div>
      </div>
      <div class="card">
        <div class="card-body">
          <button type="button" class="btn btn-info" on:click={onViewMode}>Mode: {viewModeName}</button>
        </div>
      </div>
    </div>
  </div>
  
  {#if viewModeName == "Grid"}
    <ButtonOptions bind:current={currentGridAction} options={optionsGridAction} />
    <div class="d-flex flex-wrap">
      {#each details as detail,pos (pos)}
        <div>
          <img src={detail.image} class="img-fluid rounded" style="height: 196px" data-url={detail.image} on:click={onGridAction}>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .card-body {
    padding: 0
  }
  .card {
    align-items: center;
  }
</style>
