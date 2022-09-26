<script>
  export let title;
  export let value;
  export let emptyIsOk = false;
  let prevValue = value;
  
  function change(event){
    if(emptyIsOk && value == ""){
      value = null;
      prevValue = value;
      return;
    }
    value = parseInt(value);
    if(isNaN(value))
      value = prevValue;
    else 
      prevValue = value;
  }
</script>

<div class="input-group">
  <span class="input-group-text">{title}</span>
  <input type="text" class="form-control" bind:value={value} on:change={change}>
</div>