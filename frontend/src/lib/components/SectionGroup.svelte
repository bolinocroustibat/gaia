<script lang="ts">
import type { Snippet } from "svelte"

let {
	id,
	title,
	children,
}: {
	id: string
	title: string
	children: Snippet
} = $props()
</script>

<section aria-labelledby="section-{id}" class="group">
  <header>
    <h2 id="section-{id}">{title}</h2>
  </header>
  <div class="subsections">
    {@render children()}
  </div>
</section>

<style>
  .group {
    display: grid;
    gap: clamp(2rem, 5vw, 3.25rem);
    padding: clamp(3.5rem, 8vw, 6rem) clamp(1.25rem, 6vw, 5.5rem);
    border-top: 1px solid var(--line);
  }

  h2 {
    margin: 0;
    font-size: clamp(2rem, 4vw, 3.25rem);
    font-weight: 500;
    letter-spacing: -0.045em;
    line-height: 0.92;
  }

  .subsections {
    display: grid;
    gap: clamp(2.75rem, 6vw, 4.5rem);
  }
</style>
