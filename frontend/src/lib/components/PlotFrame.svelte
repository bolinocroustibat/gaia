<script lang="ts" generics="T">
  let {
    data,
    render,
  }: {
    data: T;
    render: (data: T, width: number) => HTMLElement;
  } = $props();

  let host = $state<HTMLDivElement | undefined>();
  let width = $state(0);

  $effect(() => {
    const node = host;
    if (!node) return;
    let frame = 0;
    const observer = new ResizeObserver((entries) => {
      const next = Math.floor(entries[0]?.contentRect.width ?? 0);
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => {
        if (next !== width) width = next;
      });
    });
    observer.observe(node);
    return () => {
      cancelAnimationFrame(frame);
      observer.disconnect();
    };
  });

  $effect(() => {
    const node = host;
    const nextWidth = width;
    const value = data;
    if (!node || nextWidth < 32) return;
    const plot = render(value, nextWidth);
    node.replaceChildren(plot);
    return () => {
      plot.remove();
    };
  });
</script>

<div class="plot-host" bind:this={host}></div>

<style>
  .plot-host {
    width: 100%;
  }

  .plot-host :global(figure) {
    position: relative;
    margin: 0;
  }

  .plot-host :global(svg) {
    display: block;
    max-width: 100%;
    height: auto;
    overflow: visible;
  }

  .plot-host :global(text) {
    font-family: var(--font-mono);
  }

  .plot-host :global(.family-tip) {
    position: absolute;
    z-index: 2;
    display: grid;
    gap: 0.28rem;
    margin: 0;
    padding: 0.55rem 0.7rem;
    background: var(--bg);
    border: 1px solid var(--line);
    color: var(--paper);
    font-family: var(--font-mono);
    font-size: 11px;
    line-height: 1.45;
    pointer-events: none;
  }

  .plot-host :global(.family-tip p) {
    margin: 0;
  }

  .plot-host :global(.family-name) {
    color: var(--accent);
    letter-spacing: 0.12em;
    text-transform: uppercase;
  }

  .plot-host :global(.hr-figure:not(.is-visible) .hr-mark),
  .plot-host :global(.hr-figure:not(.is-visible) .family-tip) {
    opacity: 0;
  }

  .plot-host :global(.hr-figure .hr-mark),
  .plot-host :global(.hr-figure .family-tip) {
    transition: opacity 0.95s ease;
  }

  .plot-host :global(.hr-figure.is-visible .hr-mark[data-family="main"]),
  .plot-host :global(.hr-figure.is-visible .family-tip[data-family="main"]) {
    transition-delay: 0.15s;
  }

  .plot-host :global(.hr-figure.is-visible .hr-mark[data-family="giants"]),
  .plot-host :global(.hr-figure.is-visible .family-tip[data-family="giants"]) {
    transition-delay: 1.2s;
  }

  .plot-host :global(.hr-figure.is-visible .hr-mark[data-family="dwarfs"]),
  .plot-host :global(.hr-figure.is-visible .family-tip[data-family="dwarfs"]) {
    transition-delay: 2.25s;
  }

  @media (prefers-reduced-motion: reduce) {
    .plot-host :global(.hr-figure:not(.is-visible) .hr-mark),
    .plot-host :global(.hr-figure:not(.is-visible) .family-tip) {
      opacity: 1;
    }

    .plot-host :global(.hr-figure .hr-mark),
    .plot-host :global(.hr-figure .family-tip) {
      transition: none;
    }
  }
</style>
