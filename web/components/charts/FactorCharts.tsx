"use client";

import { ChartFrame } from "./ChartFrame";
import { clean, dataZoom, gridBase, legendBase, lineSeries, timeAxis, tipNum, tooltipBase, valueAxis } from "./base";
import { fmtNum, fmtPct, isNum } from "@/lib/format";
import { toCsv } from "@/lib/csv";
import type { FactorStats, Num } from "@/lib/types";

const QCOLORS = ["#9ecae1", "#6baed6", "#4292c6", "#2171b5", "#08306b"];

interface P {
  s: FactorStats;
  height?: number;
}

export function ICChart({ s, height = 300 }: P) {
  const ic = s.ic_series;
  return (
    <ChartFrame
      title="Rank IC 時間序列與 12 個月滾動均值"
      subtitle="長條：每期截面 Rank IC；線：12 期滾動均值"
      evidence={s.evidence_label}
      isDemo={s.is_demo}
      height={height}
      filename={`${s.factor_id}_${s.market}_rank_ic`}
      csv={() => toCsv([{ name: "date", values: ic.dates }, { name: "rank_ic", values: ic.rank_ic }, { name: "rank_ic_roll12", values: ic.rank_ic_roll12 }, { name: "ic", values: ic.ic }])}
      deps={[s]}
      build={({ p }) => ({
        tooltip: tooltipBase(p, { axisPointer: { type: "line", lineStyle: { color: p.axis } }, valueFormatter: (v: unknown) => tipNum(v, 4) }),
        legend: legendBase(p),
        grid: gridBase({ bottom: 40 }),
        dataZoom: dataZoom(p),
        xAxis: { ...timeAxis(p, ic.dates), boundaryGap: true },
        yAxis: valueAxis(p, { scale: false }),
        series: [
          { name: "Rank IC", type: "bar", data: clean(ic.rank_ic), itemStyle: { color: p.series[0], opacity: 0.45 }, barCategoryGap: "10%" },
          lineSeries("12 期滾動均值", ic.rank_ic_roll12, 1, p, { lineStyle: { width: 2.2, color: p.series[1] }, z: 3 }),
        ],
      })}
    />
  );
}

export function QuantileChart({ s, height = 320 }: P) {
  const q = s.quantiles;
  const keys = Object.keys(q.cum);
  return (
    <ChartFrame
      title="分組累積淨值（扣成本後，起始 = 1）"
      subtitle="Q1 最低因子值 … Q5 最高；LS 多空；TOP_EXCESS 頂組相對股票池等權的超額"
      evidence={s.evidence_label}
      isDemo={s.is_demo}
      height={height}
      filename={`${s.factor_id}_${s.market}_quantile_cum`}
      csv={() => toCsv([{ name: "date", values: q.dates }, ...keys.map((k) => ({ name: k, values: q.cum[k] }))])}
      deps={[s]}
      build={({ p }) => ({
        tooltip: tooltipBase(p, { valueFormatter: (v: unknown) => tipNum(v, 3) }),
        legend: legendBase(p, { selected: { TOP_EXCESS: false } }),
        grid: gridBase({ bottom: 40 }),
        dataZoom: dataZoom(p),
        xAxis: timeAxis(p, q.dates),
        yAxis: valueAxis(p, { type: "log", logBase: 2, axisLabel: { color: p.muted, fontSize: 11, formatter: (v: number) => String(+v.toFixed(2)) } }),
        series: keys.map((k, i) => {
          const qi = k.startsWith("Q") ? Number(k.slice(1)) - 1 : -1;
          if (qi >= 0) {
            const color = QCOLORS[Math.min(qi, 4)];
            return lineSeries(k, q.cum[k], 0, p, { lineStyle: { width: 1.3, color }, itemStyle: { color } });
          }
          return lineSeries(k, q.cum[k], i, p, {
            lineStyle: { width: 2.4, color: k === "LS" ? p.series[1] : p.series[2], type: k === "LS" ? "dashed" : "dotted" },
            itemStyle: { color: k === "LS" ? p.series[1] : p.series[2] },
            z: 4,
          });
        }),
      })}
    />
  );
}

export function QuantileBars({ s, height = 260 }: P) {
  const m = s.quantiles.mean_period_return;
  const keys = Object.keys(m);
  return (
    <ChartFrame
      title="各組平均月報酬（扣成本前）"
      subtitle="衡量排序力：單調遞增代表因子排序有效"
      evidence={s.evidence_label}
      isDemo={s.is_demo}
      height={height}
      filename={`${s.factor_id}_${s.market}_quantile_mean`}
      csv={() => toCsv([{ name: "group", values: keys }, { name: "mean_period_return", values: keys.map((k) => m[k]) }])}
      deps={[s]}
      build={({ p, ud }) => ({
        tooltip: tooltipBase(p, { trigger: "axis", axisPointer: { type: "shadow" }, valueFormatter: (v: unknown) => (typeof v === "number" ? fmtPct(v, 2) : "—") }),
        grid: gridBase({ top: 16 }),
        xAxis: { type: "category", data: keys, axisLabel: { color: p.muted }, axisLine: { lineStyle: { color: p.axis } } },
        yAxis: valueAxis(p, { scale: false, axisLabel: { color: p.muted, fontSize: 11, formatter: (v: number) => `${(v * 100).toFixed(1)}%` } }),
        series: [
          {
            type: "bar",
            data: keys.map((k) => ({ value: isNum(m[k]) ? m[k] : null, itemStyle: { color: (m[k] ?? 0) >= 0 ? ud.up : ud.down } })),
            label: { show: true, position: "top", color: p.muted, fontSize: 10, formatter: (q: { value: number | null }) => (isNum(q.value) ? fmtPct(q.value, 2) : "—") },
          },
        ],
      })}
    />
  );
}

export function DecayChart({ s, height = 260 }: P) {
  const d = s.decay;
  return (
    <ChartFrame
      title="因子衰減（Rank IC vs 持有天數）"
      subtitle="橫軸 h = 前瞻報酬天數"
      evidence={s.evidence_label}
      isDemo={s.is_demo}
      height={height}
      filename={`${s.factor_id}_${s.market}_decay`}
      csv={() => toCsv([{ name: "horizon_days", values: d.horizons }, { name: "rank_ic", values: d.rank_ic }])}
      deps={[s]}
      build={({ p }) => ({
        tooltip: tooltipBase(p, { valueFormatter: (v: unknown) => tipNum(v, 4) }),
        grid: gridBase({ top: 16 }),
        xAxis: { type: "category", data: d.horizons.map((h) => `h=${h}`), axisLabel: { color: p.muted }, axisLine: { lineStyle: { color: p.axis } } },
        yAxis: valueAxis(p, { scale: false }),
        series: [lineSeries("Rank IC", d.rank_ic, 0, p, { showSymbol: true, symbol: "circle", symbolSize: 7, lineStyle: { width: 2, color: p.series[0] } })],
      })}
    />
  );
}

export function DistributionChart({ s, height = 280 }: P) {
  const d = s.distribution;
  const diff = (a: Num[], b: Num[]) => a.map((v, i) => (isNum(v) && isNum(b[i]) ? v - (b[i] as number) : null));
  return (
    <ChartFrame
      title="因子值截面分佈帶（p10–p90 / p25–p75 / 中位數）"
      subtitle="每期截面分位數（標準化後），觀察分佈是否漂移或失真"
      evidence={s.evidence_label}
      isDemo={s.is_demo}
      height={height}
      filename={`${s.factor_id}_${s.market}_distribution`}
      csv={() => toCsv([{ name: "date", values: d.dates }, { name: "p10", values: d.p10 }, { name: "p25", values: d.p25 }, { name: "p50", values: d.p50 }, { name: "p75", values: d.p75 }, { name: "p90", values: d.p90 }])}
      deps={[s]}
      build={({ p }) => {
        const band = (name: string, base: Num[], top: Num[], stack: string, color: string, opacity: number) => [
          { name: `${name}_base`, type: "line", stack, data: clean(base), symbol: "none", lineStyle: { opacity: 0 }, tooltip: { show: false }, silent: true },
          { name, type: "line", stack, data: clean(diff(top, base)), symbol: "none", lineStyle: { opacity: 0 }, areaStyle: { color, opacity }, silent: true },
        ];
        return {
          tooltip: tooltipBase(p, {
            formatter: (ps: { axisValueLabel: string; dataIndex: number }[]) => {
              const i = ps[0].dataIndex;
              return `${ps[0].axisValueLabel}<br/>p90 ${fmtNum(d.p90[i], 3)}　p75 ${fmtNum(d.p75[i], 3)}<br/>中位數 ${fmtNum(d.p50[i], 3)}<br/>p25 ${fmtNum(d.p25[i], 3)}　p10 ${fmtNum(d.p10[i], 3)}`;
            },
          }),
          legend: legendBase(p, { data: ["p10–p90", "p25–p75", "中位數"] }),
          grid: gridBase({ bottom: 40 }),
          dataZoom: dataZoom(p),
          xAxis: timeAxis(p, d.dates),
          yAxis: valueAxis(p),
          series: [
            ...band("p10–p90", d.p10, d.p90, "outer", p.series[0], 0.18),
            ...band("p25–p75", d.p25, d.p75, "inner", p.series[0], 0.35),
            lineSeries("中位數", d.p50, 1, p, { lineStyle: { width: 1.8, color: p.series[1] } }),
          ],
        };
      }}
    />
  );
}

export function SubperiodChart({ s, height = 240 }: P) {
  const sp = s.subperiods;
  return (
    <ChartFrame
      title="子期間 Rank IC 均值"
      subtitle="檢查績效是否只集中在某一段時期"
      evidence={s.evidence_label}
      isDemo={s.is_demo}
      height={height}
      filename={`${s.factor_id}_${s.market}_subperiods`}
      csv={() => toCsv([{ name: "period", values: sp.map((x) => x.label) }, { name: "rank_ic_mean", values: sp.map((x) => x.rank_ic_mean) }])}
      deps={[s]}
      build={({ p, ud }) => ({
        tooltip: tooltipBase(p, { axisPointer: { type: "shadow" }, valueFormatter: (v: unknown) => tipNum(v, 4) }),
        grid: gridBase({ top: 16 }),
        xAxis: { type: "category", data: sp.map((x) => x.label), axisLabel: { color: p.muted }, axisLine: { lineStyle: { color: p.axis } } },
        yAxis: valueAxis(p, { scale: false }),
        series: [
          {
            type: "bar",
            data: sp.map((x) => ({ value: isNum(x.rank_ic_mean) ? x.rank_ic_mean : null, itemStyle: { color: (x.rank_ic_mean ?? 0) >= 0 ? ud.up : ud.down } })),
            label: { show: true, position: "top", color: p.muted, fontSize: 10, formatter: (q: { value: number | null }) => fmtNum(q.value, 4) },
          },
        ],
      })}
    />
  );
}
