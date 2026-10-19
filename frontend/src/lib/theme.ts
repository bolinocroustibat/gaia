export const theme = {
	bg: "#0c0c0c",
	paper: "#f4f1ea",
	muted: "#8a8680",
	line: "#2a2a28",
	accent: "#d6ff4a",
} as const

const bgRgb: Rgb = [0x0c, 0x0c, 0x0c]
const accentRgb: Rgb = [0xd6, 0xff, 0x4a]
const paperRgb: Rgb = [0xf4, 0xf1, 0xea]

type Rgb = [number, number, number]

function mix(from: Rgb, to: Rgb, t: number): Rgb {
	return [
		Math.round(from[0] + (to[0] - from[0]) * t),
		Math.round(from[1] + (to[1] - from[1]) * t),
		Math.round(from[2] + (to[2] - from[2]) * t),
	]
}

/** 0 is the page background, ~0.72 is the acid accent, 1 is warm paper. */
export function rampRgb(t: number): Rgb {
	const x = Math.min(1, Math.max(0, t))
	if (x < 0.72) return mix(bgRgb, accentRgb, x / 0.72)
	return mix(accentRgb, paperRgb, (x - 0.72) / 0.28)
}

export function rampCss(t: number): string {
	const [r, g, b] = rampRgb(t)
	return `rgb(${r} ${g} ${b})`
}

export function rampHex(t: number): string {
	const [r, g, b] = rampRgb(t)
	return `#${[r, g, b].map((channel) => channel.toString(16).padStart(2, "0")).join("")}`
}

export const plotStyle = {
	background: "transparent",
	color: theme.muted,
	fontFamily: '"Geist Mono", ui-monospace, monospace',
	fontSize: "11px",
}
