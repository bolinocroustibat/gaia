<script lang="ts">
import { formatCount } from "../format"
import { localeState } from "../i18n/locale.svelte"
import { t } from "../i18n/messages"
import type { CountRow } from "../types"

let { rows, barRows = [] }: { rows: CountRow[]; barRows?: CountRow[] } =
	$props()

const ORDER = [
	"galaxy_candidates",
	"qso_candidates",
	"binary_stars",
	"other_sources",
] as const

const SWATCH: Record<string, string> = {
	galaxy_candidates: "#f472b6",
	qso_candidates: "#4ec4ff",
	binary_stars: "#ff8f4a",
	other_sources: "#e0c07a",
}

type Connector = { key: string; d: string; color: string }

let chartEl = $state<HTMLDivElement | undefined>()
let connectors = $state.raw<Connector[]>([])

function rowKey(row: CountRow): string {
	return row.object_type ?? row.id ?? row.label
}

const totalRow = $derived(
	rows.find((row) => row.id === "objects_total") ?? null,
)

const labelById = $derived.by(() => {
	const map = new Map<string, string>()
	for (const row of rows) {
		if (row.id) map.set(row.id, row.label)
	}
	return map
})

const segments = $derived.by(() => {
	const total = barRows.reduce((sum, row) => sum + row.count, 0)
	if (total <= 0) return []
	const byKey = new Map(barRows.map((row) => [rowKey(row), row]))
	const ordered = ORDER.map((key) => byKey.get(key)).filter(
		(row): row is CountRow => row != null,
	)
	const seen = new Set(ordered.map(rowKey))
	for (const row of barRows) {
		const key = rowKey(row)
		if (!seen.has(key)) ordered.push(row)
	}

	const mapped = ordered.map((row) => {
		const key = rowKey(row)
		return {
			key,
			label: labelById.get(key) ?? row.label,
			count: row.count,
			share: row.count / total,
			color: SWATCH[key] ?? "var(--muted)",
			isRest: key === "other_sources",
		}
	})

	const MIN_PCT = 0.18
	let reserved = 0
	for (const seg of mapped) {
		if (!seg.isRest) reserved += Math.max(seg.share * 100, MIN_PCT)
	}
	return mapped.map((seg) => ({
		...seg,
		widthPct: seg.isRest
			? Math.max(100 - reserved, 0)
			: Math.max(seg.share * 100, MIN_PCT),
	}))
})

function measureConnectors() {
	const chart = chartEl
	if (!chart || segments.length === 0) {
		connectors = []
		return
	}

	const chartRect = chart.getBoundingClientRect()
	if (chartRect.width <= 0 || chartRect.height <= 0) {
		connectors = []
		return
	}

	const next: Connector[] = []
	for (const seg of segments) {
		const bar = chart.querySelector<HTMLElement>(`[data-seg="${seg.key}"]`)
		const item = chart.querySelector<HTMLElement>(`[data-legend="${seg.key}"]`)
		const swatch = item?.querySelector<HTMLElement>(".swatch")
		if (!bar || !item || !swatch) continue

		const barRect = bar.getBoundingClientRect()
		const swatchRect = swatch.getBoundingClientRect()

		// Tiny slices: aim at the centre. Wide remainder: aim near its left edge.
		const targetX = seg.isRest
			? barRect.left + Math.min(48, barRect.width * 0.08) - chartRect.left
			: barRect.left + barRect.width / 2 - chartRect.left
		const targetY = barRect.bottom - chartRect.top
		const startX = swatchRect.left + swatchRect.width / 2 - chartRect.left
		const startY = swatchRect.top - chartRect.top
		const midY = startY + (targetY - startY) * 0.45

		next.push({
			key: seg.key,
			color: seg.color,
			d: `M ${startX.toFixed(1)} ${startY.toFixed(1)} C ${startX.toFixed(1)} ${midY.toFixed(1)}, ${targetX.toFixed(1)} ${midY.toFixed(1)}, ${targetX.toFixed(1)} ${targetY.toFixed(1)}`,
		})
	}
	connectors = next
}

$effect(() => {
	// Re-measure when layout inputs change.
	void segments
	void localeState.value
	const chart = chartEl
	if (!chart) return

	measureConnectors()
	const frame = requestAnimationFrame(measureConnectors)
	const observer = new ResizeObserver(() => measureConnectors())
	observer.observe(chart)
	window.addEventListener("resize", measureConnectors)

	return () => {
		cancelAnimationFrame(frame)
		observer.disconnect()
		window.removeEventListener("resize", measureConnectors)
	}
})
</script>

<div class="block">
  <p class="hint">{t(localeState.value, "kpiShareHint")}</p>

  {#if totalRow}
    <div class="total">
      <p class="value accent">{formatCount(totalRow.count, localeState.value)}</p>
      <p class="label">{totalRow.label}</p>
    </div>
  {/if}

  <div class="chart" bind:this={chartEl}>
    {#if segments.length > 0}
      <div class="strip" role="img" aria-label={t(localeState.value, "kpiShareTitle")}>
        {#each segments as seg (seg.key)}
          <span
            class="seg"
            data-seg={seg.key}
            style:width="{seg.widthPct}%"
            style:background={seg.color}
            title="{seg.label.split('\n')[0]} — {formatCount(seg.count, localeState.value)}"
          ></span>
        {/each}
      </div>
    {/if}

    <svg class="connectors" aria-hidden="true">
      <defs>
        {#each segments as seg (seg.key)}
          <marker
            id="kpi-arrow-{seg.key}"
            viewBox="0 0 10 10"
            refX="5"
            refY="5"
            markerWidth="5"
            markerHeight="5"
            orient="auto-start-reverse"
          >
            <path d="M 0 1.5 L 5 5 L 0 8.5" fill="none" stroke={seg.color} stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
          </marker>
        {/each}
      </defs>
      {#each connectors as link (link.key)}
        <path
          d={link.d}
          fill="none"
          stroke={link.color}
          stroke-width="1.25"
          stroke-linecap="round"
          opacity="0.7"
          marker-end="url(#kpi-arrow-{link.key})"
        />
      {/each}
    </svg>

    <ul class="legend">
      {#each segments as seg (seg.key)}
        <li data-legend={seg.key}>
          <span class="swatch" style:background={seg.color}></span>
          <div class="body">
            <div class="figure" style:color={seg.color}>
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
              {:else if seg.key === "other_sources"}
                <svg class="mark" viewBox="0 0 96 64" aria-hidden="true">
                  <circle cx="48" cy="32" r="16" fill="currentColor" opacity="0.1" />
                  <circle cx="48" cy="32" r="9" fill="currentColor" />
                  <path
                    d="M48 10 V18 M48 46 V54 M26 32 H34 M62 32 H70 M32 16 L37 21 M59 43 L64 48 M64 16 L59 21 M32 48 L37 43"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.6"
                    stroke-linecap="round"
                    opacity="0.7"
                  />
                  <circle cx="78" cy="18" r="1.1" fill="currentColor" opacity="0.55" />
                  <circle cx="16" cy="46" r="0.9" fill="currentColor" opacity="0.45" />
                  <circle cx="82" cy="42" r="0.8" fill="currentColor" opacity="0.4" />
                </svg>
              {/if}
            </div>
            <p class="label">{seg.label}</p>
          </div>
        </li>
      {/each}
    </ul>
  </div>
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

  .total .value {
    margin: 0;
  }

  .total .label {
    margin: 0.55rem 0 0;
  }

  .chart {
    position: relative;
    display: grid;
    gap: 2.4rem;
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

  .connectors {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    overflow: visible;
  }

  .legend {
    list-style: none;
    margin: 0;
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
