import type { ColumnarFile, ColumnarTable, Manifest, PanelPayload, SectionKind } from "./types";

const BASE = "/processed";

export async function loadJson<T>(relativePath: string): Promise<T> {
  const response = await fetch(`${BASE}/${relativePath}`);
  if (!response.ok) {
    throw new Error(`Failed to load ${relativePath} (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export function loadManifest(): Promise<Manifest> {
  return loadJson<Manifest>("manifest.json");
}

export async function loadColumnar(relativePath: string): Promise<ColumnarTable> {
  const file = await loadJson<ColumnarFile>(relativePath);
  const strings: Record<string, string[]> = {};
  const numbers: Record<string, Float32Array> = {};

  for (const field of file.fields) {
    const column = file.columns[field.name];
    if (!column) continue;
    if (field.type === "string") {
      strings[field.name] = column.map((value) => String(value));
      continue;
    }
    numbers[field.name] = Float32Array.from(column as number[]);
  }

  return {
    count: file.count,
    fields: file.fields,
    strings,
    numbers,
  };
}

export async function loadPanel(kind: SectionKind, relativePath: string): Promise<PanelPayload> {
  if (kind === "kpi" || kind === "types" || kind === "funnel") {
    return { kind, summary: await loadJson(relativePath) };
  }
  if (kind === "hr") {
    return { kind, bins: await loadJson(relativePath) };
  }
  if (kind === "density") {
    return { kind, sky: await loadJson(relativePath) };
  }
  return { kind, table: await loadColumnar(relativePath) };
}
