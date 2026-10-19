import type { Locale } from "./locale.svelte"

export const messages = {
	fr: {
		siteTitle: "Qu’a vu le télescope spatial Gaia ?",
		siteIntro1:
			"Depuis 2013, Gaia tourne autour de la Terre. Comme tant d’explorations avant elle, elle répond à une envie très ancienne : mieux connaître le ciel et en dresser la carte, à une échelle que personne n’avait encore atteinte.",
		siteIntro2: "Ses mesures sont publiques. Voici ce qu’on peut y voir.",
		ledeFallback: "Ses mesures sont publiques. Voici ce qu’on peut y voir.",
		catalogLoadFailed: "Le catalogue n’a pas pu être chargé.",
		panelLoadFailed: "Ces données n’ont pas pu être chargées.",
		galaxyCanvasLabel:
			"Échantillon du disque de la Voie lactée, en trois dimensions, avec la position de la Terre",
		earth: "Terre",
		galaxyHint:
			"Glisser pour tourner · le point marque la Terre, là où se trouve Gaia",
		hrGiants: "Géantes",
		hrGiantsText:
			"Étoiles en fin de vie qui gonflent et rougissent après avoir épuisé leur cœur en hydrogène.",
		hrMainSequence: "« Séquence principale »",
		hrMainSequenceText:
			"Étoiles au stade adulte, où elles passent l’essentiel de leur vie. Plus l’étoile est massive, plus elle est chaude, brillante et bleue.",
		hrLuminosity: "Luminosité (fois le Soleil)",
		hrColorAxis:
			"Température de surface (estimée d’après la couleur bleu–rouge)",
		hrColorBlue: "Bleu",
		hrColorWhite: "Blanc",
		hrColorYellow: "Jaune",
		hrColorOrange: "Orange",
		hrColorRed: "Rouge",
		hrWhiteDwarfs: "Naines blanches",
		hrWhiteDwarfsText:
			"Cœurs d’étoiles mortes ultra-denses qui ne fusionnent plus rien et se refroidissent lentement au fil des milliards d’années.",
		orbitDistance: "Distance à l’étoile (ua)",
		orbitStar: "étoile",
		orbitMercury: "Mercure",
		orbitVenus: "Vénus",
		orbitEarth: "Terre",
		orbitMars: "Mars",
		orbitJupiter: "Jupiter",
		orbitSaturn: "Saturne",
		orbitUranus: "Uranus",
		orbitNeptune: "Neptune",
		orbitLegend:
			"La foule proche de l’étoile est celle qu’on découvre le plus facilement, pas un recensement du ciel.",
		orbitCredit: "NASA Exoplanet Archive",
		langSwitch: "Langue",
		langFr: "Français",
		langEn: "English",
		footerSourceCode: "Code source",
		footerGaiaCatalog: "Catalogue Gaia",
		footerByBolino: "par bolino",
		footerExported: "Données exportées de Gaia le",
		kpiShareTitle: "Répartition du catalogue",
		kpiShareHint:
			"Cette bande représente le catalogue des objets recensés par Gaia.",
		funnelShare: "soit {share}",
		galaxyDistanceAxis: "Milliards d'années-lumière",
		galaxyRedshiftAxis: "Décalage vers le rouge",
		galaxyNearby: "Galaxies voisines",
		galaxyDistanceLegend:
			"0,2 veut dire que la lumière est étirée d'un cinquième. La foule lointaine est celle que Gaia arrive encore à situer, pas un recensement de l'Univers.",
	},
	en: {
		siteTitle: "What has the Gaia space telescope seen?",
		siteIntro1:
			"Since 2013, Gaia has orbited Earth. Like many explorations before it, it answers an old drive: to know the sky better and map it, at a scale no one had reached yet.",
		siteIntro2: "Its measurements are public. Here is what we can see in them.",
		ledeFallback:
			"Its measurements are public. Here is what we can see in them.",
		catalogLoadFailed: "The catalogue could not be loaded.",
		panelLoadFailed: "This data could not be loaded.",
		galaxyCanvasLabel:
			"Sample of the Milky Way disk in three dimensions, with Earth’s position",
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
		orbitDistance: "Distance from the star (AU)",
		orbitStar: "star",
		orbitMercury: "Mercury",
		orbitVenus: "Venus",
		orbitEarth: "Earth",
		orbitMars: "Mars",
		orbitJupiter: "Jupiter",
		orbitSaturn: "Saturn",
		orbitUranus: "Uranus",
		orbitNeptune: "Neptune",
		orbitLegend:
			"The crowd close to the star is the one we find most easily, not a census of the sky.",
		orbitCredit: "NASA Exoplanet Archive",
		langSwitch: "Language",
		langFr: "Français",
		langEn: "English",
		footerSourceCode: "Source code",
		footerGaiaCatalog: "Gaia catalogue",
		footerByBolino: "by bolino",
		footerExported: "Data exported from Gaia on",
		kpiShareTitle: "Share of the catalogue",
		kpiShareHint: "This strip is the catalogue of objects listed by Gaia.",
		funnelShare: "{share} of them",
		galaxyDistanceAxis: "Billions of light-years",
		galaxyRedshiftAxis: "Stretch toward red",
		galaxyNearby: "Nearby galaxies",
		galaxyDistanceLegend:
			"0.2 means the light is stretched by a fifth. The distant crowd is the one Gaia can still place, not a census of the Universe.",
	},
} as const

/** External links shown in the site footer. */
export const footerLinks = {
	sourceRepo: "https://github.com/bolinocroustibat/gaia",
	gaiaArchive: "https://gea.esac.esa.int/archive/",
	author: "https://adriencarpentier.com",
} as const

export type MessageKey = keyof (typeof messages)["fr"]

export function t(loc: Locale, key: MessageKey): string {
	return messages[loc][key]
}
