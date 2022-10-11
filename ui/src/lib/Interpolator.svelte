<script>
  import Prompt from './Prompt.svelte';
  import ParametersCard from './ParametersCard.svelte';
  import JobStatus from './JobStatus.svelte';
  import Images from './Images.svelte';
  import {generate, interpolateRequest, cancelRequest} from './backendLogic.js'
  import InputText from './InputText.svelte';
  import InputNumber from './InputNumber.svelte';
  
  let width = 512;
  let height = 512;
  let classifierStrength = 12;
  let samplingSteps = 20;
  let samplingMethod = "DDIM";
  let tiling = false;
  
  let video = null;
  
  let actionText = "Generate";
  let actionDisabled = false;
  let waitImage = null;
  let jobStatus = null;
  
  let id = 1;
  let steps = [];
  onAdd();
  let nbImages = 15;
  let framesBySec = 15;
  
  function feedback(status){
    console.log("feedback", status);
    jobStatus = status;
  }
  
  function getAllParams(){
    return {
      width, 
      height, 
      classifierStrength, 
      nbImages: parseInt(nbImages), 
      framesBySec: parseInt(framesBySec),
      samplingSteps, 
      samplingMethod, 
      tiling,
      steps
    };
  }
    
  async function action(){
    if (actionText == "Generate") {
      let p = getAllParams();
      jobStatus = {status:"Starting"};
      waitImage = "working.png";
      actionText = "Cancel";
      video = null;
      let res = await interpolateRequest(p, feedback);
      video = res.video;
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
  
  function onAdd(){
    steps = [...steps, {id:id++,seed:"",prompt:""}];
  }
  
  function onDelete(event){
    let id = event.target.dataset.id;
    steps = steps.filter(s => s.id != id);
  }
  
  function switchPos(p1,p2){
    let tmp = steps[p1];
    steps[p1] = steps[p2];
    steps[p2] = tmp;
    steps = steps;
  }
  
  function onMove(event, dir){
    let id = event.target.dataset.id;
    let n = steps.length;
    let pos = steps.findIndex(s => s.id == id);
    let pos2 = (pos+dir+n)%n;
    switchPos(pos,pos2);
  }
  
  function onUp(event){
    onMove(event, -1);
  }
  
  function onDown(event){
    onMove(event, +1);
  }
</script>

<div class="container text-center">
  <div class="card">
    <div class="card-body">
      <div class="input-group">
        <span class="input-group-text">Number of images:</span>
        <input type="text" class="form-control" bind:value={nbImages}>
        <span class="input-group-text">Frames by seconds:</span>
        <input type="text" class="form-control" bind:value={framesBySec}>
      </div>
      {#each steps as step (step.id)}
        <div class="input-group">
          <span class="input-group-text">Seed:</span>
          <input type="text" class="form-control" bind:value={step.seed}>
          <span class="input-group-text">Prompt:</span>
          <input type="text" class="form-control" bind:value={step.prompt} style="width: 60%">
          <button type="button" class="btn btn-outline-danger" data-id={step.id} on:click={onDelete}><i class="bi bi-trash"></i></button>
          <button type="button" class="btn btn-outline-secondary" data-id={step.id} on:click={onUp}><i class="bi bi-chevron-up"></i></button>
          <button type="button" class="btn btn-outline-secondary" data-id={step.id} on:click={onDown}><i class="bi bi-chevron-down"></i></button>
        </div>
      {/each}
      <button type="button" class="btn btn-success" on:click={onAdd}><i class="bi bi-plus-circle"></i> New Step</button>
      <button type="button" class="btn btn-primary" disabled={actionDisabled || steps.length<2} on:click={action}>{actionText}</button>
    </div>
  </div>
  <div class="row align-items-start g-0">
    <div class="col">
      <ParametersCard 
        bind:width={width} 
        bind:height={height} 
        bind:classifierStrength={classifierStrength} 
        bind:samplingSteps={samplingSteps} 
        bind:samplingMethod={samplingMethod}
        bind:tiling={tiling}
        
        hide={["seed","subseed","subseedStrength","restoreFaces","nbImages"]}
      />
      <JobStatus status={jobStatus} />
    </div>
    
    <div class="col">
      <div class="card">
        <div class="card-body">
          {#if video}
            <video controls>
              <source src={video}>
            </video>
          {:else}
            <img src={waitImage || "success.png"}>
          {/if}
        </div>
      </div>
    </div>
  </div>
</div>

<style>
  .card-body {
    padding: 0;
    width: 100%;
  }
  .card {
    align-items: center;
  }
  .btn i {
    pointer-events: none;
  }
</style>
