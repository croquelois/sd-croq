<script>
  export let status = null
  console.log(status);
</script>

{#if status}
<div class="card">
  <div class="card-body">
    <div>Status: {status.status}</div>
    {#if status.nb}
      <div>Progess: {status.i} / {status.nb}</div>
    {/if}
  </div>
</div>
{/if}