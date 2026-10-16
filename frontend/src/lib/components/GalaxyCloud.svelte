<script lang="ts">
  import { mountGalaxyCloud } from "../charts/cloud";
  import { formatField } from "../format";
  import type { ColumnarTable } from "../types";

  let { table }: { table: ColumnarTable } = $props();

  let canvas = $state<HTMLCanvasElement | undefined>();
  let tip = $state<{ x: number; y: number; lines: string[] } | null>(null);

  const fields = ["source_id", "x_gc", "y_gc", "z_gc", "distance_pc", "phot_g_mean_mag"];

  $effect(() => {
    const node = canvas;
    const data = table;
    if (!node) return;
    return mountGalaxyCloud(node, data, (hover) => {
      if (!hover) {
        tip = null;
        return;
      }
      tip = {
        x: hover.x,
        y: hover.y,
        lines: fields.map((name) => {
          if (name === "source_id") return formatField(name, data.strings.source_id?.[hover.index] ?? "");
          const column = data.numbers[name];
          return formatField(name, column?.[hover.index] ?? Number.NaN);
        }),
      };
    });
  });
</script>

<div class="cloud">
  <canvas bind:this={canvas} aria-label="Galaxies proches en trois dimensions"></canvas>
  {#if tip}
    <p class="tip" style:left="{tip.x}px" style:top="{tip.y}px">
      {#each tip.lines as line}
        <span class:id={line.startsWith("identifiant")}>{line}</span>
      {/each}
    </p>
  {/if}
</div>
<p class="hint">Glisser pour tourner</p>

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

  .tip {
    position: absolute;
    z-index: 2;
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
