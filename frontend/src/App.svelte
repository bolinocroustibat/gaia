<script lang="ts">
  import { formatDate } from "./lib/format";
  import { localizedDataset } from "./lib/i18n/data";
  import { localeState } from "./lib/i18n/locale.svelte";
  import { footerLinks, t } from "./lib/i18n/messages";
  import { loadManifest } from "./lib/load";
  import { storySections } from "./lib/sections";
  import LanguageSwitch from "./lib/components/LanguageSwitch.svelte";
  import Section from "./lib/components/Section.svelte";
  import StoryPanel from "./lib/components/StoryPanel.svelte";
  import type { Manifest } from "./lib/types";

  let manifest = $state.raw<Manifest | null>(null);
  let failed = $state(false);

  $effect(() => {
    let cancelled = false;
    loadManifest()
      .then((value) => {
        if (!cancelled) manifest = value;
      })
      .catch(() => {
        if (!cancelled) failed = true;
      });
    return () => {
      cancelled = true;
    };
  });

  const byId = $derived(new Map(manifest?.datasets.map((dataset) => [dataset.id, dataset]) ?? []));

</script>

<LanguageSwitch />

<main>
  <header class="mast">
    <p class="index">DR3</p>
    <h1>{t(localeState.value, "siteTitle")}</h1>
    <div class="lede">
      <p>{t(localeState.value, "siteIntro1")}</p>
      <p>{t(localeState.value, "siteIntro2")}</p>
    </div>
  </header>

  {#if failed}
    <p class="pending">{t(localeState.value, "catalogLoadFailed")}</p>
  {:else if manifest}
    {#each storySections as section, index (section.id)}
      {@const meta = byId.get(section.id)}
      {#if meta}
        {@const copy = localizedDataset(localeState.value, meta)}
        <Section
          index={String(index + 1).padStart(2, "0")}
          title={copy.label}
          help={copy.helpText}
          caption={section.caption}
        >
          <StoryPanel kind={section.kind} path={meta.path} />
        </Section>
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
        {formatDate(manifest.generated_at, localeState.value)} · {manifest.release} · {manifest.credit}
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
    padding: clamp(4rem, 12vw, 8rem) clamp(1.25rem, 6vw, 5.5rem) clamp(3rem, 8vw, 5rem);
  }

  .index {
    margin: 0;
    font-family: var(--font-mono);
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    color: var(--muted);
  }

  h1 {
    margin: 0.4rem 0 1.25rem;
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
