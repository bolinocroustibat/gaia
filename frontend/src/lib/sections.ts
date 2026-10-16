import type { SectionKind } from "./types";

export type StorySection = {
  id: string;
  kind: SectionKind;
  caption?: string;
};

export const storySections: StorySection[] = [
  { id: "catalog_totals", kind: "kpi" },
  { id: "object_types", kind: "types" },
  {
    id: "sky_density_nside64",
    kind: "density",
    caption: "Échantillon d’étoiles du disque, pas tout le catalogue.",
  },
  { id: "hr_diagram_bins", kind: "hr" },
  { id: "local_galaxies_sky2d", kind: "galaxy-sky" },
  { id: "local_galaxies_space3d", kind: "galaxy-3d" },
  { id: "galaxy_funnel", kind: "funnel" },
];
