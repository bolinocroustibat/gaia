import { geoGraticule, geoPath, type GeoPermissibleObjects } from "d3-geo";
import { geoMollweide } from "d3-geo-projection";
import { nestToCorners } from "../healpix";
import { rampCss, theme } from "../theme";

export type DensitySky = {
  mode: "density";
  nside: number;
  counts: number[];
};

export type PointSky = {
  mode: "points";
  ids: string[];
  ra: Float32Array;
  dec: Float32Array;
  mag: Float32Array;
};

export type SkySpec = DensitySky | PointSky;

export type ProjectedPoints = {
  x: Float32Array;
  y: Float32Array;
};

type DensityPoly = {
  ring: [number, number][];
  color: string;
};

const polysCache = new WeakMap<number[], DensityPoly[]>();

function ringIsCompact(ring: [number, number][]): boolean {
  for (let index = 0; index < ring.length; index++) {
    const current = ring[index];
    const next = ring[(index + 1) % ring.length];
    let deltaRa = Math.abs(current[0] - next[0]);
    if (deltaRa > 180) deltaRa = 360 - deltaRa;
    if (deltaRa > 15 || Math.abs(current[1] - next[1]) > 15) return false;
  }
  return true;
}

function densityPolygons(nside: number, counts: number[]): DensityPoly[] {
  const cached = polysCache.get(counts);
  if (cached) return cached;
  let max = 1;
  for (const count of counts) {
    if (count > max) max = count;
  }
  const logMax = Math.log(max);
  const polygons: DensityPoly[] = [];
  for (let ipix = 0; ipix < counts.length; ipix++) {
    const count = counts[ipix];
    if (!count || count <= 0) continue;
    const t = Math.log(count) / logMax;
    const ring = nestToCorners(nside, ipix).reverse();
    if (!ringIsCompact(ring)) continue;
    ring.push(ring[0]);
    polygons.push({ ring, color: rampCss(0.2 + 0.8 * t) });
  }
  polysCache.set(counts, polygons);
  return polygons;
}

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
): ProjectedPoints | null {
  context.clearRect(0, 0, width, height);
  const projection = projectionFor(width, height);
  const path = geoPath(projection, context);
  const graticule = geoGraticule().step([60, 30]);
  strokeHairline(context, path, { type: "Sphere" }, 0.55);
  strokeHairline(context, path, graticule(), 0.28);

  if (spec.mode === "density") {
    for (const polygon of densityPolygons(spec.nside, spec.counts)) {
      context.fillStyle = polygon.color;
      context.beginPath();
      path({ type: "Polygon", coordinates: [polygon.ring] });
      context.fill();
    }
    return null;
  }

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
