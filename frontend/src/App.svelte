<script lang="ts">
import LanguageSwitch from "./lib/components/LanguageSwitch.svelte"
import Section from "./lib/components/Section.svelte"
import SectionGroup from "./lib/components/SectionGroup.svelte"
import StoryPanel from "./lib/components/StoryPanel.svelte"
import Subsection from "./lib/components/Subsection.svelte"
import { formatDate } from "./lib/format"
import { localizedDataset } from "./lib/i18n/data"
import { localeState } from "./lib/i18n/locale.svelte"
import { footerLinks, t } from "./lib/i18n/messages"
import { loadManifest } from "./lib/load"
import { storyItems } from "./lib/sections"
import type { Manifest } from "./lib/types"

let manifest = $state.raw<Manifest | null>(null)
let failed = $state(false)

$effect(() => {
	let cancelled = false
	loadManifest()
		.then((value) => {
			if (!cancelled) manifest = value
		})
		.catch(() => {
			if (!cancelled) failed = true
		})
	return () => {
		cancelled = true
	}
})

const byId = $derived(
	new Map(manifest?.datasets.map((dataset) => [dataset.id, dataset]) ?? []),
)

$effect(() => {
	document.title = t(localeState.value, "siteTitle")
})
</script>

<LanguageSwitch />

<main>
  <header class="mast">
    <img
      class="mast-art"
      src="/mission-gaia.webp"
      alt={t(localeState.value, "siteHeroAlt")}
    />
    <div class="mast-copy">
      <h1>{t(localeState.value, "siteTitle")}</h1>
      {#if manifest}
        <p class="mast-meta">
          {t(localeState.value, "siteMastMeta").replace(
            "{date}",
            formatDate(manifest.generated_at, localeState.value),
          )}
        </p>
      {/if}
      <div class="lede">
        <p>{t(localeState.value, "siteIntro1")}</p>
        <p>{t(localeState.value, "siteIntro2")}</p>
      </div>
    </div>
  </header>

  {#if failed}
    <p class="pending">{t(localeState.value, "catalogLoadFailed")}</p>
  {:else if manifest}
    {#each storyItems as item (item.type === "group" ? item.id : item.id)}
      {#if item.type === "panel"}
        {@const meta = byId.get(item.id)}
        {#if meta}
          {@const copy = localizedDataset(localeState.value, meta)}
          <Section
            id={item.id}
            title={copy.label}
            help={copy.helpText}
            caption={item.caption}
          >
            <StoryPanel kind={item.kind} path={meta.path} />
          </Section>
        {/if}
      {:else}
        <SectionGroup id={item.id} title={t(localeState.value, item.titleKey)}>
          {#each item.children as child (child.id)}
            {@const meta = byId.get(child.id)}
            {#if meta}
              {@const copy = localizedDataset(localeState.value, meta)}
              <Subsection id={child.id} title={copy.label} help={copy.helpText}>
                <StoryPanel kind={child.kind} path={meta.path} />
              </Subsection>
            {/if}
          {/each}
        </SectionGroup>
      {/if}
    {/each}

    <footer>
      <p>
        <a href={footerLinks.sourceRepo} target="_blank" rel="noopener noreferrer">
          {t(localeState.value, "footerSourceCode")}
        </a>
        v{__APP_VERSION__} ({__APP_COMMIT__}) ·
        <a href={footerLinks.gaiaArchive} target="_blank" rel="noopener noreferrer">
          {t(localeState.value, "footerGaiaCatalog")}
        </a>
        ·
        <a href={footerLinks.author} target="_blank" rel="noopener noreferrer">
          {t(localeState.value, "footerByBolino")}
        </a>
      </p>
      <p>
        {t(localeState.value, "footerExported")}
        {formatDate(manifest.generated_at, localeState.value)} · {manifest.credit}
        · <a href={manifest.license.url}>{manifest.license.id}</a>
      </p>
    </footer>
  {:else}
    <p class="pending" aria-hidden="true">…</p>
  {/if}
</main>

<style>
  main {
    min-height: 100vh;
  }

  .mast {
    position: relative;
    display: grid;
    grid-template-columns: minmax(0, 1fr);
    overflow: hidden;
    padding: clamp(4rem, 12vw, 8rem) clamp(1.25rem, 6vw, 5.5rem) clamp(3rem, 8vw, 5rem);
  }

  .mast-art {
    position: absolute;
    top: 3.25rem;
    right: -1rem;
    z-index: 0;
    display: block;
    width: min(70vw, 20rem);
    height: auto;
    pointer-events: none;
    user-select: none;
    mix-blend-mode: lighten;
    mask-image: radial-gradient(
      ellipse 64% 70% at 54% 48%,
      #000 0%,
      #000 42%,
      transparent 78%
    );
    -webkit-mask-image: radial-gradient(
      ellipse 64% 70% at 54% 48%,
      #000 0%,
      #000 42%,
      transparent 78%
    );
  }

  .mast-copy {
    position: relative;
    z-index: 1;
  }

  @media (min-width: 900px) {
    .mast {
      grid-template-columns: minmax(22rem, 1fr) minmax(20rem, 40vw);
      align-items: center;
      column-gap: 0.75rem;
    }

    .mast-art {
      position: relative;
      top: auto;
      right: auto;
      width: 100%;
      max-width: 38rem;
      justify-self: end;
      grid-column: 2;
      grid-row: 1;
    }

    .mast-copy {
      grid-column: 1;
      grid-row: 1;
    }
  }

  .mast-meta {
    margin: 0 0 1.1rem;
    color: var(--accent);
    font-family: var(--font-mono);
    font-size: 0.72rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
  }

  h1 {
    margin: 0 0 1.25rem;
    max-width: 18em;
    font-size: clamp(2.1rem, 5.5vw, 3.6rem);
    font-weight: 500;
    letter-spacing: -0.045em;
    line-height: 1.02;
  }

  .lede {
    display: grid;
    gap: 1rem;
    max-width: 36rem;
    color: var(--muted);
    font-size: 1.05rem;
    line-height: 1.45;
  }

  .lede p {
    margin: 0;
  }

  .pending {
    margin: 0;
    padding: 0 clamp(1.25rem, 6vw, 5.5rem) 4rem;
    color: var(--muted);
    font-family: var(--font-mono);
    letter-spacing: 0.14em;
  }

  footer {
    display: flex;
    flex-direction: column;
    gap: 0.45rem;
    padding: 1.4rem clamp(1.25rem, 6vw, 5.5rem) 2.4rem;
    border-top: 1px solid var(--line);
    color: var(--muted);
    font-family: var(--font-mono);
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  footer p {
    margin: 0;
  }

  footer a {
    color: var(--accent);
    text-decoration: none;
  }
</style>
