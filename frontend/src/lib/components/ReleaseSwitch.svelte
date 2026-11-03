<script lang="ts">
import { localeState } from "../i18n/locale.svelte"
import { t } from "../i18n/messages"

/** One position of the switch. `hint` is shown on hover even when enabled. */
export type SwitchOption = { id: string; label: string; hint?: string }

const RELEASES: SwitchOption[] = [
	{ id: "dr3", label: "DR3" },
	{ id: "dr4", label: "DR4" },
]

let {
	options = RELEASES,
	available,
	value,
	onchange,
}: {
	options?: SwitchOption[]
	available: string[]
	value: string
	onchange: (id: string) => void
} = $props()

const uid = $props.id()

// Tooltip opened by a tap, for touch screens without hover.
let tapped = $state<string | null>(null)

function unavailableText(option: SwitchOption): string {
	const loc = localeState.value
	if (option.id === "dr4") return t(loc, "releaseDr4Pending")
	return t(loc, "releaseUnavailable").replace(
		"{release}",
		`Gaia ${option.label}`,
	)
}

function tooltipText(
	option: SwitchOption,
	enabled: boolean,
): string | undefined {
	return enabled ? option.hint : unavailableText(option)
}
</script>

<div
  class="release-switch"
  role="group"
  aria-label={t(localeState.value, "releaseSwitch")}
>
  {#each options as option (option.id)}
    {@const enabled = available.includes(option.id)}
    {@const tip = tooltipText(option, enabled)}
    {@const tipId = `${uid}-${option.id}-tip`}
    <button
      type="button"
      class:active={value === option.id}
      class:tapped={tapped === option.id}
      aria-pressed={value === option.id}
      aria-disabled={enabled ? undefined : "true"}
      aria-describedby={tip ? tipId : undefined}
      onclick={() => {
        if (!enabled) {
          tapped = tapped === option.id ? null : option.id
          return
        }
        if (option.id !== value) onchange(option.id)
      }}
      onblur={() => {
        if (tapped === option.id) tapped = null
      }}
    >
      {option.label}
      {#if tip}
        <span class="tooltip" role="tooltip" id={tipId}>{tip}</span>
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
