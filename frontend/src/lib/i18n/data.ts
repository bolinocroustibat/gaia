import type { Binned2d, CountRow, DatasetMeta } from "../types"
import type { Locale } from "./locale.svelte"

const datasetEn: Record<
	string,
	{ label: string; helpText: string; sourceNote?: string }
> = {
	catalog_totals: {
		label: "What has Gaia seen?",
		helpText:
			"Almost everything Gaia has listed is a star. Everything else is only a tiny fraction of the catalogue.",
	},
	galaxy_distances: {
		label: "How far away are they?",
		helpText:
			"For the 1,367,153 galaxies whose distance is estimated. The farther right a bar sits, the more its light is pulled toward red.",
	},
	galaxy_funnel: {
		label: "How far do we see the galaxies?",
		helpText:
			"For some of the nearly 5 million likely galaxies Gaia has catalogued, Gaia can estimate how far away they are. For some of those, it can also measure their shape.",
	},
	giant_orbits: {
		label: "How far from their star do giant exoplanets orbit?",
		helpText:
			"The Gaia telescope says a little about these planets, and almost nothing about the smaller ones. But Gaia’s data can be filled in with NASA’s catalogue of confirmed exoplanets.",
		sourceNote: "NASA Exoplanet Archive, confirmed planets (pscomppars)",
	},
	hr_diagram_bins: {
		label: "When you observe this many celestial bodies, do families show up?",
		helpText:
			"Yes! Most of the objects Gaia flags are stars. For each one, when it can, it measures a brightness and a color. Plot them on a diagram and three clear groups appear: three broad families, each tied to a stage in a star’s life.",
		sourceNote: "Absolute G magnitude for sources with a reliable parallax",
	},
	milky_way_space3d: {
		label: "Galactic disk — in 3D",
		helpText:
			"A sample of stars, binary or not, spread around the Sun. From the side you see the disk thickness.",
	},
	disk_stars_sample: {
		label: "Disk star sample",
		helpText: "Subset of stars with reliable distances, for scatter plots.",
	},
}

const rowEn: Record<string, string> = {
	objects_total: "Objects listed by Gaia, including…",
	galaxy_candidates: "likely galaxies",
	qso_candidates:
		"likely quasars\nquasars are ultra-bright galactic cores powered by a supermassive black hole",
	binary_stars: "likely binary stars",
	other_sources: "likely single stars and other objects",
	galaxy_candidates_total:
		"Likely galaxies\nThe ones Gaia tells apart from stars.",
	galaxy_candidates_with_redshift:
		"With an estimated distance\nTheir light is stretched toward red: the more it stretches, the farther they are.",
	galaxy_candidates_with_shape:
		"With a measured shape\nFrom space, without the blur of the atmosphere, Gaia reconstructs their light profile.",
	galaxy_candidates_without_redshift: "No known far distance",
	strict_galaxies_nss: "Nearby: other flagged sources (~58k)",
	strict_galaxies_nearby_parallax: "With measured distance (parallax, 3D map)",
	strict_galaxies_with_redshift: "With distance from redshift",
	object_type: "Object type",
}

const axisEn: Record<string, string> = {
	bp_rp: "Surface temperature (estimated from the blue–red color)",
	mg: "Luminosity (times the Sun)",
}

const fieldEn: Record<string, string> = {
	source_id: "identifier",
	ra: "right ascension",
	dec: "declination",
	phot_g_mean_mag: "brightness",
	parallax: "parallax",
	bp_rp: "color",
	x_gc: "x",
	y_gc: "y",
	z_gc: "z",
	distance_pc: "distance",
}

export function localizedDataset(
	loc: Locale,
	meta: DatasetMeta,
): Pick<DatasetMeta, "label" | "helpText" | "sourceNote"> {
	if (loc === "fr") {
		return {
			label: meta.label,
			helpText: meta.helpText,
			sourceNote: meta.sourceNote,
		}
	}
	const en = datasetEn[meta.id]
	if (!en) {
		return {
			label: meta.label,
			helpText: meta.helpText,
			sourceNote: meta.sourceNote,
		}
	}
	return {
		label: en.label,
		helpText: en.helpText,
		sourceNote: en.sourceNote ?? meta.sourceNote,
	}
}

export function localizedRowLabel(loc: Locale, row: CountRow): string {
	if (loc === "fr") return row.label
	const key = row.id ?? row.object_type
	if (key && rowEn[key]) return rowEn[key]
	return row.label
}

export function localizedRows(loc: Locale, rows: CountRow[]): CountRow[] {
	if (loc === "fr") return rows
	return rows.map((row) => ({ ...row, label: localizedRowLabel(loc, row) }))
}

export function localizedBins(loc: Locale, bins: Binned2d): Binned2d {
	if (loc === "fr") return bins
	return {
		...bins,
		x: { ...bins.x, label: axisEn[bins.x.id] ?? bins.x.label },
		y: { ...bins.y, label: axisEn[bins.y.id] ?? bins.y.label },
	}
}

export function localizedFieldLabel(loc: Locale, name: string): string {
	if (loc === "fr") return fieldFr[name] ?? name
	return fieldEn[name] ?? name
}

const fieldFr: Record<string, string> = {
	source_id: "identifiant",
	ra: "ascension droite",
	dec: "déclinaison",
	phot_g_mean_mag: "brillance",
	parallax: "parallaxe",
	bp_rp: "couleur",
	x_gc: "x",
	y_gc: "y",
	z_gc: "z",
	distance_pc: "distance",
}
