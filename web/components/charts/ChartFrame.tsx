"use client";

import { useCallback, useEffect, useMemo, useRef, type ReactNode } from "react";
import * as echarts from "echarts/core";
import { BarChart, HeatmapChart, LineChart } from "echarts/charts";
import {
  DataZoomComponent, GraphicComponent, GridComponent, LegendComponent, MarkLineComponent, TooltipComponent, VisualMapComponent,
} from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";
import type { EChartsCoreOption } from "echarts/core";
import { useSettings } from "../Providers";
import { EvidenceTag, cx } from "../ui";
import type { Palette, UpDown } from "@/lib/chartTheme";

echarts.use([
  LineChart, BarChart, HeatmapChart,
  GridComponent, TooltipComponent, LegendComponent, DataZoomComponent, VisualMapComponent, GraphicComponent, MarkLineComponent,
  CanvasRenderer,
]);

export interface ChartCtx {
  p: Palette;
  ud: UpDown;
}

function download(name: string, href: string) {
  const a = document.createElement("a");
  a.href = href;
  a.download = name;
  document.body.appendChild(a);
  a.click();
  a.remove();
}

interface Props {
  title: string;
  subtitle?: ReactNode;
  /** 證據標籤，顯示於右上角。示範資料請傳 "示範資料"。 */
  evidence: string;
  isDemo: boolean;
  height?: number;
  /** 依主題與漲跌色建構 ECharts option；deps 為資料依賴（長度需固定）。 */
  build: (ctx: ChartCtx) => EChartsCoreOption;
  deps: unknown[];
  csv?: () => string;
  filename?: string;
  className?: string;
  footer?: ReactNode;
}

export function ChartFrame({ title, subtitle, evidence, isDemo, height = 300, build, deps, csv, filename, className, footer }: Props) {
  const { palette: p, updown: ud } = useSettings();
  const elRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<echarts.ECharts | null>(null);

  const option = useMemo<EChartsCoreOption>(() => {
    const base = build({ p, ud }) as Record<string, unknown>;
    const graphic = Array.isArray(base.graphic) ? (base.graphic as unknown[]) : [];
    return {
      backgroundColor: "transparent",
      animation: false,
      textStyle: { color: p.text, fontFamily: "inherit" },
      ...base,
      graphic,
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [p, ud, isDemo, ...deps]);

  useEffect(() => {
    const el = elRef.current;
    if (!el) return;
    const chart = echarts.init(el, undefined, { renderer: "canvas" });
    chartRef.current = chart;
    const ro = new ResizeObserver(() => chart.resize());
    ro.observe(el);
    return () => {
      ro.disconnect();
      chart.dispose();
      chartRef.current = null;
    };
  }, []);

  useEffect(() => {
    chartRef.current?.setOption(option, { notMerge: true });
  }, [option]);

  const exportPng = useCallback(() => {
    const c = chartRef.current;
    if (!c) return;
    download(`${filename ?? "chart"}.png`, c.getDataURL({ type: "png", pixelRatio: 2, backgroundColor: p.bg }));
  }, [filename, p.bg]);

  const exportCsv = useCallback(() => {
    if (!csv) return;
    const url = URL.createObjectURL(new Blob(["﻿" + csv()], { type: "text/csv;charset=utf-8" }));
    download(`${filename ?? "chart"}.csv`, url);
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }, [csv, filename]);

  return (
    <figure className={cx("min-w-0 rounded-xl border border-line bg-surface p-3", className)}>
      <figcaption className="mb-1 flex flex-wrap items-start justify-between gap-2">
        <div className="min-w-0">
          <div className="text-sm font-semibold">{title}</div>
          {subtitle ? <div className="text-xs text-muted">{subtitle}</div> : null}
        </div>
        <div className="flex items-center gap-1.5">
          <button onClick={exportPng} className="rounded border border-line px-1.5 py-0.5 text-[11px] text-muted hover:bg-surface2" title="匯出 PNG">
            PNG
          </button>
          {csv ? (
            <button onClick={exportCsv} className="rounded border border-line px-1.5 py-0.5 text-[11px] text-muted hover:bg-surface2" title="匯出 CSV">
              CSV
            </button>
          ) : null}
          <EvidenceTag label={evidence} />
        </div>
      </figcaption>
      <div className="relative">
        <div ref={elRef} style={{ height }} className="w-full" role="img" aria-label={title} />
        {isDemo ? (
          <div aria-hidden className="pointer-events-none absolute inset-0 flex items-center justify-center overflow-hidden">
            <span className="rotate-[-12deg] select-none whitespace-nowrap text-5xl font-black text-demo opacity-[0.13]">示範資料</span>
          </div>
        ) : null}
      </div>
      {footer ? <div className="mt-1 text-[11px] text-muted">{footer}</div> : null}
    </figure>
  );
}
