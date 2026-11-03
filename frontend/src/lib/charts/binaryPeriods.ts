import * as Plot from "@observablehq/plot"
import { formatCompact, formatCount } from "../format"
import type { Locale } from "../i18n/locale.svelte"
import { type MessageKey, t } from "../i18n/messages"
import { plotStyle, theme } from "../theme"
import type { PeriodHistogram } from "../types"

const YEAR_DAYS = 365.25

const marginRight = 20
const marginBottom = 58
const marginLeft = 52
const marginTop = 28

/** One stacked series: its id in the data file, its colour, its legend. */
export type PeriodSeries = { id: string; fill: string; labelKey: MessageKey }

export type StackedPeriodConfig = {
	/** Stack and legend order, bottom to top. */
	series: PeriodSeries[]
	countAxisKey: MessageKey
	captionKey: MessageKey
}

// Site neons, bottom to top: the three signs, then their mix. Violet and cyan
// are close for deuteranopes, so violet goes first: lime always sits between
// them in the stack. Every pair that touches is >= 10 OKLab ΔE apart under
// colour blindness.
const binaryConfig: StackedPeriodConfig = {
	series: [
		{ id: "eclipse", fill: theme.violet, labelKey: "binaryEclipse" },
		{ id: "spectrum", fill: theme.accent, labelKey: "binarySpectrum" },
		{ id: "position", fill: theme.cyan, labelKey: "binaryPosition" },
		{ id: "both", fill: theme.pink, labelKey: "binaryBoth" },
	],
	countAxisKey: "binaryCountAxis",
	captionKey: "binaryPeriodLegend",
}

/** Gaia DR4 planet detection methods: the binary-star signs, colours, order. */
export const planetSeries: PeriodSeries[] = [
	{ id: "transit", fill: theme.violet, labelKey: "planetTransit" },
	{ id: "radial", fill: theme.accent, labelKey: "binarySpectrum" },
	{ id: "astrometry", fill: theme.cyan, labelKey: "binaryPosition" },
	{ id: "both", fill: theme.pink, labelKey: "binaryBoth" },
]

const planetConfig: StackedPeriodConfig = {
	series: planetSeries,
	countAxisKey: "planetCountAxis",
	captionKey: "planetPeriodLegend",
}

type Bar = {
	p0: number
	p1: number
	y0: number
	y1: number
	count: number
	series: PeriodSeries
}

export type BinaryPeriodPlotInput = {
	bins: PeriodHistogram
	locale: Locale
}

const tickMarks = [
	{ days: 1 / 24, fr: "1 heure", en: "1 hour" },
	{ days: 1, fr: "1 jour", en: "1 day" },
	{ days: 10, fr: "10 jours", en: "10 days" },
	{ days: YEAR_DAYS, fr: "1 an", en: "1 year" },
	{ days: 10 * YEAR_DAYS, fr: "10 ans", en: "10 years" },
]

function localeTag(locale: Locale): string {
	return locale === "fr" ? "fr-FR" : "en-US"
}

function formatAmount(value: number, locale: Locale, digits: number): string {
	return new Intl.NumberFormat(localeTag(locale), {
		maximumFractionDigits: digits,
		minimumFractionDigits: value >= 10 ? 0 : digits,
	}).format(value)
}

export function formatPeriod(days: number, locale: Locale): string {
	if (days >= YEAR_DAYS) {
		const years = days / YEAR_DAYS
		const text = formatAmount(years, locale, years >= 10 ? 0 : 1)
		if (locale === "fr") return `${text} ${years >= 2 ? "ans" : "an"}`
		return `${text} ${years >= 2 ? "years" : "year"}`
	}
	if (days < 1) {
		const hours = days * 24
		return `${formatAmount(hours, locale, hours >= 10 ? 0 : 1)} h`
	}
	const text = formatAmount(days, locale, days >= 10 ? 0 : 1)
	if (locale === "fr") return `${text} ${days >= 2 ? "jours" : "jour"}`
	return `${text} ${days >= 2 ? "days" : "day"}`
}

function barsFrom(bins: PeriodHistogram, order: PeriodSeries[]): Bar[] {
	const edges = bins.period.edges
	const byId = new Map(bins.series.map((series) => [series.id, series.counts]))
	const bars: Bar[] = []
	const binCount = Math.max(0, edges.length - 1)
	for (let index = 0; index < binCount; index += 1) {
		const p0 = edges[index] ?? 0
		const p1 = edges[index + 1] ?? p0
		if (p0 <= 0 || p1 <= p0) continue
		let y0 = 0
		for (const series of order) {
			const count = byId.get(series.id)?.[index] ?? 0
			if (count <= 0) continue
			bars.push({ p0, p1, y0, y1: y0 + count, count, series })
			y0 += count
		}
	}
	return bars
}

function stackedMax(bars: Bar[]): number {
	return bars.reduce((highest, bar) => Math.max(highest, bar.y1), 1)
}

function tip(bar: Bar, locale: Locale): string {
	const count = formatCount(bar.count, locale)
	const label = t(locale, bar.series.labelKey)
	const span = `${formatPeriod(bar.p0, locale)} – ${formatPeriod(bar.p1, locale)}`
	return `${count} · ${label} · ${span}`
}

export function binaryPeriodPlot(
	input: BinaryPeriodPlotInput,
	width: number,
): HTMLElement {
	return stackedPeriodPlot(input, width, binaryConfig)
}

export function planetPeriodPlot(
	input: BinaryPeriodPlotInput,
	width: number,
): HTMLElement {
	return stackedPeriodPlot(input, width, planetConfig)
}

function stackedPeriodPlot(
	input: BinaryPeriodPlotInput,
	width: number,
	config: StackedPeriodConfig,
): HTMLElement {
	const { bins, locale } = input
	const edges = bins.period.edges
	const height = Math.round(Math.min(440, Math.max(300, width * 0.48)))
	const bars = barsFrom(bins, config.series)
	const domainMin = edges[0] ?? 0.1
	const domainMax = edges[edges.length - 1] ?? 1
	const ticks = tickMarks.filter(
		(mark) => mark.days > domainMin && mark.days < domainMax,
	)
	const maxCount = stackedMax(bars)
	// A real log scale would drop every label that is not a power of ten,
	// including “1 year”. The axis is linear in log10(days) instead.
	const logMin = Math.log10(domainMin)
	const logMax = Math.log10(domainMax)

	const svg = Plot.plot({
		width,
		height,
		marginTop,
		marginRight,
		marginBottom,
		marginLeft,
		style: plotStyle,
		x: {
			domain: [logMin, logMax],
			axis: null,
			nice: false,
		},
		y: {
			domain: [0, maxCount * 1.08],
			label: t(locale, config.countAxisKey),
			labelArrow: false,
			grid: false,
			tickFormat: (value: number) => formatCompact(value, locale),
			nice: false,
		},
		marks: [
			Plot.gridY({ stroke: theme.line }),
			Plot.axisX({
				anchor: "bottom",
				label: t(locale, "binaryPeriodAxis"),
				labelAnchor: "center",
				labelArrow: false,
				ticks: ticks.map((mark) => Math.log10(mark.days)),
				tickFormat: (value: number) => {
					const mark = ticks.find(
						(item) => Math.abs(Math.log10(item.days) - value) < 0.02,
					)
					if (!mark) return ""
					return locale === "fr" ? mark.fr : mark.en
				},
			}),
			Plot.frame({ stroke: theme.line }),
			Plot.rect(bars, {
				x1: (bar: Bar) => Math.log10(bar.p0),
				x2: (bar: Bar) => Math.log10(bar.p1),
				y1: "y0",
				y2: "y1",
				fill: (bar: Bar) => bar.series.fill,
				insetLeft: 0.4,
				insetRight: 0.4,
				title: (bar: Bar) => tip(bar, locale),
			}),
		],
	}) as SVGSVGElement

	const figure = document.createElement("figure")
	figure.className = "binary-figure"
	const legend = document.createElement("ul")
	legend.className = "binary-legend"
	for (const series of config.series) {
		const item = document.createElement("li")
		const swatch = document.createElement("span")
		swatch.className = "binary-swatch"
		swatch.style.background = series.fill
		item.append(swatch, document.createTextNode(t(locale, series.labelKey)))
		legend.append(item)
	}
	const caption = document.createElement("figcaption")
	caption.textContent = t(locale, config.captionKey).replace(
		"{count}",
		formatCount(bins.solutions, locale),
	)
	figure.append(svg, legend, caption)
	return figure
}
