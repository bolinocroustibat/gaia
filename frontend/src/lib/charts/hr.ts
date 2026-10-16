import * as Plot from "@observablehq/plot";
import { plotStyle, rampHex, theme } from "../theme";
import type { Binned2d } from "../types";

type Cell = {
  x1: number;
  x2: number;
  y1: number;
  y2: number;
  count: number;
};

function cellsFromBins(bins: Binned2d): Cell[] {
  const cells: Cell[] = [];
  const xEdges = bins.x.edges;
  const yEdges = bins.y.edges;
  for (let yIndex = 0; yIndex < yEdges.length - 1; yIndex++) {
    const row = bins.counts[yIndex];
    if (!row) continue;
    for (let xIndex = 0; xIndex < xEdges.length - 1; xIndex++) {
      const count = row[xIndex] ?? 0;
      if (count <= 0) continue;
      cells.push({
        x1: xEdges[xIndex],
        x2: xEdges[xIndex + 1],
        y1: yEdges[yIndex],
        y2: yEdges[yIndex + 1],
        count,
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
    y: { label: bins.y.label },
    color: {
      type: "log",
      label: "Nombre",
      range: [rampHex(0.22), theme.accent, theme.paper],
    },
    marks: [
      Plot.frame({ stroke: theme.line }),
      Plot.rect(cells, {
        x1: "x1",
        x2: "x2",
        y1: "y1",
        y2: "y2",
        fill: "count",
        inset: 0,
      }),
    ],
  }) as HTMLElement;
}
