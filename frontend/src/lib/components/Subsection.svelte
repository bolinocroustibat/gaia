<script lang="ts">
import type { Snippet } from "svelte"
import { keepPunctuation } from "../format"

let {
	id,
	title,
	help,
	controls,
	children,
}: {
	id: string
	title: string
	help: string
	controls?: Snippet
	children: Snippet
} = $props()

const paragraphs = $derived(
	help
		.split(/\n\s*\n/)
		.map((part) => part.trim())
		.filter(Boolean),
)
</script>

<article aria-labelledby="subsection-{id}" class="subsection">
  <header>
    <h3 id="subsection-{id}">{keepPunctuation(title)}</h3>
    {#if paragraphs.length}
      <div class="help">
        {#each paragraphs as paragraph}
          <p>{keepPunctuation(paragraph)}</p>
        {/each}
      </div>
    {/if}
    {@render controls?.()}
  </header>
  <div class="stage">
    {@render children()}
  </div>
</article>

<style>
  .subsection {
    display: grid;
    gap: clamp(1.25rem, 3vw, 2rem);
  }

  h3 {
    margin: 0 0 0.65rem;
    font-size: clamp(1.35rem, 2.8vw, 2.1rem);
    font-weight: 500;
    letter-spacing: -0.035em;
    line-height: 1.05;
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

  .stage {
    min-width: 0;
    min-height: 8rem;
  }
</style>
