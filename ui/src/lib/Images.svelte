<script>
  import newUniqueId from 'locally-unique-id-generator'
  import { onMount } from 'svelte';
  import {createEventDispatcher} from 'svelte';

  const dispatch = createEventDispatcher();
  export let images = [];
  export let seeds = null;
  export let hasRegenerate = false;
  
  let width = 512;
  let current = 0;
  let alreadySaved = false;
  let myCarousel;
  let carouselId = newUniqueId();
  onMount(function(){
    if(images.length == 0)
      return;
    myCarousel.addEventListener('slide.bs.carousel', event => {
      current = event.to;
      alreadySaved = false;
    });
  });
  function copySeed(){
    navigator.clipboard.writeText(seeds[current]);
  }
  function onRegenerate(event){
    dispatch('regenerate', images[current]);
  }
  function sendToImg2Img(){
    dispatch('send', {where: "img2img", image: images[current], seed: seeds && seeds[current]});
  }
  function sendToCanvas(){
    dispatch('send', {where: "canvas", image: images[current], seed: seeds && seeds[current]});
  }
  function save(){
    alreadySaved = true;
    dispatch('save', {image: images[current], seed: seeds && seeds[current]});
  }
  function onLoad(event){
    let newWidth = event.currentTarget.clientWidth;
    if(newWidth > width)
      width = newWidth;
  }
</script>

{#if images.length == 0}
  <img src="noImage.png" />
{:else}
  <div bind:this={myCarousel} id={carouselId} class="carousel slide" data-bs-interval="false" style="width: {width}px">
    <div class="carousel-indicators">
      {#each images as image,index (index)}
        <button type="button" data-bs-target={"#"+carouselId} data-bs-slide-to={index} class:active={index == 0}></button>
      {/each}
    </div>
    <div class="carousel-inner">
      {#each images as image,index (index)}
        <div class="carousel-item" class:active={index == 0}>
          <img on:load={onLoad} src={image} class="d-block" alt="...">
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
    {#if seeds}
      <button type="button" class="btn btn-outline-primary" on:click={copySeed}>Copy Seed</button>
    {/if}
    {#if hasRegenerate}
      <button type="button" class="btn btn-outline-primary" on:click={onRegenerate}>Regenerate</button>
    {/if}
    <button type="button" class="btn btn-outline-primary" on:click={sendToImg2Img}>To img2img</button>
    <button type="button" class="btn btn-outline-primary" on:click={sendToCanvas}>To canvas</button>
    <button type="button" class="btn btn-outline-primary" disabled={alreadySaved} on:click={save}>To history</button>
  </div>
{/if}