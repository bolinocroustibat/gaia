<script lang="ts">
import { localeState } from "../i18n/locale.svelte"
import { t } from "../i18n/messages"
import type { ReleaseId } from "../types"

const RELEASES: { id: ReleaseId; label: string }[] = [
	{ id: "dr3", label: "DR3" },
	{ id: "dr4", label: "DR4" },
]

let {
	available,
	value,
	onchange,
}: {
	available: ReleaseId[]
	value: ReleaseId
	onchange: (release: ReleaseId) => void
} = $props()

const uid = $props.id()

// Tooltip opened by a tap, for touch screens without hover.
let tapped = $state<ReleaseId | null>(null)

function unavailableText(release: { id: ReleaseId; label: string }): string {
	const loc = localeState.value
	if (release.id === "dr4") return t(loc, "releaseDr4Pending")
	return t(loc, "releaseUnavailable").replace(
		"{release}",
		`Gaia ${release.label}`,
	)
}
</script>

<div
  class="release-switch"
  role="group"
  aria-label={t(localeState.value, "releaseSwitch")}
>
  {#each RELEASES as release (release.id)}
    {@const enabled = available.includes(release.id)}
    {@const tipId = `${uid}-${release.id}-tip`}
    <button
      type="button"
      class:active={value === release.id}
      class:tapped={tapped === release.id}
      aria-pressed={value === release.id}
      aria-disabled={enabled ? undefined : "true"}
      aria-describedby={enabled ? undefined : tipId}
      onclick={() => {
        if (!enabled) {
          tapped = tapped === release.id ? null : release.id
          return
        }
        if (release.id !== value) onchange(release.id)
      }}
      onblur={() => {
        if (tapped === release.id) tapped = null
      }}
    >
      {release.label}
      {#if !enabled}
        <span class="tooltip" role="tooltip" id={tipId}>
          {unavailableText(release)}
        </span>
      {/if}
    </button>
  {/each}
</div>

<style>
  .release-switch {
    position: relative;
    display: inline-flex;
    margin-top: 0.9rem;
    border: 1px solid var(--line);
  }

  button {
    margin: 0;
    padding: 0.35rem 0.6rem;
    border: none;
    background: transparent;
    color: var(--muted);
    font-family: var(--font-mono);
    font-size: 0.68rem;
    letter-spacing: 0.14em;
    cursor: pointer;
    transition: color 0.15s ease, background 0.15s ease;
  }

  button:hover:not([aria-disabled="true"]) {
    color: var(--paper);
  }

  button.active {
    background: var(--line);
    color: var(--accent);
  }

  button[aria-disabled="true"] {
    color: color-mix(in srgb, var(--muted) 50%, transparent);
    cursor: not-allowed;
  }

  button + button {
    border-left: 1px solid var(--line);
  }

  /* Anchored to the switch's left edge so it never overflows a narrow screen. */
  .tooltip {
    position: absolute;
    top: calc(100% + 0.45rem);
    left: 0;
    z-index: 10;
    width: max-content;
    max-width: min(17rem, calc(100vw - 2.5rem));
    padding: 0.5rem 0.65rem;
    border: 1px solid var(--line);
    background: var(--bg);
    color: var(--paper);
    font-family: var(--font);
    font-size: 0.78rem;
    letter-spacing: 0;
    line-height: 1.4;
    text-align: left;
    white-space: normal;
    pointer-events: none;
    opacity: 0;
    visibility: hidden;
    transition: opacity 0.12s ease, visibility 0.12s;
  }

  button:hover .tooltip,
  button:focus-visible .tooltip,
  button.tapped .tooltip {
    opacity: 1;
    visibility: visible;
  }
</style>
