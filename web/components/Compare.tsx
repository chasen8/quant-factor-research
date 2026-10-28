"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useMemo } from "react";
import { useJson, useJsonMap } from "@/lib/hooks";
import { paths } from "@/lib/data";
import { fmtNum, fmtPct, fmtSignedPct, isNum } from "@/lib/format";
import { parseIds } from "@/lib/filter";
import { toCsv } from "@/lib/csv";
import type { CompareData, Factor, FactorStats, Num } from "@/lib/types";
import { BirthCertificate, Btn, Card, DemoNote, ErrorBox, EvidenceTag, Loading, NotApplicable, PageTitle } from "./ui";
import { useSettings } from "./Providers";
import { MarketSwitch } from "./FactorAnalysis";
import { ChartFrame } from "./charts/ChartFrame";
import { dataZoom, gridBase, heatmapOption, legendBase, symmetricMax, tooltipBase, valueAxis } from "./charts/base";
import { DASHES } from "@/lib/chartTheme";

const MAX = 5;

export function Compare() {
  const sp = useSearchParams();
  const router = useRouter();
  const { market, manifest } = useSettings();
  const { data: factors, error } = useJson<Factor[]>(paths.factors);
  const { data: cmp } = useJson<CompareData>(paths.compare(market));

  const valid = useMemo(() => new Set((factors ?? []).map((f) => f.id)), [factors]);
  const ids = useMemo(() => parseIds(sp.get("ids"), factors ? valid : undefined, MAX), [sp, valid, factors]);
  const inMarket = (id: string) => !!cmp && cmp.factor_ids.includes(id);
  const usable = ids.filter(inMarket);
  const missing = ids.filter((id) => cmp && !inMarket(id));

  const { data: statsMap } = useJsonMap<FactorStats>(usable.map((id) => paths.stats(market, id)));
  const stats = usable.map((id) => statsMap[paths.stats(market, id)]).filter((s): s is FactorStats => !!s);

  const setIds = (next: string[]) => router.replace(next.length ? `/compare/?ids=${next.join(",")}` : "/compare/");
  const nameOf = (id: string) => factors?.find((f) => f.id === id)?.name_zh ?? id;

  if (error) return <ErrorBox error={error} />;
  if (!factors) return <Loading what="因子" />;

  const addable = factors.filter((f) => !ids.includes(f.id) && inMarket(f.id));

  return (
    <div>
      <PageTitle title="因子比較" sub="並排比較 2–5 個因子；指標與圖表皆來自所選市場的示範資料。" />
      <div className="mb-4 space-y-3">
        <MarketSwitch markets={manifest?.markets ?? []} />
        <div className="flex flex-wrap items-center gap-2">
          {ids.map((id, i) => (
            <span key={id} className="inline-flex items-center gap-1.5 rounded-lg border border-line bg-surface px-2 py-1 text-sm">
              <ColorDot i={i} />
              <Link href={`/factors/${id}/`} className="hover:underline">
                {nameOf(id)}
              </Link>
              <span className="font-mono text-[11px] text-muted">{id}</span>
              <button aria-label={`移除 ${id}`} onClick={() => setIds(ids.filter((x) => x !== id))} className="ml-1 text-muted hover:text-fg">
                ✕
              </button>
            </span>
          ))}
          {ids.length < MAX ? (
            <select
              aria-label="加入因子"
              value=""
              onChange={(e) => e.target.value && setIds([...ids, e.target.value])}
              className="rounded-lg border border-line bg-surface px-2 py-1.5 text-sm"
            >
              <option value="">＋ 加入因子（{ids.length}/{MAX}）</option>
              {addable.map((f) => (
                <option key={f.id} value={f.id}>
                  {f.id}　{f.name_zh}
                </option>
              ))}
            </select>
          ) : null}
          {ids.length ? <Btn onClick={() => setIds([])}>清除</Btn> : null}
        </div>
      </div>

      {ids.length < 2 ? (
        <Card className="text-center text-sm text-muted">
          請選擇至少 2 個因子開始比較，或到<Link href="/factors/" className="mx-1 text-accent hover:underline">因子資料庫</Link>勾選後按「比較」。
        </Card>
      ) : null}
      {missing.length ? (
        <div className="mb-3">
          <NotApplicable>
            此市場不適用：{missing.map((m) => `${nameOf(m)}（${m}）`).join("、")} 在所選市場沒有分析結果，已排除於下方比較之外。
          </NotApplicable>
        </div>
      ) : null}

      {ids.length >= 2 && usable.length >= 2 && cmp ? (
        stats.length < usable.length ? (
          <Loading what="比較資料" />
        ) : (
          <CompareBody ids={usable} stats={stats} cmp={cmp} nameOf={nameOf} />
        )
      ) : null}
    </div>
  );
}

function ColorDot({ i }: { i: number }) {
  const { palette } = useSettings();
  return <span aria-hidden className="inline-block h-2.5 w-4 rounded-sm" style={{ background: palette.series[i % palette.series.length] }} />;
}

function CompareBody({ ids, stats, cmp, nameOf }: { ids: string[]; stats: FactorStats[]; cmp: CompareData; nameOf: (id: string) => string }) {
  const first = stats[0];
  const ev = first.evidence_label;
  const demo = first.is_demo;

  const rows: { label: string; get: (s: FactorStats) => string; best?: (s: FactorStats) => Num; hi?: boolean }[] = [
    { label: "Rank IC 均值", get: (s) => fmtNum(s.summary.rank_ic_mean, 4), best: (s) => s.summary.rank_ic_mean, hi: true },
    { label: "Rank ICIR（年化）", get: (s) => fmtNum(s.summary.rank_icir_ann, 2), best: (s) => s.summary.rank_icir_ann, hi: true },
    { label: "Rank IC t 值（Newey-West）", get: (s) => fmtNum(s.summary.rank_ic_tstat_nw, 2), best: (s) => s.summary.rank_ic_tstat_nw, hi: true },
    { label: "樣本外 Rank IC", get: (s) => fmtNum(s.summary.oos_rank_ic_mean, 4), best: (s) => s.summary.oos_rank_ic_mean, hi: true },
    { label: "多空 Sharpe（扣成本後）", get: (s) => fmtNum(s.summary.ls_sharpe_net, 2), best: (s) => s.summary.ls_sharpe_net, hi: true },
    { label: "多空年化報酬（扣成本後）", get: (s) => fmtSignedPct(s.summary.ls_ann_return_net, 2), best: (s) => s.summary.ls_ann_return_net, hi: true },
    { label: "多空年化報酬（扣成本前）", get: (s) => fmtSignedPct(s.summary.ls_ann_return_gross, 2) },
    { label: "多空最大回撤（扣成本後）", get: (s) => fmtPct(s.summary.ls_mdd_net, 1), best: (s) => (isNum(s.summary.ls_mdd_net) ? -s.summary.ls_mdd_net : null), hi: true },
    { label: "換手（年化）", get: (s) => fmtNum(s.summary.turnover_ann, 2), best: (s) => (isNum(s.summary.turnover_ann) ? -s.summary.turnover_ann : null), hi: true },
    { label: "DSR", get: (s) => fmtNum(s.summary.dsr, 3), best: (s) => s.summary.dsr, hi: true },
    { label: "試驗次數 n_trials", get: (s) => String(s.provenance.n_trials) },
  ];

  const idx = ids.map((id) => cmp.factor_ids.indexOf(id));
  const sub = (m: Num[][]) => idx.map((a) => idx.map((b) => m[a]?.[b] ?? null));
  const labelOf = (id: string) => id;
  const subPeriods = first.subperiods.map((x) => x.label);

  return (
    <div className="space-y-4">
      {demo ? <DemoNote>比較頁的所有數字皆為合成示範資料；各因子的出生證明見表格下方。</DemoNote> : null}

      <Card className="p-0">
        <div className="flex items-center justify-between px-4 pt-3">
          <h2 className="text-sm font-semibold">指標並排</h2>
          <EvidenceTag label={ev} />
        </div>
        <div className="scroll-x p-2">
          <table className="w-full min-w-[32rem] text-sm">
            <thead className="text-xs text-muted">
              <tr>
                <th className="px-2 py-1.5 text-left font-medium">指標</th>
                {stats.map((s, i) => (
                  <th key={s.factor_id} className="px-2 py-1.5 text-right font-medium">
                    <div className="flex items-center justify-end gap-1">
                      <ColorDot i={i} />
                      <Link href={`/factors/${s.factor_id}/`} className="text-accent hover:underline">
                        {s.factor_id}
                      </Link>
                    </div>
                    <div className="text-[10px] font-normal">{nameOf(s.factor_id)}</div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => {
                const vals = stats.map((s) => r.best?.(s) ?? null);
                const top = r.hi ? Math.max(...vals.filter(isNum)) : null;
                return (
                  <tr key={r.label} className="border-t border-line">
                    <td className="px-2 py-1.5 text-muted">{r.label}</td>
                    {stats.map((s, i) => (
                      <td key={s.factor_id} className={`num px-2 py-1.5 text-right ${isNum(vals[i]) && top !== null && vals[i] === top && stats.length > 1 ? "font-bold text-accent" : ""}`}>
                        {r.get(s)}
                      </td>
                    ))}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <p className="px-4 pb-2 text-[11px] text-muted">粗體藍字為該列較佳者（回撤、換手以較低為佳）；僅供閱讀，不代表統計上顯著較優。</p>
        <details className="border-t border-line px-4 py-2">
          <summary className="cursor-pointer text-xs text-accent">各因子出生證明</summary>
          <div className="grid gap-3 md:grid-cols-2">
            {stats.map((s) => (
              <div key={s.factor_id}>
                <div className="mt-2 text-xs font-semibold">{s.factor_id}</div>
                <BirthCertificate p={s.provenance} evidence={s.evidence_label} />
              </div>
            ))}
          </div>
        </details>
      </Card>

      <ChartFrame
        title="多空組合累積淨值疊圖（扣成本後，起始 = 1）"
        subtitle="線型與顏色皆區分因子"
        evidence={ev}
        isDemo={demo}
        height={340}
        filename={`compare_ls_${ids.join("_")}`}
        csv={() => {
          const dates = Array.from(new Set(stats.flatMap((s) => s.quantiles.dates))).sort();
          const maps = stats.map((s) => new Map(s.quantiles.dates.map((d, i) => [d, s.quantiles.cum.LS?.[i] ?? null] as const)));
          return toCsv([{ name: "date", values: dates }, ...stats.map((s, i) => ({ name: s.factor_id, values: dates.map((d) => maps[i].get(d) ?? null) }))]);
        }}
        deps={[stats]}
        build={({ p }) => ({
          tooltip: tooltipBase(p, { valueFormatter: (v: unknown) => (typeof v === "number" ? v.toFixed(3) : "—") }),
          legend: legendBase(p),
          grid: gridBase({ bottom: 40 }),
          dataZoom: dataZoom(p),
          xAxis: { type: "time", axisLabel: { color: p.muted, fontSize: 11, hideOverlap: true }, axisLine: { lineStyle: { color: p.axis } }, splitLine: { show: false } },
          yAxis: valueAxis(p, { type: "log", logBase: 2, axisLabel: { color: p.muted, fontSize: 11, formatter: (v: number) => String(+v.toFixed(2)) } }),
          series: stats.map((s, i) => ({
            name: s.factor_id,
            type: "line",
            showSymbol: false,
            data: s.quantiles.dates.map((d, k) => [d, s.quantiles.cum.LS?.[k] ?? null]),
            lineStyle: { width: 1.8, type: DASHES[i % DASHES.length], color: p.series[i % p.series.length] },
            itemStyle: { color: p.series[i % p.series.length] },
          })),
        })}
      />

      <div className="grid gap-4 lg:grid-cols-2">
        <ChartFrame
          title="因子值相關係數（截面 Spearman 的時間平均）"
          subtitle="越接近 1 代表兩因子選股越像、分散效果越差"
          evidence={cmp.is_demo ? "示範資料" : ev}
          isDemo={cmp.is_demo}
          height={Math.max(260, ids.length * 56 + 70)}
          filename="compare_factor_corr"
          deps={[cmp, ids.join("|")]}
          build={({ p, ud }) =>
            heatmapOption(p, ud, {
              x: ids.map(labelOf),
              y: ids.map(labelOf),
              cells: sub(cmp.factor_corr).flatMap((row, y) => row.map((v, x) => [x, y, v] as [number, number, number | null])),
              min: -1,
              max: 1,
              scheme: "corr",
            })
          }
        />
        <ChartFrame
          title="多空月報酬相關係數"
          subtitle="用於評估組合時的報酬分散程度"
          evidence={cmp.is_demo ? "示範資料" : ev}
          isDemo={cmp.is_demo}
          height={Math.max(260, ids.length * 56 + 70)}
          filename="compare_return_corr"
          deps={[cmp, ids.join("|")]}
          build={({ p, ud }) =>
            heatmapOption(p, ud, {
              x: ids.map(labelOf),
              y: ids.map(labelOf),
              cells: sub(cmp.ls_return_corr).flatMap((row, y) => row.map((v, x) => [x, y, v] as [number, number, number | null])),
              min: -1,
              max: 1,
              scheme: "corr",
            })
          }
        />
      </div>

      <ChartFrame
        title="分期間穩定性：子期間 Rank IC 均值"
        subtitle="期間 × 因子；顏色為漲跌色（正 = 預測方向正確）"
        evidence={ev}
        isDemo={demo}
        height={Math.max(220, subPeriods.length * 44 + 90)}
        filename="compare_subperiod_ic"
        deps={[stats]}
        build={({ p, ud }) => {
          const all = stats.flatMap((s) => s.subperiods.map((x) => x.rank_ic_mean));
          const m = symmetricMax(all, 0.005);
          return heatmapOption(p, ud, {
            x: stats.map((s) => s.factor_id),
            y: subPeriods,
            cells: stats.flatMap((s, x) => subPeriods.map((label, y) => [x, y, s.subperiods.find((q) => q.label === label)?.rank_ic_mean ?? null] as [number, number, number | null])),
            min: -m,
            max: m,
            scheme: "updown",
            digits: 4,
          });
        }}
      />
    </div>
  );
}
