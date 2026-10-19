<script lang="ts">
  import { formatCount } from "../format";
  import { localeState } from "../i18n/locale.svelte";
  import { t } from "../i18n/messages";
  import type { CountRow } from "../types";

  let { rows }: { rows: CountRow[] } = $props();

  const VB_W = 1000;
  const TOP_H = 64;
  const TAPER = 152;
  const BOT_H = 64;
  const VB_H = TOP_H + TAPER + BOT_H;

  function splitLabel(label: string): { title: string; detail: string } {
    const [title, ...rest] = label.split("\n");
    return { title: title ?? "", detail: rest.join("\n") };
  }

  const top = $derived(rows[0] ?? null);
  const bottom = $derived(rows[1] ?? null);
  const topCopy = $derived(top ? splitLabel(top.label) : null);
  const bottomCopy = $derived(bottom ? splitLabel(bottom.label) : null);

  const ratio = $derived(
    top && bottom && top.count > 0 ? Math.min(1, bottom.count / top.count) : 0,
  );

  const path = $derived.by(() => {
    if (!bottom || ratio <= 0) return "";
    const mouth = Math.max(VB_W * ratio, 28);
    const x0 = (VB_W - mouth) / 2;
    const x1 = x0 + mouth;
    const yNeck = TOP_H + TAPER;
    return [
      "M 0 0",
      `H ${VB_W}`,
      `V ${TOP_H}`,
      `L ${x1} ${yNeck}`,
      `V ${VB_H}`,
      `H ${x0}`,
      `V ${yNeck}`,
      `L 0 ${TOP_H}`,
      "Z",
    ].join(" ");
  });

  const shareLabel = $derived.by(() => {
    if (ratio <= 0) return "";
    const loc = localeState.value;
    const share = new Intl.NumberFormat(loc === "fr" ? "fr-FR" : "en-US", {
      style: "percent",
      maximumFractionDigits: 0,
    }).format(ratio);
    return t(loc, "funnelShare").replace("{share}", share);
  });
</script>

<div class="funnel">
  {#if top && topCopy}
    <div class="step">
      <p class="count">{formatCount(top.count, localeState.value)}</p>
      <p class="name">{topCopy.title}</p>
      {#if topCopy.detail}
        <p class="detail">{topCopy.detail}</p>
      {/if}
    </div>
  {/if}

  {#if path}
    <svg
      class="shape"
      viewBox="0 0 {VB_W} {VB_H}"
      aria-hidden="true"
    >
      <path d={path} fill="#f472b6" />
    </svg>
  {/if}

  {#if bottom && bottomCopy}
    <div class="step">
      <p class="count kept">{formatCount(bottom.count, localeState.value)}</p>
      {#if shareLabel}
        <p class="share">{shareLabel}</p>
      {/if}
      <p class="name">{bottomCopy.title}</p>
      {#if bottomCopy.detail}
        <p class="detail">{bottomCopy.detail}</p>
      {/if}
    </div>
  {/if}
</div>

<style>
  .funnel {
    display: grid;
    gap: 1.15rem;
  }

  .count {
    margin: 0;
    font-size: clamp(2.4rem, 6vw, 4.4rem);
    font-weight: 500;
    letter-spacing: -0.055em;
    line-height: 0.9;
    font-variant-numeric: tabular-nums;
  }

  .count.kept {
    color: #f472b6;
  }

  .share,
  .name,
  .detail {
    margin: 0;
  }

  .share {
    margin-top: 0.45rem;
    font-family: var(--font-mono);
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    color: var(--muted);
  }

  .name {
    margin-top: 0.55rem;
    font-size: 1.05rem;
  }

  .detail {
    margin-top: 0.35rem;
    max-width: 34rem;
    color: var(--muted);
    line-height: 1.45;
  }

  .shape {
    display: block;
    width: 100%;
    height: auto;
  }
</style>
