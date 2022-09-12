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
  
  async function action(){
    if (actionText == "Generate") {
      jobStatus = {status:"Starting"};
      waitImage = "working.png";
      actionText = "Cancel";
      let res = await generate(getAllParams(), null, feedback);
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
</script>

<div class="container text-center">
  <div class="row align-items-start g-0">
    <div class="card" style="align-items: normal">
      <div class="card-body">
        <div class="input-group mb-3">
          <input type="text" class="form-control" placeholder="Enter your prompt here" bind:value={prompt}>
          <button class="btn btn-primary" type="button" disabled={actionDisabled} on:click={action}>{actionText}</button>
        </div>
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
      <ParametersCard2 
        bind:samplingSteps={samplingSteps} 
        bind:samplingMethod={samplingMethod} 
        bind:denoiserStrength={denoiserStrength} 
        bind:denoiserStrengthFactor={denoiserStrengthFactor}
        bind:nbLoopback={nbLoopback}
        bind:saveLoopback={saveLoopback}
      />
      <JobStatus status={jobStatus} />
    </div>
    
    <div class="col">
      <div class="card">
        <div class="card-body">
          {#if waitImage}
            <img src={waitImage}>
          {:else}
            <Images images={images} seeds={seeds} on:send={send}/>
          {/if}
        </div>
      </div>
    </div>
  </div>
</div>

<style>
  .card {
    align-items: center;
  }
</style>
