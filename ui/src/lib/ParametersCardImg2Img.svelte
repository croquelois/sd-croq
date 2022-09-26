<script>
  import InputRange from './InputRange.svelte';
  import InputText from './InputText.svelte';
  import InputNumber from './InputNumber.svelte';
  import InputChoices from './InputChoices.svelte';
  import InputCheckbox from './InputCheckbox.svelte';
  
  let samplingMethodChoices = ["DDIM", "LMS", "PLMS", "Euler a", "Euler", "Heun", "DPM2", "DPM2 a"];
  
  export let denoiserStrength = 0.63;
</script>

<div class="card">
  <div class="card-body">
    <InputRange title="Denoiser Strength" min=0 max=1 bind:value={denoiserStrength} />
  </div>
</div>