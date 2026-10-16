<script lang="ts">
  import { formatCount } from "../format";
  import type { CountRow } from "../types";

  let { rows }: { rows: CountRow[] } = $props();
</script>

<ul>
  {#each rows as row (row.id ?? row.label)}
    <li>
      <p class="value" class:accent={row.id === "objects_total"}>{formatCount(row.count)}</p>
      <p class="label">{row.label}</p>
    </li>
  {/each}
</ul>

<style>
  ul {
    list-style: none;
    margin: 0.5rem 0 0;
    padding: 0;
    display: grid;
    gap: 2.2rem;
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
