"use client";

import { useEffect, useState } from "react";
import { useJson } from "@/lib/hooks";
import { paths } from "@/lib/data";
import { fmtInt, fmtNum, fmtPct, fmtSignedPct, sign } from "@/lib/format";
import { toCsv } from "@/lib/csv";
import { DASHES } from "@/lib/chartTheme";
import type { BacktestIndex, BacktestResult, Factor } from "@/lib/types";
import { Card, DemoNote, ErrorBox, Loading, MetricCard, PageTitle, Pill } from "./ui";
import { useSettings } from "./Providers";
import { MarketSwitch } from "./FactorAnalysis";
import { ChartFrame } from "./charts/ChartFrame";
import { clean, dataZoom, gridBase, heatmapOption, legendBase, symmetricMax, timeAxis, tooltipBase, valueAxis } from "./charts/base";

function tone(v: number | null | undefined): "up" | "down" | "none" {
  const s = sign(v);
  return s > 0 ? "up" : s < 0 ? "down" : "none";
}

export function Backtest() {
  const { market, manifest } = useSettings();
  const { data: index, error } = useJson<BacktestIndex>(paths.backtestIndex);
  const { data: factors } = useJson<Factor[]>(paths.factors);
  const [presetId, setPresetId] = useState<string>("");

  const presets = (index?.presets ?? []).filter((p) => p.market === market);
  useEffect(() => {
    if (presets.length && !presets.some((p) => p.id === presetId)) setPresetId(presets[0].id);
  }, [presets, presetId]);

  const preset = presets.find((p) => p.id === presetId);
  const { data: r, error: rErr } = useJson<BacktestResult>(preset ? paths.backtest(market, preset.id) : null);

  if (error) return <ErrorBox error={error} />;
  if (!index) return <Loading what="回測清單" />;

  const nameOf = (id: string) => factors?.find((f) => f.id === id)?.name_zh ?? id;

  return (
    <div>
      <PageTitle title="量化策略回測" sub="選擇市場與預先算好的策略組合，檢視淨值、回撤、年度與月度報酬。" />
      <div className="mb-4 space-y-3">
        <MarketSwitch markets={manifest?.markets ?? []} />
        <div className="flex flex-wrap items-center gap-2">
          <label className="flex min-w-0 flex-1 items-center gap-2 text-sm">
            <span className="shrink-0 text-muted">策略組合</span>
            <select
              value={presetId}
              onChange={(e) => setPresetId(e.target.value)}
              className="min-w-0 flex-1 rounded-lg border border-line bg-surface px-2 py-1.5"
              aria-label="策略組合"
            >
              {presets.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.label}
                  {p.rebalance === "Q" ? "（季調倉）" : ""}
                </option>
              ))}
            </select>
          </label>
          <Pill tone="accent">自訂回測於第二階段開放</Pill>
        </div>
        <p className="text-xs text-muted">
          目前只提供預先計算的組合；自訂因子、權重、參數與調倉頻率的回測（FastAPI 後端）於第二階段開放，屆時每次執行都會累計試驗次數並顯示 DSR。
        </p>
      </div>

      {rErr ? <ErrorBox error={rErr} /> : null}
      {preset && !r && !rErr ? <Loading what="回測結果" /> : null}
      {r ? <Result r={r} nameOf={nameOf} /> : null}
    </div>
  );
}

function Result({ r, nameOf }: { r: BacktestResult; nameOf: (id: string) => string }) {
  const m = r.metrics;
  const pv = r.provenance;
  const ev = r.evidence_label;
  const card = (label: string, value: string, o: { sub?: string; tone?: "up" | "down" | "none"; hint?: string } = {}) => (
    <MetricCard label={label} value={value} sub={o.sub} tone={o.tone} hint={o.hint} provenance={pv} evidence={ev} />
  );
  const years = Array.from(new Set(r.monthly.map((x) => x.year))).sort((a, b) => a - b);
  const months = Array.from({ length: 12 }, (_, i) => `${i + 1}月`);

  return (
    <div className="space-y-4">
      {r.is_demo ? <DemoNote>此回測使用合成資料，績效不代表任何真實策略；成本已含（見各指標卡出生證明）。</DemoNote> : null}
      <Card>
        <div className="text-sm font-semibold">{r.preset.label}</div>
        <div className="mt-1 flex flex-wrap gap-1.5 text-xs">
          {r.preset.factors.map((f) => (
            <Pill key={f.id} title={nameOf(f.id)}>
              {f.id} × {fmtNum(f.weight, 2)}
            </Pill>
          ))}
          <Pill>調倉 {r.preset.rebalance === "M" ? "月" : "季"}</Pill>
          <Pill>頂 1/{r.preset.top_q} 等權</Pill>
          <Pill>基準：股票池等權（不計成本）</Pill>
          <Pill>試驗次數 n_trials = {fmtInt(pv.n_trials)}</Pill>
        </div>
      </Card>

      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        {card("年化報酬 CAGR（扣成本後）", fmtPct(m.cagr, 2), { sub: `扣成本前 ${fmtPct(m.cagr_gross, 2)}`, tone: tone(m.cagr) })}
        {card("超額年化（vs 基準）", fmtSignedPct(m.excess_cagr, 2), { tone: tone(m.excess_cagr) })}
        {card("Sharpe", fmtNum(m.sharpe, 2), { sub: `Sortino ${fmtNum(m.sortino, 2)}` })}
        {card("最大回撤 MDD", fmtPct(m.mdd, 1), { sub: `Calmar ${fmtNum(m.calmar, 2)}`, hint: "正數 = 回撤幅度" })}
        {card("年化波動", fmtPct(m.vol, 1), { sub: `月勝率 ${fmtPct(m.win_rate, 0)}` })}
        {card("Alpha（年化）", fmtSignedPct(m.alpha_ann, 2), { sub: `Beta ${fmtNum(m.beta, 2)}`, tone: tone(m.alpha_ann) })}
        {card("資訊比率", fmtNum(m.info_ratio, 2), { sub: `追蹤誤差 ${fmtPct(m.tracking_error, 2)}` })}
        {card("成本拖累（年化）", fmtPct(m.cost_drag_ann, 2), { sub: "手續費＋稅＋滑價" })}
      </div>

      <div className="grid grid-cols-2 gap-3 md:grid-cols-3">
        {card("年化換手", fmtNum(m.turnover_ann, 2), { sub: "單邊，倍數" })}
        {card("調倉次數", fmtInt(m.n_rebalances), { sub: pv.rebalance === "M" ? "月調倉" : "季調倉" })}
        {card("交易筆數", fmtInt(m.n_trades), { sub: "買進＋賣出累計" })}
      </div>

      <ChartFrame
        title="策略淨值 vs 基準（起始 = 1）"
        subtitle="策略為扣成本後；基準為股票池等權、月調倉、不計成本"
        evidence={ev}
        isDemo={r.is_demo}
        height={340}
        filename={`backtest_${r.preset.market}_${r.preset.id}_nav`}
        csv={() => toCsv([{ name: "date", values: r.dates }, { name: "nav", values: r.nav }, { name: "bench_nav", values: r.bench_nav }, { name: "drawdown", values: r.drawdown }])}
        deps={[r]}
        build={({ p }) => ({
          tooltip: tooltipBase(p, { valueFormatter: (v: unknown) => (typeof v === "number" ? v.toFixed(3) : "—") }),
          legend: legendBase(p),
          grid: gridBase({ bottom: 40 }),
          dataZoom: dataZoom(p),
          xAxis: timeAxis(p, r.dates),
          yAxis: valueAxis(p, { type: "log", logBase: 2, axisLabel: { color: p.muted, fontSize: 11, formatter: (v: number) => String(+v.toFixed(2)) } }),
          series: [
            { name: "策略（扣成本後）", type: "line", data: clean(r.nav), showSymbol: false, sampling: "lttb", lineStyle: { width: 2, color: p.series[0] }, itemStyle: { color: p.series[0] } },
            { name: "基準（股票池等權）", type: "line", data: clean(r.bench_nav), showSymbol: false, sampling: "lttb", lineStyle: { width: 1.6, type: DASHES[1], color: p.series[1] }, itemStyle: { color: p.series[1] } },
          ],
        })}
      />

      <div className="grid gap-4 lg:grid-cols-2">
        <ChartFrame
          title="回撤曲線"
          subtitle="策略相對歷史高點的跌幅（≤ 0）"
          evidence={ev}
          isDemo={r.is_demo}
          height={260}
          filename={`backtest_${r.preset.market}_${r.preset.id}_drawdown`}
          deps={[r]}
          build={({ p, ud }) => ({
            tooltip: tooltipBase(p, { valueFormatter: (v: unknown) => (typeof v === "number" ? fmtPct(v, 2) : "—") }),
            grid: gridBase({ top: 16, bottom: 40 }),
            dataZoom: dataZoom(p),
            xAxis: timeAxis(p, r.dates),
            yAxis: valueAxis(p, { scale: false, max: 0, axisLabel: { color: p.muted, fontSize: 11, formatter: (v: number) => `${(v * 100).toFixed(0)}%` } }),
            series: [
              { name: "回撤", type: "line", data: clean(r.drawdown), showSymbol: false, sampling: "lttb", lineStyle: { width: 1.2, color: ud.down }, itemStyle: { color: ud.down }, areaStyle: { color: ud.down, opacity: 0.22 } },
            ],
          })}
        />
        <ChartFrame
          title="年度報酬：策略 vs 基準"
          evidence={ev}
          isDemo={r.is_demo}
          height={260}
          filename={`backtest_${r.preset.market}_${r.preset.id}_annual`}
          csv={() => toCsv([{ name: "year", values: r.annual.map((a) => a.year) }, { name: "strategy", values: r.annual.map((a) => a.strat) }, { name: "benchmark", values: r.annual.map((a) => a.bench) }])}
          deps={[r]}
          build={({ p }) => ({
            tooltip: tooltipBase(p, { axisPointer: { type: "shadow" }, valueFormatter: (v: unknown) => (typeof v === "number" ? fmtPct(v, 1) : "—") }),
            legend: legendBase(p),
            grid: gridBase({ bottom: 8 }),
            xAxis: { type: "category", data: r.annual.map((a) => String(a.year)), axisLabel: { color: p.muted, fontSize: 11 }, axisLine: { lineStyle: { color: p.axis } } },
            yAxis: valueAxis(p, { scale: false, axisLabel: { color: p.muted, fontSize: 11, formatter: (v: number) => `${(v * 100).toFixed(0)}%` } }),
            series: [
              { name: "策略", type: "bar", data: clean(r.annual.map((a) => a.strat)), itemStyle: { color: p.series[0] } },
              { name: "基準", type: "bar", data: clean(r.annual.map((a) => a.bench)), itemStyle: { color: p.series[1], decal: { symbol: "rect", dashArrayX: [1, 0], dashArrayY: [2, 3], rotation: 0.6 } } },
            ],
          })}
        />
      </div>

      <ChartFrame
        title="月度報酬熱力圖（策略，扣成本後）"
        subtitle="列 = 年，欄 = 月；顏色為漲跌色"
        evidence={ev}
        isDemo={r.is_demo}
        height={Math.max(260, years.length * 24 + 100)}
        filename={`backtest_${r.preset.market}_${r.preset.id}_monthly`}
        csv={() => toCsv([{ name: "year", values: r.monthly.map((x) => x.year) }, { name: "month", values: r.monthly.map((x) => x.month) }, { name: "return", values: r.monthly.map((x) => x.ret) }])}
        deps={[r]}
        build={({ p, ud }) => {
          const mx = symmetricMax(r.monthly.map((x) => x.ret), 0.02);
          return heatmapOption(p, ud, {
            x: months,
            y: years.map(String),
            cells: r.monthly.map((x) => [x.month - 1, years.indexOf(x.year), x.ret] as [number, number, number | null]),
            min: -mx,
            max: mx,
            scheme: "updown",
            percent: true,
            digits: 1,
          });
        }}
      />
    </div>
  );
}
