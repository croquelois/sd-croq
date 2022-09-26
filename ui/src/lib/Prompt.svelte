<script>
  import {createEventDispatcher} from 'svelte';
  const dispatch = createEventDispatcher();
  
  export let prompt = "";
  export let negativePrompt = "";
  export let actionText = "Generate";
  export let actionDisabled = false;
  
  let advanced = false;
  function toggleAdvanced(){ advanced = !advanced; }
  
  function action(){
    let data = {prompt};
    if(advanced)
      data.negativePrompt = negativePrompt
    dispatch("action", data);
  }
</script>

<div class="row align-items-start g-0">
  <div class="card" style="align-items: normal">
    <div class="card-body p-0">
      <div class="input-group">
        <button class="btn btn-outline-secondary" type="button" on:click={toggleAdvanced}>
          {#if !advanced}
            <i class="bi bi-chevron-down"></i>
          {:else}
            <i class="bi bi-chevron-up"></i>
          {/if}
        </button>
        <input type="text" class="form-control" placeholder="Enter your prompt here" bind:value={prompt}>
        <button class="btn btn-primary" type="button" disabled={actionDisabled} on:click={action}>{actionText}</button>
      </div>
      {#if advanced}
        <div class="input-group">
          <span class="input-group-text" id="basic-addon1">Negative</span>
          <input type="text" class="form-control" placeholder="Negative prompt" bind:value={negativePrompt}>
        </div>
      {/if}
    </div>
  </div>
</div>