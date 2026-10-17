<script lang="ts">
  import { formatCount } from "../format";
  import { localeState } from "../i18n/locale.svelte";
  import type { CountRow } from "../types";
  import BrokenBars from "./BrokenBars.svelte";

  let { rows, barRows = [] }: { rows: CountRow[]; barRows?: CountRow[] } = $props();
</script>

<ul>
  {#each rows as row (row.id ?? row.label)}
    <li>
      <div class="figure">
        <p class="value" class:accent={row.id === "objects_total"}>{formatCount(row.count, localeState.value)}</p>
        {#if row.id === "galaxy_candidates"}
          <svg class="mark" viewBox="0 0 96 64" aria-hidden="true">
            <ellipse cx="48" cy="32" rx="34" ry="16" fill="currentColor" opacity="0.12" transform="rotate(-28 48 32)" />
            <path d="M50 30c10-8 22-8 30-2 6 5 8 12 4 16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" />
            <path d="M46 34C36 42 24 42 16 36c-6-5-8-12-4-16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" />
            <ellipse cx="48" cy="32" rx="6.5" ry="4" fill="currentColor" transform="rotate(-28 48 32)" />
            <circle cx="78" cy="22" r="1" fill="currentColor" />
            <circle cx="18" cy="44" r="1" fill="currentColor" />
            <circle cx="72" cy="46" r="0.8" fill="currentColor" opacity="0.65" />
          </svg>
        {:else if row.id === "qso_candidates"}
          <svg class="mark" viewBox="0 0 96 64" aria-hidden="true">
            <circle cx="48" cy="32" r="22" fill="currentColor" opacity="0.08" />
            <circle cx="48" cy="32" r="7" fill="currentColor" />
            <path d="M48 32 L8 20 M48 32 L88 20 M48 32 L8 44 M48 32 L88 44" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" opacity="0.55" />
          </svg>
        {:else if row.id === "binary_stars"}
          <svg class="mark" viewBox="0 0 96 64" aria-hidden="true">
            <ellipse cx="48" cy="34" rx="32" ry="15" fill="none" stroke="currentColor" stroke-width="1.2" opacity="0.45" transform="rotate(-18 48 34)" />
            <circle cx="34" cy="38" r="10" class="paper" />
            <circle cx="64" cy="28" r="6" fill="currentColor" />
          </svg>
        {/if}
      </div>
      <p class="label">{row.label}</p>
    </li>
  {/each}
</ul>

{#if barRows.length > 0}
  <div class="kpi-bars">
    <BrokenBars rows={barRows} />
  </div>
{/if}

<style>
  ul {
    list-style: none;
    margin: 0.5rem 0 0;
    padding: 0;
    display: grid;
    gap: 2.2rem;
  }

  .kpi-bars {
    margin-top: clamp(2rem, 5vw, 3rem);
  }

  .figure {
    display: flex;
    align-items: center;
    gap: clamp(1rem, 3vw, 1.75rem);
  }

  .mark {
    width: clamp(4.2rem, 9vw, 5.6rem);
    height: auto;
    flex: none;
    color: var(--accent);
    overflow: visible;
  }

  .paper {
    fill: var(--paper);
  }

  .value {
    margin: 0;
    font-size: clamp(2.8rem, 7vw, 5rem);
    font-weight: 500;
    letter-spacing: -0.055em;
    line-height: 0.9;
    font-variant-numeric: tabular-nums;
  }

  .value.accent {
    color: var(--accent);
  }

  .label {
    margin: 0.55rem 0 0;
    color: var(--muted);
    font-family: var(--font-mono);
    font-size: 0.78rem;
    letter-spacing: 0.04em;
  }
</style>
