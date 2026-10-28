"use client";

import Link from "next/link";
import { useJson } from "@/lib/hooks";
import { paths, marketKind } from "@/lib/data";
import { categoryLabel } from "@/lib/filter";
import { fmtNum, fmtInt } from "@/lib/format";
import type { Dashboard as DashboardData, Factor, LevelId, MarketKind } from "@/lib/types";
import { Card, DemoNote, ErrorBox, EvidenceTag, LevelBadge, Loading, PageTitle, Pill, SectionTitle, cx } from "./ui";
import { ChartFrame } from "./charts/ChartFrame";
import { gridBase, tooltipBase, valueAxis } from "./charts/base";
import { useSettings } from "./Providers";

const LEVELS: LevelId[] = ["L0", "L1", "L2", "L3", "L4"];
const LEVEL_COLOR: Record<LevelId, string> = {
  L0: "bg-slate-400/50",
  L1: "bg-sky-400",
  L2: "bg-cyan-500",
  L3: "bg-emerald-500",
  L4: "bg-emerald-700",
};

function Kpi({ label, value, sub, children }: { label: string; value: string; sub?: string; children?: React.ReactNode }) {
  return (
    <Card>
      <div className="text-xs text-muted">{label}</div>
      <div className="num text-3xl font-bold">{value}</div>
      {sub ? <div className="text-xs text-muted">{sub}</div> : null}
      {children}
    </Card>
  );
}

function LevelBar({ kind, counts }: { kind: MarketKind; counts: Record<LevelId, number> }) {
  const total = LEVELS.reduce((a, l) => a + counts[l], 0) || 1;
  return (
    <div className="mt-2">
      <div className="mb-0.5 flex justify-between text-[11px] text-muted">
        <span>{kind === "TW" ? "台股" : "美股"}</span>
        <span className="num">{LEVELS.map((l) => `${l}:${counts[l]}`).join("　")}</span>
      </div>
      <div className="flex h-2.5 overflow-hidden rounded-full bg-surface2" role="img" aria-label={`${kind} 驗證等級分布`}>
        {LEVELS.map((l) => (counts[l] ? <div key={l} className={LEVEL_COLOR[l]} style={{ width: `${(counts[l] / total) * 100}%` }} title={`${l}：${counts[l]}`} /> : null))}
      </div>
    </div>
  );
}

export function Dashboard() {
  const { data: d, error } = useJson<DashboardData>(paths.dashboard);
  const { data: factors } = useJson<Factor[]>(paths.factors);
  const { manifest } = useSettings();
  if (error) return <ErrorBox error={error} />;
  if (!d) return <Loading what="儀表板" />;

  const cats = Object.entries(d.counts.by_category).sort((a, b) => b[1] - a[1]);
  const byId = new Map((factors ?? []).map((f) => [f.id, f]));
  const marketLabel = (id: string) => (marketKind(id as never) === "TW" ? "示範台股" : "示範美股");

  return (
    <div>
      <PageTitle title="量化研究儀表板" sub="收錄統計為真實的資料庫內容；所有績效數字皆來自合成示範資料。" />

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <Kpi label="已收錄因子" value={fmtInt(d.counts.factors)} sub={`文獻實證 ${d.counts.by_evidence["文獻實證"] ?? 0}｜尚未驗證 ${d.counts.by_evidence["尚未驗證"] ?? 0}`} />
        <Kpi label="驗證等級分布（L0–L4）" value={`L0 × ${d.counts.by_level.TW.L0}`} sub="尚無任何因子通過真實資料驗證">
          <LevelBar kind="TW" counts={d.counts.by_level.TW} />
          <LevelBar kind="US" counts={d.counts.by_level.US} />
        </Kpi>
        <Kpi label="論文" value={fmtInt(d.counts.papers)} sub="已驗 DOI＋摘要，多數未核對全文" />
        <Kpi label="GitHub 專案" value={fmtInt(d.counts.repos)} sub="附授權風險標示" />
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <ChartFrame
          title="因子類別分布"
          subtitle="各類別收錄的因子數"
          evidence="收錄統計"
          isDemo={false}
          height={Math.max(200, cats.length * 36 + 30)}
          filename="category_distribution"
          deps={[d]}
          build={({ p }) => ({
            tooltip: tooltipBase(p, { axisPointer: { type: "shadow" } }),
            grid: gridBase({ top: 8, left: 8 }),
            xAxis: valueAxis(p, { scale: false, minInterval: 1 }),
            yAxis: { type: "category", inverse: true, data: cats.map(([c]) => categoryLabel(c)), axisLabel: { color: p.muted, fontSize: 11 }, axisLine: { lineStyle: { color: p.axis } } },
            series: [
              {
                type: "bar",
                data: cats.map(([, n], i) => ({ value: n, itemStyle: { color: p.series[i % p.series.length] } })),
                label: { show: true, position: "right", color: p.text, fontSize: 11 },
                barMaxWidth: 22,
              },
            ],
          })}
        />

        <Card>
          <div className="mb-2 flex items-center justify-between">
            <h2 className="text-sm font-semibold">研究進度：驗證等級矩陣</h2>
            <EvidenceTag label="收錄統計" />
          </div>
          <p className="mb-2 text-xs text-muted">每格為一個因子，右側兩個徽章分別為台股／美股等級。示範資料不會讓等級升級，因此全部是 L0。</p>
          <div className="grid max-h-80 grid-cols-2 gap-1.5 overflow-y-auto pr-1 sm:grid-cols-3">
            {(factors ?? []).map((f) => (
              <Link key={f.id} href={`/factors/${f.id}/`} className="flex items-center justify-between gap-1 rounded-md border border-line bg-surface2 px-2 py-1 hover:border-accent" title={f.name_zh}>
                <span className="truncate font-mono text-[11px]">{f.id}</span>
                <span className="flex shrink-0 gap-0.5">
                  <LevelBadge level={f.validation_level.TW} />
                  <LevelBadge level={f.validation_level.US} />
                </span>
              </Link>
            ))}
          </div>
        </Card>
      </div>

      <SectionTitle right={<EvidenceTag label="示範資料" />}>績效摘要：Rank IC 均值 Top 10</SectionTitle>
      <div className="relative overflow-hidden rounded-xl border border-demoline bg-surface p-4">
        <div aria-hidden className="pointer-events-none absolute inset-0 flex items-center justify-center overflow-hidden">
          <span className="rotate-[-12deg] select-none whitespace-nowrap text-6xl font-black text-demo opacity-10 sm:text-8xl">示範資料</span>
        </div>
        <div className="relative">
          <DemoNote>
            這整個區塊都是合成示範資料，不是研究結果。正式版只會列出「自行回測」且驗證等級 ≥ L1 的因子；目前沒有任何因子達標。
          </DemoNote>
          <div className="scroll-x mt-3">
            <table className="w-full min-w-[28rem] text-left text-sm">
              <thead className="text-xs text-muted">
                <tr>
                  <th className="py-1 pr-2 font-medium">#</th>
                  <th className="py-1 pr-2 font-medium">因子</th>
                  <th className="py-1 pr-2 font-medium">市場</th>
                  <th className="py-1 pr-2 text-right font-medium">Rank IC</th>
                  <th className="py-1 text-right font-medium">ICIR 年化</th>
                </tr>
              </thead>
              <tbody>
                {d.top_rank_ic.map((r, i) => (
                  <tr key={`${r.factor_id}-${r.market}`} className="border-t border-line">
                    <td className="num py-1.5 pr-2 text-muted">{i + 1}</td>
                    <td className="py-1.5 pr-2">
                      <Link href={`/factors/${r.factor_id}/`} className="text-accent hover:underline">
                        {byId.get(r.factor_id)?.name_zh ?? r.factor_id}
                      </Link>
                      <span className="ml-1 font-mono text-[11px] text-muted">{r.factor_id}</span>
                    </td>
                    <td className="py-1.5 pr-2">
                      <Pill tone="warn">{marketLabel(r.market)}</Pill>
                    </td>
                    <td className="num py-1.5 pr-2 text-right">{fmtNum(r.rank_ic_mean, 4)}</td>
                    <td className="num py-1.5 text-right">{fmtNum(r.rank_icir_ann, 2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {manifest ? (
            <p className="mt-2 text-[11px] text-muted">資料來源：合成示範資料，引擎版本 {manifest.engine_version}，產生時間 {manifest.generated_at}。</p>
          ) : null}
        </div>
      </div>

      <SectionTitle>最近新增</SectionTitle>
      <Card>
        <ul className="divide-y divide-line">
          {d.recent.map((r) => (
            <li key={`${r.type}-${r.id}`} className="flex flex-wrap items-center gap-2 py-2 text-sm">
              <span className="num w-24 shrink-0 text-xs text-muted">{r.date}</span>
              <Pill tone={r.type === "factor" ? "accent" : r.type === "paper" ? "neutral" : "ok"}>
                {r.type === "factor" ? "因子" : r.type === "paper" ? "論文" : "專案"}
              </Pill>
              {r.type === "factor" ? (
                <Link href={`/factors/${r.id}/`} className={cx("min-w-0 flex-1 break-words text-accent hover:underline")}>
                  {r.title}
                </Link>
              ) : (
                <Link href="/sources/" className="min-w-0 flex-1 break-words hover:underline">
                  {r.title}
                </Link>
              )}
            </li>
          ))}
        </ul>
      </Card>
    </div>
  );
}
