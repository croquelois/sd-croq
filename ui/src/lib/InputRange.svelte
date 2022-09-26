<script>
  export let title;
  export let value;
  let prevValue = value;
  
  export let min = null;
  export let max = null;
  export let step = null;
  
  function change(event){
    value = parseFloat(value);
    if(isNaN(value)){
      value = prevValue;
      return;
    }
    if(min !== null && value < min)
      value = min;
    if(max !== null && value > max)
      value = max;
    if(step)
      value = value - (value % step);
    prevValue = value;
  }
</script>

<div class="input-group">
  <span class="input-group-text">{title}</span>
  <input type="text" class="form-control" bind:value={value} on:change={change}>
</div>