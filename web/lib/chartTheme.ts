export interface Palette {
  text: string;
  muted: string;
  grid: string;
  axis: string;
  bg: string;
  tooltipBg: string;
  watermark: string;
  accent: string;
  /** 色盲友善（Okabe-Ito）序列色 */
  series: string[];
}

const SERIES = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#D55E00", "#56B4E9", "#F0E442"];
const SERIES_DARK = ["#56B4E9", "#F0A830", "#2FC79A", "#E59BC6", "#F07B3F", "#7FC8F0", "#F0E442"];

export const LIGHT: Palette = {
  text: "#1f2937",
  muted: "#6b7280",
  grid: "#e5e7eb",
  axis: "#9ca3af",
  bg: "#ffffff",
  tooltipBg: "#ffffff",
  watermark: "rgba(180,120,0,0.13)",
  accent: "#1d4ed8",
  series: SERIES,
};

export const DARK: Palette = {
  text: "#e5e7eb",
  muted: "#9ca3af",
  grid: "#2b3340",
  axis: "#6b7280",
  bg: "#161b22",
  tooltipBg: "#1f2733",
  watermark: "rgba(240,180,60,0.14)",
  accent: "#7aa2ff",
  series: SERIES_DARK,
};

export const DASHES: ("solid" | "dashed" | "dotted")[] = ["solid", "dashed", "dotted", "solid", "dashed", "dotted", "solid"];
export const SYMBOLS = ["circle", "rect", "triangle", "diamond", "pin", "arrow", "none"];

/** 漲跌色 */
export interface UpDown {
  up: string;
  down: string;
}
export const UPDOWN_RED_UP: UpDown = { up: "#d93636", down: "#1a9a5a" };
export const UPDOWN_GREEN_UP: UpDown = { up: "#1a9a5a", down: "#d93636" };
