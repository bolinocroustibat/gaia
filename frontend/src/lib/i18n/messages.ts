import type { Locale } from "./locale.svelte";

export const messages = {
  fr: {
    ledeFallback: "Le catalogue, en quelques images.",
    catalogLoadFailed: "Le catalogue n’a pas pu être chargé.",
    panelLoadFailed: "Ces données n’ont pas pu être chargées.",
    galaxyCanvasLabel:
      "Échantillon du disque de la Voie lactée, en trois dimensions, avec la position de la Terre",
    earth: "Terre",
    galaxyHint: "Glisser pour tourner · le point marque la Terre, là où se trouve Gaia",
    langSwitch: "Langue",
    langFr: "Français",
    langEn: "English",
  },
  en: {
    ledeFallback: "The catalogue in a few charts.",
    catalogLoadFailed: "The catalogue could not be loaded.",
    panelLoadFailed: "This data could not be loaded.",
    galaxyCanvasLabel: "Sample of the Milky Way disk in three dimensions, with Earth’s position",
    earth: "Earth",
    galaxyHint: "Drag to rotate · the dot marks Earth, where Gaia lives",
    langSwitch: "Language",
    langFr: "Français",
    langEn: "English",
  },
} as const;

export type MessageKey = keyof (typeof messages)["fr"];

export function t(loc: Locale, key: MessageKey): string {
  return messages[loc][key];
}
