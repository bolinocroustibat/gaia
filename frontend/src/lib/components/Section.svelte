<script lang="ts">
import type { Snippet } from "svelte"

let {
	id,
	title,
	help,
	caption,
	children,
}: {
	id: string
	title: string
	help: string
	caption?: string
	children: Snippet
} = $props()

const paragraphs = $derived(
	help
		.split(/\n\s*\n/)
		.map((part) => part.trim())
		.filter(Boolean),
)
</script>

<section aria-labelledby="section-{id}">
  <header>
    <h2 id="section-{id}">{title}</h2>
    <div class="help">
      {#each paragraphs as paragraph}
        <p>{paragraph}</p>
      {/each}
    </div>
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

  h2 {
    margin: 0 0 0.9rem;
    font-size: clamp(2rem, 4vw, 3.25rem);
    font-weight: 500;
    letter-spacing: -0.045em;
    line-height: 0.92;
  }

  .help {
    display: grid;
    gap: 0.85rem;
    max-width: 28rem;
    color: var(--muted);
    line-height: 1.45;
  }

  .help p {
    margin: 0;
  }

  .caption {
    margin: 1.25rem 0 0;
    font-family: var(--font-mono);
    font-size: 0.72rem;
    letter-spacing: 0.04em;
    color: var(--muted);
    line-height: 1.4;
  }

  .stage {
    min-width: 0;
    min-height: 8rem;
  }

</style>
