// 型別照抄 docs/data-contract.md（engine → web）。改欄位要先改合約文件。
export type Num = number | null;
export type MarketId = "DEMO_TW" | "DEMO_US" | "TW" | "US";
export type MarketKind = "TW" | "US";
export type LevelId = "L0" | "L1" | "L2" | "L3" | "L4";

export interface CostModel {
  buy_commission: number;
  sell_commission: number;
  sell_tax: number;
  slippage: number;
}

export interface MarketInfo {
  id: MarketId;
  label: string;
  is_demo: boolean;
  n_stocks: number;
  start: string;
  end: string;
  oos_start: string;
  cost_model: CostModel;
  benchmark: string;
}

export interface Manifest {
  generated_at: string;
  engine_version: string;
  git_commit: string | null;
  is_demo: boolean;
  markets: MarketInfo[];
  factor_ids: string[];
}

export interface FactorVariable {
  symbol: string;
  meaning: string;
  unit: string;
}
export interface FactorParam {
  name: string;
  default: number | string;
  range: string;
  description: string;
}
export interface RepoRef {
  repo: string;
  license: string;
  usage: string;
}
export interface KnownResult {
  source: string;
  market: string;
  period: string;
  result: string;
  location: string;
  evidence: string;
}

export interface Factor {
  id: string;
  name_zh: string;
  name_en: string;
  category: string;
  subcategory: string;
  aliases: string[];
  formula_latex: string;
  formula_original?: string;
  location_in_source?: string;
  variables: FactorVariable[];
  formula_source_type: string;
  direction: 1 | -1;
  unit: string;
  required_fields: string[];
  frequency: string;
  params: FactorParam[];
  pit_rules: string[];
  corporate_action_notes: string;
  suggested_markets: { TW?: string; US?: string };
  paper_ids: string[];
  paper_ids_note?: string;
  repo_refs: RepoRef[];
  known_results: KnownResult[];
  evidence_status: string;
  validation_level: { TW: LevelId; US: LevelId };
  limitations: string;
  same_name_different_formula: string;
  transaction_cost_note: string;
  python: string;
}

export interface Paper {
  id: string;
  title: string;
  authors: string[];
  year: number;
  venue: string;
  doi: string | null;
  doi_url: string | null;
  free_url: string | null;
  category: string;
  market: string;
  sample_period: string;
  method: string;
  reported_results: string;
  code_availability: string;
  tw_us_suitability: string;
  limitations: string;
  verification_status: string;
  fulltext_checked: boolean;
  factor_ids: string[];
}

export type LicenseRisk = "ok" | "copyleft" | "none" | "restricted";

export interface Repo {
  id: string;
  url: string;
  purpose: string;
  factor_count: string;
  formula_explicit: string;
  language: string;
  backtest: string;
  pushed_at: string;
  stars: number | null;
  queried_on: string;
  license: string;
  license_risk: LicenseRisk;
  integration: "高" | "中高" | "中" | "低";
  limitations: string;
  academic_basis: string | null;
  recommended: boolean;
  factor_ids: string[];
}

export interface Provenance {
  data_source: string;
  universe: string;
  avg_n_stocks: number;
  start: string;
  end: string;
  oos_start: string;
  rebalance: "M" | "Q";
  horizon_days: number;
  n_quantiles: number;
  cost_model: CostModel;
  n_trials: number;
  engine_version: string;
  params: Record<string, number>;
}

export interface FactorSummary {
  ic_mean: Num; ic_std: Num; icir: Num; icir_ann: Num; ic_tstat_nw: Num; ic_win_rate: Num;
  rank_ic_mean: Num; rank_ic_std: Num; rank_icir: Num; rank_icir_ann: Num;
  rank_ic_tstat_nw: Num; rank_ic_win_rate: Num;
  is_rank_ic_mean: Num; oos_rank_ic_mean: Num; oos_rank_ic_tstat_nw: Num;
  coverage_mean: Num; monotonicity: Num;
  ls_ann_return_gross: Num; ls_ann_return_net: Num; ls_sharpe_gross: Num; ls_sharpe_net: Num;
  ls_mdd_net: Num; top_excess_ann_net: Num; top_sharpe_net: Num;
  turnover_ann: Num; factor_autocorr_1: Num; dsr: Num;
}

export interface BiasCheck {
  key: string;
  status: "pass" | "warn" | "fail";
  message: string;
}

export interface FactorStats {
  factor_id: string;
  market: MarketId;
  is_demo: boolean;
  evidence_label: string;
  provenance: Provenance;
  summary: FactorSummary;
  ic_series: { dates: string[]; ic: Num[]; rank_ic: Num[]; rank_ic_roll12: Num[] };
  quantiles: {
    n_q: number;
    dates: string[];
    cum: Record<string, Num[]>;
    mean_period_return: Record<string, Num>;
  };
  decay: { horizons: number[]; rank_ic: Num[] };
  distribution: { dates: string[]; p10: Num[]; p25: Num[]; p50: Num[]; p75: Num[]; p90: Num[] };
  subperiods: { label: string; start: string; end: string; rank_ic_mean: Num }[];
  bias_checks: BiasCheck[];
}

export interface CompareData {
  market: MarketId;
  is_demo: boolean;
  factor_ids: string[];
  factor_corr: Num[][];
  ls_return_corr: Num[][];
}

export interface BacktestPreset {
  id: string;
  market: MarketId;
  label: string;
  factors: { id: string; weight: number }[];
  rebalance: "M" | "Q";
  top_q: number;
}
export interface BacktestIndex {
  presets: BacktestPreset[];
}

export interface BacktestMetrics {
  cagr: Num; vol: Num; sharpe: Num; sortino: Num; mdd: Num; calmar: Num;
  win_rate: Num; turnover_ann: Num; n_rebalances: number; n_trades: number;
  cost_drag_ann: Num; excess_cagr: Num; beta: Num; alpha_ann: Num;
  info_ratio: Num; tracking_error: Num; cagr_gross: Num;
}

export interface BacktestResult {
  preset: BacktestPreset;
  is_demo: boolean;
  evidence_label: string;
  provenance: Provenance;
  dates: string[];
  nav: Num[];
  bench_nav: Num[];
  drawdown: Num[];
  annual: { year: number; strat: Num; bench: Num }[];
  monthly: { year: number; month: number; ret: Num }[];
  metrics: BacktestMetrics;
}

export interface Dashboard {
  is_demo: boolean;
  counts: {
    factors: number;
    papers: number;
    repos: number;
    by_category: Record<string, number>;
    by_evidence: Record<string, number>;
    by_level: Record<MarketKind, Record<LevelId, number>>;
  };
  top_rank_ic: { factor_id: string; market: MarketId; rank_ic_mean: Num; rank_icir_ann: Num; is_demo: boolean }[];
  recent: { type: "paper" | "repo" | "factor"; id: string; title: string; date: string }[];
}
