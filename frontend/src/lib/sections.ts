import type { SectionKind } from "./types";

export type StorySection = {
  id: string;
  kind: SectionKind;
  caption?: string;
};

export const storySections: StorySection[] = [
  { id: "catalog_totals", kind: "kpi" },
  { id: "object_types", kind: "types" },
  { id: "hr_diagram_bins", kind: "hr" },
  { id: "milky_way_sky2d", kind: "galaxy-sky" },
  { id: "milky_way_space3d", kind: "galaxy-3d" },
  { id: "galaxy_funnel", kind: "funnel" },
];
