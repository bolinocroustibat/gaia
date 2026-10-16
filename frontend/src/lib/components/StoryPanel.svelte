<script lang="ts">
  import { funnelRows } from "../charts/funnel";
  import { hrPlot } from "../charts/hr";
  import { loadPanel } from "../load";
  import type { SectionKind } from "../types";
  import type { PanelPayload } from "../types";
  import BrokenBars from "./BrokenBars.svelte";
  import GalaxyCloud from "./GalaxyCloud.svelte";
  import KpiStrip from "./KpiStrip.svelte";
  import LogBars from "./LogBars.svelte";
  import PlotFrame from "./PlotFrame.svelte";
  import SkyMap from "./SkyMap.svelte";

  let { kind, path }: { kind: SectionKind; path: string } = $props();

  let host = $state<HTMLDivElement | undefined>();
  let payload = $state.raw<PanelPayload | null>(null);
  let failed = $state(false);

  $effect(() => {
    const node = host;
    const target = path;
    const panel = kind;
    if (!node) return;
    let cancelled = false;
    let started = false;
    payload = null;
    failed = false;

    const observer = new IntersectionObserver(
      (entries) => {
        if (started || !entries.some((entry) => entry.isIntersecting)) return;
        started = true;
        observer.disconnect();
        loadPanel(panel, target)
          .then((value) => {
            if (!cancelled) payload = value;
          })
          .catch(() => {
            if (!cancelled) failed = true;
          });
      },
      { rootMargin: "320px" },
    );
    observer.observe(node);

    return () => {
      cancelled = true;
      observer.disconnect();
    };
  });
</script>

<div bind:this={host}>
  {#if payload?.kind === "kpi"}
    <KpiStrip rows={payload.summary.rows ?? []} />
  {:else if payload?.kind === "types"}
    <BrokenBars rows={payload.summary.rows ?? []} />
  {:else if payload?.kind === "funnel"}
    <LogBars rows={funnelRows(payload.summary.steps ?? [])} />
  {:else if payload?.kind === "hr"}
    <PlotFrame data={payload.bins} render={hrPlot} />
  {:else if payload?.kind === "galaxy-sky"}
    <SkyMap
      sky={{
        ids: payload.table.strings.source_id ?? [],
        ra: payload.table.numbers.ra,
        dec: payload.table.numbers.dec,
        mag: payload.table.numbers.phot_g_mean_mag,
      }}
    />
  {:else if payload?.kind === "galaxy-3d"}
    <GalaxyCloud table={payload.table} />
  {:else if failed}
    <p class="pending">Ces données n’ont pas pu être chargées.</p>
  {:else}
    <p class="pending" aria-hidden="true">…</p>
  {/if}
</div>

<style>
  .pending {
    margin: 0;
    color: var(--muted);
    font-family: var(--font-mono);
    letter-spacing: 0.14em;
  }
</style>
