import type { CountRow } from "../types";

const FUNNEL_IDS = ["galaxy_candidates_total", "galaxy_candidates_with_redshift"];

export function funnelRows(steps: CountRow[]): CountRow[] {
  const byId = new Map(steps.map((step) => [step.id, step]));
  return FUNNEL_IDS.flatMap((id) => {
    const step = byId.get(id);
    if (!step || step.count <= 0) return [];
    return [step];
  });
}
