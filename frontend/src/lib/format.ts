const countFormat = new Intl.NumberFormat("fr-FR");
const compactFormat = new Intl.NumberFormat("fr-FR", {
  notation: "compact",
  maximumFractionDigits: 1,
});
const measureFormat = new Intl.NumberFormat("fr-FR", {
  maximumFractionDigits: 2,
});
const dateFormat = new Intl.DateTimeFormat("fr-FR", { dateStyle: "long" });

export function formatCount(value: number): string {
  return countFormat.format(value);
}

export function formatCompact(value: number): string {
  return compactFormat.format(value);
}

export function formatMeasure(value: number): string {
  return measureFormat.format(value);
}

export function formatDate(iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return dateFormat.format(date);
}

const FIELD_LABELS: Record<string, string> = {
  source_id: "identifiant",
  ra: "ascension droite",
  dec: "déclinaison",
  phot_g_mean_mag: "brillance",
  x_gc: "x",
  y_gc: "y",
  z_gc: "z",
  distance_pc: "distance",
};

const FIELD_UNITS: Record<string, string> = {
  ra: "°",
  dec: "°",
  phot_g_mean_mag: "mag",
  x_gc: "kpc",
  y_gc: "kpc",
  z_gc: "kpc",
  distance_pc: "pc",
};

export function formatField(name: string, value: string | number): string {
  const label = FIELD_LABELS[name] ?? name;
  if (name === "source_id") return `${label} ${value}`;
  const unit = FIELD_UNITS[name];
  const text = typeof value === "number" ? formatMeasure(value) : value;
  return unit ? `${label} ${text} ${unit}` : `${label} ${text}`;
}
