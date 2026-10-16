<script lang="ts">
  import { formatCompact } from "../format";
  import type { CountRow } from "../types";

  let { rows }: { rows: CountRow[] } = $props();

  const LINEAR = 0.68;
  const DOTS = 0.16;
  const CAP = 0.06;

  function niceCeiling(value: number): number {
    if (value <= 0) return 1;
    const exponent = Math.floor(Math.log10(value));
    const base = 10 ** exponent;
    const steps = [1, 2, 2.5, 5, 10];
    return (steps.find((step) => step * base >= value) ?? 10) * base;
  }

  const scaleMax = $derived.by(() => {
    const counts = rows.map((row) => row.count).sort((a, b) => a - b);
    const second = counts.length > 1 ? counts[counts.length - 2] : counts[0];
    return niceCeiling(second ?? 1);
  });

  const brokenKey = $derived.by(() => {
    if (rows.length === 0) return null;
    const largest = rows.reduce((best, row) => (row.count > best.count ? row : best));
    if (largest.count <= scaleMax) return null;
    return largest.object_type ?? largest.label;
  });

  function rowKey(row: CountRow): string {
    return row.object_type ?? row.label;
  }

  function solidWidth(count: number): number {
    return Math.max(0, Math.min(count / scaleMax, 1)) * LINEAR * 100;
  }

  const ticks = $derived.by(() => {
    const marks: { label: string; left: string }[] = [];
    for (let step = 1; step <= 5; step += 1) {
      const value = (scaleMax / 5) * step;
      marks.push({
        label: formatCompact(value),
        left: `${(value / scaleMax) * LINEAR * 100}%`,
      });
    }
    return marks;
  });
</script>

<div class="chart">
  {#each rows as row (rowKey(row))}
    <p class="name">{row.label}</p>
    <div class="track">
      {#if rowKey(row) === brokenKey}
        <div class="bar" style:width="{LINEAR * 100}%"></div>
        <div class="dots" style:width="{DOTS * 100}%"></div>
        <div class="bar cap" style:width="{CAP * 100}%"></div>
      {:else}
        <div class="bar" style:width="{solidWidth(row.count)}%"></div>
      {/if}
      {#each ticks as tick (tick.left)}
        <span class="guide" style:left={tick.left}></span>
      {/each}
    </div>
    <p class="count">{formatCompact(row.count)}</p>
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
    grid-template-columns: minmax(10rem, 18rem) minmax(0, 1fr) auto;
    column-gap: 0.85rem;
    row-gap: 0.85rem;
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
    display: flex;
    align-items: center;
    height: 14px;
  }

  .bar {
    position: relative;
    z-index: 1;
    flex: none;
    height: 100%;
    min-width: 2px;
    background: var(--accent);
  }

  .dots {
    position: relative;
    z-index: 1;
    flex: none;
    height: 100%;
    margin-left: 0.55rem;
    background-image: radial-gradient(circle, var(--accent) 1.25px, transparent 1.45px);
    background-size: 8px 14px;
    background-repeat: repeat-x;
    background-position: left center;
  }

  .cap {
    margin-left: 0.55rem;
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
