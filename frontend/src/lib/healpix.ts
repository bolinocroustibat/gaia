/** Nested HEALPix pixel corners as [ra, dec] degrees. Face-local math from Healpix_cxx. */

const JRLL = [2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4];
const JPLL = [1, 3, 5, 7, 0, 2, 4, 6, 1, 3, 5, 7];

type Xyf = { ix: number; iy: number; face: number };

function nestToXyf(nside: number, ipix: number): Xyf {
  const pixelsPerFace = nside * nside;
  const face = Math.floor(ipix / pixelsPerFace);
  let rest = ipix - face * pixelsPerFace;
  let ix = 0;
  let iy = 0;
  let scale = 1;
  while (scale < nside) {
    ix += (rest & 1) * scale;
    iy += ((rest >>> 1) & 1) * scale;
    rest >>>= 2;
    scale <<= 1;
  }
  return { ix, iy, face };
}

function xyfToLonLat(nside: number, ix: number, iy: number, face: number): [number, number] {
  const x = ix / nside;
  const y = iy / nside;
  const jr = JRLL[face] - x - y;
  let nr: number;
  let z: number;
  if (jr < 1) {
    nr = jr;
    const tmp = (nr * nr) / 3;
    z = 1 - tmp;
  } else if (jr > 3) {
    nr = 4 - jr;
    const tmp = (nr * nr) / 3;
    z = tmp - 1;
  } else {
    nr = 1;
    z = ((2 - jr) * 2) / 3;
  }
  let tmp = JPLL[face] * nr + x - y;
  if (tmp < 0) tmp += 8;
  if (tmp >= 8) tmp -= 8;
  const phi = nr < 1e-12 ? 0 : ((Math.PI / 4) * tmp) / nr;
  const dec = (Math.asin(Math.max(-1, Math.min(1, z))) * 180) / Math.PI;
  let ra = (phi * 180) / Math.PI;
  ra %= 360;
  if (ra < 0) ra += 360;
  return [ra, dec];
}

const CORNER_OFFSETS: ReadonlyArray<readonly [number, number]> = [
  [0, 0],
  [1, 0],
  [1, 1],
  [0, 1],
];

export function nestToCorners(nside: number, ipix: number): [number, number][] {
  const { ix, iy, face } = nestToXyf(nside, ipix);
  return CORNER_OFFSETS.map(([dx, dy]) => xyfToLonLat(nside, ix + dx, iy + dy, face));
}
