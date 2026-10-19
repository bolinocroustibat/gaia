<script lang="ts">
import { type Locale, localeState, setLocale } from "../i18n/locale.svelte"
import { t } from "../i18n/messages"

const options: { value: Locale; labelKey: "langFr" | "langEn" }[] = [
	{ value: "en", labelKey: "langEn" },
	{ value: "fr", labelKey: "langFr" },
]
</script>

<nav class="lang-switch" aria-label={t(localeState.value, "langSwitch")}>
  {#each options as option (option.value)}
    <button
      type="button"
      class:active={localeState.value === option.value}
      aria-current={localeState.value === option.value ? "true" : undefined}
      onclick={() => setLocale(option.value)}
    >
      {option.value.toUpperCase()}
      <span class="visually-hidden">{t(localeState.value, option.labelKey)}</span>
    </button>
  {/each}
</nav>

<style>
  .lang-switch {
    position: fixed;
    top: clamp(1rem, 3vw, 1.35rem);
    right: clamp(1.25rem, 6vw, 5.5rem);
    z-index: 20;
    display: flex;
    gap: 0;
    border: 1px solid var(--line);
    background: color-mix(in srgb, var(--bg) 88%, transparent);
    backdrop-filter: blur(8px);
  }

  button {
    margin: 0;
    padding: 0.45rem 0.65rem;
    border: none;
    background: transparent;
    color: var(--muted);
    font-family: var(--font-mono);
    font-size: 0.72rem;
    letter-spacing: 0.14em;
    cursor: pointer;
    transition: color 0.15s ease, background 0.15s ease;
  }

  button:hover {
    color: var(--paper);
  }

  button.active {
    background: var(--line);
    color: var(--accent);
  }

  button + button {
    border-left: 1px solid var(--line);
  }

  .visually-hidden {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
  }
</style>
