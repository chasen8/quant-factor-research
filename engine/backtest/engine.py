"""向量化截面回測（04 文件第 5 節）。

流程：調倉日 t（月末，或季末）取已預處理的 z（t 日收盤前資料，PIT）-> 多因子加權 z 合成 S = sum_k w_k z_k
-> 取 S 最高的 1/top_q 等權 -> t+1 收盤成交 -> 持有到下一調倉日 t'+1，期間每日權重隨價格漂移
-> 成交日當天扣成本：(1 + r_day) x (1 - c) - 1，c = 買進 sum(dw>0) x (buy_commission+slippage)
   + 賣出 sum(dw<0) x (sell_commission+sell_tax+slippage)。
基準 = 股票池等權（月調倉、不計成本）。績效以日頻 NAV 計（年化 252），beta/alpha/IR 以月報酬計（年化 12）。
無風險利率預設 0（Sharpe 不扣 rf，須在文件註明）。
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd

from .. import ENGINE_VERSION, metrics as M
from ..data.base import CostModel
from ..evaluate.context import EvalContext
from ..evaluate.factor_eval import provenance
from ..registry import Registry, default_params
from .costs import drift_weights, trade_cost  # noqa: F401

MIN_NAMES = 30


@dataclass
class Preset:
    id: str
    market: str
    label: str
    factors: list  # [(factor_id, weight)]
    rebalance: str = "M"  # "M" | "Q"
    top_q: int = 5

    def as_dict(self) -> dict:
        return {"id": self.id, "market": self.market, "label": self.label,
                "factors": [{"id": f, "weight": float(w)} for f, w in self.factors],
                "rebalance": self.rebalance, "top_q": self.top_q}


def default_presets(market_id: str, names_zh: dict, available: set) -> list[Preset]:
    out = []
    for fid in ["MOM_12_1", "REV_1M", "BM", "GPOA", "VOL_252", "ILLIQ"]:
        if fid in available:
            out.append(Preset(fid, market_id, f"{names_zh[fid]}（頂 20% 等權，月調倉）", [(fid, 1.0)], "M", 5))
    multi = [("BM", 1 / 3), ("GPOA", 1 / 3), ("MOM_12_1", 1 / 3)]
    if all(f in available for f, _ in multi):
        out.append(Preset("VQM_EW", market_id, "價值+品質+動能等權合成（頂 20% 等權，月調倉）", multi, "M", 5))
        out.append(Preset("VQM_EW_Q", market_id, "價值+品質+動能等權合成（頂 20% 等權，季調倉）", multi, "Q", 5))
    return out


def simulate(P: np.ndarray, events: list, cm: CostModel | None):
    """events: [(進場日位置 e, 目標權重 w)]，e 嚴格遞增。進場日 e 的收盤成交。

    回傳 dict：e0、ret_net/ret_gross（e0..T-1 逐日報酬；e0 當天只有成本）、turnover（不含首次建倉）、
    costs、n_trades（含首次建倉）。"""
    T, N = P.shape
    e0 = events[0][0]
    n = T - e0
    ret_g = np.zeros(n)
    ret_n = np.zeros(n)
    turnovers, costs, n_trades = [], [], 0
    old = np.zeros(N)
    zero_cm = CostModel(0.0, 0.0, 0.0, 0.0)
    for j, (e, w) in enumerate(events):
        c, tu, nt = trade_cost(old, w, cm if cm is not None else zero_cm)
        if j == 0:
            ret_n[0] = -c
        else:
            ret_n[e - e0] = (1.0 + ret_g[e - e0]) * (1.0 - c) - 1.0
            turnovers.append(tu)
        costs.append(c)
        n_trades += nt
        e_next = events[j + 1][0] if j + 1 < len(events) else T - 1
        if e_next > e:
            ratio = np.nan_to_num(P[e + 1:e_next + 1] / P[e], nan=1.0)
            V = ratio @ w
            Vprev = np.concatenate([[1.0], V[:-1]])
            g = V / Vprev - 1.0
            ret_g[e + 1 - e0:e_next + 1 - e0] = g
            ret_n[e + 1 - e0:e_next + 1 - e0] = g
            old = w * ratio[-1] / V[-1]
        else:
            old = w
    return {"e0": e0, "ret_net": ret_n, "ret_gross": ret_g, "turnover": turnovers, "costs": costs,
            "n_trades": n_trades}


def build_events(ctx: EvalContext, zs: dict, preset: Preset):
    """依 preset 產生 [(進場位置, 權重)]，並回傳使用到的月度調倉索引 k。"""
    n_rb = ctx.n_rb
    ks = np.arange(n_rb)
    if preset.rebalance == "Q":
        months = ctx.rb_dates.month.values
        ks = ks[np.isin(months, (3, 6, 9, 12))]
    events, used = [], []
    for k in ks:
        S = np.zeros(ctx.N)
        ok = np.ones(ctx.N, dtype=bool)
        for fid, wt in preset.factors:
            zk = zs[fid][k]
            ok &= np.isfinite(zk)
            S += wt * np.nan_to_num(zk, nan=0.0)
        ok &= ctx.elig_rb[k]
        n = int(ok.sum())
        if n < MIN_NAMES:
            continue  # 本期因子不足：不調倉（沿用舊部位）
        n_sel = max(int(math.ceil(n / preset.top_q)), 1)
        idx = np.where(ok)[0]
        top = idx[np.argsort(-S[idx], kind="stable")[:n_sel]]
        w = np.zeros(ctx.N)
        w[top] = 1.0 / n_sel
        events.append((int(ctx.rb[k]) + 1, w))
        used.append(int(k))
    return events, used


def _month_year_returns(nav: pd.Series):
    m_end = nav.groupby([nav.index.year, nav.index.month]).last()
    m_ret = m_end.pct_change()
    m_ret.iloc[0] = m_end.iloc[0] / 1.0 - 1.0
    y_end = nav.groupby(nav.index.year).last()
    y_ret = y_end.pct_change()
    y_ret.iloc[0] = y_end.iloc[0] / 1.0 - 1.0
    return m_ret, y_ret


def _n(x):
    return None if x is None or not np.isfinite(x) else float(x)


def run_backtest(ctx: EvalContext, reg: Registry, zs: dict, preset: Preset) -> dict:
    cm = ctx.md.cost
    events, used = build_events(ctx, zs, preset)
    if not events:
        raise RuntimeError(f"preset {preset.id}: 沒有任何可用的調倉日")
    sim = simulate(ctx.P, events, cm)
    e0 = sim["e0"]
    # 基準：股票池等權，月調倉，不計成本；與策略同一起點
    bevents = []
    for k in range(ctx.n_rb):
        e = int(ctx.rb[k]) + 1
        if e < e0:
            continue
        ok = ctx.elig_rb[k] & np.isfinite(ctx.P[e])
        if ok.sum() == 0:
            continue
        w = ok / ok.sum()
        bevents.append((e, w.astype(float)))
    bsim = simulate(ctx.P, bevents, None)

    dates = ctx.dates[e0:]
    r_n, r_g, r_b = sim["ret_net"], sim["ret_gross"].copy(), bsim["ret_net"]
    # gross：e0 當天無成本，其餘為毛報酬
    nav = pd.Series(np.cumprod(1.0 + r_n), index=dates)

    nav_b = pd.Series(np.cumprod(1.0 + r_b), index=dates)
    dd = M.drawdown_series(nav.to_numpy())

    m_ret, y_ret = _month_year_returns(nav)
    mb_ret, yb_ret = _month_year_returns(nav_b)
    m_df = pd.concat([m_ret, mb_ret], axis=1, keys=["s", "b"]).dropna()
    ex = (m_df["s"] - m_df["b"]).to_numpy()
    if len(m_df) > 2 and m_df["b"].var() > 0:
        beta = float(np.cov(m_df["s"], m_df["b"], ddof=1)[0, 1] / m_df["b"].var(ddof=1))
        alpha = float((m_df["s"].mean() - beta * m_df["b"].mean()) * 12)
    else:
        beta = alpha = math.nan
    te = float(np.std(ex, ddof=1) * math.sqrt(12)) if len(ex) > 2 else math.nan
    ir = float(np.mean(ex) / np.std(ex, ddof=1) * math.sqrt(12)) if len(ex) > 2 and np.std(ex) > 0 else math.nan

    cagr_n = M.cagr(r_n, 252)
    cagr_g = M.cagr(r_g, 252)
    cagr_b = M.cagr(r_b, 252)
    per_year = 12 if preset.rebalance == "M" else 4
    to_ann = float(np.mean(sim["turnover"]) * per_year) if sim["turnover"] else math.nan
    metrics = {
        "cagr": cagr_n, "vol": M.ann_vol(r_n, 252), "sharpe": M.sharpe(r_n, 252), "sortino": M.sortino(r_n, 252),
        "mdd": M.max_drawdown(nav.to_numpy()), "calmar": M.calmar(r_n, 252),
        "win_rate": float((m_ret > 0).mean()), "turnover_ann": to_ann,
        "n_rebalances": len(events), "n_trades": int(sim["n_trades"]),
        "cost_drag_ann": cagr_g - cagr_n, "excess_cagr": cagr_n - cagr_b, "beta": beta, "alpha_ann": alpha,
        "info_ratio": ir, "tracking_error": te, "cagr_gross": cagr_g,
    }
    metrics = {k: (v if k in ("n_rebalances", "n_trades") else _n(v)) for k, v in metrics.items()}

    params = {}
    for fid, _ in preset.factors:
        for k, v in default_params(reg.by_id[fid]).items():
            params[f"{fid}.{k}"] = float(v)
    prov = provenance(ctx, params, 1, preset.rebalance)
    ds = [d.strftime("%Y-%m-%d") for d in dates]
    return {
        "preset": preset.as_dict(), "is_demo": ctx.md.is_demo,
        "evidence_label": "示範資料" if ctx.md.is_demo else "自行回測",
        "provenance": prov, "dates": ds, "nav": nav.tolist(), "bench_nav": nav_b.tolist(),
        "drawdown": dd.tolist(),
        "annual": [{"year": int(y), "strat": _n(a), "bench": _n(yb_ret.get(y))} for y, a in y_ret.items()],
        "monthly": [{"year": int(y), "month": int(m), "ret": _n(v)} for (y, m), v in m_ret.items()],
        "metrics": metrics,
    }
