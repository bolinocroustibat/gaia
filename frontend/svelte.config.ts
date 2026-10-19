import { type SvelteConfig, vitePreprocess } from "@sveltejs/vite-plugin-svelte"

export default {
	preprocess: vitePreprocess(),
} satisfies SvelteConfig
