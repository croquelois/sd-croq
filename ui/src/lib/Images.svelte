<script>
  import newUniqueId from 'locally-unique-id-generator'
  import { onMount } from 'svelte';
  import {createEventDispatcher} from 'svelte';
  
  const dispatch = createEventDispatcher();
  export let details = [];
  export let hasRegenerate = false;
  export let actions = [];
  
  let width = 512;
  let current = 0;
  let alreadySaved = false;
  let myCarousel;
  let carouselId = newUniqueId();
  onMount(function(){
    if(details.length == 0)
      return;
    myCarousel.addEventListener('slide.bs.carousel', event => {
      current = event.to;
      alreadySaved = false;
    });
  });
  function copySeed(){
    navigator.clipboard.writeText(details[current].params.seed);
  }
  function onRegenerate(event){
    dispatch('regenerate', details[current]);
  }
  function sendToImg2Img(){
    dispatch('send', {where: "img2img", ...(details[current])});
  }
  function sendToCanvas(){
    dispatch('send', {where: "canvas", ...(details[current])});
  }
  function sendToLab(){
    dispatch('send', {where: "lab", ...(details[current])});
  }
  function save(){
    alreadySaved = true;
    dispatch('save', details[current]);
  }
  function onLoad(event){
    let newWidth = event.currentTarget.clientWidth;
    if(newWidth > width)
      width = newWidth;
  }
</script>

{#if details.length == 0}
  <img src="noImage.png" />
{:else}
  <div bind:this={myCarousel} id={carouselId} class="carousel slide" data-bs-interval="false" style="width: {width}px">
    <div class="carousel-indicators">
      {#each details as detail,index (index)}
        <button type="button" data-bs-target={"#"+carouselId} data-bs-slide-to={index} class:active={index == 0}></button>
      {/each}
    </div>
    <div class="carousel-inner">
      {#each details as detail,index (index)}
        <div class="carousel-item" class:active={index == 0}>
          <img on:load={onLoad} src={detail.image} class="d-block" alt="...">
        </div>
      {/each}
    </div>
    <button class="carousel-control-prev" type="button" data-bs-target={"#"+carouselId} data-bs-slide="prev">
      <span class="carousel-control-prev-icon" aria-hidden="true"></span>
      <span class="visually-hidden">Previous</span>
    </button>
    <button class="carousel-control-next" type="button" data-bs-target={"#"+carouselId} data-bs-slide="next">
      <span class="carousel-control-next-icon" aria-hidden="true"></span>
      <span class="visually-hidden">Next</span>
    </button>
  </div>
  <div class="btn-group mt-1" role="group">
    {#if actions.indexOf("copy seed") != -1}
      <button type="button" class="btn btn-outline-primary" on:click={copySeed}>Copy Seed</button>
    {/if}
    {#if actions.indexOf("regenerate") != -1}
      <button type="button" class="btn btn-outline-primary" on:click={onRegenerate}>Regenerate</button>
    {/if}
    {#if actions.indexOf("to img2img") != -1}
      <button type="button" class="btn btn-outline-primary" on:click={sendToImg2Img}>To img2img</button>
    {/if}
    {#if actions.indexOf("to canvas") != -1}
      <button type="button" class="btn btn-outline-primary" on:click={sendToCanvas}>To canvas</button>
    {/if}
    {#if actions.indexOf("to lab") != -1}
      <button type="button" class="btn btn-outline-primary" on:click={sendToLab}>To lab</button>
    {/if}
    {#if actions.indexOf("history") != -1}
      <button type="button" class="btn btn-outline-primary" disabled={alreadySaved} on:click={save}>To history</button>
    {/if}
  </div>
{/if}