<script>
  import InputNumber from './InputNumber.svelte';
  import { onMount } from 'svelte';

  export let width = 1024;
  export let height = 1024;
  
  let myCanvas;
  let ctx = null;
  let rect = null;
  
  const mouse = {
      button : false,
      x : 0,
      y : 0,
      down : false,
      up : false,
      element : null,
      event(e) {
          const m = mouse;
          m.bounds = m.element.getBoundingClientRect();
          m.x = e.pageX - m.bounds.left - scrollX;
          m.y = e.pageY - m.bounds.top - scrollY;
          const prevButton = m.button;
          m.button = e.type === "mousedown" ? true : e.type === "mouseup" ? false : mouse.button;
          if (!prevButton && m.button) { m.down = true }
          if (prevButton && !m.button) { m.up = true }
      },
      start(element) {
          mouse.element = element;
          "down,up,move".split(",").forEach(name => document.addEventListener("mouse" + name, mouse.event));
      }
  }
  function loadImage(url) {
      const image = new Image();
      image.src = url;
      image.onload = () => refresh = true;
      return image;
  }
  //const baseImage = new Image(width, height);
  
  let transparentPattern = null;
  function drawTransparentPattern(ctx){
    ctx.clearRect(0, 0, width, height);
    for(let x=0;x<width+10;x+=10)
      for(let y=0;y<height+10;y+=10){
        ctx.fillStyle = ((x + y)/10 % 2) ? "#EEE" : "white";
        ctx.fillRect(x, y, 10, 10);
      }
    transparentPattern = ctx.getImageData(0, 0, width, height);
  }
  function draw() {
      if(!ctx)
        return;
      ctx.clearRect(0, 0, width, height);
      if(!transparentPattern)
        drawTransparentPattern(ctx);
      else
        ctx.putImageData(transparentPattern, 0,0 )
          
      //ctx.drawImage(baseImage, 0, 0, ctx.canvas.width, ctx.canvas.width);
      ctx.lineWidth = 1;
      ctx.setLineDash([10, 20]);
      ctx.strokeStyle = "red";
      if(rect)
        ctx.strokeRect(rect.x1, rect.y1, 512, 512);
  }
  
  let refresh = true;
  function mainLoop() {
      if (refresh || mouse.button) {
          refresh = false;
          rect = {
            x1: mouse.x - 256,
            y1: mouse.y - 256,
            x2: mouse.x + 256,
            y2: mouse.y + 256,
          };
          draw();
      }
      requestAnimationFrame(mainLoop)
  }
  
  onMount(function(){
    //requestAnimationFrame(mainLoop);
    ctx = myCanvas.getContext("2d");
    //mouse.start(myCanvas);
  });
</script>
<div>
  <InputNumber title="width" bind:value={width} />
  <InputNumber title="height" bind:value={height} />
  <canvas bind:this={myCanvas} width={width} height={height} style="border:1px solid #000000;">
  </canvas>

</div>