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
  
  export let hide = [];
</script>

<div class="card">
  <div class="card-body">
  {#if hide.indexOf("width") == -1}
    <InputRange title="width" min=64 max=1024 step=64 bind:value={width} />
  {/if}
  {#if hide.indexOf("height") == -1}
    <InputRange title="height" min=64 max=1024 step=64 bind:value={height} />
  {/if}
  {#if hide.indexOf("classifierStrength") == -1}
    <InputRange title="classifier strength" min=0 max=30 step=0.5 bind:value={classifierStrength} />
  {/if}
  {#if hide.indexOf("seed") == -1}
    <InputNumber title="seed" bind:value={seed} emptyIsOk=true />
  {/if}
  {#if hide.indexOf("subseed") == -1}
    <InputNumber title="subseed" bind:value={subseed} emptyIsOk=true />
  {/if}
  {#if hide.indexOf("subseedStrength") == -1}
    <InputRange title="subseed strength" min=0 max=1 bind:value={subseedStrength} />
  {/if}
  {#if hide.indexOf("nbImages") == -1}
    <InputRange title="nbImages" min=0 step=1 bind:value={nbImages} />
  {/if}
  {#if hide.indexOf("samplingSteps") == -1}
    <InputRange title="Sampling Steps" min=1 max=500 step=1 bind:value={samplingSteps} />
  {/if}
  {#if hide.indexOf("samplingMethod") == -1}
    <InputChoices title="Sampling Methods" choices={samplingMethodChoices} bind:value={samplingMethod} />
  {/if}
  {#if hide.indexOf("restoreFaces") == -1}
    <InputCheckbox title="Restore faces" bind:value={restoreFaces} />
  {/if}
  {#if hide.indexOf("tiling") == -1}
    <InputCheckbox title="Tiling" bind:value={tiling} />
  {/if}
  </div>
</div>