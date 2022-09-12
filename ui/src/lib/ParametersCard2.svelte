<script>
  import InputRange from './InputRange.svelte';
  import InputText from './InputText.svelte';
  import InputNumber from './InputNumber.svelte';
  import InputChoices from './InputChoices.svelte';
  import InputCheckbox from './InputCheckbox.svelte';
  
  let samplingMethodChoices = ["DDIM", "LMS", "DPM2", "Euler", "Heun"];

  export let samplingSteps = 20;
  export let samplingMethod = "DDIM";
  export let denoiserStrength = 0.63;
  export let denoiserStrengthFactor = 0.50;
  export let nbLoopback = 0;
  export let saveLoopback = false;
</script>

<div class="card">
  <div class="card-body">
    <InputRange title="Sampling Steps" min=1 max=250 step=1 bind:value={samplingSteps} />
    <InputChoices title="Sampling Methods" choices={samplingMethodChoices} bind:value={samplingMethod} />
    <InputRange title="Denoiser Strength" min=0 max=1 bind:value={denoiserStrength} />
    <InputRange title="Denoiser Loopback Factor" min=0 max=1 bind:value={denoiserStrengthFactor} />
    <InputRange title="Nb Loopback" min=0 step=1 bind:value={nbLoopback} />
    <InputCheckbox title="Save all loopback" bind:value={saveLoopback} />
  </div>
</div>