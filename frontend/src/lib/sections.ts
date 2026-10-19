import type { SectionKind } from "./types"

export type StoryPanel = {
	type: "panel"
	id: string
	kind: SectionKind
	caption?: string
}

export type StoryGroup = {
	type: "group"
	id: string
	titleKey: "sectionGalaxies"
	children: Omit<StoryPanel, "type">[]
}

export type StoryItem = StoryPanel | StoryGroup

export const storyItems: StoryItem[] = [
	{ type: "panel", id: "catalog_totals", kind: "kpi" },
	{ type: "panel", id: "hr_diagram_bins", kind: "hr" },
	{ type: "panel", id: "giant_orbits", kind: "orbits" },
	{
		type: "group",
		id: "galaxies",
		titleKey: "sectionGalaxies",
		children: [
			{ id: "galaxy_funnel", kind: "funnel" },
			{ id: "galaxy_distances", kind: "galaxy-distances" },
		],
	},
	{ type: "panel", id: "milky_way_space3d", kind: "galaxy-3d" },
]
