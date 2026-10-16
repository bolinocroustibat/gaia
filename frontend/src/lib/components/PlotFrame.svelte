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
</style>
