<script>
  import Prompt from './Prompt.svelte';
  import ParametersCard from './ParametersCard.svelte';
  import ParametersCardImg2Img from './ParametersCardImg2Img.svelte';
  import JobStatus from './JobStatus.svelte';
  import Images from './Images.svelte';
  import { params } from './paramsStore.js';
  import {generate, cancelRequest} from './backendLogic.js'
  import InputNumber from './InputNumber.svelte';
  import { onMount } from 'svelte';
  import InputCheckbox from './InputCheckbox.svelte';
  import InputChoices from './InputChoices.svelte';
  import InputRange from './InputRange.svelte';
  import InputText from './InputText.svelte';
  import { MyMask } from './MyMask.js';
  import {loadImage,drawGradientImage} from './imageUtil.js';
  import {mouse} from './mouse.js';

  export let canvasWidth = 1024;
  export let canvasHeight = 1024;
  
  let myMask;
  let isDrawMyMaskMode = false;
  let maskBrushColor = "white";
  let maskBrushSize = 20;
  
  let prompt = "beautiful forest landscape, germany, photography";
  let width = 512;
  let height = 512;
  let negativePrompt = "";
  let classifierStrength = 12;
  let subseedStrength = 0.0;
  let seed = null;
  let subseed = null;
  let nbImages = 1;
  let samplingSteps = 20;
  let samplingMethod = "DDIM";
  let restoreFaces = false;
  let tiling = false;
  
  let denoiserStrength = 1.00;
  
  let actionText = "Generate";
  let actionDisabled = false;
  let waitImage = null; // @@CROQ@@ did I need it ?
  let jobStatus = null;
  
  let refresh = true;
  
  let activate = true; // debug stuff
  
  let selectedImage = null;
  let images = [];
  
  let selectedMask = null;
  let selectedAlphaMask = null;
  let maskImages = [];
  
  let myCanvas;
  let ctx = null;
  let rect = null;
  let currentCanvasImage = null;
  
  let alphaToApply = null;
  
  let inpaintMask = true;
  let inpaintingFill = "latent noise";
  let maskBlur = 5;
  let inpaintingFillMethod = ['fill', 'original', 'latent noise', 'latent nothing'];
    
  function feedback(status){
    jobStatus = status;
  }
  
  function getAllParams(){
    return {
      prompt, negativePrompt, width, height, useAlpha: true, classifierStrength,
      seed, subseed, subseedStrength, nbImages, samplingSteps, samplingMethod, restoreFaces, tiling, denoiserStrength,
      inpaintingFill, inpaintMask, inpaintingFullRes: false, maskBlur};
  }
  
  async function loadImageAndApplyGradient(url){
    if(!alphaToApply)
      return await loadImage(url);
    let image = await loadImage(url);
    let canvas = document.createElement('canvas');
    let ctx = canvas.getContext('2d');
    canvas.width = width;
    canvas.height = height;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(image, 0, 0);
    let imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    let w = imageData.width;
    let h = imageData.height;
    for(let x=0;x<w;x++){
      for(let y=0;y<h;y++){
        let off = (y*w + x)*4 + 3;
        let a = 1-alphaToApply[off];
        imageData.data[off] = Math.floor(a*255);
      }
    }
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.putImageData(imageData, 0, 0);
    return await loadImage(canvas.toDataURL());
  }
  
  function getSelectedImage(){
    let canvas = document.createElement('canvas');
    let ctx = canvas.getContext('2d');
    let w = width;
    let h = height;
    canvas.width = canvasWidth;
    canvas.height = canvasHeight;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(currentCanvasImage, 0, 0);
    let imageData = ctx.getImageData(rect.x1, rect.y1, w, h);
    canvas.width = w;
    canvas.height = h;
    ctx.clearRect(0, 0, w, h);
    ctx.putImageData(imageData, 0, 0);
    alphaToApply = [];
    for(let x=0;x<w;x++){
      for(let y=0;y<h;y++){
        let off = (y*w + x)*4 + 3; // alpha
        // 255 mean opaque, 0 mean transparent
        alphaToApply[off] = (imageData.data[off]/255);
      }
    }
    return new Promise(res => canvas.toBlob(res));
  }
  
  // need to run getSelectedImage first
  function getMaskImage(alphaToApply){
    let canvas = document.createElement('canvas');
    let ctx = canvas.getContext('2d');
    let w = width;
    let h = height;
    canvas.width = w;
    canvas.height = h;
    ctx.clearRect(0, 0, w, h);
    if(selectedMask)
      ctx.drawImage(selectedMask, 0, 0);
    let gradientData = ctx.getImageData(0, 0, w, h);
    for(let x=0;x<w;x++){
      for(let y=0;y<h;y++){
        let off = (y*w + x)*4 + 3; // alpha, but I do -1 later, so it's blue
        // 255 mean opaque, 0 mean transparent
        alphaToApply[off] *= (1-gradientData.data[off-1]/255);
      }
    }
    return new Promise(res => canvas.toBlob(res));
  }
  
  async function drawAtCurrentPos(imageUrl){
    let image = await loadImageAndApplyGradient(imageUrl);
    let canvas = document.createElement('canvas');
    let ctx = canvas.getContext('2d');
    canvas.width = canvasWidth;
    canvas.height = canvasHeight;
    ctx.globalCompositeOperation = "source-over";
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(currentCanvasImage, 0, 0);
    ctx.drawImage(image, rect.x1, rect.y1);
    currentCanvasImage = await loadImage(canvas.toDataURL());
    refresh = true;
  }

  async function drawSelectedImage(){
    drawAtCurrentPos(selectedImage.src);
    selectedImage = null;
    isDrawMyMaskMode = false;
    images = [];
    setRefresh();
  }
  async function cancelDrawing(){
    selectedImage = null;
    images = [];
    setRefresh();
  }
        
  async function action(){
    if (actionText == "Generate") {
      jobStatus = {status:"Starting"};
      waitImage = "working.png";
      actionText = "Cancel";
      images = [];
      setRefresh();
      let image = await getSelectedImage();
      let mask = await (isDrawMyMaskMode?myMask.getMaskImage(rect.x1, rect.y1, width, height, alphaToApply):getMaskImage(alphaToApply));
      let res = await generate(getAllParams(), image, mask, feedback);
      images = res.images || [];
      waitImage = res.status == "error" ? "error.png" : null;
      selectedAlphaMask = selectedMask = null;
      setRefresh();
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
  
  
  async function mask2alpha(selectedMask){
    let canvas = document.createElement('canvas');
    let ctx = canvas.getContext('2d');
    let w = width;
    let h = height;
    canvas.width = w;
    canvas.height = h;
    ctx.clearRect(0, 0, w, h);
    ctx.drawImage(selectedMask, 0, 0);
    let imageData = ctx.getImageData(0, 0, w, h);
    for(let x=0;x<w;x++){
      for(let y=0;y<h;y++){
        let off = (y*w + x)*4;
        imageData.data[off+3] = imageData.data[off];
        imageData.data[off+0] = imageData.data[off+1] = imageData.data[off+2] = 255;
      }
    }
    ctx.clearRect(0, 0, w, h);
    ctx.putImageData(imageData, 0, 0);
    return await loadImage(canvas.toDataURL());
  }
  
  async function selectMask(event){
    if(selectedMask == event.target){
      selectedAlphaMask = selectedMask = null;
    }else{
      selectedAlphaMask = await mask2alpha(event.target);
      selectedMask = event.target;
    }
    isDrawMyMaskMode = false;
    setRefresh();
  }
  
  async function selectImage(event){
    if(selectedImage == event.target){
      selectedImage = null;
    }else{
      selectedImage = event.target;
    }
    isDrawMyMaskMode = false;
    setRefresh();
  }
  async function emptyInitialCanvas(){
    let canvas = document.createElement('canvas');
    let ctx = canvas.getContext('2d');
    canvas.width = canvasWidth;
    canvas.height = canvasHeight;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    currentCanvasImage = await loadImage(canvas.toDataURL());
    setRefresh();
  }
  async function drawImageInTheMiddle(imageUrl, p){
    let image = await loadImage(imageUrl);
    let canvas = document.createElement('canvas');
    let ctx = canvas.getContext('2d');
    canvas.width = canvasWidth;
    canvas.height = canvasHeight;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(image, canvas.width/2-p.width/2, canvas.height/2-p.height/2);
    currentCanvasImage = await loadImage(canvas.toDataURL());
    setRefresh();
  }
  params.subscribe(p => drawImageInTheMiddle(p.inputImageUrl,p));
  
  let transparentPattern = null;
  function drawTransparentPattern(ctx){
    let w = myCanvas.width;
    let h = myCanvas.height;
    ctx.clearRect(0, 0, w, h);
    for(let x=0;x<w+10;x+=10)
      for(let y=0;y<h+10;y+=10){
        ctx.fillStyle = ((x + y)/10 % 2) ? "#EEE" : "white";
        ctx.fillRect(x, y, 10, 10);
      }
    transparentPattern = ctx.getImageData(0, 0, w, h);
  }
  
  function clearMask(){
    myMask.clear();
    setRefresh();
  }
  
  function setRefresh(){
    refresh = true;
  }
    
  async function draw() {
      await myMask.prepareImg();
      if(!ctx)
        return;
      ctx.putImageData(transparentPattern, 0, 0);
      myMask.drawImgInto(ctx);
      if(currentCanvasImage)
        ctx.drawImage(currentCanvasImage, 0, 0);
      if(selectedImage){
        ctx.drawImage(await loadImageAndApplyGradient(selectedImage.src), rect.x1, rect.y1);
      }
      if(isDrawMyMaskMode)
        myMask.drawImgInto(ctx);
      ctx.lineWidth = 1;
      ctx.setLineDash([10, 20]);
      ctx.strokeStyle = "red";
      if(rect){
        if(selectedAlphaMask){
          ctx.drawImage(selectedAlphaMask, rect.x1, rect.y1);
        }
        ctx.strokeRect(rect.x1, rect.y1, width, height);
      }
  }
  
  function applySnapToGrid(p){
    if(!snapToGrid){
      let x = Math.floor(p.x);
      let y = Math.floor(p.y);
      return {x,y}
    }
    const gridSize = 128;
    let mx = canvasWidth/2;
    let my = canvasHeight/2;
    let x = mx+Math.round((p.x-mx)/gridSize)*gridSize;
    let y = my+Math.round((p.y-my)/gridSize)*gridSize;
    return {x,y}
  }
  
  async function mainLoop() {
      if (refresh || mouse.button) {
          refresh = false;
          if(!images.length && mouse.button && !isDrawMyMaskMode){
            let {x,y} = applySnapToGrid(mouse);
            rect = {
              x1: x - width/2,
              y1: y - height/2,
              x2: x + width/2,
              y2: y + height/2,
            };
            selectedImage = null;
            images = [];
          }
          if(isDrawMyMaskMode && mouse.button){
            let x = Math.floor(mouse.x);
            let y = Math.floor(mouse.y);
            myMask.draw(x,y,maskBrushSize,maskBrushColor);
          }
          await draw();
      }
      requestAnimationFrame(mainLoop)
  }
  
  onMount(async function(){
    ctx = myCanvas.getContext("2d");
    myMask = new MyMask(canvasWidth, canvasHeight);
    if(activate){
      requestAnimationFrame(mainLoop);
      mouse.start(myCanvas);
    }
    drawTransparentPattern(ctx);
    let maskNames = ["L","R","U","D","LU","LD","RU","RD","LUD","LUR","LDR","RUD","LUDR"];
    maskImages = await Promise.all(maskNames.map(async name => ({name, img: await drawGradientImage(name,false, width, height)})));
    emptyInitialCanvas();
    //drawImageInTheMiddle("working.png", {width:512,height:512});
    rect = {
      x1: canvasWidth/2 - 512/2,
      y1: canvasHeight/2 - 512/2,
      x2: canvasWidth/2 + 512/2,
      y2: canvasHeight/2 + 512/2,
    };
  });
  
  let snapToGrid = false;
  function onSnapToGrid(){
    snapToGrid = !snapToGrid;
  }
</script>


<Prompt 
  bind:prompt={prompt} 
  bind:negativePrompt={negativePrompt}
  bind:actionText={actionText} actionDisabled={actionDisabled} on:action={action} 
/>
<div class="d-flex flex-row">
  <div>
    <InputNumber title="canvas width" bind:value={canvasWidth} />
    <InputNumber title="canvas height" bind:value={canvasHeight} />
    <ParametersCard 
      bind:classifierStrength={classifierStrength} 
      bind:width
      bind:height
      bind:seed={seed}
      bind:subseed={subseed}
      bind:subseedStrength={subseedStrength}
      bind:nbImages={nbImages}
      bind:samplingSteps={samplingSteps} 
      bind:samplingMethod={samplingMethod}
      bind:restoreFaces={restoreFaces}
      bind:tiling={tiling}
    />
    <ParametersCardImg2Img
      bind:denoiserStrength={denoiserStrength}
    />
      
    <div class="card">
      <div class="card-body">
        <InputCheckbox title="inpaint mask" bind:value={inpaintMask} />
        <InputChoices title="inpainting fill" choices={inpaintingFillMethod} bind:value={inpaintingFill} />
        <InputRange title="mask blur" min=0 max=25 step=1 bind:value={maskBlur} />
        <div class="btn-group" role="group">
          <input type="checkbox" class="btn-check" id="btncheck1" bind:checked={isDrawMyMaskMode} on:change={setRefresh} autocomplete="off">
          <label class="btn btn-outline-primary" for="btncheck1">Draw Mask Mode</label>
        </div>
        {#if isDrawMyMaskMode}
          <InputRange title="brush size" min=0 max=100 step=1 bind:value={maskBrushSize} />
          <InputText title="brush color" bind:value={maskBrushColor} />
          <button class="btn btn-danger" type="button" on:click={clearMask}>Clear mask</button>
        {/if}
        
      </div>
    </div>
    <JobStatus status={jobStatus} />
  </div>

  <div >
    <div class="card">
      <div class="card-body">
        <canvas bind:this={myCanvas} width={canvasWidth} height={canvasHeight} style="border:1px solid #000000;">
        </canvas>
      </div>
    </div>
  </div>
  <div >
    <div>
      <button class="btn btn-danger" type="button" on:click={emptyInitialCanvas}>clear canvas</button>
      <button class="btn btn-info" type="button" on:click={onSnapToGrid}>{snapToGrid?"un":""}snap to grid</button>
    </div>
    
    <div >
      {#each maskImages as mask (mask.name)}
        <img width=64 height=64 src={mask.img} class="imgBorder" 
              class:selected={selectedMask && (mask.name==selectedMask.dataset.name)}
              data-name={mask.name}
              on:click={selectMask}/>
      {/each}
    </div>
    <div >
      {#each images as image (image)}
        <img width=64 height=64 src={image} class="imgBorder" 
              class:selected={selectedImage && (image==selectedImage.src)}
              on:click={selectImage}/>
      {/each}
    </div>
    <div>
      {#if images.length}
        <button class="btn btn-primary" type="button" disabled={!selectedImage} on:click={drawSelectedImage}>draw</button>
        <button class="btn btn-secondary" type="button" on:click={cancelDrawing}>cancel</button>
      {/if}
    </div>
  </div>
</div>

<style>
  .imgBorder {
    border: 2px solid;
  }
  .selected {
    border-color: red;
  }
</style>