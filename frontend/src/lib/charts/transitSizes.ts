import * as Plot from "@observablehq/plot"
import { formatCount } from "../format"
import type { Locale } from "../i18n/locale.svelte"
import { type MessageKey, t } from "../i18n/messages"
import { plotStyle, theme } from "../theme"
import type { TransitPlanet } from "../types"
import { formatPeriod, planetSeries } from "./binaryPeriods"

/** Solar-system radii, in Jupiter radii (IAU nominal equatorial values). */
const landmarks: { id: MessageKey; radius: number }[] = [
	{ id: "transitEarth", radius: 6378 / 71492 },
	{ id: "transitNeptune", radius: 24764 / 71492 },
	{ id: "transitJupiter", radius: 1 },
]

const marginTop = 20
const marginRight = 72
const marginBottom = 48
const marginLeft = 52

/** Transits keep the colour they have in the period chart. */
const transitFill =
	planetSeries.find((series) => series.id === "transit")?.fill ?? theme.paper

export type TransitPlotInput = {
	planets: TransitPlanet[]
	locale: Locale
}

function localeTag(locale: Locale): string {
	return locale === "fr" ? "fr-FR" : "en-US"
}

function tip(planet: TransitPlanet, locale: Locale): string {
	const format = new Intl.NumberFormat(localeTag(locale), {
		maximumSignificantDigits: 3,
	})
	const unit = locale === "fr" ? "ua" : "AU"
	const parts = [
		`Gaia DR4 ${planet.id}`,
		t(locale, "transitRadius").replace(
			"{radius}",
			format.format(planet.radius),
		),
		`${format.format(planet.au)} ${unit}`,
	]
	if (planet.period != null) parts.push(formatPeriod(planet.period, locale))
	return parts.join(" · ")
}

/** 1, 2 and 5 times each power of ten inside the domain, like a ruler. */
function logTicks([low, high]: [number, number]): number[] {
	const ticks: number[] = []
	for (
		let power = Math.floor(Math.log10(low));
		power <= Math.ceil(Math.log10(high));
		power += 1
	) {
		for (const step of [1, 2, 5]) {
			const value = step * 10 ** power
			if (value >= low && value <= high) ticks.push(value)
		}
	}
	return ticks
}

function formatTick(value: number, locale: Locale): string {
	return new Intl.NumberFormat(localeTag(locale), {
		maximumSignificantDigits: 2,
	}).format(value)
}

function logDomain(values: number[], pad: number): [number, number] {
	const lowest = Math.min(...values)
	const highest = Math.max(...values)
	return [lowest / pad, highest * pad]
}

export function transitSizePlot(
	input: TransitPlotInput,
	width: number,
): HTMLElement {
	const { planets, locale } = input
	const height = Math.round(Math.min(420, Math.max(300, width * 0.5)))
	const xDomain = logDomain(
		planets.map((planet) => planet.au),
		1.4,
	)
	const yDomain = logDomain(
		planets.map((planet) => planet.radius),
		1.4,
	)
	// Landmarks only where they fall inside the data, so the axis stays tight.
	const shown = landmarks
		.filter((mark) => mark.radius > yDomain[0] && mark.radius < yDomain[1])
		.map((mark) => ({ ...mark, label: t(locale, mark.id) }))

	const svg = Plot.plot({
		width,
		height,
		marginTop,
		marginRight,
		marginBottom,
		marginLeft,
		style: plotStyle,
		x: {
			type: "log",
			domain: xDomain,
			label: t(locale, "orbitDistance"),
			labelAnchor: "center",
			labelArrow: false,
			ticks: logTicks(xDomain),
			tickFormat: (value: number) => formatTick(value, locale),
			nice: false,
		},
		y: {
			type: "log",
			domain: yDomain,
			label: t(locale, "transitRadiusAxis"),
			labelArrow: false,
			ticks: logTicks(yDomain),
			tickFormat: (value: number) => formatTick(value, locale),
			nice: false,
		},
		marks: [
			Plot.frame({ stroke: theme.line }),
			Plot.ruleY(shown, {
				y: "radius",
				stroke: theme.paper,
				strokeOpacity: 0.35,
				strokeDasharray: "3,3",
			}),
			Plot.text(shown, {
				y: "radius",
				text: "label",
				frameAnchor: "right",
				textAnchor: "start",
				dx: 6,
				fill: theme.paper,
				fontSize: 11,
			}),
			Plot.dot(planets, {
				x: "au",
				y: "radius",
				r: width < 560 ? 2.4 : 2.8,
				fill: transitFill,
				fillOpacity: 0.75,
				title: (planet: TransitPlanet) => tip(planet, locale),
			}),
		],
	}) as SVGSVGElement

	const figure = document.createElement("figure")
	figure.className = "transit-figure"
	const caption = document.createElement("figcaption")
	caption.textContent = t(locale, "transitLegend").replace(
		"{count}",
		formatCount(planets.length, locale),
	)
	figure.append(svg, caption)
	return figure
}
