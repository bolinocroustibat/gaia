<script lang="ts">
  import { formatCount } from "../format";
  import { localeState } from "../i18n/locale.svelte";
  import { t } from "../i18n/messages";
  import type { CountRow } from "../types";

  let { rows }: { rows: CountRow[] } = $props();

  const BAND = 9.25;
  const TAPER = 6;
  const VB = 100;

  function splitLabel(label: string): { title: string; detail: string } {
    const [title, ...rest] = label.split("\n");
    return { title: title ?? "", detail: rest.join("\n") };
  }

  function shareText(ratio: number): string {
    const loc = localeState.value;
    const share = new Intl.NumberFormat(loc === "fr" ? "fr-FR" : "en-US", {
      style: "percent",
      maximumFractionDigits: 0,
    }).format(ratio);
    return t(loc, "funnelShare").replace("{share}", share);
  }

  const steps = $derived.by(() => {
    const top = rows[0]?.count ?? 0;
    return rows.map((row) => ({
      ...row,
      ...splitLabel(row.label),
      share: top > 0 && row.count < top ? row.count / top : 0,
    }));
  });

  const rowTemplate = $derived(
    steps
      .flatMap((_, index) => (index === 0 ? [`${BAND}rem`] : [`${TAPER}rem`, `${BAND}rem`]))
      .join(" "),
  );

  const outline = $derived.by(() => {
    const n = steps.length;
    if (n === 0) return "";
    const top = steps[0].count;
    if (top <= 0) return "";
    const total = n * BAND + (n - 1) * TAPER;
    const band = (BAND / total) * VB;
    const taper = n > 1 ? (TAPER / total) * VB : 0;
    const bands = steps.map((step, index) => {
      const width = Math.min(VB, Math.max((step.count / top) * VB, 3.2));
      const x0 = (VB - width) / 2;
      const y0 = index * (band + taper);
      return { x0, x1: x0 + width, y0, y1: y0 + band };
    });
    const first = bands[0];
    const last = bands[n - 1];
    const parts = [`M ${first.x0} ${first.y0}`, `H ${first.x1}`, `V ${first.y1}`];
    for (let index = 0; index < n - 1; index++) {
      const above = bands[index];
      const below = bands[index + 1];
      const dy = (below.y0 - above.y1) * 0.48;
      parts.push(
        `C ${above.x1} ${above.y1 + dy}, ${below.x1} ${below.y0 - dy}, ${below.x1} ${below.y0}`,
        `V ${below.y1}`,
      );
    }
    parts.push(`H ${last.x0}`);
    for (let index = n - 1; index > 0; index--) {
      const below = bands[index];
      const above = bands[index - 1];
      const dy = (below.y0 - above.y1) * 0.48;
      parts.push(
        `V ${below.y0}`,
        `C ${below.x0} ${below.y0 - dy}, ${above.x0} ${above.y1 + dy}, ${above.x0} ${above.y1}`,
      );
    }
    parts.push(`V ${first.y0}`, "Z");
    return parts.join(" ");
  });

  const ghost = $derived.by(() => {
    const top = steps[0];
    if (!top || top.count <= 0 || steps.length < 2) return null;
    return { x: 0, width: VB };
  });
</script>

<div class="funnel">
  {#if outline}
    <svg class="shape" viewBox="0 0 {VB} {VB}" preserveAspectRatio="none" aria-hidden="true">
      <defs>
        <linearGradient id="galaxy-funnel-fill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#c984a6" />
          <stop offset="42%" stop-color="#ee8eb8" />
          <stop offset="100%" stop-color="#f472b6" />
        </linearGradient>
      </defs>
      {#if ghost}
        <rect x={ghost.x} y="0" width={ghost.width} height={VB} fill="#f472b6" opacity="0.07" />
      {/if}
      <path d={outline} fill="url(#galaxy-funnel-fill)" />
    </svg>
  {/if}

  <div class="steps" style:--rows={rowTemplate}>
    {#each steps as step, index (step.id ?? index)}
      <article class="step" style:grid-row={index * 2 + 1}>
        <p class="count">{formatCount(step.count, localeState.value)}</p>
        {#if step.share > 0}
          <p class="share">{shareText(step.share)}</p>
        {/if}
        <p class="name">{step.title}</p>
        {#if step.detail}
          <p class="detail">{step.detail}</p>
        {/if}
      </article>
    {/each}
  </div>
</div>

<style>
  .funnel {
    display: grid;
    grid-template-columns: minmax(11rem, 24rem) minmax(0, 36rem);
    column-gap: clamp(2.25rem, 5vw, 4.5rem);
    align-items: stretch;
    justify-content: start;
  }

  .shape {
    grid-column: 1;
    grid-row: 1;
    width: 100%;
    height: 100%;
  }

  .steps {
    grid-column: 2;
    grid-row: 1;
    display: grid;
    grid-template-rows: var(--rows);
    min-width: 0;
  }

  .step {
    align-self: center;
    min-width: 0;
  }

  .count {
    margin: 0;
    font-size: clamp(2.15rem, 4.4vw, 3.45rem);
    font-weight: 500;
    letter-spacing: -0.055em;
    line-height: 0.9;
    font-variant-numeric: tabular-nums;
  }

  .step:nth-child(2) .count {
    color: #f4a4c8;
  }

  .step:nth-child(3) .count {
    color: #f472b6;
  }

  .share,
  .name,
  .detail {
    margin: 0;
  }

  .share {
    margin-top: 0.4rem;
    font-family: var(--font-mono);
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    color: var(--muted);
  }

  .name {
    margin-top: 0.45rem;
    font-size: 1.05rem;
  }

  .detail {
    margin-top: 0.3rem;
    max-width: 34rem;
    color: var(--muted);
    line-height: 1.45;
  }

  @media (max-width: 720px) {
    .funnel {
      grid-template-columns: 1fr;
      row-gap: 1.5rem;
    }

    .shape {
      height: 16rem;
      max-width: none;
    }

    .steps {
      grid-row: 2;
      grid-column: 1;
      display: flex;
      flex-direction: column;
      gap: 1.75rem;
    }
  }
</style>
