import type { Palette, UpDown } from "@/lib/chartTheme";
import { DASHES } from "@/lib/chartTheme";
import { fmtNum, isNum } from "@/lib/format";
import type { Num } from "@/lib/types";

type Opt = Record<string, unknown>;

export function tooltipBase(p: Palette, extra: Opt = {}): Opt {
  return {
    trigger: "axis",
    confine: true,
    backgroundColor: p.tooltipBg,
    borderColor: p.grid,
    textStyle: { color: p.text, fontSize: 12 },
    axisPointer: { type: "cross", lineStyle: { color: p.axis }, crossStyle: { color: p.axis }, label: { backgroundColor: p.muted } },
    ...extra,
  };
}

export function legendBase(p: Palette, extra: Opt = {}): Opt {
  return { top: 0, type: "scroll", textStyle: { color: p.muted, fontSize: 11 }, pageTextStyle: { color: p.muted }, itemWidth: 22, itemHeight: 8, ...extra };
}

export function timeAxis(p: Palette, dates: string[]): Opt {
  return {
    type: "category",
    data: dates,
    boundaryGap: false,
    axisLine: { lineStyle: { color: p.axis } },
    axisLabel: { color: p.muted, fontSize: 11, hideOverlap: true },
    axisTick: { show: false },
  };
}

export function valueAxis(p: Palette, extra: Opt = {}): Opt {
  return {
    type: "value",
    scale: true,
    splitLine: { lineStyle: { color: p.grid } },
    axisLabel: { color: p.muted, fontSize: 11 },
    axisLine: { show: false },
    ...extra,
  };
}

export function gridBase(extra: Opt = {}): Opt {
  return { left: 8, right: 14, top: 36, bottom: 8, containLabel: true, ...extra };
}

export function dataZoom(p: Palette, withSlider = true): Opt[] {
  const inside = { type: "inside", filterMode: "none" };
  if (!withSlider) return [inside];
  return [
    inside,
    {
      type: "slider",
      height: 16,
      bottom: 4,
      filterMode: "none",
      borderColor: p.grid,
      textStyle: { color: p.muted, fontSize: 10 },
      fillerColor: "rgba(120,140,200,0.18)",
    },
  ];
}

/** null 會被 ECharts 視為斷點（不連線）；NaN 不會出現。 */
export function clean(a: Num[]): (number | null)[] {
  return a.map((v) => (isNum(v) ? v : null));
}

export function lineSeries(name: string, data: Num[], i: number, p: Palette, extra: Opt = {}): Opt {
  return {
    name,
    type: "line",
    data: clean(data),
    showSymbol: false,
    smooth: false,
    lineStyle: { width: 1.6, type: DASHES[i % DASHES.length], color: p.series[i % p.series.length] },
    itemStyle: { color: p.series[i % p.series.length] },
    ...extra,
  };
}

export function tipNum(v: unknown, digits = 3): string {
  return typeof v === "number" ? fmtNum(v, digits) : "—";
}

export interface HeatSpec {
  x: string[];
  y: string[];
  /** [xIndex, yIndex, value] */
  cells: [number, number, number | null][];
  min: number;
  max: number;
  /** 顏色：diverging（相關係數用）或 updown（報酬／IC 用漲跌色） */
  scheme: "corr" | "updown";
  digits?: number;
  percent?: boolean;
  height?: number;
  showLabels?: boolean;
  invertY?: boolean;
}

export function heatmapOption(p: Palette, ud: UpDown, s: HeatSpec): Opt {
  const fmt = (v: number) => (s.percent ? `${(v * 100).toFixed(s.digits ?? 1)}%` : v.toFixed(s.digits ?? 2));
  const colors = s.scheme === "corr" ? ["#2166ac", p.bg, "#b2182b"] : [ud.down, p.bg, ud.up];
  return {
    tooltip: {
      confine: true,
      backgroundColor: p.tooltipBg,
      borderColor: p.grid,
      textStyle: { color: p.text, fontSize: 12 },
      formatter: (q: { data: [number, number, number | null] }) => {
        const [xi, yi, v] = q.data;
        return `${s.y[yi]} × ${s.x[xi]}<br/><b>${isNum(v) ? fmt(v) : "—"}</b>`;
      },
    },
    grid: { left: 8, right: 12, top: 8, bottom: 52, containLabel: true },
    xAxis: { type: "category", data: s.x, splitArea: { show: false }, axisLabel: { color: p.muted, fontSize: 10, interval: 0 }, axisLine: { lineStyle: { color: p.axis } } },
    yAxis: { type: "category", data: s.y, inverse: s.invertY ?? true, axisLabel: { color: p.muted, fontSize: 10, interval: 0 }, axisLine: { lineStyle: { color: p.axis } } },
    visualMap: {
      min: s.min,
      max: s.max,
      calculable: false,
      orient: "horizontal",
      left: "center",
      bottom: 0,
      itemWidth: 10,
      itemHeight: 120,
      textStyle: { color: p.muted, fontSize: 10 },
      inRange: { color: colors },
      formatter: (v: number) => fmt(v),
    },
    series: [
      {
        type: "heatmap",
        data: s.cells.map(([x, y, v]) => ({ value: [x, y, isNum(v) ? v : "-"], itemStyle: isNum(v) ? undefined : { color: p.grid } })),
        label: {
          show: s.showLabels ?? true,
          fontSize: 10,
          color: p.text,
          formatter: (q: { data: { value: [number, number, number | string] } }) => {
            const v = q.data.value[2];
            return typeof v === "number" ? fmt(v) : "—";
          },
        },
        itemStyle: { borderColor: p.bg, borderWidth: 1 },
        emphasis: { itemStyle: { borderColor: p.text, borderWidth: 1 } },
      },
    ],
  };
}

export function symmetricMax(values: Num[], floor = 0.01): number {
  const m = Math.max(floor, ...values.filter(isNum).map((v) => Math.abs(v)));
  return m;
}
