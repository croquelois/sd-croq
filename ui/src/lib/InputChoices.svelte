<script>
  export let title;
  export let value;
  export let choices = [];
</script>

<div class="input-group">
  <span class="input-group-text">{title}</span>
  <select class="form-select" bind:value={value} >
    {#each choices as choice (choice)}
      <option value={choice}>{choice}</option>
    {/each}
  </select>
</div>