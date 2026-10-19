<script lang="ts">
  import { funnelRows } from "../charts/funnel";
  import { hrPlot } from "../charts/hr";
  import { localizedBins, localizedRows } from "../i18n/data";
  import { localeState } from "../i18n/locale.svelte";
  import { t } from "../i18n/messages";
  import { loadPanel } from "../load";
  import type { SectionKind } from "../types";
  import type { PanelPayload } from "../types";
  import Funnel from "./Funnel.svelte";
  import GalaxyCloud from "./GalaxyCloud.svelte";
  import KpiStrip from "./KpiStrip.svelte";
  import PlotFrame from "./PlotFrame.svelte";

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

  const kpiRows = $derived(
    payload?.kind === "kpi" ? localizedRows(localeState.value, payload.summary.rows ?? []) : [],
  );
  const kpiBarRows = $derived(
    payload?.kind === "kpi" ? localizedRows(localeState.value, payload.summary.bar_rows ?? []) : [],
  );
  const funnel = $derived(
    payload?.kind === "funnel"
      ? localizedRows(localeState.value, funnelRows(payload.summary.steps ?? []))
      : [],
  );
  const hrBins = $derived(
    payload?.kind === "hr" ? localizedBins(localeState.value, payload.bins) : null,
  );
  const hrView = $derived(
    hrBins ? { bins: hrBins, locale: localeState.value } : null,
  );
</script>

<div bind:this={host}>
  {#if payload?.kind === "kpi"}
    <KpiStrip rows={kpiRows} barRows={kpiBarRows} />
  {:else if payload?.kind === "funnel"}
    <Funnel rows={funnel} />
  {:else if hrView}
    <PlotFrame data={hrView} render={hrPlot} />
  {:else if payload?.kind === "galaxy-3d"}
    <GalaxyCloud table={payload.table} />
  {:else if failed}
    <p class="pending">{t(localeState.value, "panelLoadFailed")}</p>
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
