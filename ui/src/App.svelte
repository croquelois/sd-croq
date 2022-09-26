<script>
  import { onMount } from 'svelte';
  import Txt2img from './lib/Txt2img.svelte';
  import Img2img from './lib/Img2img.svelte';
  import Canvas from './lib/Canvas.svelte';
  import Lab from './lib/Lab.svelte';
  import History from './lib/History.svelte';
  
  let tabs = ["txt2img", "img2img", "canvas", "lab", "history"];
  
  let tab = "txt2img";
  function routeTab(){
    let newTab = window.location.href.split("#")[1];
    if(tabs.indexOf(newTab) == -1)
      newTab = "txt2img";
    if(newTab == tab)
      return;
    tab = newTab;
  }
  routeTab();
  
  window.addEventListener('hashchange', routeTab);

  function changeTab(event){
    tab = event.srcElement.getAttribute("href");
    window.location.hash = tab;
  }
  
  
</script>

<main>
  <ul class="nav nav-tabs" role="tablist">
    {#each tabs as t (t)}
      <li class="nav-item" role="presentation">
        <a href="#{t}" on:click={changeTab} class="nav-link" class:active={tab == t} type="button" role="tab">{t}</a>
      </li>
    {/each}
  </ul>
  <div class="tab-content">
    <div class="tab-pane fade" class:show={tab == "txt2img"} class:active={tab == "txt2img"} role="tabpanel" tabindex="0">
      <Txt2img />
    </div>
    <div class="tab-pane fade" class:show={tab == "img2img"} class:active={tab == "img2img"} role="tabpanel" tabindex="1">
      <Img2img />
    </div>
    <div class="tab-pane fade" class:show={tab == "lab"} class:active={tab == "lab"} role="tabpanel" tabindex="2">
      <Lab />
    </div>
    <div class="tab-pane fade" class:show={tab == "canvas"} class:active={tab == "canvas"} role="tabpanel" tabindex="2">
      <Canvas />
    </div>
    <div class="tab-pane fade" class:show={tab == "history"} class:active={tab == "history"} role="tabpanel" tabindex="3">
      <History />
    </div>
  </div>
</main>


<style>
</style>
