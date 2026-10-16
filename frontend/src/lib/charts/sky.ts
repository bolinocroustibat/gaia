import { geoGraticule, geoPath, type GeoPermissibleObjects } from "d3-geo";
import { geoMollweide } from "d3-geo-projection";
import { rampCss, theme } from "../theme";

export type SkySpec = {
  ids: string[];
  ra: Float32Array;
  dec: Float32Array;
  mag: Float32Array;
};

export type ProjectedPoints = {
  x: Float32Array;
  y: Float32Array;
};

function projectionFor(width: number, height: number) {
  const projection = geoMollweide().precision(0.2).reflectX(true);
  projection.fitExtent(
    [
      [8, 8],
      [width - 8, height - 8],
    ],
    { type: "Sphere" },
  );
  return projection;
}

function strokeHairline(
  context: CanvasRenderingContext2D,
  path: ReturnType<typeof geoPath>,
  object: GeoPermissibleObjects,
  alpha: number,
) {
  context.save();
  context.globalAlpha = alpha;
  context.strokeStyle = theme.muted;
  context.lineWidth = 1;
  context.beginPath();
  path(object);
  context.stroke();
  context.restore();
}

export function drawSky(
  context: CanvasRenderingContext2D,
  width: number,
  height: number,
  spec: SkySpec,
): ProjectedPoints {
  context.clearRect(0, 0, width, height);
  const projection = projectionFor(width, height);
  const path = geoPath(projection, context);
  const graticule = geoGraticule().step([60, 30]);
  strokeHairline(context, path, { type: "Sphere" }, 0.55);
  strokeHairline(context, path, graticule(), 0.28);

  const count = spec.ra.length;
  const xs = new Float32Array(count);
  const ys = new Float32Array(count);
  let minMag = Infinity;
  let maxMag = -Infinity;
  for (let i = 0; i < count; i++) {
    const mag = spec.mag[i];
    if (mag < minMag) minMag = mag;
    if (mag > maxMag) maxMag = mag;
  }
  const span = maxMag - minMag || 1;
  for (let i = 0; i < count; i++) {
    const projected = projection([spec.ra[i], spec.dec[i]]);
    if (!projected) {
      xs[i] = Number.NaN;
      ys[i] = Number.NaN;
      continue;
    }
    xs[i] = projected[0];
    ys[i] = projected[1];
    const t = 1 - (spec.mag[i] - minMag) / span;
    context.fillStyle = rampCss(0.28 + 0.72 * t);
    context.fillRect(projected[0], projected[1], 1.6, 1.6);
  }
  return { x: xs, y: ys };
}

export function nearestPoint(px: number, py: number, points: ProjectedPoints, radius = 8): number {
  const limit = radius * radius;
  let best = -1;
  let bestDistance = limit;
  const { x, y } = points;
  for (let i = 0; i < x.length; i++) {
    const dx = x[i] - px;
    const dy = y[i] - py;
    if (Number.isNaN(dx) || Number.isNaN(dy)) continue;
    const distance = dx * dx + dy * dy;
    if (distance < bestDistance) {
      bestDistance = distance;
      best = i;
    }
  }
  return best;
}
