<script>
  import newUniqueId from 'locally-unique-id-generator'
  export let title;
  export let value;
  let id = newUniqueId();
</script>

<div class="form-check">
  <input class="form-check-input" type="checkbox" bind:checked={value} id={id}>
  <label class="form-check-label" for={id}>{title}</label>
</div>

<style>
  .form-check {
    text-align: left;
  }
</style>