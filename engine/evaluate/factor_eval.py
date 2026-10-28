"""單一因子評估：IC / Rank IC、分組、LS 與 TOP_EXCESS、衰減、子期間、DSR、偏誤檢查。

流程（月末調倉；訊號 t 日收盤、t+1 收盤成交、前瞻報酬從 t+1 起算，無任何負向 shift）：
  1. registry 算出完整日頻因子矩陣 -> 取調倉日列 -> preprocess（winsorize 1/99 -> z -> x direction）
  2. IC：z 與 h=21 日前瞻報酬的逐截面 Pearson / Spearman；ICIR = mean/std，年化 x sqrt(12)
  3. t 值：Newey-West（Bartlett），lag = ceil((h-1)/21) = 1。原因：IC 是月頻序列（每 ~21 交易日一點），
     相鄰兩點的 21 日前瞻視窗只因月長不一而重疊 0~1 日，換算成「樣本」單位是 1 期；
     04 文件的 lag = h-1 是以日頻重疊樣本為前提，月頻取樣後等價於這個值（見 metrics.nw_lag_for_horizon）。
  4. 分組：5 分位（Q5 = 預期報酬最高，已乘 direction）等權，持有到下一調倉日（t_k+1 -> t_{k+1}+1 收盤）。
     Q1..Q5 的累積淨值、LS、TOP_EXCESS 皆為「扣成本後」；mean_period_return 為扣成本「前」的各組月平均報酬
     （單調性衡量因子排序力，不該混入換手成本）。
  5. LS = Q5 - Q1（空頭腿成本見 backtest.costs，不含借券費）；TOP_EXCESS = Q5 淨報酬 - 股票池等權基準（基準不計成本）。
     top_sharpe_net = TOP_EXCESS 月序列的 Sharpe（年化 sqrt(12)，rf=0）。
  6. DSR 用 LS 扣成本後的月報酬；n_trials 為實際試過的參數組數（MVP 預設參數 = 1）。
"""
from __future__ import annotations

import math
import warnings
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from scipy import stats as sps

from .. import ENGINE_VERSION, metrics as M
from ..backtest.costs import drift_weights, trade_cost
from ..preprocess import preprocess_rows
from ..registry import Registry, default_params
from .bias import bias_checks
from .context import EvalContext
from .ic import rowwise_pearson, rowwise_rank_ic

H_IC = 21
N_Q = 5
HORIZONS = [1, 5, 10, 20, 60, 120]
SUBPERIODS = [("2010-2014", "2010-01-01", "2014-12-31"), ("2015-2019", "2015-01-01", "2019-12-31"),
              ("2020-2021", "2020-01-01", "2021-12-31"), ("2022-2025", "2022-01-01", "2025-12-31")]
EVIDENCE_DEMO = "示範資料"


def assign_groups(z_row: np.ndarray, n_q: int = N_Q) -> np.ndarray:
    """依 z 的平均排名分 n_q 組（0 = 最低、n_q-1 = 最高）；無效值 -1。同值並列落在同組。"""
    g = np.full(z_row.shape, -1, dtype=int)
    m = np.isfinite(z_row)
    n = int(m.sum())
    if n == 0:
        return g
    r = sps.rankdata(z_row[m], method="average")
    g[m] = np.clip(np.floor((r - 0.5) / n * n_q).astype(int), 0, n_q - 1)
    return g


@dataclass
class FactorEval:
    factor_id: str
    stats: dict
    z: np.ndarray                      # n_rb x N（preprocess 後）
    ls_net: np.ndarray                 # 長度 n_rb（第 k 個為 k->k+1 持有期；最後為 NaN）
    ric: np.ndarray
    extras: dict = field(default_factory=dict)


def _num(x):
    return None if x is None or not np.isfinite(x) else float(x)


def provenance(ctx: EvalContext, params: dict, n_trials: int, rebalance: str = "M") -> dict:
    md = ctx.md
    return {
        "data_source": md.data_source, "universe": md.universe_desc,
        "avg_n_stocks": round(ctx.avg_n_stocks, 1),
        "start": ctx.rb_dates[0].strftime("%Y-%m-%d"), "end": ctx.rb_dates[-1].strftime("%Y-%m-%d"),
        "oos_start": ctx.oos_start.strftime("%Y-%m-%d"), "rebalance": rebalance,
        "horizon_days": H_IC, "n_quantiles": N_Q, "cost_model": md.cost.as_dict(),
        "n_trials": n_trials, "engine_version": ENGINE_VERSION, "params": params,
    }


def simulate_groups(ctx: EvalContext, z: np.ndarray, hold: np.ndarray, n_q: int = N_Q):
    """各組等權持有的逐期毛報酬/淨報酬/換手；基準 = 股票池等權。

    回傳 dict：gross[q], net[q], turnover[q]（長度 n_rb 的陣列；k 期 = t_k+1 -> t_{k+1}+1），
    cost_short1（Q1 當空頭腿的成本），bench。第 0..first_valid-1 期為 NaN。"""
    n_rb, N = z.shape
    cm = ctx.md.cost
    gross = np.full((n_q, n_rb), np.nan)
    net = np.full((n_q, n_rb), np.nan)
    turn = np.full((n_q, n_rb), np.nan)
    cost_short1 = np.full(n_rb, np.nan)
    bench = np.full(n_rb, np.nan)
    w_prev = [None] * n_q
    w_prev_short = None
    for k in range(n_rb - 1):
        h = np.nan_to_num(hold[k], nan=0.0)
        ge = ctx.elig_rb[k] & np.isfinite(hold[k])
        if ge.any():
            bench[k] = float(hold[k][ge].mean())
        grp = assign_groups(z[k], n_q)
        have = (grp >= 0).any()
        for q in range(n_q):
            if have:
                mem = grp == q
                w = mem / mem.sum() if mem.any() else np.zeros(N)
            elif w_prev[q] is not None:
                w = w_prev[q]  # 本期無有效因子值：沿用漂移後權重，不交易
            else:
                continue
            old = w_prev[q] if w_prev[q] is not None else np.zeros(N)
            c, to, _ = trade_cost(old, w, cm)
            r = float(w @ h)
            gross[q, k] = r
            net[q, k] = (1.0 + r) * (1.0 - c) - 1.0
            turn[q, k] = to if w_prev[q] is not None else np.nan  # 首次建倉不算換手
            w_prev[q] = drift_weights(w, hold[k])
        if have or w_prev_short is not None:
            mem = (grp == 0) if have else None
            w = (mem / mem.sum() if mem.any() else np.zeros(N)) if have else w_prev_short
            old = w_prev_short if w_prev_short is not None else np.zeros(N)
            c, _, _ = trade_cost(old, w, cm, short=True)
            cost_short1[k] = c
            w_prev_short = drift_weights(w, hold[k])
    return {"gross": gross, "net": net, "turnover": turn, "cost_short1": cost_short1, "bench": bench}


def evaluate_factor(ctx: EvalContext, reg: Registry, fid: str, params: dict | None = None,
                    n_trials: int = 1, raw_full: pd.DataFrame | None = None) -> FactorEval:
    f = reg.by_id[fid]
    dparams = default_params(f)
    use = dict(dparams)
    use.update(params or {})
    if raw_full is None:
        raw_full = reg.compute(fid, ctx.md.data, **use)
    raw = raw_full.to_numpy(dtype=float)[ctx.rb]
    raw[~np.isfinite(raw)] = np.nan
    direction = int(f["direction"])
    z, xw, cov, n_valid = preprocess_rows(raw, ctx.elig_rb, direction)
    n_rb = ctx.n_rb

    # ---- IC ----
    fwd = ctx.fwd_return(H_IC)
    ic = rowwise_pearson(z, fwd)
    ric = rowwise_rank_ic(z, fwd)
    lag = M.nw_lag_for_horizon(H_IC)

    def basic(x):
        v = x[np.isfinite(x)]
        if len(v) < 3:
            return math.nan, math.nan, math.nan, math.nan, math.nan, math.nan
        mu, sd = float(v.mean()), float(v.std(ddof=1))
        icir = mu / sd if sd > 0 else math.nan
        return mu, sd, icir, icir * math.sqrt(12), M.newey_west_tstat(v, lag), float((v > 0).mean())

    ic_mean, ic_std, icir, icir_ann, ic_t, ic_win = basic(ic)
    r_mean, r_std, r_icir, r_icir_ann, r_t, r_win = basic(ric)
    oi = ctx.oos_idx
    is_r = ric[:oi][np.isfinite(ric[:oi])]
    oos_r = ric[oi:][np.isfinite(ric[oi:])]
    is_mean = float(is_r.mean()) if len(is_r) else math.nan
    oos_mean = float(oos_r.mean()) if len(oos_r) else math.nan
    oos_t = M.newey_west_tstat(oos_r, lag) if len(oos_r) >= 3 else math.nan

    # ---- 衰減 ----
    decay = []
    for h in HORIZONS:
        r_h = rowwise_rank_ic(z, ctx.fwd_return(h))
        v = r_h[np.isfinite(r_h)]
        decay.append(_num(v.mean()) if len(v) else None)

    # ---- 因子排名自相關（月，lag 1）----
    ac = rowwise_rank_ic(z[1:], z[:-1])
    ac1 = float(np.nanmean(ac)) if np.isfinite(ac).any() else math.nan

    # ---- 分組 / LS / TOP_EXCESS ----
    hold = ctx.hold_return()
    sim = simulate_groups(ctx, z, hold)
    gross, net, turn = sim["gross"], sim["net"], sim["turnover"]
    ls_gross = gross[N_Q - 1] - gross[0]
    # 淨 LS = 毛 LS - 多頭腿成本 - 空頭腿成本（多頭腿成本由淨/毛還原：net = (1+g)(1-c)-1 -> c = 1-(1+net)/(1+g)）
    c_long = 1.0 - (1.0 + net[N_Q - 1]) / (1.0 + gross[N_Q - 1])
    ls_net = ls_gross - c_long - sim["cost_short1"]
    top_excess = net[N_Q - 1] - sim["bench"]
    valid_k = np.where(np.isfinite(gross[N_Q - 1]))[0]
    k0 = int(valid_k[0]) if len(valid_k) else None

    q_means = [float(np.nanmean(gross[q])) if np.isfinite(gross[q]).any() else math.nan for q in range(N_Q)]
    mono = (float(sps.spearmanr(np.arange(1, N_Q + 1), q_means)[0])
            if np.isfinite(q_means).all() else math.nan)

    def cum_block(series: np.ndarray):
        s = np.nan_to_num(series[k0:n_rb - 1], nan=0.0)
        return np.concatenate([[1.0], np.cumprod(1.0 + s)])

    quantiles = {"n_q": N_Q, "dates": [], "cum": {}, "mean_period_return": {}}
    if k0 is not None:
        qd = [ctx.rb_dates[k0]] + [ctx.rb_dates[k + 1] for k in range(k0, n_rb - 1)]
        quantiles["dates"] = [d.strftime("%Y-%m-%d") for d in qd]
        for q in range(N_Q):
            quantiles["cum"][f"Q{q + 1}"] = cum_block(net[q]).tolist()
            quantiles["mean_period_return"][f"Q{q + 1}"] = _num(q_means[q])
        quantiles["cum"]["LS"] = cum_block(ls_net).tolist()
        quantiles["cum"]["TOP_EXCESS"] = cum_block(top_excess).tolist()

    def fin(x):
        return x[np.isfinite(x)]

    lsg, lsn, tex = fin(ls_gross), fin(ls_net), fin(top_excess)
    sk, ku = M.skew_kurt(lsn)
    sr_pp = M.sharpe(lsn, 1.0) if len(lsn) > 2 else math.nan  # 每期（非年化）
    dsr = M.deflated_sharpe(sr_pp, len(lsn), sk, ku, n_trials) if np.isfinite(sr_pp) else math.nan
    turnover_ann = (float(np.nanmean(turn[N_Q - 1])) * 12.0) if np.isfinite(turn[N_Q - 1]).any() else math.nan

    # ---- 分佈（winsorized 原始因子值，未乘 direction）----
    dist = {"dates": [], "p10": [], "p25": [], "p50": [], "p75": [], "p90": []}
    ok_rows = np.where(np.isfinite(xw).sum(axis=1) > 0)[0]
    if len(ok_rows):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            pq = np.nanpercentile(xw[ok_rows], [10, 25, 50, 75, 90], axis=1)
        dist["dates"] = [ctx.rb_dates[i].strftime("%Y-%m-%d") for i in ok_rows]
        for name, row in zip(("p10", "p25", "p50", "p75", "p90"), pq):
            dist[name] = [_num(v) for v in row]

    # ---- IC 序列（修剪頭尾無效段）----
    vi = np.where(np.isfinite(ric))[0]
    if len(vi):
        sl = slice(int(vi[0]), int(vi[-1]) + 1)
    else:
        sl = slice(0, 0)
    roll12 = pd.Series(ric).rolling(12, min_periods=12).mean().to_numpy()
    ic_series = {
        "dates": [d.strftime("%Y-%m-%d") for d in ctx.rb_dates[sl]],
        "ic": [_num(v) for v in ic[sl]], "rank_ic": [_num(v) for v in ric[sl]],
        "rank_ic_roll12": [_num(v) for v in roll12[sl]],
    }

    # ---- 子期間 ----
    subs = []
    for label, s, e in SUBPERIODS:
        m = (ctx.rb_dates >= pd.Timestamp(s)) & (ctx.rb_dates <= pd.Timestamp(e))
        v = ric[m]
        v = v[np.isfinite(v)]
        subs.append({"label": label, "start": s, "end": e, "rank_ic_mean": _num(v.mean()) if len(v) else None})

    cov_ok = cov[n_valid > 0]
    summary = {
        "ic_mean": ic_mean, "ic_std": ic_std, "icir": icir, "icir_ann": icir_ann, "ic_tstat_nw": ic_t,
        "ic_win_rate": ic_win, "rank_ic_mean": r_mean, "rank_ic_std": r_std, "rank_icir": r_icir,
        "rank_icir_ann": r_icir_ann, "rank_ic_tstat_nw": r_t, "rank_ic_win_rate": r_win,
        "is_rank_ic_mean": is_mean, "oos_rank_ic_mean": oos_mean, "oos_rank_ic_tstat_nw": oos_t,
        "coverage_mean": float(cov_ok.mean()) if len(cov_ok) else math.nan, "monotonicity": mono,
        "ls_ann_return_gross": M.cagr(lsg, 12), "ls_ann_return_net": M.cagr(lsn, 12),
        "ls_sharpe_gross": M.sharpe(lsg, 12), "ls_sharpe_net": M.sharpe(lsn, 12),
        "ls_mdd_net": M.max_drawdown(M.nav_from_returns(lsn)) if len(lsn) else math.nan,
        "top_excess_ann_net": M.cagr(tex, 12), "top_sharpe_net": M.sharpe(tex, 12),
        "turnover_ann": turnover_ann, "factor_autocorr_1": ac1, "dsr": dsr,
    }
    summary = {k: _num(v) for k, v in summary.items()}
    prov = provenance(ctx, {k: float(v) for k, v in use.items()}, n_trials)
    stats = {
        "factor_id": fid, "market": ctx.md.market_id, "is_demo": ctx.md.is_demo,
        "evidence_label": EVIDENCE_DEMO if ctx.md.is_demo else "自行回測",
        "provenance": prov, "summary": summary, "ic_series": ic_series, "quantiles": quantiles,
        "decay": {"horizons": HORIZONS, "rank_ic": decay}, "distribution": dist, "subperiods": subs,
        "bias_checks": bias_checks(ctx, summary, n_trials, len(vi), len(dparams)),
    }
    return FactorEval(fid, stats, z, ls_net, ric, {"top_excess": top_excess})
