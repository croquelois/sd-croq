<script>
  import InputRange from './InputRange.svelte';
  import InputText from './InputText.svelte';
  import InputNumber from './InputNumber.svelte';
  import InputChoices from './InputChoices.svelte';
  import InputCheckbox from './InputCheckbox.svelte';
  
  let samplingMethodChoices = ["DDIM", "LMS", "PLMS", "Euler a", "Euler", "Heun", "DPM2", "DPM2 a"];
  
  export let width = 512;
  export let height = 512;
  export let classifierStrength = 7.5;
  export let seed = null;
  export let subseed = null;
  export let subseedStrength = 0.0;
  export let nbImages = 1;
  export let samplingSteps = 20;
  export let samplingMethod = "DDIM";
  export let restoreFaces = false;
  export let tiling = false;
</script>

<div class="card">
  <div class="card-body">
    <InputRange title="width" min=64 max=1024 step=64 bind:value={width} />
    <InputRange title="height" min=64 max=1024 step=64 bind:value={height} />
    <InputRange title="classifier strength" min=0 max=30 step=0.5 bind:value={classifierStrength} />
    <InputNumber title="seed" bind:value={seed} emptyIsOk=true />
    <InputNumber title="subseed" bind:value={subseed} emptyIsOk=true />
    <InputRange title="subseed strength" min=0 max=1 bind:value={subseedStrength} />
    <InputRange title="nbImages" min=0 step=1 bind:value={nbImages} />
    <InputRange title="Sampling Steps" min=1 max=500 step=1 bind:value={samplingSteps} />
    <InputChoices title="Sampling Methods" choices={samplingMethodChoices} bind:value={samplingMethod} />
    <InputCheckbox title="Restore faces" bind:value={restoreFaces} />
    <InputCheckbox title="Tiling" bind:value={tiling} />
  </div>
</div>