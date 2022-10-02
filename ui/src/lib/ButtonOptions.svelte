<script>
  import newUniqueId from 'locally-unique-id-generator'
  import {createEventDispatcher} from 'svelte';

  const dispatch = createEventDispatcher();

  let optionId = newUniqueId();
  export let current = null;
  export let options = [];
  
  function onClick(event){
    current = event.target.dataset.option;
    dispatch("change", current);
  }
</script>

<div class="btn-group" role="group">
{#each options as option (option)}
  <input type="radio" class="btn-check" name="btnradio" 
         id={optionId + option} autocomplete="off"
         data-option={option} checked={current==option} on:click={onClick}>
  <label class="btn btn-outline-primary" for={optionId + option}>{option}</label>
{/each}
</div>