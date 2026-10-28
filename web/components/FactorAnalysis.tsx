"use client";

import { useSettings } from "./Providers";
import { BirthCertificate, Card, DemoNote, ErrorBox, EvidenceTag, Loading, MetricCard, NotApplicable, Pill, cx } from "./ui";
import { DecayChart, DistributionChart, ICChart, QuantileBars, QuantileChart, SubperiodChart } from "./charts/FactorCharts";
import { useJson } from "@/lib/hooks";
import { paths } from "@/lib/data";
import { fmtInt, fmtNum, fmtPct, fmtSignedPct, sign } from "@/lib/format";
import type { CompareData, Factor, FactorStats, MarketId } from "@/lib/types";

function tone(v: number | null | undefined): "up" | "down" | "none" {
  const s = sign(v);
  return s > 0 ? "up" : s < 0 ? "down" : "none";
}

const STATUS = {
  pass: { icon: "✓", cls: "bg-okbg text-ok", label: "通過" },
  warn: { icon: "!", cls: "bg-warnbg text-warn", label: "警示" },
  fail: { icon: "✕", cls: "bg-badbg text-bad", label: "未通過" },
} as const;

const CHECK_NAME: Record<string, string> = {
  survivorship: "存活者偏誤",
  lookahead: "前視偏誤 / PIT",
  data_snooping: "資料窺探（試驗次數）",
  overfitting: "過度配適（樣本內外）",
  small_sample: "樣本數過小",
  demo_data: "示範資料",
};

export function MarketSwitch({ markets }: { markets: { id: MarketId; label: string }[] }) {
  const { market, setMarket } = useSettings();
  return (
    <div className="flex flex-wrap items-center gap-2 text-sm">
      <span className="text-muted">市場</span>
      {markets.map((m) => (
        <button
          key={m.id}
          onClick={() => setMarket(m.id)}
          aria-pressed={market === m.id}
          className={cx("rounded-lg border px-3 py-1", market === m.id ? "border-accent bg-accentsoft text-accent" : "border-line bg-surface hover:bg-surface2")}
        >
          {m.label}
        </button>
      ))}
    </div>
  );
}

export function FactorAnalysis({ factor }: { factor: Factor }) {
  const { market, manifest } = useSettings();
  const { data: cmp, error: cmpErr } = useJson<CompareData>(paths.compare(market));
  const available = cmp ? cmp.factor_ids.includes(factor.id) : undefined;
  const { data: s, error } = useJson<FactorStats>(available ? paths.stats(market, factor.id) : null);

  return (
    <div className="space-y-4">
      <MarketSwitch markets={manifest?.markets ?? []} />
      {cmpErr ? <ErrorBox error={cmpErr} /> : null}
      {!cmp && !cmpErr ? <Loading what="分析" /> : null}
      {available === false ? (
        <NotApplicable>
          此市場不適用：「{factor.name_zh}」在 {manifest?.markets.find((m) => m.id === market)?.label ?? market} 沒有分析結果
          （例如台股月營收類因子在美股沒有對應資料）。請切換到其他市場。
        </NotApplicable>
      ) : null}
      {error ? <ErrorBox error={error} /> : null}
      {available && !s && !error ? <Loading what="分析" /> : null}
      {s ? <Analysis factor={factor} s={s} /> : null}
    </div>
  );
}

function Analysis({ factor, s }: { factor: Factor; s: FactorStats }) {
  const m = s.summary;
  const pv = s.provenance;
  const ev = s.evidence_label;
  const card = (label: string, value: string, o: { sub?: string; tone?: "up" | "down" | "none"; hint?: string } = {}) => (
    <MetricCard label={label} value={value} sub={o.sub} tone={o.tone} hint={o.hint} provenance={pv} evidence={ev} />
  );
  return (
    <div className="space-y-4">
      {s.is_demo ? <DemoNote /> : null}

      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        {card("Rank IC 均值", fmtNum(m.rank_ic_mean, 4), { sub: `t(NW) ${fmtNum(m.rank_ic_tstat_nw, 2)}　勝率 ${fmtPct(m.rank_ic_win_rate, 0)}`, tone: tone(m.rank_ic_mean) })}
        {card("Rank ICIR（年化）", fmtNum(m.rank_icir_ann, 2), { sub: `月頻 ${fmtNum(m.rank_icir, 3)}` })}
        {card("樣本外 Rank IC", fmtNum(m.oos_rank_ic_mean, 4), { sub: `樣本內 ${fmtNum(m.is_rank_ic_mean, 4)}｜t(NW) ${fmtNum(m.oos_rank_ic_tstat_nw, 2)}`, tone: tone(m.oos_rank_ic_mean) })}
        {card("單調性", fmtNum(m.monotonicity, 2), { sub: "組號 vs 平均報酬 Spearman", hint: "1 代表各組報酬完全依序遞增" })}
        {card("換手（年化）", fmtNum(m.turnover_ann, 2), { sub: `因子自相關(1) ${fmtNum(m.factor_autocorr_1, 2)}` })}
        {card("覆蓋率", fmtPct(m.coverage_mean, 1), { sub: `平均檔數 ${pv.avg_n_stocks.toFixed(0)}` })}
        {card("頂組超額年化（扣成本後）", fmtSignedPct(m.top_excess_ann_net, 2), { sub: `資訊比率 ${fmtNum(m.top_sharpe_net, 2)}`, tone: tone(m.top_excess_ann_net) })}
        {card("多空最大回撤（扣成本後）", fmtPct(m.ls_mdd_net, 1), { sub: "正數 = 回撤幅度" })}
      </div>

      <Card>
        <h3 className="mb-2 text-sm font-semibold">多空組合績效：扣成本前 vs 扣成本後</h3>
        <div className="grid gap-3 sm:grid-cols-2">
          <div className="rounded-lg bg-surface2 p-3">
            <div className="text-xs text-muted">扣成本前（Gross）</div>
            <div className={cx("num text-xl font-semibold", tone(m.ls_ann_return_gross) === "up" ? "text-up" : tone(m.ls_ann_return_gross) === "down" ? "text-down" : "")}>
              {fmtSignedPct(m.ls_ann_return_gross, 2)}
            </div>
            <div className="num text-xs text-muted">年化報酬　Sharpe {fmtNum(m.ls_sharpe_gross, 2)}</div>
          </div>
          <div className="rounded-lg bg-surface2 p-3">
            <div className="text-xs text-muted">扣成本後（Net）</div>
            <div className={cx("num text-xl font-semibold", tone(m.ls_ann_return_net) === "up" ? "text-up" : tone(m.ls_ann_return_net) === "down" ? "text-down" : "")}>
              {fmtSignedPct(m.ls_ann_return_net, 2)}
            </div>
            <div className="num text-xs text-muted">年化報酬　Sharpe {fmtNum(m.ls_sharpe_net, 2)}</div>
          </div>
        </div>
        <p className="mt-2 text-xs text-muted">多空兩腿各自計成本，不含借券費。成本假設見下方出生證明。</p>
        <details className="mt-2">
          <summary className="cursor-pointer text-xs text-accent">出生證明（資料源、股票池、期間、成本、n_trials、引擎版本）</summary>
          <BirthCertificate p={pv} evidence={ev} />
        </details>
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        <ICChart s={s} />
        <QuantileChart s={s} />
        <QuantileBars s={s} />
        <DecayChart s={s} />
        <DistributionChart s={s} />
        <SubperiodChart s={s} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <h3 className="mb-2 flex items-center justify-between text-sm font-semibold">
            偏誤檢查 <EvidenceTag label={ev} />
          </h3>
          <ul className="space-y-2">
            {s.bias_checks.map((b) => {
              const st = STATUS[b.status];
              return (
                <li key={b.key} className="flex gap-2 text-sm">
                  <span className={cx("mt-0.5 inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-xs font-bold", st.cls)} aria-label={st.label}>
                    {st.icon}
                  </span>
                  <div>
                    <div className="font-medium">{CHECK_NAME[b.key] ?? b.key}</div>
                    <div className="text-xs text-muted">{b.message}</div>
                  </div>
                </li>
              );
            })}
          </ul>
        </Card>

        <Card>
          <h3 className="mb-2 text-sm font-semibold">試驗次數與 Deflated Sharpe</h3>
          <div className="grid grid-cols-2 gap-3">
            <div className="rounded-lg bg-surface2 p-3">
              <div className="text-xs text-muted">n_trials（試驗次數 N）</div>
              <div className="num text-xl font-semibold">{fmtInt(pv.n_trials)}</div>
            </div>
            <div className="rounded-lg bg-surface2 p-3">
              <div className="text-xs text-muted">DSR</div>
              <div className="num text-xl font-semibold">{fmtNum(m.dsr, 3)}</div>
            </div>
          </div>
          <p className="mt-2 text-xs text-muted">
            DSR 低於 0.95 不得升級到 L3。{pv.n_trials === 1 ? "n_trials = 1 時 DSR 等同 PSR（機率型 Sharpe），並未反映多重檢定。" : null}
            驗證等級：台股 {factor.validation_level.TW}、美股 {factor.validation_level.US}（示範資料不會讓等級升級）。
          </p>
          <h4 className="mb-1 mt-4 text-sm font-semibold">參數（唯讀）</h4>
          <div className="scroll-x">
            <table className="w-full text-left text-xs">
              <thead className="text-muted">
                <tr>
                  <th className="py-1 pr-3 font-medium">名稱</th>
                  <th className="py-1 pr-3 font-medium">使用值</th>
                  <th className="py-1 pr-3 font-medium">範圍</th>
                  <th className="py-1 font-medium">說明</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(pv.params).map(([k, v]) => {
                  const meta = factor.params.find((x) => x.name === k);
                  return (
                    <tr key={k} className="border-t border-line align-top">
                      <td className="py-1 pr-3 font-mono">{k}</td>
                      <td className="num py-1 pr-3">{fmtNum(v, Number.isInteger(v) ? 0 : 3)}</td>
                      <td className="py-1 pr-3">{meta?.range ?? "—"}</td>
                      <td className="py-1">{meta?.description ?? "—"}</td>
                    </tr>
                  );
                })}
                <tr className="border-t border-line">
                  <td className="py-1 pr-3 font-mono">n_quantiles</td>
                  <td className="num py-1 pr-3">{pv.n_quantiles}</td>
                  <td className="py-1 pr-3">—</td>
                  <td className="py-1">分組數</td>
                </tr>
                <tr className="border-t border-line">
                  <td className="py-1 pr-3 font-mono">rebalance</td>
                  <td className="py-1 pr-3">{pv.rebalance === "M" ? "月" : "季"}</td>
                  <td className="py-1 pr-3">—</td>
                  <td className="py-1">調倉頻率（前瞻 {pv.horizon_days} 交易日）</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p className="mt-2 text-xs text-muted">
            <Pill tone="accent">第二階段</Pill> 自訂參數於第二階段開放；目前只展示預先算好的預設組合。
          </p>
        </Card>
      </div>
    </div>
  );
}
