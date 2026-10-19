import * as Plot from "@observablehq/plot";
import type { Locale } from "../i18n/locale.svelte";
import { t } from "../i18n/messages";
import { plotStyle, theme } from "../theme";
import type { OrbitPlanet } from "../types";

/** Solar-system semi-major axes, in astronomical units. */
const landmarks = [
  { id: "orbitMercury" as const, au: 0.387 },
  { id: "orbitVenus" as const, au: 0.723 },
  { id: "orbitEarth" as const, au: 1 },
  { id: "orbitMars" as const, au: 1.524 },
  { id: "orbitJupiter" as const, au: 5.2 },
  { id: "orbitSaturn" as const, au: 9.583 },
  { id: "orbitUranus" as const, au: 19.19 },
  { id: "orbitNeptune" as const, au: 30.07 },
];

const marginRight = 20;
const marginBottom = 48;
const marginLeft = 8;
const labelSize = 11;
const rowPitch = 15;
const labelGap = 12;
/** Geist Mono at 11px is about this wide per character. */
const monoWidth = 6.6;

export type OrbitPlotInput = {
  planets: OrbitPlanet[];
  locale: Locale;
};

function jitter(name: string): number {
  let hash = 2166136261;
  for (let index = 0; index < name.length; index += 1) {
    hash ^= name.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return ((hash >>> 0) / 4294967295 - 0.5) * 1.65;
}

function localeTag(locale: Locale): string {
  return locale === "fr" ? "fr-FR" : "en-US";
}

function formatTick(value: number, locale: Locale): string {
  return new Intl.NumberFormat(localeTag(locale), { maximumSignificantDigits: 2 }).format(value);
}

function labelWidth(label: string): number {
  return label.length * monoWidth;
}

function overlapsLane(
  lane: { left: number; right: number }[] | undefined,
  left: number,
  right: number,
): boolean {
  return (lane ?? []).some((item) => left < item.right + labelGap && right > item.left - labelGap);
}

/**
 * Stack names that would collide. A name that runs into the previous one
 * sits on the next row up, so a tight group reads outward from the frame
 * instead of dropping back underneath.
 */
function labelRows(
  marks: { au: number; label: string }[],
  domain: [number, number],
  innerWidth: number,
): number[] {
  const log0 = Math.log(domain[0]);
  const span = Math.log(domain[1]) - log0;
  const lanes: { left: number; right: number }[][] = [];
  let previous: { right: number; row: number } | undefined;
  return marks.map((mark) => {
    const center = ((Math.log(mark.au) - log0) / span) * innerWidth;
    const half = labelWidth(mark.label) / 2;
    const left = center - half;
    const right = center + half;
    let row = previous && left < previous.right + labelGap ? previous.row + 1 : 0;
    while (overlapsLane(lanes[row], left, right)) row += 1;
    (lanes[row] ??= []).push({ left, right });
    previous = { right, row };
    return row;
  });
}

function tip(planet: OrbitPlanet, locale: Locale): string {
  const format = new Intl.NumberFormat(localeTag(locale), { maximumSignificantDigits: 3 });
  const unit = locale === "fr" ? "ua" : "AU";
  const place = `${format.format(planet.au)} ${unit}`;
  if (planet.period == null) return `${planet.name} · ${place}`;
  const days = format.format(planet.period);
  const period = locale === "fr" ? `${days} jours` : `${days} days`;
  return `${planet.name} · ${place} · ${period}`;
}

export function orbitPlot(input: OrbitPlotInput, width: number): HTMLElement {
  const { planets, locale } = input;
  const dots = planets.map((planet) => ({ ...planet, y: jitter(planet.name) }));
  const distances = planets.map((planet) => planet.au).filter((au) => au > 0);
  const lowest = Math.min(...distances, landmarks[0].au);
  const highest = Math.max(...distances, landmarks[landmarks.length - 1].au);
  const domain: [number, number] = [lowest / 1.35, highest * 1.35];
  const innerWidth = Math.max(1, width - marginLeft - marginRight);
  const named = landmarks.map((landmark) => ({
    ...landmark,
    label: t(locale, landmark.id),
  }));
  const rows = labelRows(named, domain, innerWidth);
  const marks = named.map((landmark, index) => ({
    ...landmark,
    row: rows[index],
    dy: -(4 + rows[index] * rowPitch),
  }));
  const marginTop = 22 + Math.max(...rows) * rowPitch + labelSize;
  const height = Math.round(
    Math.min(440, Math.max(300, width * 0.46, marginTop + marginBottom + 150)),
  );
  const log0 = Math.log(domain[0]);
  const logSpan = Math.log(domain[1]) - log0;
  const star = t(locale, "orbitStar");
  const starWidth = labelWidth(star);
  const ticks = [0.01, 0.1, 1, 10, 100, 1000, 10000].filter((tick) => {
    if (tick <= domain[0] || tick >= domain[1]) return false;
    const center = ((Math.log(tick) - log0) / logSpan) * innerWidth;
    const half = labelWidth(formatTick(tick, locale)) / 2;
    return center - half > starWidth + labelGap;
  });

  const svg = Plot.plot({
    width,
    height,
    marginTop,
    marginRight,
    marginBottom,
    marginLeft,
    style: plotStyle,
    x: {
      type: "log",
      domain,
      label: t(locale, "orbitDistance"),
      labelAnchor: "center",
      labelArrow: false,
      ticks,
      tickFormat: (value: number) => formatTick(value, locale),
      nice: false,
    },
    y: { axis: null, domain: [-1.15, 1.15] },
    marks: [
      Plot.frame({ stroke: theme.line }),
      Plot.ruleX(marks, {
        x: "au",
        stroke: theme.paper,
        strokeOpacity: 0.55,
        strokeWidth: 1,
      }),
      Plot.dot(dots, {
        x: "au",
        y: "y",
        r: width < 560 ? 2.1 : 2.5,
        fill: theme.accent,
        fillOpacity: 0.42,
        title: (planet: OrbitPlanet) => tip(planet, locale),
      }),
      ...marks.map((mark) =>
        Plot.text([mark], {
          x: "au",
          text: "label",
          frameAnchor: "top",
          lineAnchor: "bottom",
          dy: mark.dy,
          fill: theme.paper,
          fontSize: 11,
        }),
      ),
      Plot.text([{ label: star }], {
        x: domain[0],
        text: "label",
        frameAnchor: "bottom",
        lineAnchor: "top",
        textAnchor: "start",
        dy: 9,
        fill: theme.muted,
        fontSize: labelSize,
      }),
    ],
  }) as SVGSVGElement;
  for (const mark of marks) {
    if (mark.row === 0) continue;
    const stem = document.createElementNS("http://www.w3.org/2000/svg", "line");
    const x = marginLeft + ((Math.log(mark.au) - log0) / logSpan) * innerWidth;
    stem.setAttribute("x1", String(x));
    stem.setAttribute("x2", String(x));
    stem.setAttribute("y1", String(marginTop - (1 + mark.row * rowPitch)));
    stem.setAttribute("y2", String(marginTop));
    stem.setAttribute("stroke", theme.paper);
    stem.setAttribute("stroke-opacity", "0.4");
    svg.append(stem);
  }

  const figure = document.createElement("figure");
  figure.className = "orbit-figure";
  const caption = document.createElement("figcaption");
  caption.textContent = t(locale, "orbitLegend");
  const credit = document.createElement("p");
  credit.className = "orbit-credit";
  credit.textContent = t(locale, "orbitCredit");
  figure.append(svg, caption, credit);
  return figure;
}
