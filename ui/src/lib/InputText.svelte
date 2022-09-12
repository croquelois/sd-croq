<script>
  export let title;
  export let value;
</script>

<div class="input-group mb-3">
  <span class="input-group-text">{title}</span>
  <input type="text" class="form-control" bind:value={value}>
</div>