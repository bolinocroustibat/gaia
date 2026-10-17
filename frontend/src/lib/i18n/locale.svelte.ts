export type Locale = "fr" | "en";

const STORAGE_KEY = "gaia-locale";

function readInitial(): Locale {
  if (typeof localStorage !== "undefined") {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved === "fr" || saved === "en") return saved;
  }
  if (typeof navigator !== "undefined" && navigator.language.toLowerCase().startsWith("fr")) {
    return "fr";
  }
  return "en";
}

export const localeState = $state({ value: readInitial() as Locale });

export function setLocale(next: Locale): void {
  localeState.value = next;
  if (typeof localStorage !== "undefined") {
    localStorage.setItem(STORAGE_KEY, next);
  }
  if (typeof document !== "undefined") {
    document.documentElement.lang = next;
  }
}

export function syncDocumentLang(): void {
  if (typeof document !== "undefined") {
    document.documentElement.lang = localeState.value;
  }
}
