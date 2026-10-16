import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { rampRgb } from "../theme";
import type { ColumnarTable } from "../types";

export type CloudHover = {
  index: number;
  x: number;
  y: number;
};

/** Frame the camera on the bulk of the cloud. A few distant stars would otherwise stretch the view into rays. */
function percentile(values: Float32Array, fraction: number): number {
  const sorted = Array.from(values).sort((a, b) => a - b);
  const index = Math.min(sorted.length - 1, Math.max(0, Math.round(fraction * (sorted.length - 1))));
  return sorted[index] ?? 0;
}

/** Sun in the galactocentric frame used for x_gc, y_gc, z_gc.
 * Matches DEFAULT_GALACTOCENTRIC_FRAME: 8.3 kpc from the Galactic center, 20.8 pc above the plane.
 * Earth and Gaia coincide with the Sun at kiloparsec scale.
 */
const OBSERVER_KPC = new THREE.Vector3(-8.3, 0, 0.0208);
const ACCENT_HEX = 0xd6ff4a;
const HALO_HEX = 0x0c0c0c;

function dotMarker(size: number, color: number, order: number): THREE.Points {
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute(
    "position",
    new THREE.BufferAttribute(new Float32Array(OBSERVER_KPC.toArray()), 3),
  );
  const material = new THREE.PointsMaterial({
    color,
    size,
    sizeAttenuation: false,
    depthTest: false,
    depthWrite: false,
    transparent: true,
  });
  const dot = new THREE.Points(geometry, material);
  dot.renderOrder = order;
  return dot;
}

export function mountGalaxyCloud(
  canvas: HTMLCanvasElement,
  table: ColumnarTable,
  onHover: (hover: CloudHover | null) => void,
  marker: HTMLElement,
): () => void {
  const x = table.numbers.x_gc;
  const y = table.numbers.y_gc;
  const z = table.numbers.z_gc;
  const mag = table.numbers.phot_g_mean_mag;
  const count = table.count;

  let minMag = Infinity;
  let maxMag = -Infinity;
  for (let i = 0; i < count; i++) {
    if (mag[i] < minMag) minMag = mag[i];
    if (mag[i] > maxMag) maxMag = mag[i];
  }
  const magSpan = maxMag - minMag || 1;
  const x0 = percentile(x, 0.02);
  const x1 = percentile(x, 0.98);
  const y0 = percentile(y, 0.02);
  const y1 = percentile(y, 0.98);
  const z0 = percentile(z, 0.02);
  const z1 = percentile(z, 0.98);
  const cx = (x0 + x1) / 2;
  const cy = (y0 + y1) / 2;
  const cz = (z0 + z1) / 2;
  const span = Math.max(x1 - x0, y1 - y0, z1 - z0, 1);

  const positions = new Float32Array(count * 3);
  const colors = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) {
    positions[i * 3] = x[i];
    positions[i * 3 + 1] = y[i];
    positions[i * 3 + 2] = z[i];
    const t = 1 - (mag[i] - minMag) / magSpan;
    const [r, g, b] = rampRgb(0.28 + 0.72 * t);
    colors[i * 3] = r / 255;
    colors[i * 3 + 1] = g / 255;
    colors[i * 3 + 2] = b / 255;
  }

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));
  geometry.computeBoundingSphere();

  const material = new THREE.PointsMaterial({
    size: span * 0.008,
    vertexColors: true,
    transparent: true,
    opacity: 0.92,
    sizeAttenuation: true,
    depthWrite: false,
  });
  const points = new THREE.Points(geometry, material);

  const dotHalo = dotMarker(14, HALO_HEX, 1);
  const dot = dotMarker(7, ACCENT_HEX, 2);

  const scene = new THREE.Scene();
  scene.add(points);
  scene.add(dotHalo);
  scene.add(dot);

  const camera = new THREE.PerspectiveCamera(42, 1, span / 200, span * 20);
  // Galactic height is z. Keep that axis upright so the disk lies flat, edge-on as a horizontal band.
  camera.up.set(0, 0, 1);
  camera.position.set(cx + span * 0.15, cy - span * 0.95, cz + span * 0.42);

  const renderer = new THREE.WebGLRenderer({
    canvas,
    antialias: true,
    alpha: true,
  });
  renderer.setClearColor(0x000000, 0);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

  const controls = new OrbitControls(camera, canvas);
  controls.target.set(cx, cy, cz);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.update();

  const raycaster = new THREE.Raycaster();
  raycaster.params.Points.threshold = span * 0.012;
  const pointer = new THREE.Vector2();
  const projected = new THREE.Vector3();
  let viewWidth = 1;
  let viewHeight = 1;

  const placeMarker = () => {
    projected.copy(OBSERVER_KPC).project(camera);
    const inView =
      projected.z >= -1 &&
      projected.z <= 1 &&
      projected.x >= -1 &&
      projected.x <= 1 &&
      projected.y >= -1 &&
      projected.y <= 1;
    if (!inView) {
      marker.hidden = true;
      return;
    }
    const x = (projected.x * 0.5 + 0.5) * viewWidth;
    const y = (-projected.y * 0.5 + 0.5) * viewHeight;
    const flip = x > viewWidth * 0.72;
    marker.hidden = false;
    marker.style.transform = flip
      ? `translate(${x - 10}px, ${y}px) translate(-100%, -50%)`
      : `translate(${x + 12}px, ${y}px) translateY(-50%)`;
  };

  const resize = () => {
    const rect = canvas.getBoundingClientRect();
    const width = Math.max(1, Math.floor(rect.width));
    const height = Math.max(1, Math.floor(rect.height));
    viewWidth = width;
    viewHeight = height;
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height, false);
  };
  const resizeObserver = new ResizeObserver(resize);
  resizeObserver.observe(canvas);
  resize();

  const onMove = (event: PointerEvent) => {
    const rect = canvas.getBoundingClientRect();
    pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    raycaster.setFromCamera(pointer, camera);
    const hits = raycaster.intersectObject(points);
    const hit = hits[0];
    if (!hit || hit.index === undefined) {
      onHover(null);
      return;
    }
    onHover({
      index: hit.index,
      x: event.clientX - rect.left + 14,
      y: event.clientY - rect.top + 14,
    });
  };
  const onLeave = () => onHover(null);
  canvas.addEventListener("pointermove", onMove);
  canvas.addEventListener("pointerleave", onLeave);

  let frame = 0;
  const loop = () => {
    controls.update();
    placeMarker();
    renderer.render(scene, camera);
    frame = requestAnimationFrame(loop);
  };
  loop();

  return () => {
    cancelAnimationFrame(frame);
    resizeObserver.disconnect();
    canvas.removeEventListener("pointermove", onMove);
    canvas.removeEventListener("pointerleave", onLeave);
    controls.dispose();
    geometry.dispose();
    material.dispose();
    for (const object of [dotHalo, dot]) {
      object.geometry.dispose();
      const objectMaterial = object.material;
      if (Array.isArray(objectMaterial)) objectMaterial.forEach((entry) => entry.dispose());
      else objectMaterial.dispose();
    }
    renderer.dispose();
  };
}
