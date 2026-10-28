# 資料合約：engine → web（JSON）

Python 引擎（`engine/`）產生 JSON 檔到 `web/public/data/`，Next.js 靜態網站只讀這些檔。**雙方都以本文件為準**；改欄位要先改本文件。
產生指令：`C:\trading-data\quant-factors\venv\Scripts\python.exe -m engine.cli build --demo --out web/public/data`
產生的 JSON **提交進 git**（決定性種子、總量目標 < 15MB），讓 web 不需 Python 就能 `npm run dev`。

通用規則：
- 時間序列一律「欄式」：`{"dates": ["2014-01-31", ...], "x": [..]}`，日期 ISO `YYYY-MM-DD`。
- NaN/Inf 一律輸出 `null`。數值保留 6 位有效數字。
- 報酬一律小數（0.012 = 1.2%）。年化以每年 12 期（月頻）或 252（日頻）。
- 所有結果檔都帶 `is_demo` 與 `evidence_label`；示範資料的 `evidence_label` 固定為 `"示範資料"`。
- 市場 ID：`DEMO_TW`（示範台股，合成資料，台股成本模型）、`DEMO_US`（示範美股，合成資料，美股成本模型）。日後真資料用 `TW`、`US`。

## 檔案清單

```
web/public/data/
├─ manifest.json
├─ factors.json            factors/factors.yaml 的直接轉換（去掉 smoke_test_params）
├─ papers.json             factors/papers.yaml 轉換 ＋ 反查 factor_ids
├─ repos.json              factors/repos.yaml 轉換 ＋ 反查 factor_ids
├─ dashboard.json
├─ stats/{market}/{factor_id}.json
├─ compare/{market}.json
└─ backtests/index.json, backtests/{market}/{preset_id}.json
```

## TypeScript 型別（web 端照抄到 `web/lib/types.ts`）

```ts
type Num = number | null;
type MarketId = "DEMO_TW" | "DEMO_US" | "TW" | "US";

interface CostModel {               // 單邊比例
  buy_commission: number;           // TW 0.001425；US 0
  sell_commission: number;          // TW 0.001425；US 0
  sell_tax: number;                 // TW 0.003；US 0
  slippage: number;                 // 預設 TW 0.0010；US 0.0005
}

interface Manifest {
  generated_at: string; engine_version: string; git_commit: string | null;
  is_demo: boolean;
  markets: { id: MarketId; label: string; is_demo: boolean; n_stocks: number;
             start: string; end: string; oos_start: string; cost_model: CostModel;
             benchmark: string; }[];
  factor_ids: string[];
}

// factors.json：Factor[]，欄位即 factors.yaml 每個因子的全部欄位（見 docs/research/03-factor-database.md）
// 重要欄位：id, name_zh, name_en, category, subcategory, aliases, formula_latex, variables[{symbol,meaning,unit}],
// formula_source_type, direction, unit, required_fields, frequency, params[{name,default,range,description}],
// pit_rules, corporate_action_notes, suggested_markets{TW,US}, paper_ids, repo_refs[{repo,license,...}],
// known_results[{source,market,period,result,location,evidence}], evidence_status, validation_level{TW,US},
// limitations, same_name_different_formula, transaction_cost_note, python

interface Paper {
  id: string;                       // 與 factors.yaml 的 paper_ids 相同，如 "02a:P-A01"
  title: string; authors: string[]; year: number; venue: string;
  doi: string | null; doi_url: string | null; free_url: string | null;
  category: string; market: string; sample_period: string;
  method: string; reported_results: string; code_availability: string;
  tw_us_suitability: string; limitations: string;
  verification_status: string;      // 如「已驗證 DOI + 摘要」
  fulltext_checked: boolean;        // 是否已核對全文（目前多為 false）
  factor_ids: string[];             // 由 engine 反查
}

interface Repo {
  id: string;                       // "owner/name"
  url: string; purpose: string; factor_count: string; formula_explicit: string;
  language: string; backtest: string; pushed_at: string; stars: number | null;
  queried_on: string; license: string; license_risk: "ok" | "copyleft" | "none" | "restricted";
  integration: "高" | "中高" | "中" | "低"; limitations: string; academic_basis: string | null;
  recommended: boolean; factor_ids: string[];
}

interface FactorStats {
  factor_id: string; market: MarketId; is_demo: boolean; evidence_label: string;
  provenance: { data_source: string; universe: string; avg_n_stocks: number;
                start: string; end: string; oos_start: string; rebalance: "M";
                horizon_days: number; n_quantiles: number; cost_model: CostModel;
                n_trials: number; engine_version: string; params: Record<string, number>; };
  summary: {
    ic_mean: Num; ic_std: Num; icir: Num; icir_ann: Num; ic_tstat_nw: Num; ic_win_rate: Num;
    rank_ic_mean: Num; rank_ic_std: Num; rank_icir: Num; rank_icir_ann: Num;
    rank_ic_tstat_nw: Num; rank_ic_win_rate: Num;
    is_rank_ic_mean: Num; oos_rank_ic_mean: Num; oos_rank_ic_tstat_nw: Num;
    coverage_mean: Num; monotonicity: Num;           // 組號與平均報酬的 Spearman
    ls_ann_return_gross: Num; ls_ann_return_net: Num; ls_sharpe_gross: Num; ls_sharpe_net: Num;
    ls_mdd_net: Num; top_excess_ann_net: Num; top_sharpe_net: Num;
    turnover_ann: Num; factor_autocorr_1: Num; dsr: Num;
  };
  ic_series: { dates: string[]; ic: Num[]; rank_ic: Num[]; rank_ic_roll12: Num[] };
  quantiles: { n_q: number; dates: string[];
               cum: Record<string, Num[]>;                // "Q1".."Q5", "LS", "TOP_EXCESS"（皆扣成本後累積淨值，起始 1）
               mean_period_return: Record<string, Num> }; // "Q1".."Q5"
  decay: { horizons: number[]; rank_ic: Num[] };          // [1,5,10,20,60,120]
  distribution: { dates: string[]; p10: Num[]; p25: Num[]; p50: Num[]; p75: Num[]; p90: Num[] };
  subperiods: { label: string; start: string; end: string; rank_ic_mean: Num }[];
  bias_checks: { key: string; status: "pass" | "warn" | "fail"; message: string }[];
}

interface CompareData {
  market: MarketId; is_demo: boolean; factor_ids: string[];
  factor_corr: Num[][];             // 截面 Spearman 相關的時間平均
  ls_return_corr: Num[][];          // 多空月報酬相關
}

interface BacktestIndex { presets: { id: string; market: MarketId; label: string;
  factors: { id: string; weight: number }[]; rebalance: "M" | "Q"; top_q: number; }[] }

interface BacktestResult {
  preset: BacktestIndex["presets"][number]; is_demo: boolean; evidence_label: string;
  provenance: FactorStats["provenance"];
  dates: string[]; nav: Num[]; bench_nav: Num[]; drawdown: Num[];
  annual: { year: number; strat: Num; bench: Num }[];
  monthly: { year: number; month: number; ret: Num }[];
  metrics: { cagr: Num; vol: Num; sharpe: Num; sortino: Num; mdd: Num; calmar: Num;
             win_rate: Num; turnover_ann: Num; n_rebalances: number; n_trades: number;
             cost_drag_ann: Num; excess_cagr: Num; beta: Num; alpha_ann: Num;
             info_ratio: Num; tracking_error: Num; cagr_gross: Num };
}

interface Dashboard {
  is_demo: boolean;
  counts: { factors: number; papers: number; repos: number;
            by_category: Record<string, number>; by_evidence: Record<string, number>;
            by_level: Record<"TW" | "US", Record<"L0"|"L1"|"L2"|"L3"|"L4", number>> };
  top_rank_ic: { factor_id: string; market: MarketId; rank_ic_mean: Num; rank_icir_ann: Num; is_demo: boolean }[];
  recent: { type: "paper" | "repo" | "factor"; id: string; title: string; date: string }[];
}
```

## 慣例補充（引擎 v0.1.0 實作後確認，web 端必讀）
- **因子不一定每個市場都有**：`stats/{market}/` 只存在適用的因子（例如 REV_YOY、REV_MOM_3_12 是台股月營收，DEMO_US 沒有）。web 端以 `compare/{market}.json` 的 `factor_ids` 判斷某市場有哪些因子，缺的顯示「此市場不適用」，不可報錯。
- `provenance.rebalance` 可能是 `"M"` 或 `"Q"`（季調倉回測 preset）。
- **符號**：`ls_mdd_net`、`metrics.mdd` 為**正數**（0.25 = 回撤 25%）；`drawdown` 序列為 **≤ 0**。
- `quantiles.mean_period_return` 是**扣成本前**的各組月平均報酬（衡量排序力）；`quantiles.cum` 是**扣成本後**累積淨值。
- `top_sharpe_net`：TOP_EXCESS 月序列（頂組淨報酬 − 股票池等權基準）的年化 Sharpe，即資訊比率。
- LS 成本：多空兩腿各自計成本，不含借券費。
- 回測 `dates`/`nav` 為**日頻**（約 4000 點）；基準為股票池等權、月調倉、不計成本。
- `provenance.params` 在回測中鍵名為 `"FACTOR_ID.param"`。
- DSR 在 `n_trials = 1` 時等同 PSR（機率型 Sharpe）；介面應顯示 n_trials 讓使用者知道這點。

## 示範資料的規則
- 合成資料只用來展示介面；`validation_level` **永遠不因示範資料而升級**（維持 L0）。
- 任何示範結果的圖表在 web 端都要加「示範資料」浮水印，且 `top_rank_ic` 區塊整區標示示範。
