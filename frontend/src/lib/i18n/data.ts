import type { Binned2d, CountRow, DatasetMeta } from "../types";
import type { Locale } from "./locale.svelte";

const datasetEn: Record<
  string,
  { label: string; helpText: string; sourceNote?: string }
> = {
  catalog_totals: {
    label: "Catalogue size",
    helpText:
      "Four round numbers: the whole catalogue, likely galaxies and quasars, and likely binary stars.",
  },
  object_types: {
    label: "Object types",
    helpText: "A simplified split of the catalogue. Very tall bars are clipped on screen.",
  },
  galaxy_funnel: {
    label: "Galaxies: how many and how far?",
    helpText:
      "First the list of likely galaxies, then nearby objects whose distance we can estimate.",
  },
  hr_diagram_bins: {
    label: "When you observe this many celestial bodies, do families show up?",
    helpText:
      "Yes! Most of the objects Gaia flags are stars. For each one, when it can, the probe measures a brightness and a color. Plot them on a diagram and three clear groups appear: three broad families, each tied to a stage in a star’s life.",
    sourceNote: "Gaia DR3 absolute G magnitude for sources with a reliable parallax",
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
};

const rowEn: Record<string, string> = {
  objects_total: "Objects listed by Gaia, including…",
  galaxy_candidates: "likely galaxies",
  qso_candidates:
    "likely quasars (ultra-bright galactic cores powered by a supermassive black hole)",
  binary_stars: "likely binary stars",
  other_sources: "Mostly single stars and other objects",
  galaxy_candidates_total: "Likely galaxies (Gaia list)",
  galaxy_candidates_with_redshift: "Far away: distance measured",
  galaxy_candidates_without_redshift: "No known far distance",
  strict_galaxies_nss: "Nearby: other flagged sources (~58k)",
  strict_galaxies_nearby_parallax: "With measured distance (parallax, 3D map)",
  strict_galaxies_with_redshift: "With distance from redshift",
  object_type: "Object type",
};

const axisEn: Record<string, string> = {
  bp_rp: "Surface temperature (estimated from the blue–red color)",
  mg: "Luminosity (times the Sun)",
};

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
};

export function localizedDataset(
  loc: Locale,
  meta: DatasetMeta,
): Pick<DatasetMeta, "label" | "helpText" | "sourceNote"> {
  if (loc === "fr") {
    return { label: meta.label, helpText: meta.helpText, sourceNote: meta.sourceNote };
  }
  const en = datasetEn[meta.id];
  if (!en) {
    return { label: meta.label, helpText: meta.helpText, sourceNote: meta.sourceNote };
  }
  return {
    label: en.label,
    helpText: en.helpText,
    sourceNote: en.sourceNote ?? meta.sourceNote,
  };
}

export function localizedRowLabel(loc: Locale, row: CountRow): string {
  if (loc === "fr") return row.label;
  const key = row.id ?? row.object_type;
  if (key && rowEn[key]) return rowEn[key];
  return row.label;
}

export function localizedRows(loc: Locale, rows: CountRow[]): CountRow[] {
  if (loc === "fr") return rows;
  return rows.map((row) => ({ ...row, label: localizedRowLabel(loc, row) }));
}

export function localizedBins(loc: Locale, bins: Binned2d): Binned2d {
  if (loc === "fr") return bins;
  return {
    ...bins,
    x: { ...bins.x, label: axisEn[bins.x.id] ?? bins.x.label },
    y: { ...bins.y, label: axisEn[bins.y.id] ?? bins.y.label },
  };
}

export function localizedFieldLabel(loc: Locale, name: string): string {
  if (loc === "fr") return fieldFr[name] ?? name;
  return fieldEn[name] ?? name;
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
};
