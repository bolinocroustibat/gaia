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
    hrGiants: "Géantes",
    hrGiantsText:
      "Étoiles en fin de vie qui gonflent et rougissent après avoir épuisé leur cœur en hydrogène.",
    hrMainSequence: "« Séquence principale »",
    hrMainSequenceText:
      "Étoiles au stade adulte, où elles passent l’essentiel de leur vie. Plus l’étoile est massive, plus elle est chaude, brillante et bleue.",
    hrLuminosity: "Luminosité (fois le Soleil)",
    hrColorAxis: "Température de surface (estimée d’après la couleur bleu–rouge)",
    hrColorBlue: "Bleu",
    hrColorWhite: "Blanc",
    hrColorYellow: "Jaune",
    hrColorOrange: "Orange",
    hrColorRed: "Rouge",
    hrWhiteDwarfs: "Naines blanches",
    hrWhiteDwarfsText:
      "Cœurs d’étoiles mortes ultra-denses qui ne fusionnent plus rien et se refroidissent lentement au fil des milliards d’années.",
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
    hrGiants: "Giants",
    hrGiantsText:
      "Stars near the end of their life. They swell and turn red after exhausting the hydrogen in their core.",
    hrMainSequence: "“Main sequence”",
    hrMainSequenceText:
      "Stars in their adult stage, where they spend most of their life. The more massive a star, the hotter, brighter, and bluer it is.",
    hrLuminosity: "Luminosity (times the Sun)",
    hrColorAxis: "Surface temperature (estimated from the blue–red color)",
    hrColorBlue: "Blue",
    hrColorWhite: "White",
    hrColorYellow: "Yellow",
    hrColorOrange: "Orange",
    hrColorRed: "Red",
    hrWhiteDwarfs: "White dwarfs",
    hrWhiteDwarfsText:
      "Ultra-dense cores of dead stars. They no longer fuse anything and cool slowly over billions of years.",
    langSwitch: "Language",
    langFr: "Français",
    langEn: "English",
  },
} as const;

export type MessageKey = keyof (typeof messages)["fr"];

export function t(loc: Locale, key: MessageKey): string {
  return messages[loc][key];
}
