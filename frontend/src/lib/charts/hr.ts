import * as Plot from "@observablehq/plot";
import { plotStyle, theme } from "../theme";
import type { Binned2d } from "../types";

type Rgb = [number, number, number];

type Cell = {
  x1: number;
  x2: number;
  y1: number;
  y2: number;
  fill: string;
};

const background: Rgb = [0x0c, 0x0c, 0x0c];

/** Stellar tint along BP−RP: blue, then white-yellow, then red. */
const starStops: { at: number; rgb: Rgb }[] = [
  { at: -0.5, rgb: [80, 150, 255] },
  { at: 0.2, rgb: [190, 214, 255] },
  { at: 0.85, rgb: [255, 228, 170] },
  { at: 1.5, rgb: [255, 156, 64] },
  { at: 2.4, rgb: [255, 72, 48] },
  { at: 3.6, rgb: [176, 32, 42] },
  { at: 5, rgb: [120, 18, 28] },
];

function mix(from: Rgb, to: Rgb, t: number): Rgb {
  return [
    Math.round(from[0] + (to[0] - from[0]) * t),
    Math.round(from[1] + (to[1] - from[1]) * t),
    Math.round(from[2] + (to[2] - from[2]) * t),
  ];
}

function starRgb(bpRp: number): Rgb {
  if (bpRp <= starStops[0].at) return starStops[0].rgb;
  const last = starStops[starStops.length - 1];
  if (bpRp >= last.at) return last.rgb;
  for (let index = 1; index < starStops.length; index++) {
    const next = starStops[index];
    const previous = starStops[index - 1];
    if (bpRp > next.at) continue;
    const span = next.at - previous.at;
    const t = span === 0 ? 0 : (bpRp - previous.at) / span;
    return mix(previous.rgb, next.rgb, t);
  }
  return last.rgb;
}

function fillFor(bpRp: number, count: number, logMax: number): string {
  const presence = Math.log(count) / logMax;
  const density = presence ** 2.6;
  const brightness = 0.62 * density;
  const [r, g, b] = mix(background, starRgb(bpRp), brightness);
  return `rgb(${r} ${g} ${b})`;
}

function cellsFromBins(bins: Binned2d): Cell[] {
  const cells: Cell[] = [];
  const xEdges = bins.x.edges;
  const yEdges = bins.y.edges;
  let max = 1;
  for (const row of bins.counts) {
    if (!row) continue;
    for (const count of row) {
      if (count > max) max = count;
    }
  }
  const logMax = Math.log(max);
  for (let yIndex = 0; yIndex < yEdges.length - 1; yIndex++) {
    const row = bins.counts[yIndex];
    if (!row) continue;
    for (let xIndex = 0; xIndex < xEdges.length - 1; xIndex++) {
      const count = row[xIndex] ?? 0;
      if (count <= 0) continue;
      const x1 = xEdges[xIndex];
      const x2 = xEdges[xIndex + 1];
      cells.push({
        x1,
        x2,
        y1: yEdges[yIndex],
        y2: yEdges[yIndex + 1],
        fill: fillFor((x1 + x2) / 2, count, logMax),
      });
    }
  }
  return cells;
}

export function hrPlot(bins: Binned2d, width: number): HTMLElement {
  const cells = cellsFromBins(bins);
  return Plot.plot({
    width,
    height: Math.round(Math.min(640, Math.max(420, width * 0.72))),
    marginTop: 20,
    marginRight: 24,
    marginBottom: 48,
    marginLeft: 72,
    style: plotStyle,
    x: { label: bins.x.label },
    y: { label: bins.y.label, reverse: bins.y.id === "mg" },
    marks: [
      Plot.frame({ stroke: theme.line }),
      Plot.rect(cells, {
        x1: "x1",
        x2: "x2",
        y1: "y1",
        y2: "y2",
        fill: "fill",
        inset: 0,
      }),
    ],
  }) as HTMLElement;
}
