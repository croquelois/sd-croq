<script>
  import InputChoices from './InputChoices.svelte';
  import {adminClean, getModels, setModel} from './backend.js'
  import { onMount } from 'svelte';
  
  let models = [];
  let currentModel = "";
  
  let requestPending = 0;
  async function onAdminClean(){
    requestPending++
    await adminClean();
    requestPending--
  }
  async function onSelectModel(){
    requestPending++
    await setModel(currentModel);
    requestPending--
  }
  async function refreshModels(){
    requestPending++
    let ret = await getModels();
    if(ret.status != "ok"){
      console.log(ret);
    }else{
      models = ret.list;
      currentModel = ret.model;
    }
    requestPending--
  }
  onMount(function(){
    refreshModels();
  });
  
</script>

<div class="container text-center">    
  <div class="row align-items-start g-0">
    <button type="button" class="btn btn-danger" disabled={requestPending} on:click={onAdminClean}>
      Clean dangling files
    </button>
    <div class="input-group">
      <span class="input-group-text">Model</span>
      <select class="form-select" bind:value={currentModel} >
        {#each models as model (model)}
          <option value={model}>{model}</option>
        {/each}
      </select>
      <button type="button" class="btn btn-primary" disabled={requestPending} on:click={onSelectModel}>
        Select
      </button>
    </div>
  </div>
</div>
