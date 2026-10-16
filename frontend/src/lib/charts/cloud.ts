import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { rampRgb } from "../theme";
import type { ColumnarTable } from "../types";

export type CloudHover = {
  index: number;
  x: number;
  y: number;
};

export function mountGalaxyCloud(
  canvas: HTMLCanvasElement,
  table: ColumnarTable,
  onHover: (hover: CloudHover | null) => void,
): () => void {
  const x = table.numbers.x_gc;
  const y = table.numbers.y_gc;
  const z = table.numbers.z_gc;
  const mag = table.numbers.phot_g_mean_mag;
  const count = table.count;

  let minX = Infinity;
  let minY = Infinity;
  let minZ = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;
  let maxZ = -Infinity;
  let minMag = Infinity;
  let maxMag = -Infinity;
  for (let i = 0; i < count; i++) {
    if (x[i] < minX) minX = x[i];
    if (y[i] < minY) minY = y[i];
    if (z[i] < minZ) minZ = z[i];
    if (x[i] > maxX) maxX = x[i];
    if (y[i] > maxY) maxY = y[i];
    if (z[i] > maxZ) maxZ = z[i];
    if (mag[i] < minMag) minMag = mag[i];
    if (mag[i] > maxMag) maxMag = mag[i];
  }
  const magSpan = maxMag - minMag || 1;
  const cx = (minX + maxX) / 2;
  const cy = (minY + maxY) / 2;
  const cz = (minZ + maxZ) / 2;
  const span = Math.max(maxX - minX, maxY - minY, maxZ - minZ, 1);

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

  const scene = new THREE.Scene();
  scene.add(points);

  const camera = new THREE.PerspectiveCamera(42, 1, span / 200, span * 20);
  camera.position.set(cx + span * 0.15, cy - span * 0.9, cz + span * 0.55);

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

  const resize = () => {
    const rect = canvas.getBoundingClientRect();
    const width = Math.max(1, Math.floor(rect.width));
    const height = Math.max(1, Math.floor(rect.height));
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
    renderer.dispose();
  };
}
