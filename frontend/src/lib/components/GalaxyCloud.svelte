<script lang="ts">
  import { mountGalaxyCloud } from "../charts/cloud";
  import { formatField } from "../format";
  import { localeState } from "../i18n/locale.svelte";
  import { t } from "../i18n/messages";
  import type { ColumnarTable } from "../types";

  let { table }: { table: ColumnarTable } = $props();

  let canvas = $state<HTMLCanvasElement | undefined>();
  let marker = $state<HTMLElement | undefined>();
  let tip = $state<{ x: number; y: number; lines: { field: string; text: string }[] } | null>(null);

  const fields = ["source_id", "x_gc", "y_gc", "z_gc", "distance_pc", "phot_g_mean_mag"];

  $effect(() => {
    const node = canvas;
    const label = marker;
    const data = table;
    const loc = localeState.value;
    if (!node || !label) return;
    return mountGalaxyCloud(node, data, (hover) => {
      if (!hover) {
        tip = null;
        return;
      }
      tip = {
        x: hover.x,
        y: hover.y,
        lines: fields.map((name) => {
          const value =
            name === "source_id"
              ? (data.strings.source_id?.[hover.index] ?? "")
              : (data.numbers[name]?.[hover.index] ?? Number.NaN);
          return { field: name, text: formatField(name, value, loc) };
        }),
      };
    }, label);
  });
</script>

<div class="cloud">
  <canvas bind:this={canvas} aria-label={t(localeState.value, "galaxyCanvasLabel")}></canvas>
  <p class="observer" bind:this={marker} hidden>{t(localeState.value, "earth")}</p>
  {#if tip}
    <p class="tip" style:left="{tip.x}px" style:top="{tip.y}px">
      {#each tip.lines as line (line.field)}
        <span class:id={line.field === "source_id"}>{line.text}</span>
      {/each}
    </p>
  {/if}
</div>
<p class="hint">{t(localeState.value, "galaxyHint")}</p>

<style>
  .cloud {
    position: relative;
    width: 100%;
    height: min(70vh, 720px);
    min-height: 420px;
    cursor: grab;
  }

  .cloud:active {
    cursor: grabbing;
  }

  canvas {
    width: 100%;
    height: 100%;
    display: block;
    touch-action: none;
  }

  .observer {
    position: absolute;
    z-index: 2;
    left: 0;
    top: 0;
    margin: 0;
    padding: 0.12rem 0.38rem;
    background: color-mix(in srgb, var(--bg) 78%, transparent);
    color: var(--accent);
    font-family: var(--font-mono);
    font-size: 0.72rem;
    letter-spacing: 0.14em;
    line-height: 1.2;
    text-transform: uppercase;
    white-space: nowrap;
    pointer-events: none;
  }

  .tip {
    position: absolute;
    z-index: 3;
    margin: 0;
    display: grid;
    gap: 0.15rem;
    max-width: 20rem;
    padding: 0.55rem 0.7rem;
    background: var(--bg);
    border: 1px solid var(--line);
    color: var(--paper);
    font-family: var(--font-mono);
    font-size: 11px;
    line-height: 1.45;
    pointer-events: none;
  }

  .id {
    color: var(--accent);
  }

  .hint {
    margin: 0.85rem 0 0;
    color: var(--muted);
    font-family: var(--font-mono);
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }
</style>
