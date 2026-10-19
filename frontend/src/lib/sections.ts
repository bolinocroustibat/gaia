import type { SectionKind } from "./types"

export type StorySection = {
	id: string
	kind: SectionKind
	caption?: string
}

export const storySections: StorySection[] = [
	{ id: "catalog_totals", kind: "kpi" },
	{ id: "hr_diagram_bins", kind: "hr" },
	{ id: "giant_orbits", kind: "orbits" },
	{ id: "milky_way_space3d", kind: "galaxy-3d" },
	{ id: "galaxy_funnel", kind: "funnel" },
	{ id: "galaxy_distances", kind: "galaxy-distances" },
]
