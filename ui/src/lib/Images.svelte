<script>
  import newUniqueId from 'locally-unique-id-generator'
  import { onMount } from 'svelte';
  import {createEventDispatcher} from 'svelte';

  const dispatch = createEventDispatcher();
  export let images = [];
  export let seeds = null;
  let width = 512;
  let current = 0;
  let myCarousel;
  let carouselId = newUniqueId();
  onMount(function(){
    if(images.length == 0)
      return;
    myCarousel.addEventListener('slide.bs.carousel', event => {
      current = event.to;
    });
  });
  function copySeed(){
    navigator.clipboard.writeText(seeds[current]);
  }
  function sendToImg2Img(){
    dispatch('send', {where: "img2img", image: images[current], seed: seeds && seeds[current]});
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
  {#if seeds}
    <button type="button" class="btn btn-success mt-1" on:click={copySeed}>Copy Seed</button>
  {/if}
  <button type="button" class="btn btn-success mt-1" on:click={sendToImg2Img}>Send to img2img</button>
{/if}