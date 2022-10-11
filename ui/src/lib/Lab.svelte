<script>
  import JobStatus from './JobStatus.svelte';
  import Images from './Images.svelte';
  import { paramsLab } from './paramsStore.js';
  import {cancelRequest, faceCorrectionRequest, upscaleRequest, interrogateRequest} from './backendLogic.js'
    
  let inputImageUrl = null;
  let resultImage = null;
  let resultPrompt = "";
  let actionDisabled = false;
  let waitImage = "noImage.png";
  let jobStatus = null;
  let correctFaceBtnText = "Correct Face";
  let interrogateBtnText = "Interrogate";
  let upscaleBtnText = "Upscale";
  let currentAction = "";
  
  function feedback(status){
    console.log("feedback", status);
    jobStatus = status;
  }
  
  function setAllParams(p){
    if(p.inputImageUrl)
      inputImageUrl = p.inputImageUrl;
  }
  paramsLab.subscribe(setAllParams);
  
  async function correctFace(){
    if(correctFaceBtnText == "Correct Face") {
      jobStatus = {status:"Starting"};
      waitImage = "working.png";
      correctFaceBtnText = "Cancel";
      currentAction = "Correct Face";
      let resImage = await fetch(inputImageUrl);
      let image = await resImage.blob();
      let res = await faceCorrectionRequest(image, feedback);
      resultImage = (res.images || [])[0] || null;
      waitImage = res.status == "error" ? "error.png" : null;
      actionDisabled = false;
      currentAction = "";
      correctFaceBtnText = "Correct Face";
      jobStatus = null;
    } else if(correctFaceBtnText == "Cancel") {
      waitImage = "cancelling.png";
      actionDisabled = true;
      correctFaceBtnText = "Cancelling...";
      await cancelRequest();
    }
  }
  
  async function interrogate(){
    if(interrogateBtnText == "Interrogate") {
      jobStatus = {status:"Starting"};
      waitImage = "working.png";
      interrogateBtnText = "Cancel";
      currentAction = "Interrogate";
      resultPrompt = "";
      let resImage = await fetch(inputImageUrl);
      let image = await resImage.blob();
      let res = await interrogateRequest(image, feedback);
      resultPrompt = res.prompt || "";
      resultImage = null;
      waitImage = res.status == "error" ? "error.png" : "noImage.png";
      actionDisabled = false;
      currentAction = "";
      interrogateBtnText = "Interrogate";
      jobStatus = null;
    } else if(interrogateBtnText == "Cancel") {
      waitImage = "cancelling.png";
      actionDisabled = true;
      interrogateBtnText = "Cancelling...";
      await cancelRequest();
    }
  }
  
  async function upscale(){
    if(upscaleBtnText == "Upscale") {
      jobStatus = {status:"Starting"};
      waitImage = "working.png";
      interrogateBtnText = "Cancel";
      currentAction = "Upscale";
      let resImage = await fetch(inputImageUrl);
      let image = await resImage.blob();
      let res = await upscaleRequest(image, feedback);
      resultImage = (res.images || [])[0] || null;
      waitImage = res.status == "error" ? "error.png" : null;
      actionDisabled = false;
      upscaleBtnText = "Upscale";
      currentAction = "";
      jobStatus = null;
    } else if(upscaleBtnText == "Cancel") {
      waitImage = "cancelling.png";
      actionDisabled = true;
      upscaleBtnText = "Cancelling...";
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
          {#if (waitImage || !resultImage)}
            <img src={waitImage}>
          {:else}
            <img src={resultImage}>
          {/if}
        </div>
        <JobStatus status={jobStatus} />
      </div>
    </div>
  </div>
    
  <div class="row align-items-start g-0">
    <button type="button" class="btn btn-primary mt-1" 
          disabled={actionDisabled || !inputImageUrl || (currentAction && currentAction != "Correct Face")} 
          on:click={correctFace}>{correctFaceBtnText}</button>
    <button type="button" class="btn btn-primary mt-1"
          disabled={actionDisabled || !inputImageUrl || (currentAction && currentAction != "Upscale")}
          on:click={upscale}>{upscaleBtnText}</button>
    <div class="input-group mt-1">
      <button class="btn btn-primary" type="button"
            disabled={actionDisabled || !inputImageUrl|| (currentAction && currentAction != "Interrogate")}
            on:click={interrogate}>{interrogateBtnText}</button>
      <input type="text" readonly class="form-control" value={resultPrompt}>
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
