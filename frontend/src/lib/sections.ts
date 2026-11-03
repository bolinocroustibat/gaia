import type { MessageKey } from "./i18n/messages"
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
	titleKey: "sectionGalaxies" | "sectionBinaries"
	children: Omit<StoryPanel, "type">[]
}

/** One switch for a whole section: each position shows its own charts. */
export type StoryViews = {
	type: "views"
	id: string
	/** Dataset whose label titles the section. */
	lead: string
	options: { id: string; labelKey: MessageKey; hintKey?: MessageKey }[]
	/** Section help per position; the lead dataset's help when absent. */
	helpKeys: Partial<Record<string, MessageKey>>
	views: Record<string, Omit<StoryPanel, "type">[]>
}

export type StoryItem = StoryPanel | StoryGroup | StoryViews

export const storyItems: StoryItem[] = [
	{ type: "panel", id: "catalog_totals", kind: "kpi" },
	{ type: "panel", id: "hr_diagram_bins", kind: "hr" },
	{
		type: "group",
		id: "binaries",
		titleKey: "sectionBinaries",
		children: [{ id: "binary_periods", kind: "binary-periods" }],
	},
	{
		type: "views",
		id: "exoplanets",
		lead: "giant_orbits",
		options: [
			{ id: "nasa", labelKey: "viewNasa", hintKey: "viewNasaHint" },
			{ id: "dr4", labelKey: "viewDr4" },
		],
		helpKeys: { dr4: "exoplanetsDr4Help" },
		views: {
			nasa: [{ id: "giant_orbits", kind: "orbits" }],
			dr4: [
				{ id: "planet_distances", kind: "planet-distances" },
				{ id: "planet_periods", kind: "planet-periods" },
				{ id: "transit_sizes", kind: "transit-sizes" },
			],
		},
	},
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
