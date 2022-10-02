<script>
  import { historyStore } from './historyStore.js';
  import InputText from './InputText.svelte';
  import { onMount } from 'svelte';
  let history = [];
  historyStore.subscribe(h => history = h.reverse());
  let user;
  let userInput;
  
  let transfertModalElement;
  let transfertModal;
  let modalUser = "";
  let infoModalElement;
  let infoModal;
  let infoModalText;
  let editModalElement;
  let editModal;
  let editModalText;
  
  let currentUrl = null;
  
  let isGridMode = false;

  onMount(async function(){
    userInput.addEventListener("keyup", event => {
      if(event.key !== "Enter") return;
      historyStore.setUser(user);
    });
    transfertModal = new bootstrap.Modal(transfertModalElement, {});
    infoModal = new bootstrap.Modal(infoModalElement, {});
    editModal = new bootstrap.Modal(editModalElement, {});
  });
  
  function refresh(){
    historyStore.setUser(user);
  }
  function deleteOne(event){
    historyStore.deleteOne(event.target.dataset.url);
  }
  function detail(event){
    let url = event.target.dataset.url;
    let info = history.find(h => h.url == url);
    infoModalText = JSON.stringify(info, "", 2);
    infoModal.show();
  }
  
  
  function onEdit(event){
    currentUrl = event.target.dataset.url;
    let h = history.find(h => h.url == currentUrl);
    editModalText = h.title || "";
    editModal.show();
  }
  function applyEdit(){
    let h = history.find(h => h.url == currentUrl);
    h.title = editModalText;
    historyStore.update(h);
    currentUrl = null;
  }
  
  function transfert(event){
    currentUrl = event.target.dataset.url;
    transfertModal.show();
  }
  function applyTransfert(){
    historyStore.transfert(history.find(h => h.url == currentUrl), modalUser);
    currentUrl = null;
  }
  function backToOrigin(event){
    let url = event.target.dataset.url;
  }
  refresh();
  
  function onViewMode(){
    isGridMode = !isGridMode;
  }
</script>

<div bind:this={transfertModalElement} class="modal modal-sm" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">Transfert to</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
      </div>
      <div class="modal-body">
        <InputText title="destination user" bind:value={modalUser} />
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
        <button type="button" class="btn btn-primary" on:click={applyTransfert} data-bs-dismiss="modal">Apply changes</button>
      </div>
    </div>
  </div>
</div>

<div bind:this={editModalElement} class="modal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">Change the title</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
      </div>
      <div class="modal-body">
        <InputText title="title" bind:value={editModalText} />
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
        <button type="button" class="btn btn-primary" on:click={applyEdit} data-bs-dismiss="modal">Apply changes</button>
      </div>
    </div>
  </div>
</div>

<div bind:this={infoModalElement} class="modal modal-xl" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">Info</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
      </div>
      <div class="modal-body">
        <pre>{infoModalText}</pre>
      </div>
    </div>
  </div>
</div>

<div class="container">
  <div class="row align-items-start g-0">
    <div class="d-flex justify-content-between">
      <button type="button" class="btn btn-info" on:click={onViewMode}>Mode</button>
      <button type="button" class="btn btn-primary" style="width: 100%" on:click={refresh}>Refresh</button>
      <input bind:this={userInput} type="text" placeholder="default user" class="rounded" size="10" bind:value={user}>
    </div>
  </div>
  {#if history.length}
  <div class:d-flex={isGridMode} class:flex-wrap={isGridMode}>
    {#each history as h}
      {#if isGridMode}
        <div>
          <img src={h.url} class="img-fluid rounded" style="height: 196px" data-url={h.url} on:click={detail}>
        </div>
      {:else}
        <div class="row align-items-start g-0">
          <div class="card p-0">
            <div class="row g-0">
              <div class="col-md-2">
                <img src={h.url} class="img-fluid rounded-start" style="height: 196px">
              </div>
              <div class="col-md-10">
                <div class="card-body">
                  <div class="d-flex justify-content-between">
                    <h5 class="card-title">{h.title || h.prompt}</h5>
                    <div>
                      <button type="button" data-url={h.url} class="btn btn-sm btn-danger" on:click={deleteOne}><i class="bi-trash"></i></button>
                      <button type="button" data-url={h.url} class="btn btn-sm btn-info" on:click={onEdit}><i class="bi-pencil-square"></i></button>
                      <button type="button" data-url={h.url} class="btn btn-sm btn-info" on:click={detail}><i class="bi-question-circle"></i></button>
                      <button type="button" data-url={h.url} class="btn btn-sm btn-info" on:click={transfert}><i class="bi-folder-symlink"></i></button>
                      <button type="button" data-url={h.url} class="btn btn-sm btn-info" on:click={backToOrigin}><i class="bi-arrow-return-left"></i></button>
                    </div>
                  </div>
                  <div class="card-text">classifier strength: {h["classifierStrength"]}</div>
                  <div class="card-text">sampling method: <b>{h["samplingMethod"]}</b> with <b>{h["samplingSteps"]}</b> steps</div>
                  <div class="card-text float-end"><small class="text-muted">seed: {h["seed"]}</small></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      {/if}
    {/each}
  </div>
  {:else}
    Empty history
  {/if}
</div>
<style>
.btn {
  height: fit-content;
}
.btn i {
  pointer-events: none;
}
</style>