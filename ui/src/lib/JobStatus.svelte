<script>
  export let nbQueued = 0;
  export let status = null
</script>

{#if status}
<div class="card">
  <div class="card-body">
    <div>Status: {status.status}</div>
    {#if nbQueued > 1}
      <div>nbQueued: {nbQueued}</div>
    {/if}
    {#if status.nb}
      <div>Progess: {status.i} / {status.nb}</div>
    {/if}
  </div>
</div>
{/if}