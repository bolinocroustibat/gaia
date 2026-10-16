<script lang="ts">
  import type { Snippet } from "svelte";

  let {
    index,
    title,
    help,
    caption,
    children,
  }: {
    index: string;
    title: string;
    help: string;
    caption?: string;
    children: Snippet;
  } = $props();
</script>

<section aria-labelledby="section-{index}">
  <header>
    <p class="index">{index}</p>
    <h2 id="section-{index}">{title}</h2>
    <p class="help">{help}</p>
    {#if caption}
      <p class="caption">{caption}</p>
    {/if}
  </header>
  <div class="stage">
    {@render children()}
  </div>
</section>

<style>
  section {
    display: grid;
    gap: clamp(1.75rem, 4vw, 2.75rem);
    padding: clamp(3.5rem, 8vw, 6rem) clamp(1.25rem, 6vw, 5.5rem);
    border-top: 1px solid var(--line);
  }

  .index,
  .caption {
    margin: 0;
    font-family: var(--font-mono);
    font-size: 0.72rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--muted);
  }

  h2 {
    margin: 0.55rem 0 0.9rem;
    font-size: clamp(2rem, 4vw, 3.25rem);
    font-weight: 500;
    letter-spacing: -0.045em;
    line-height: 0.92;
  }

  .help {
    margin: 0;
    max-width: 28rem;
    color: var(--muted);
    line-height: 1.45;
  }

  .caption {
    margin-top: 1.25rem;
    letter-spacing: 0.04em;
    text-transform: none;
    line-height: 1.4;
  }

  .stage {
    min-width: 0;
    min-height: 8rem;
  }

</style>
