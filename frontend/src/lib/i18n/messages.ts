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
    hrGiants: "Géantes rouges",
    hrGiantsText:
      "Étoiles en fin de vie, qui gonflent et tendent vers le rouge car elles manquent de carburant.",
    hrMainSequence: "Séquence principale",
    hrMainSequenceText:
      "Le stade le plus long de la vie d’une étoile. Sur cette ligne, les étoiles ont différentes masses, donc différentes couleurs et luminosités.",
    hrWhiteDwarfs: "Naines blanches",
    hrWhiteDwarfsText: "Étoiles mortes qui se sont effondrées.",
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
    hrGiants: "Red giants",
    hrGiantsText: "Stars near the end of their life. They swell and turn red as they run out of fuel.",
    hrMainSequence: "Main sequence",
    hrMainSequenceText:
      "The longest stage of a star’s life. Along this line, stars of different masses have different colors and luminosities.",
    hrWhiteDwarfs: "White dwarfs",
    hrWhiteDwarfsText: "Dead stars that have collapsed.",
    langSwitch: "Language",
    langFr: "Français",
    langEn: "English",
  },
} as const;

export type MessageKey = keyof (typeof messages)["fr"];

export function t(loc: Locale, key: MessageKey): string {
  return messages[loc][key];
}
