import * as Plot from "@observablehq/plot"
import { formatCompact, formatCount } from "../format"
import type { Locale } from "../i18n/locale.svelte"
import { t } from "../i18n/messages"
import { plotStyle, theme } from "../theme"
import type { DistanceHistogram } from "../types"

type Rgb = [number, number, number]

/** Unstretched light is the page white. Deep red once the stretch is clearly cosmological. */
const near: Rgb = [0xf4, 0xf1, 0xea]
const far: Rgb = [0xc4, 0x27, 0x2f]
/** Redshift at which the bar reaches full deep red (below zMax in this sample). */
const FULL_RED_AT_Z = 0.4
/** Between sqrt (too pink at 1 Gly) and a steep power (too white there). */
const RED_RAMP_POWER = 1.35

const marginRight = 20
const marginBottom = 58
const marginLeft = 52
const marginTop = 52

type Bar = {
	gly0: number
	gly1: number
	z0: number
	z1: number
	count: number
	fill: string
}

export type GalaxyDistancePlotInput = {
	bins: DistanceHistogram
	locale: Locale
}

function mix(from: Rgb, to: Rgb, amount: number): Rgb {
	return [
		Math.round(from[0] + (to[0] - from[0]) * amount),
		Math.round(from[1] + (to[1] - from[1]) * amount),
		Math.round(from[2] + (to[2] - from[2]) * amount),
	]
}

function css(rgb: Rgb): string {
	return `rgb(${rgb[0]} ${rgb[1]} ${rgb[2]})`
}

function localeTag(locale: Locale): string {
	return locale === "fr" ? "fr-FR" : "en-US"
}

function formatRedshift(value: number, locale: Locale): string {
	return new Intl.NumberFormat(localeTag(locale), {
		minimumFractionDigits: 1,
		maximumFractionDigits: 1,
	}).format(value)
}

function formatGly(value: number, locale: Locale): string {
	return new Intl.NumberFormat(localeTag(locale), {
		maximumFractionDigits: value < 1 ? 2 : 1,
	}).format(value)
}

/** Distance at one redshift, read off the stored edges. */
function glyAt(redshift: number, zEdges: number[], glyEdges: number[]): number {
	if (redshift <= zEdges[0]) return glyEdges[0]
	const last = zEdges.length - 1
	if (redshift >= zEdges[last]) return glyEdges[last]
	let index = 0
	while (index < last - 1 && zEdges[index + 1] < redshift) index += 1
	const span = zEdges[index + 1] - zEdges[index]
	const share = span === 0 ? 0 : (redshift - zEdges[index]) / span
	return glyEdges[index] + share * (glyEdges[index + 1] - glyEdges[index])
}

function barsFrom(bins: DistanceHistogram): Bar[] {
	const zEdges = bins.z.edges
	const glyEdges = bins.distance.edges
	const bars: Bar[] = []
	for (let index = 0; index < bins.counts.length; index += 1) {
		const count = bins.counts[index] ?? 0
		if (count <= 0) continue
		const gly0 = glyEdges[index] ?? 0
		const gly1 = glyEdges[index + 1] ?? gly0
		const z0 = zEdges[index] ?? 0
		const z1 = zEdges[index + 1] ?? z0
		const midZ = (z0 + z1) / 2
		const linear =
			FULL_RED_AT_Z === 0 ? 0 : Math.min(1, Math.max(0, midZ / FULL_RED_AT_Z))
		const stretch = linear ** RED_RAMP_POWER
		bars.push({
			gly0,
			gly1,
			z0,
			z1,
			count,
			fill: css(mix(near, far, stretch)),
		})
	}
	return bars
}

function tip(bar: Bar, locale: Locale): string {
	const count = formatCount(bar.count, locale)
	const place = `${formatGly(bar.gly0, locale)}–${formatGly(bar.gly1, locale)}`
	const stretch = `${formatRedshift(bar.z0, locale)}–${formatRedshift(bar.z1, locale)}`
	const unit =
		locale === "fr" ? "milliards d'années-lumière" : "billions of light-years"
	const shift = locale === "fr" ? "décalage" : "stretch"
	return `${count} · ${place} ${unit} · ${shift} ${stretch}`
}

export function galaxyDistancePlot(
	input: GalaxyDistancePlotInput,
	width: number,
): HTMLElement {
	const { bins, locale } = input
	const zEdges = bins.z.edges
	const glyEdges = bins.distance.edges
	const height = Math.round(Math.min(440, Math.max(300, width * 0.48)))
	const maxGly = glyEdges[glyEdges.length - 1] ?? 1
	const bars = barsFrom(bins)
	const maxCount = bars.reduce(
		(highest, bar) => Math.max(highest, bar.count),
		1,
	)
	const distanceTicks: number[] = []
	const distanceStep = maxGly > 8 ? 2 : 1
	for (let tick = distanceStep; tick < maxGly; tick += distanceStep)
		distanceTicks.push(tick)

	const domainMax = maxGly * 1.02
	const nearby = t(locale, "galaxyNearby")
	const nearbyWidth = nearby.length * 6.6
	const innerWidth = Math.max(1, width - marginLeft - marginRight)
	const redshiftTicks = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1, 1.2, 1.5]
		.filter(
			(redshift) =>
				redshift > zEdges[0] && redshift < zEdges[zEdges.length - 1],
		)
		.map((redshift) => ({ redshift, gly: glyAt(redshift, zEdges, glyEdges) }))
		.filter(
			(tick) => (tick.gly / domainMax) * innerWidth - 18 > nearbyWidth + 10,
		)

	const svg = Plot.plot({
		width,
		height,
		marginTop,
		marginRight,
		marginBottom,
		marginLeft,
		style: plotStyle,
		x: {
			domain: [0, domainMax],
			axis: null,
			nice: false,
		},
		y: {
			domain: [0, maxCount * 1.08],
			label: null,
			grid: false,
			tickFormat: (value: number) => formatCompact(value, locale),
			nice: false,
		},
		marks: [
			Plot.gridY({ stroke: theme.line }),
			Plot.axisX({
				anchor: "bottom",
				label: t(locale, "galaxyDistanceAxis"),
				labelAnchor: "center",
				labelArrow: false,
				ticks: distanceTicks,
				tickFormat: (value: number) => formatGly(value, locale),
			}),
			Plot.axisX({
				anchor: "top",
				label: t(locale, "galaxyRedshiftAxis"),
				labelAnchor: "center",
				labelArrow: false,
				ticks: redshiftTicks.map((tick) => tick.gly),
				tickFormat: (value: number) => {
					if (redshiftTicks.length === 0) return ""
					const nearest = redshiftTicks.reduce((best, tick) =>
						Math.abs(tick.gly - value) < Math.abs(best.gly - value)
							? tick
							: best,
					)
					return formatRedshift(nearest.redshift, locale)
				},
			}),
			Plot.frame({ stroke: theme.line }),
			Plot.rect(bars, {
				x1: "gly0",
				x2: "gly1",
				y1: 0,
				y2: "count",
				fill: "fill",
				inset: 0.4,
				title: (bar: Bar) => tip(bar, locale),
			}),
			Plot.text([{ label: nearby }], {
				x: 0,
				text: "label",
				frameAnchor: "top",
				lineAnchor: "bottom",
				textAnchor: "start",
				dy: -6,
				fill: theme.paper,
				fontSize: 11,
			}),
		],
	}) as SVGSVGElement

	const figure = document.createElement("figure")
	figure.className = "distance-figure"
	const caption = document.createElement("figcaption")
	caption.textContent = t(locale, "galaxyDistanceLegend")
	figure.append(svg, caption)
	return figure
}
