<script lang="ts">
  import { formatCount } from "../format";
  import { localeState } from "../i18n/locale.svelte";
  import { t } from "../i18n/messages";
  import type { CountRow } from "../types";

  let { rows, barRows = [] }: { rows: CountRow[]; barRows?: CountRow[] } = $props();

  const ORDER = [
    "galaxy_candidates",
    "qso_candidates",
    "binary_stars",
    "other_sources",
  ] as const;

  const SWATCH: Record<string, string> = {
    galaxy_candidates: "#f472b6",
    qso_candidates: "#4ec4ff",
    binary_stars: "#ff8f4a",
    other_sources: "#e0c07a",
  };

  function rowKey(row: CountRow): string {
    return row.object_type ?? row.id ?? row.label;
  }

  const totalRow = $derived(rows.find((row) => row.id === "objects_total") ?? null);

  const labelById = $derived.by(() => {
    const map = new Map<string, string>();
    for (const row of rows) {
      if (row.id) map.set(row.id, row.label);
    }
    return map;
  });

  const segments = $derived.by(() => {
    const total = barRows.reduce((sum, row) => sum + row.count, 0);
    if (total <= 0) return [];
    const byKey = new Map(barRows.map((row) => [rowKey(row), row]));
    const ordered = ORDER.map((key) => byKey.get(key)).filter(
      (row): row is CountRow => row != null,
    );
    const seen = new Set(ordered.map(rowKey));
    for (const row of barRows) {
      const key = rowKey(row);
      if (!seen.has(key)) ordered.push(row);
    }

    const mapped = ordered.map((row) => {
      const key = rowKey(row);
      return {
        key,
        label: labelById.get(key) ?? row.label,
        count: row.count,
        share: row.count / total,
        color: SWATCH[key] ?? "var(--muted)",
        isRest: key === "other_sources",
      };
    });

    const MIN_PCT = 0.18;
    let reserved = 0;
    for (const seg of mapped) {
      if (!seg.isRest) reserved += Math.max(seg.share * 100, MIN_PCT);
    }
    return mapped.map((seg) => ({
      ...seg,
      widthPct: seg.isRest ? Math.max(100 - reserved, 0) : Math.max(seg.share * 100, MIN_PCT),
    }));
  });
</script>

<div class="block">
  <p class="hint">{t(localeState.value, "kpiShareHint")}</p>

  {#if segments.length > 0}
    <div
      class="strip"
      role="img"
      aria-label={t(localeState.value, "kpiShareTitle")}
    >
      {#each segments as seg (seg.key)}
        <span
          class="seg"
          style:width="{seg.widthPct}%"
          style:background={seg.color}
          title="{seg.label.split('\n')[0]} — {formatCount(seg.count, localeState.value)}"
        ></span>
      {/each}
    </div>
  {/if}

  <ul class="legend">
    {#if totalRow}
      <li class="total">
        <div class="body">
          <p class="value accent">{formatCount(totalRow.count, localeState.value)}</p>
          <p class="label">{totalRow.label}</p>
        </div>
      </li>
    {/if}

    {#each segments as seg (seg.key)}
      <li>
        <span class="swatch" style:background={seg.color}></span>
        <div class="body">
          <div class="figure" style:color={seg.isRest ? "var(--paper)" : seg.color}>
            <p class="value">{formatCount(seg.count, localeState.value)}</p>
            {#if seg.key === "galaxy_candidates"}
              <svg class="mark" viewBox="0 0 96 64" aria-hidden="true">
                <ellipse cx="48" cy="32" rx="34" ry="16" fill="currentColor" opacity="0.12" transform="rotate(-28 48 32)" />
                <path d="M50 30c10-8 22-8 30-2 6 5 8 12 4 16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" />
                <path d="M46 34C36 42 24 42 16 36c-6-5-8-12-4-16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" />
                <ellipse cx="48" cy="32" rx="6.5" ry="4" fill="currentColor" transform="rotate(-28 48 32)" />
                <circle cx="78" cy="22" r="1" fill="currentColor" />
                <circle cx="18" cy="44" r="1" fill="currentColor" />
                <circle cx="72" cy="46" r="0.8" fill="currentColor" opacity="0.65" />
              </svg>
            {:else if seg.key === "qso_candidates"}
              <svg class="mark" viewBox="0 0 96 64" aria-hidden="true">
                <circle cx="48" cy="32" r="22" fill="currentColor" opacity="0.08" />
                <circle cx="48" cy="32" r="7" fill="currentColor" />
                <path d="M48 32 L8 20 M48 32 L88 20 M48 32 L8 44 M48 32 L88 44" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" opacity="0.55" />
              </svg>
            {:else if seg.key === "binary_stars"}
              <svg class="mark" viewBox="0 0 96 64" aria-hidden="true">
                <ellipse cx="48" cy="34" rx="32" ry="15" fill="none" stroke="currentColor" stroke-width="1.2" opacity="0.45" transform="rotate(-18 48 34)" />
                <circle cx="34" cy="38" r="10" class="paper" />
                <circle cx="64" cy="28" r="6" fill="currentColor" />
              </svg>
            {/if}
          </div>
          <p class="label">{seg.label}</p>
        </div>
      </li>
    {/each}
  </ul>
</div>

<style>
  .block {
    display: grid;
    gap: 1.25rem;
  }

  .hint {
    margin: 0;
    max-width: 36rem;
    color: var(--muted);
    font-size: 0.85rem;
    line-height: 1.4;
  }

  .strip {
    display: flex;
    width: 100%;
    height: 28px;
    overflow: hidden;
    background: var(--line);
  }

  .seg {
    flex: none;
    height: 100%;
    min-width: 2px;
  }

  .legend {
    list-style: none;
    margin: 0.5rem 0 0;
    padding: 0;
    display: grid;
    gap: 2.2rem;
  }

  .legend > li {
    display: grid;
    grid-template-columns: 0.85rem minmax(0, 1fr);
    gap: clamp(0.85rem, 2.5vw, 1.25rem);
    align-items: start;
  }

  .legend > li.total {
    grid-template-columns: minmax(0, 1fr);
  }

  .swatch {
    width: 0.85rem;
    height: 0.85rem;
    margin-top: 0.55rem;
    flex: none;
  }

  .body {
    min-width: 0;
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
    color: var(--paper);
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
    white-space: pre-line;
  }
</style>
