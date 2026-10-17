import * as Plot from "@observablehq/plot";
import type { Locale } from "../i18n/locale.svelte";
import { t } from "../i18n/messages";
import { plotStyle, theme } from "../theme";
import type { Binned2d } from "../types";

type Rgb = [number, number, number];

type Cell = {
  x1: number;
  x2: number;
  y1: number;
  y2: number;
  fill: string;
};

const background: Rgb = [0x0c, 0x0c, 0x0c];

/** Stellar tint along BP−RP: blue, then white-yellow, then red. */
const starStops: { at: number; rgb: Rgb }[] = [
  { at: -0.5, rgb: [80, 150, 255] },
  { at: 0.2, rgb: [190, 214, 255] },
  { at: 0.85, rgb: [255, 228, 170] },
  { at: 1.5, rgb: [255, 156, 64] },
  { at: 2.4, rgb: [255, 72, 48] },
  { at: 3.6, rgb: [176, 32, 42] },
  { at: 5, rgb: [120, 18, 28] },
];

function mix(from: Rgb, to: Rgb, t: number): Rgb {
  return [
    Math.round(from[0] + (to[0] - from[0]) * t),
    Math.round(from[1] + (to[1] - from[1]) * t),
    Math.round(from[2] + (to[2] - from[2]) * t),
  ];
}

function starRgb(bpRp: number): Rgb {
  if (bpRp <= starStops[0].at) return starStops[0].rgb;
  const last = starStops[starStops.length - 1];
  if (bpRp >= last.at) return last.rgb;
  for (let index = 1; index < starStops.length; index++) {
    const next = starStops[index];
    const previous = starStops[index - 1];
    if (bpRp > next.at) continue;
    const span = next.at - previous.at;
    const t = span === 0 ? 0 : (bpRp - previous.at) / span;
    return mix(previous.rgb, next.rgb, t);
  }
  return last.rgb;
}

function fillFor(bpRp: number, count: number, logMax: number): string {
  const presence = Math.log(count) / logMax;
  const density = presence ** 2.6;
  const brightness = 0.62 * density;
  const [r, g, b] = mix(background, starRgb(bpRp), brightness);
  return `rgb(${r} ${g} ${b})`;
}

function cellsFromBins(bins: Binned2d): Cell[] {
  const cells: Cell[] = [];
  const xEdges = bins.x.edges;
  const yEdges = bins.y.edges;
  let max = 1;
  for (const row of bins.counts) {
    if (!row) continue;
    for (const count of row) {
      if (count > max) max = count;
    }
  }
  const logMax = Math.log(max);
  for (let yIndex = 0; yIndex < yEdges.length - 1; yIndex++) {
    const row = bins.counts[yIndex];
    if (!row) continue;
    for (let xIndex = 0; xIndex < xEdges.length - 1; xIndex++) {
      const count = row[xIndex] ?? 0;
      if (count <= 0) continue;
      const x1 = xEdges[xIndex];
      const x2 = xEdges[xIndex + 1];
      cells.push({
        x1,
        x2,
        y1: yEdges[yIndex],
        y2: yEdges[yIndex + 1],
        fill: fillFor((x1 + x2) / 2, count, logMax),
      });
    }
  }
  return cells;
}

/**
 * Each mark is a slim loop around a ridge of (color, absolute magnitude).
 * The angle is taken from the ridge on screen, so it stays on the sequence
 * when the chart gets wider or taller.
 */
const familyMarks = {
  giants: {
    ridge: [
      [1.15, 0.55],
      [1.5, 0.95],
      [1.85, 1.5],
      [2.2, 2.05],
      [2.55, 2.65],
      [2.9, 3.25],
    ],
    thickness: 0.05,
    phase: 0.7,
    wobble: 1.6,
  },
  main: {
    ridge: [
      [0.4, 2.25],
      [0.7, 3.5],
      [1.0, 4.9],
      [1.35, 6.4],
      [1.7, 7.5],
      [2.05, 8.35],
      [2.4, 9.5],
      [2.75, 10.55],
      [3.1, 11.45],
      [3.4, 12.55],
    ],
    thickness: 0.042,
    phase: 2.1,
    wobble: 1.1,
  },
  dwarfs: {
    ridge: [
      [-0.28, 10.8],
      [0.0, 11.7],
      [0.28, 12.6],
      [0.55, 13.5],
      [0.82, 14.25],
    ],
    thickness: 0.04,
    phase: 1.2,
    wobble: 1.3,
  },
} as const;

type FamilyMark = (typeof familyMarks)[keyof typeof familyMarks];

const marginTop = 20;
const marginRight = 24;
const marginBottom = 68;
const marginLeft = 78;

/** Absolute G magnitude of the Sun. Axis ticks are shown as multiples of its light. */
const sunAbsoluteG = 4.67;
const solarTicks = [1000, 100, 10, 1, 0.1, 0.01, 0.001, 0.0001];

function solarMagnitude(timesSun: number): number {
  return sunAbsoluteG - 2.5 * Math.log10(timesSun);
}

/**
 * Rounded main-sequence anchors for Gaia BP−RP: a color name plus a surface
 * temperature. Giants of the same color run a little cooler, so this is a
 * guide, not a thermometer for every star.
 */
const colorStops = [
  { bpRp: -0.25, celsius: 12000, name: "hrColorBlue" },
  { bpRp: 0.35, celsius: 8000, name: "hrColorWhite" },
  { bpRp: 0.82, celsius: 5500, name: "hrColorYellow" },
  { bpRp: 1.6, celsius: 4000, name: "hrColorOrange" },
  { bpRp: 3.2, celsius: 2500, name: "hrColorRed" },
] as const;

function colorStopsFor(width: number) {
  if (width >= 720) return colorStops;
  return colorStops.filter((stop) => stop.name === "hrColorBlue" || stop.name === "hrColorYellow" || stop.name === "hrColorRed");
}

function celsiusLabel(celsius: number, locale: Locale): string {
  const language = locale === "fr" ? "fr-FR" : "en-GB";
  const formatted = new Intl.NumberFormat(language, { maximumFractionDigits: 0 }).format(celsius);
  return `${formatted} °C`;
}

function stackColorTicks(svg: SVGSVGElement): void {
  const ns = "http://www.w3.org/2000/svg";
  for (const node of svg.querySelectorAll("text")) {
    const raw = node.textContent ?? "";
    if (!raw.includes("\n")) continue;
    const [name, temperature] = raw.split("\n");
    const x = node.getAttribute("x") ?? "0";
    node.textContent = "";
    const nameSpan = document.createElementNS(ns, "tspan");
    nameSpan.setAttribute("x", x);
    nameSpan.textContent = name ?? "";
    const temperatureSpan = document.createElementNS(ns, "tspan");
    temperatureSpan.setAttribute("x", x);
    temperatureSpan.setAttribute("dy", "1.2em");
    temperatureSpan.textContent = temperature ?? "";
    node.append(nameSpan, temperatureSpan);
  }
}

function solarTickLabel(timesSun: number, locale: Locale): string {
  const language = locale === "fr" ? "fr-FR" : "en-GB";
  const digits = timesSun >= 1 ? 0 : Math.round(-Math.log10(timesSun));
  const formatted = new Intl.NumberFormat(language, {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(timesSun);
  return `${formatted}×`;
}

type PlotScale = {
  px: (x: number) => number;
  py: (y: number) => number;
  x: (px: number) => number;
  y: (py: number) => number;
};

function plotScale(bins: Binned2d, width: number, height: number): PlotScale {
  const x0 = bins.x.edges[0];
  const x1 = bins.x.edges[bins.x.edges.length - 1];
  const y0 = bins.y.edges[0];
  const y1 = bins.y.edges[bins.y.edges.length - 1];
  const innerW = width - marginLeft - marginRight;
  const innerH = height - marginTop - marginBottom;
  return {
    px: (x) => ((x - x0) / (x1 - x0)) * innerW,
    py: (y) => ((y - y0) / (y1 - y0)) * innerH,
    x: (px) => x0 + (px / innerW) * (x1 - x0),
    y: (py) => y0 + (py / innerH) * (y1 - y0),
  };
}

function markerPoints(mark: FamilyMark, scale: PlotScale, width: number, height: number): { x: number; y: number }[] {
  const ry = mark.thickness * (height - marginTop - marginBottom);
  const spine = mark.ridge.map(([x, y]) => ({ x: scale.px(x), y: scale.py(y) }));
  const frames = spine.map((point, index) => {
    const previous = spine[Math.max(0, index - 1)];
    const next = spine[Math.min(spine.length - 1, index + 1)];
    let tx = next.x - previous.x;
    let ty = next.y - previous.y;
    const length = Math.hypot(tx, ty) || 1;
    tx /= length;
    ty /= length;
    return { point, tx, ty, nx: -ty, ny: tx };
  });
  const wobbleAt = (t: number) =>
    1 +
    mark.wobble *
      (0.055 * Math.sin(2 * t + mark.phase) + 0.03 * Math.sin(3 * t + mark.phase * 1.4));
  const offset = (index: number, side: 1 | -1) => {
    const frame = frames[index];
    const t = (index / (frames.length - 1)) * Math.PI;
    const span = ry * wobbleAt(t);
    return {
      x: frame.point.x + frame.nx * span * side,
      y: frame.point.y + frame.ny * span * side,
    };
  };
  const left = frames.map((_, index) => offset(index, 1));
  const right = frames.map((_, index) => offset(index, -1));
  const cap = (frame: (typeof frames)[number], span: number, from: number) => {
    const points: { x: number; y: number }[] = [];
    const steps = 5;
    for (let step = 1; step < steps; step++) {
      const angle = from + (step / steps) * Math.PI;
      points.push({
        x: frame.point.x + (Math.cos(angle) * frame.nx + Math.sin(angle) * frame.tx) * span,
        y: frame.point.y + (Math.cos(angle) * frame.ny + Math.sin(angle) * frame.ty) * span,
      });
    }
    return points;
  };
  const end = frames[frames.length - 1];
  const start = frames[0];
  const loop = [
    ...left,
    ...cap(end, ry * wobbleAt(Math.PI), 0),
    ...right.reverse(),
    ...cap(start, ry * wobbleAt(0), Math.PI),
  ];
  return loop.map((point) => ({ x: scale.x(point.x), y: scale.y(point.y) }));
}

function markerInk(svg: SVGSVGElement): void {
  const ns = "http://www.w3.org/2000/svg";
  const defs = document.createElementNS(ns, "defs");
  const filter = document.createElementNS(ns, "filter");
  filter.id = "hr-marker";
  filter.setAttribute("x", "-15%");
  filter.setAttribute("y", "-15%");
  filter.setAttribute("width", "130%");
  filter.setAttribute("height", "130%");
  const turbulence = document.createElementNS(ns, "feTurbulence");
  turbulence.setAttribute("type", "fractalNoise");
  turbulence.setAttribute("baseFrequency", "0.6");
  turbulence.setAttribute("numOctaves", "2");
  turbulence.setAttribute("seed", "4");
  turbulence.setAttribute("result", "noise");
  const displace = document.createElementNS(ns, "feDisplacementMap");
  displace.setAttribute("in", "SourceGraphic");
  displace.setAttribute("in2", "noise");
  displace.setAttribute("scale", "3");
  filter.append(turbulence, displace);
  defs.append(filter);
  svg.prepend(defs);
}

/** Top-left of each tooltip, in data units, sitting in a quiet part of the frame. */
const tipPlaces = {
  giants: { x: 3.28, y: -0.2 },
  main: { x: 3.42, y: 5.5 },
  dwarfs: { x: 1.05, y: 13.5 },
} as const;

function familyTips(
  families: { id: keyof typeof tipPlaces; name: string; text: string }[],
  scale: PlotScale,
  width: number,
  height: number,
): HTMLElement {
  const layer = document.createElement("div");
  const tipWidth = Math.min(220, Math.max(132, width * 0.32));
  for (const family of families) {
    const place = tipPlaces[family.id];
    const tip = document.createElement("div");
    tip.className = "family-tip";
    tip.dataset.family = family.id;
    tip.style.width = `${tipWidth}px`;
    const left = marginLeft + scale.px(place.x);
    const top = marginTop + scale.py(place.y);
    const reserve = family.id === "main" ? 112 : 76;
    tip.style.left = `${Math.max(8, Math.min(left, width - tipWidth - 8))}px`;
    tip.style.top = `${Math.max(8, Math.min(top, height - marginBottom - reserve))}px`;
    const name = document.createElement("p");
    name.className = "family-name";
    name.textContent = family.name;
    const text = document.createElement("p");
    text.textContent = family.text;
    tip.append(name, text);
    layer.append(tip);
  }
  return layer;
}

export type HrPlotInput = {
  bins: Binned2d;
  locale: Locale;
};

export function hrPlot(input: HrPlotInput, width: number): HTMLElement {
  const { bins, locale } = input;
  const cells = cellsFromBins(bins);
  const height = Math.round(Math.min(640, Math.max(420, width * 0.72)));
  const scale = plotScale(bins, width, height);
  const strokeWidth = Math.max(2.5, width * 0.0036);
  const families = [
    {
      id: "giants" as const,
      name: t(locale, "hrGiants"),
      text: t(locale, "hrGiantsText"),
    },
    {
      id: "main" as const,
      name: t(locale, "hrMainSequence"),
      text: t(locale, "hrMainSequenceText"),
    },
    {
      id: "dwarfs" as const,
      name: t(locale, "hrWhiteDwarfs"),
      text: t(locale, "hrWhiteDwarfsText"),
    },
  ];
  const svg = Plot.plot({
    width,
    height,
    marginTop,
    marginRight,
    marginBottom,
    marginLeft,
    style: plotStyle,
    x: {
      label: bins.x.id === "bp_rp" ? t(locale, "hrColorAxis") : bins.x.label,
      labelArrow: bins.x.id === "bp_rp" ? false : undefined,
      ticks: bins.x.id === "bp_rp" ? colorStopsFor(width).map((stop) => stop.bpRp) : undefined,
      tickFormat:
        bins.x.id === "bp_rp"
          ? (value: number) => {
              const stops = colorStopsFor(width);
              const nearest = stops.reduce((best, stop) =>
                Math.abs(stop.bpRp - value) < Math.abs(best.bpRp - value) ? stop : best,
              );
              return `${t(locale, nearest.name)}\n${celsiusLabel(nearest.celsius, locale)}`;
            }
          : undefined,
    },
    y: {
      label: bins.y.id === "mg" ? t(locale, "hrLuminosity") : bins.y.label,
      labelArrow: bins.y.id === "mg" ? false : undefined,
      reverse: bins.y.id === "mg",
      ticks: bins.y.id === "mg" ? solarTicks.map(solarMagnitude) : undefined,
      tickFormat:
        bins.y.id === "mg"
          ? (value: number) => {
              const timesSun = 10 ** ((sunAbsoluteG - value) / 2.5);
              const nearest = solarTicks.reduce((best, tick) =>
                Math.abs(Math.log10(tick) - Math.log10(timesSun)) <
                Math.abs(Math.log10(best) - Math.log10(timesSun))
                  ? tick
                  : best,
              );
              return solarTickLabel(nearest, locale);
            }
          : undefined,
    },
    marks: [
      Plot.frame({ stroke: theme.line }),
      Plot.rect(cells, {
        x1: "x1",
        x2: "x2",
        y1: "y1",
        y2: "y2",
        fill: "fill",
        inset: 0,
      }),
      ...families.map((family) =>
        Plot.line(markerPoints(familyMarks[family.id], scale, width, height), {
          x: "x",
          y: "y",
          curve: "catmull-rom-closed",
          fill: "none",
          stroke: theme.accent,
          strokeOpacity: 0.5,
          strokeWidth,
          strokeLinecap: "round",
          strokeLinejoin: "round",
          imageFilter: "url(#hr-marker)",
          ariaLabel: () => family.name,
          ariaDescription: family.text,
        }),
      ),
    ],
  }) as SVGSVGElement;
  stackColorTicks(svg);
  markerInk(svg);
  const marks = svg.querySelectorAll('[filter="url(#hr-marker)"]');
  families.forEach((family, index) => {
    const mark = marks[index];
    if (!mark) return;
    mark.classList.add("hr-mark");
    mark.setAttribute("data-family", family.id);
  });
  const figure = document.createElement("figure");
  figure.className = "hr-figure";
  figure.append(svg, familyTips(families, scale, width, height));
  revealWhenVisible(figure);
  return figure;
}

/** Marks and notes stay hidden until the diagram has been scrolled into view. */
function revealWhenVisible(figure: HTMLElement): void {
  let frames = 0;
  const arm = () => {
    if (!figure.isConnected) {
      if (frames++ > 8) return;
      requestAnimationFrame(arm);
      return;
    }
    const observer = new IntersectionObserver(
      (entries) => {
        if (!entries.some((entry) => entry.isIntersecting)) return;
        figure.classList.add("is-visible");
        observer.disconnect();
      },
      { threshold: 0.28 },
    );
    observer.observe(figure);
    const parent = figure.parentElement;
    if (!parent) return;
    const removal = new MutationObserver(() => {
      if (figure.isConnected) return;
      observer.disconnect();
      removal.disconnect();
    });
    removal.observe(parent, { childList: true });
  };
  requestAnimationFrame(arm);
}
