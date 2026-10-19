import { localizedFieldLabel } from "./i18n/data"
import type { Locale } from "./i18n/locale.svelte"

function tag(loc: Locale): string {
	return loc === "fr" ? "fr-FR" : "en-US"
}

export function formatCount(value: number, loc: Locale): string {
	return new Intl.NumberFormat(tag(loc)).format(value)
}

export function formatCompact(value: number, loc: Locale): string {
	return new Intl.NumberFormat(tag(loc), {
		notation: "compact",
		maximumFractionDigits: 1,
	}).format(value)
}

export function formatMeasure(value: number, loc: Locale): string {
	return new Intl.NumberFormat(tag(loc), {
		maximumFractionDigits: 2,
	}).format(value)
}

export function formatDate(iso: string, loc: Locale): string {
	const date = new Date(iso)
	if (Number.isNaN(date.getTime())) return iso
	return new Intl.DateTimeFormat(tag(loc), { dateStyle: "long" }).format(date)
}

const FIELD_UNITS: Record<string, string> = {
	ra: "°",
	dec: "°",
	phot_g_mean_mag: "mag",
	x_gc: "kpc",
	y_gc: "kpc",
	z_gc: "kpc",
	distance_pc: "pc",
	parallax: "mas",
}

export function formatField(
	name: string,
	value: string | number,
	loc: Locale,
): string {
	const label = localizedFieldLabel(loc, name)
	if (name === "source_id") return `${label} ${value}`
	const unit = FIELD_UNITS[name]
	const text = typeof value === "number" ? formatMeasure(value, loc) : value
	return unit ? `${label} ${text} ${unit}` : `${label} ${text}`
}
