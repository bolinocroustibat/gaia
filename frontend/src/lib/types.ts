export type DatasetFormat = "summary" | "binned2d" | "columnar"

export type ReleaseId = "dr3" | "dr4"

export type DatasetMeta = {
	id: string
	release?: ReleaseId
	/** A second file the chart compares against, such as the NASA orbits. */
	comparePath?: string
	path: string
	tier: string
	format: DatasetFormat | string
	label: string
	helpText: string
	sourceNote?: string
	credit?: string
	count?: number
	tooltipFields?: string[]
}

export type Manifest = {
	schemaVersion: number
	release: string
	generated_at: string
	license: { id: string; url: string }
	credit: string
	source_id_type: string
	datasets: DatasetMeta[]
}

export type CountRow = {
	id?: string
	object_type?: string
	label: string
	count: number
}

export type SummaryFile = {
	release: string
	generated_at: string
	credit: string
	license: { id: string; url: string }
	rows?: CountRow[]
	bar_rows?: CountRow[]
	steps?: CountRow[]
}

export type BinnedAxis = {
	id: string
	label: string
	unit: string
	edges: number[]
}

export type Binned2d = {
	x: BinnedAxis
	y: BinnedAxis
	counts: number[][]
}

export type ColumnField = {
	name: string
	type: "string" | "number"
	unit?: string
}

export type ColumnarFile = {
	schemaVersion: number
	dataset: string
	count: number
	fields: ColumnField[]
	columns: Record<string, string[] | number[]>
}

export type ColumnarTable = {
	count: number
	fields: ColumnField[]
	strings: Record<string, string[]>
	numbers: Record<string, Float32Array>
}

export type OrbitPlanet = {
	name: string
	host: string
	au: number
	period: number | null
}

/** One Gaia DR4 planet candidate placed by its distance to its star. */
export type OrbitCandidate = {
	id: string
	method: string
	au: number
	period: number | null
	mass: number | null
	radius: number | null
}

/** One transiting Gaia DR4 candidate with an estimated radius. */
export type TransitPlanet = {
	id: string
	au: number
	period: number | null
	radius: number
}

export type DistanceHistogram = {
	cosmology: string
	distance_kind: string
	z: { id: string; edges: number[] }
	distance: { id: string; unit: string; edges: number[] }
	counts: number[]
}

export type PeriodSeries = {
	id: string
	counts: number[]
}

export type PeriodHistogram = {
	period: { id: string; unit: string; edges: number[] }
	series: PeriodSeries[]
	solutions: number
	sources?: number
}

export type SectionKind =
	| "kpi"
	| "hr"
	| "galaxy-3d"
	| "funnel"
	| "orbits"
	| "galaxy-distances"
	| "binary-periods"
	| "planet-distances"
	| "planet-periods"
	| "transit-sizes"

export type PanelPayload =
	| { kind: "kpi" | "funnel"; summary: SummaryFile }
	| { kind: "hr"; bins: Binned2d }
	| { kind: "galaxy-3d"; table: ColumnarTable }
	| { kind: "orbits"; planets: OrbitPlanet[] }
	| { kind: "galaxy-distances"; bins: DistanceHistogram }
	| { kind: "binary-periods"; bins: PeriodHistogram }
	| {
			kind: "planet-distances"
			planets: OrbitPlanet[]
			candidates: OrbitCandidate[]
	  }
	| { kind: "planet-periods"; bins: PeriodHistogram }
	| { kind: "transit-sizes"; planets: TransitPlanet[] }
