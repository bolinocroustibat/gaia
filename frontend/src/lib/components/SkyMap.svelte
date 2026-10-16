<script lang="ts">
  import { formatField } from "../format";
  import { drawSky, nearestPoint, type ProjectedPoints, type SkySpec } from "../charts/sky";

  let { sky }: { sky: SkySpec } = $props();

  let canvas = $state<HTMLCanvasElement | undefined>();
  let tip = $state<{ x: number; y: number; lines: string[] } | null>(null);

  $effect(() => {
    const node = canvas;
    const spec = sky;
    if (!node) return;
    const context = node.getContext("2d");
    if (!context) return;

    let projected: ProjectedPoints | null = null;
    let frame = 0;

    const paint = () => {
      const rect = node.getBoundingClientRect();
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const width = Math.max(1, Math.floor(rect.width));
      const height = Math.max(1, Math.floor(rect.height));
      node.width = Math.floor(width * dpr);
      node.height = Math.floor(height * dpr);
      context.setTransform(dpr, 0, 0, dpr, 0, 0);
      projected = drawSky(context, width, height, spec);
    };

    const observer = new ResizeObserver(() => {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(paint);
    });
    observer.observe(node);
    paint();

    const onMove = (event: PointerEvent) => {
      if (!projected) return;
      const rect = node.getBoundingClientRect();
      const px = event.clientX - rect.left;
      const py = event.clientY - rect.top;
      const index = nearestPoint(px, py, projected);
      if (index < 0) {
        tip = null;
        return;
      }
      tip = {
        x: px + 14,
        y: py + 14,
        lines: [
          formatField("source_id", spec.ids[index] ?? ""),
          formatField("ra", spec.ra[index]),
          formatField("dec", spec.dec[index]),
          formatField("phot_g_mean_mag", spec.mag[index]),
        ],
      };
    };
    const onLeave = () => {
      tip = null;
    };

    node.addEventListener("pointermove", onMove);
    node.addEventListener("pointerleave", onLeave);

    return () => {
      cancelAnimationFrame(frame);
      observer.disconnect();
      node.removeEventListener("pointermove", onMove);
      node.removeEventListener("pointerleave", onLeave);
    };
  });

</script>

<div class="map">
  <canvas bind:this={canvas} aria-label="Échantillon du disque galactique sur le ciel"></canvas>
  {#if tip}
    <p class="tip" style:left="{tip.x}px" style:top="{tip.y}px">
      {#each tip.lines as line}
        <span class:id={line.startsWith("identifiant")}>{line}</span>
      {/each}
    </p>
  {/if}
</div>
<p class="legend">
  <span>faible</span>
  <span class="ramp"></span>
  <span>brillante</span>
</p>

<style>
  .map {
    position: relative;
    width: 100%;
    aspect-ratio: 2 / 1;
  }

  canvas {
    width: 100%;
    height: 100%;
    display: block;
  }

  .tip {
    position: absolute;
    z-index: 2;
    margin: 0;
    display: grid;
    gap: 0.15rem;
    max-width: 18rem;
    padding: 0.55rem 0.7rem;
    background: var(--bg);
    border: 1px solid var(--line);
    color: var(--paper);
    font-family: var(--font-mono);
    font-size: 11px;
    line-height: 1.45;
    pointer-events: none;
  }

  .id {
    color: var(--accent);
  }

  .legend {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    margin: 0.85rem 0 0;
    color: var(--muted);
    font-family: var(--font-mono);
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .ramp {
    width: 7.5rem;
    height: 4px;
    background: linear-gradient(90deg, var(--ramp-start), var(--accent), var(--paper));
  }
</style>
