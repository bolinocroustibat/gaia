import type { Locale } from "./locale.svelte";

export const messages = {
  fr: {
    siteTitle: "Qu’a vu le télescope spatial Gaia ?",
    siteIntro1:
      "Depuis 2013, Gaia tourne autour de la Terre. Comme tant d’explorations avant elle, elle répond à une envie très ancienne : mieux connaître le ciel et en dresser la carte — mais à une échelle que personne n’avait encore atteinte.",
    siteIntro2: "En explorant ses dernières données ouvertes, que pouvons-nous apprendre ?",
    ledeFallback: "En explorant ses dernières données ouvertes, que pouvons-nous apprendre ?",
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
    footerSourceCode: "Code source",
    footerGaiaCatalog: "Catalogue Gaia",
    footerByBolino: "par bolino",
    footerExported: "Données exportées de Gaia le",
    kpiShareTitle: "Répartition du catalogue",
    kpiShareHint: "Cette bande représente le catalogue des objets recensés par Gaia.",
  },
  en: {
    siteTitle: "What has the Gaia space telescope seen?",
    siteIntro1:
      "Since 2013, Gaia has orbited Earth. Like many explorations before it, it answers an old drive: to know the sky better and map it — this time at a scale no one had reached yet.",
    siteIntro2: "By exploring its latest open data, what can we learn?",
    ledeFallback: "By exploring its latest open data, what can we learn?",
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
    footerSourceCode: "Source code",
    footerGaiaCatalog: "Gaia catalogue",
    footerByBolino: "by bolino",
    footerExported: "Data exported from Gaia on",
    kpiShareTitle: "Share of the catalogue",
    kpiShareHint: "This strip is the catalogue of objects listed by Gaia.",
  },
} as const;

/** External links shown in the site footer. */
export const footerLinks = {
  sourceRepo: "https://github.com/bolinocroustibat/gaia",
  gaiaArchive: "https://gea.esac.esa.int/archive/",
  author: "https://adriencarpentier.com",
} as const;

export type MessageKey = keyof (typeof messages)["fr"];

export function t(loc: Locale, key: MessageKey): string {
  return messages[loc][key];
}
