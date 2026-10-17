<script lang="ts">
  import { formatCompact } from "../format";
  import { localeState } from "../i18n/locale.svelte";
  import type { CountRow } from "../types";

  let { rows }: { rows: CountRow[] } = $props();

  const max = $derived(Math.max(1, ...rows.map((row) => row.count)));

  function share(count: number): number {
    if (count <= 1 || max <= 1) return 0;
    return Math.log10(count) / Math.log10(max);
  }

  const ticks = $derived.by(() => {
    const loc = localeState.value;
    const logMax = Math.log10(max);
    if (!Number.isFinite(logMax) || logMax <= 0) return [];
    const marks: { label: string; left: string }[] = [];
    for (let power = 0; power < logMax; power += 3) {
      marks.push({
        label: formatCompact(10 ** power, loc),
        left: `${(power / logMax) * 100}%`,
      });
    }
    return marks;
  });
</script>

<div class="chart">
  {#each rows as row (row.id ?? row.object_type ?? row.label)}
    <p class="name">{row.label}</p>
    <div class="track">
      <div class="bar" style:width="{share(row.count) * 100}%"></div>
      {#each ticks as tick (tick.left)}
        <span class="guide" style:left={tick.left}></span>
      {/each}
    </div>
    <p class="count">{formatCompact(row.count, localeState.value)}</p>
  {/each}
  <div class="axis" aria-hidden="true">
    {#each ticks as tick (tick.left)}
      <span style:left={tick.left}>{tick.label}</span>
    {/each}
  </div>
</div>

<style>
  .chart {
    display: grid;
    grid-template-columns: minmax(9rem, 16rem) minmax(0, 1fr) auto;
    column-gap: 0.85rem;
    row-gap: 0.7rem;
    align-items: center;
  }

  .name,
  .count {
    margin: 0;
    font-family: var(--font-mono);
    font-size: 0.72rem;
    line-height: 1.35;
    font-variant-numeric: tabular-nums;
  }

  .name {
    color: var(--muted);
    text-align: right;
  }

  .count {
    color: var(--paper);
    min-width: 4.5rem;
  }

  .track {
    position: relative;
    height: 14px;
    background: transparent;
  }

  .bar {
    position: relative;
    z-index: 1;
    height: 100%;
    min-width: 2px;
    background: var(--accent);
  }

  .guide {
    position: absolute;
    z-index: 0;
    top: -0.35rem;
    bottom: -0.35rem;
    width: 1px;
    background: var(--line);
  }

  .axis {
    grid-column: 2;
    position: relative;
    height: 1.4rem;
    margin-top: 0.15rem;
  }

  .axis span {
    position: absolute;
    top: 0;
    transform: translateX(-50%);
    font-family: var(--font-mono);
    font-size: 0.68rem;
    color: var(--muted);
    white-space: nowrap;
  }

  @media (max-width: 640px) {
    .chart {
      grid-template-columns: minmax(0, 1fr) auto;
    }

    .name {
      grid-column: 1 / -1;
      text-align: left;
    }

    .axis {
      grid-column: 1;
    }
  }
</style>
