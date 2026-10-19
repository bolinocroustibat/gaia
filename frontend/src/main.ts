import { mount } from "svelte"
import "@fontsource/geist/latin-400.css"
import "@fontsource/geist/latin-500.css"
import "@fontsource/geist-mono/latin-400.css"
import App from "./App.svelte"
import { syncDocumentLang } from "./lib/i18n/locale.svelte"
import "./app.css"

syncDocumentLang()

const target = document.getElementById("app")
if (!target) throw new Error("Missing #app")

const app = mount(App, { target })

export default app
