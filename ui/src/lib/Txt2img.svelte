<script>
  import Prompt from './Prompt.svelte';
  import ParametersCard from './ParametersCard.svelte';
  import JobStatus from './JobStatus.svelte';
  import Images from './Images.svelte';
  import { params } from './paramsStore.js';
  import { historyStore } from './historyStore.js';
  import {generate, interpolateRequest, cancelRequest} from './backendLogic.js'
  import InputText from './InputText.svelte';
  
  
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
  
  let images = [];
  let seeds = null;
  let details = [];
  let video = null;
  
  let actionText = "Generate";
  let actionDisabled = false;
  let waitImage = null;
  let jobStatus = null;
  
  function feedback(status){
    console.log("feedback", status);
    jobStatus = status;
  }
  
  function getAllParams(){
    console.log(typeof samplingSteps);
    return {prompt, negativePrompt, width, height, classifierStrength, seed, subseed, subseedStrength, nbImages, samplingSteps, samplingMethod, restoreFaces, tiling};
  }
  
  async function action(){
    if (actionText == "Generate") {
      jobStatus = {status:"Starting"};
      waitImage = "working.png";
      actionText = "Cancel";
      let res = await generate(getAllParams(), null, null, feedback);
      images = res.images || [];
      console.log(res);
      console.log(res.opt);
      if(res.opt && res.opt.seed !== undefined && res.opt.seed !== null)
        seeds = images.map((img,i) => res.opt.seed + i);
      else
        seeds = null;
      console.log(seeds);
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
  
  function send(event){
    let p = getAllParams();
    p.seed = event.detail.seed;
    p.inputImageUrl = event.detail.image;
    params.set(p);
    window.location.hash = event.detail.where;
  }
  
  function save(event){
    let p = getAllParams();
    p.seed = event.detail.seed;
    p.url = event.detail.image;
    historyStore.append(p);
    window.location.hash = "history";
  }
  
  let nbQueued = 0;
  
  async function regenerateImage(event){
    if (actionText != "Generate")
      return;
    let url = event.target ? event.target.dataset.url : event.detail;
    let pos = images.findIndex(img => img == url);
    if(pos == -1)
      return;
    let p = getAllParams();
    p.seed = seeds[pos];
    p.nbImages = 1;
    jobStatus = {status:"Starting"};
    waitImage = "working.png";
    actionText = "Cancel";
    let res = await generate(p, null, null, feedback);
    if(res.images && res.images.length == 1)
      images[pos] = res.images[0];
    waitImage = res.status == "error" ? "error.png" : null;
    actionDisabled = false;
    actionText = "Generate";
    jobStatus = null;
  }
  
  let viewModeName = "Carousel";
  function onViewMode(){
    if(viewModeName == "Carousel")
      viewModeName = "Grid";
    else
      viewModeName = "Carousel";
  }
  
</script>

<div class="container text-center">
  <Prompt 
    bind:prompt={prompt} 
    bind:negativePrompt={negativePrompt}
    bind:actionText={actionText} bind:actionDisabled={actionDisabled} on:action={action} 
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
      
      <JobStatus status={jobStatus} nbQueued={nbQueued} />
    </div>
    
    <div class="col">
      <div class="card">
        <div class="card-body">
          {#if waitImage || viewModeName == "Grid"}
            <img src={waitImage || "success.png"}>
          {:else}
            <Images images={images} seeds={seeds} on:send={send} on:save={save} on:regenerate={regenerateImage} hasRegenerate=true />
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
    <div class="d-flex flex-wrap">
      {#each images as url (url)}
        <div>
          <img src={url} class="img-fluid rounded" style="height: 196px" data-url={url} on:click={regenerateImage}>
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
