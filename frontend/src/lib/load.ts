import type {
	ColumnarFile,
	ColumnarTable,
	Manifest,
	OrbitPlanet,
	PanelPayload,
	SectionKind,
} from "./types"

const BASE = "/processed"

export async function loadJson<T>(relativePath: string): Promise<T> {
	const response = await fetch(`${BASE}/${relativePath}`)
	if (!response.ok) {
		throw new Error(`Failed to load ${relativePath} (${response.status})`)
	}
	return response.json() as Promise<T>
}

export function loadManifest(): Promise<Manifest> {
	return loadJson<Manifest>("manifest.json")
}

export async function loadColumnar(
	relativePath: string,
): Promise<ColumnarTable> {
	const file = await loadJson<ColumnarFile>(relativePath)
	const strings: Record<string, string[]> = {}
	const numbers: Record<string, Float32Array> = {}

	for (const field of file.fields) {
		const column = file.columns[field.name]
		if (!column) continue
		if (field.type === "string") {
			strings[field.name] = column.map((value) => String(value))
			continue
		}
		numbers[field.name] = Float32Array.from(column as number[])
	}

	return {
		count: file.count,
		fields: file.fields,
		strings,
		numbers,
	}
}

function finiteNumber(value: unknown): number | null {
	return typeof value === "number" && Number.isFinite(value) ? value : null
}

export async function loadOrbits(relativePath: string): Promise<OrbitPlanet[]> {
	const file = await loadJson<ColumnarFile>(relativePath)
	const names = file.columns.pl_name ?? []
	const hosts = file.columns.hostname ?? []
	const distances = file.columns.pl_orbsmax ?? []
	const periods = file.columns.pl_orbper ?? []
	const planets: OrbitPlanet[] = []
	for (let index = 0; index < names.length; index += 1) {
		const au = finiteNumber(distances[index])
		if (au === null || au <= 0) continue
		planets.push({
			name: String(names[index] ?? ""),
			host: String(hosts[index] ?? ""),
			au,
			period: finiteNumber(periods[index]),
		})
	}
	return planets
}

export async function loadPanel(
	kind: SectionKind,
	relativePath: string,
): Promise<PanelPayload> {
	if (kind === "kpi" || kind === "funnel") {
		return { kind, summary: await loadJson(relativePath) }
	}
	if (kind === "hr") {
		return { kind, bins: await loadJson(relativePath) }
	}
	if (kind === "orbits") {
		return { kind, planets: await loadOrbits(relativePath) }
	}
	if (kind === "galaxy-distances") {
		return { kind, bins: await loadJson(relativePath) }
	}
	return { kind, table: await loadColumnar(relativePath) }
}
