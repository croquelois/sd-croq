<script>
  export let title;
  export let value;
</script>

<div class="input-group">
  <span class="input-group-text">{title}</span>
  <input type="text" class="form-control" bind:value={value}>
</div>