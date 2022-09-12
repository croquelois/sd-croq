<script>
  import InputRange from './InputRange.svelte';
  import InputText from './InputText.svelte';
  import InputNumber from './InputNumber.svelte';
  import InputChoices from './InputChoices.svelte';
  import InputCheckbox from './InputCheckbox.svelte';
  
  export let width = 512;
  export let height = 512;
  export let classifierStrength = 7.5;
  export let seed = null;
  export let nbImages = 1;
</script>

<div class="card">
  <div class="card-body">
    <InputRange title="width" min=64 max=1024 step=64 bind:value={width} />
    <InputRange title="height" min=64 max=1024 step=64 bind:value={height} />
    <InputRange title="classifier strength" min=0 max=30 step=0.5 bind:value={classifierStrength} />
    <InputNumber title="seed" bind:value={seed} emptyIsOk=true />
    <InputRange title="nbImages" min=0 step=1 bind:value={nbImages} />
  </div>
</div>