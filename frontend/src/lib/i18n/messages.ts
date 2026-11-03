import type { Locale } from "./locale.svelte"

export const messages = {
	fr: {
		siteTitle: "Qu’a vu le télescope spatial Gaia ?",
		siteIntro1:
			"Depuis 2013, le télescope Gaia tourne autour de la Terre pour accomplir la plus grande mission de cartographie de l’histoire de l’humanité. Comme tous les explorateurs avant elle, elle répond à une envie très ancienne : dresser la carte de notre voisinage, de l’univers, à une échelle que personne n’avait encore atteinte avant.",
		siteIntro2:
			"Ses mesures sont publiques, et de nouvelles données sont publiées régulièrement. Voici ce qu’on peut y voir aujourd’hui.",
		siteMastMeta: "Cartographie ouverte · export du {date}",
		siteHeroAlt:
			"Le télescope spatial Gaia, vu de trois quarts sur fond d’étoiles",
		sectionGalaxies: "Des galaxies",
		sectionBinaries: "Des étoiles binaires",
		ledeFallback:
			"Ses mesures sont publiques, et de nouvelles données sont publiées régulièrement. Voici ce qu’on peut y voir aujourd’hui.",
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
		viewNasa: "NASA",
		viewNasaHint:
			"Planètes confirmées par tous les télescopes, d’après le NASA Exoplanet Archive",
		viewDr4: "DR4",
		exoplanetsDr4Help:
			"Gaia DR4 publie ses propres candidates : des planètes que Gaia a trouvées seule, en voyant leur étoile zigzaguer dans le ciel, s’approcher et s’éloigner, ou perdre un peu de lumière. D’autres télescopes devront encore les confirmer.",
		orbitLaneNasa: "Confirmées (NASA)",
		orbitLaneGaia: "Candidates Gaia DR4",
		orbitCompareLegend:
			"{nasa} planètes confirmées et {gaia} candidates Gaia DR4 dont on a pu estimer la distance à leur étoile.",
		planetMass: "{mass} masses de Jupiter",
		planetTransit: "La lumière baisse",
		planetCountAxis: "Nombre de planètes",
		planetPeriodLegend:
			"Ce graphique montre les {count} candidates dont Gaia a mesuré la durée d’un tour.",
		transitRadiusAxis: "Rayon (rayons de Jupiter)",
		transitJupiter: "Jupiter",
		transitNeptune: "Neptune",
		transitEarth: "Terre",
		transitRadius: "{radius} rayons de Jupiter",
		transitLegend:
			"{count} planètes qui passent devant leur étoile, dont Gaia a pu estimer la taille.",
		langSwitch: "Langue",
		langFr: "Français",
		langEn: "English",
		releaseSwitch: "Version du catalogue Gaia",
		releaseUnavailable: "Pas de données {release} pour cette visualisation.",
		releaseDr4Pending:
			"Les données Gaia DR4 ne sont pas encore publiées. Elles le seront à partir de décembre 2026.",
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
		binaryPeriodAxis: "Durée d’un tour",
		binaryCountAxis: "Nombre d’orbites",
		binaryEclipse: "Une étoile cache l’autre",
		binarySpectrum: "L’étoile s’approche et s’éloigne",
		binaryBoth: "Plusieurs de ces signes",
		binaryPosition: "L’étoile zigzague dans le ciel",
		binaryPeriodLegend:
			"Ce graphique montre les {count} orbites dont Gaia a pu mesurer la durée, parmi les 813\u202f687 étoiles binaires probables qu’elle a repérées.",
	},
	en: {
		siteTitle: "What has the Gaia space telescope seen?",
		siteIntro1:
			"Since 2013, the Gaia telescope has orbited Earth to carry out the greatest mapping mission in human history. Like all explorers before it, it answers an old drive: to map our cosmic neighborhood and the universe at a scale no one had reached before.",
		siteIntro2:
			"Its measurements are public, and new data is published regularly. Here is what we can see in them today.",
		siteMastMeta: "Open map · data from {date}",
		siteHeroAlt:
			"The Gaia space telescope, seen from an angle against a star field",
		sectionGalaxies: "Galaxies",
		sectionBinaries: "Binary stars",
		ledeFallback:
			"Its measurements are public, and new data is published regularly. Here is what we can see in them today.",
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
		viewNasa: "NASA",
		viewNasaHint:
			"Planets confirmed by all telescopes, from the NASA Exoplanet Archive",
		viewDr4: "DR4",
		exoplanetsDr4Help:
			"Gaia DR4 publishes its own candidates: planets Gaia found on its own, by seeing their star zigzag across the sky, move toward and away from us, or lose a little light. Other telescopes still have to confirm them.",
		orbitLaneNasa: "Confirmed (NASA)",
		orbitLaneGaia: "Gaia DR4 candidates",
		orbitCompareLegend:
			"{nasa} confirmed planets and {gaia} Gaia DR4 candidates whose distance to their star could be estimated.",
		planetMass: "{mass} Jupiter masses",
		planetTransit: "The light dips",
		planetCountAxis: "Number of planets",
		planetPeriodLegend:
			"This chart shows the {count} candidates whose orbit length Gaia measured.",
		transitRadiusAxis: "Radius (Jupiter radii)",
		transitJupiter: "Jupiter",
		transitNeptune: "Neptune",
		transitEarth: "Earth",
		transitRadius: "{radius} Jupiter radii",
		transitLegend:
			"{count} planets that pass in front of their star, whose size Gaia could estimate.",
		langSwitch: "Language",
		langFr: "Français",
		langEn: "English",
		releaseSwitch: "Gaia catalogue release",
		releaseUnavailable: "No {release} data for this visualization.",
		releaseDr4Pending:
			"Gaia DR4 data is not published yet. It will be from December 2026.",
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
		binaryPeriodAxis: "Time for one orbit",
		binaryCountAxis: "Number of orbits",
		binaryEclipse: "One star hides the other",
		binarySpectrum: "The star moves toward and away from us",
		binaryBoth: "Several of these signs",
		binaryPosition: "The star zigzags across the sky",
		binaryPeriodLegend:
			"This chart shows the {count} orbits whose length Gaia could measure, out of the 813,687 likely binary stars it spotted.",
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
