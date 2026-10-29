"""EXP-003 選股與組合類 C1 馬可維茲 / C2 共整合配對 / C3 PCA 殘差反轉 / C4 神經網路。
規格權威：docs/experiments/EXP-003-ten-models-tw.md（參數不得改）。實作選擇見 docs/experiments/exp003/xs.md。

用法：
  python experiments/exp003_xs.py --segments IS     # 只跑 IS（除錯用，不寫正式輸出）
  python experiments/exp003_xs.py                   # IS + OOS（OOS 只跑一次）
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import warnings
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
for _p in (ROOT, ROOT / "experiments"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import exp001_lowvol as E1  # noqa: E402
from engine import metrics as M  # noqa: E402
from engine.data.base import CostModel  # noqa: E402

OUT_DIR = ROOT / "docs" / "experiments" / "exp003"
CACHE_DIR = Path(r"C:\trading-data\quant-factors\exp003")
SEED = 20261029
N_PERM = 2000
LIMIT = 0.095
SEGMENTS = E1.SEGMENTS
COST_BASE = E1.COST_BASE                                  # 個股：買 0.1425%+0.10%；賣 0.1425%+0.3%+0.10%
COST_ZERO = E1.COST_ZERO
COST_0050 = CostModel(0.001425, 0.001425, 0.001, 0.0005)  # 0050：滑價 0.05%、證交稅 0.1%
SHORT_FEE = 0.0008                                        # 借券費（放空時一次性）
TOPN = 50
CAP = 0.10
LOOK = 252


# =============================================================== 共用：候選股
def top_liquid(R: np.ndarray, AMT: np.ndarray, pool_row: np.ndarray, t: int,
               n: int = TOPN, win: int = LOOK, amt_win: int = 60) -> np.ndarray:
    """股票池中有完整 win 日報酬者，依過去 amt_win 日平均成交金額取前 n 名（欄位索引遞增排序）。只用 <= t 的資料。"""
    if t < win - 1 or t < amt_win - 1:
        return np.zeros(0, dtype=int)
    full = np.isfinite(R[t - win + 1:t + 1]).all(axis=0)
    cand = np.nonzero(pool_row & full)[0]
    if len(cand) == 0:
        return cand
    a = AMT[t - amt_win + 1:t + 1, cand].mean(axis=0)
    order = np.argsort(-a, kind="stable")
    return np.sort(cand[order[:n]])


# =============================================================== C1 馬可維茲
def max_sharpe_long_only(mu: np.ndarray, cov: np.ndarray, cap: float = CAP) -> tuple[np.ndarray, bool]:
    """只做多最大 Sharpe（rf=0）：Σw=1、0<=w<=cap，SLSQP。失敗回 (1/N, False)。"""
    n = len(mu)
    w_eq = np.full(n, 1.0 / n)
    if n * cap < 1.0 - 1e-12 or not (np.isfinite(mu).all() and np.isfinite(cov).all()):
        return w_eq, False
    mua, cva = mu * 252.0, cov * 252.0

    def f(w):
        s = math.sqrt(max(float(w @ cva @ w), 1e-18))
        return -float(mua @ w) / s

    def g(w):
        s = math.sqrt(max(float(w @ cva @ w), 1e-18))
        return -(mua / s - float(mua @ w) * (cva @ w) / s ** 3)

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            res = minimize(f, w_eq, jac=g, method="SLSQP", bounds=[(0.0, cap)] * n,
                           constraints=[{"type": "eq", "fun": lambda w: w.sum() - 1.0, "jac": lambda w: np.ones(n)}],
                           options={"maxiter": 500, "ftol": 1e-10})
    except Exception:
        return w_eq, False
    w = res.x
    ok = bool(res.success and np.isfinite(w).all() and w.min() >= -1e-8 and w.max() <= cap + 1e-8
              and abs(w.sum() - 1.0) < 1e-6)
    if not ok:
        return w_eq, False
    w = np.clip(w, 0.0, cap)
    return w, True


def c1_target_at(R, AMT, pool_row, t) -> dict | None:
    sel = top_liquid(R, AMT, pool_row, t)
    if len(sel) < math.ceil(1.0 / CAP):
        return None
    Rw = R[t - LOOK + 1:t + 1][:, sel]
    w, ok = max_sharpe_long_only(Rw.mean(axis=0), np.cov(Rw, rowvar=False, ddof=1))
    wS = np.zeros(R.shape[1]); wS[sel] = w
    wB = np.zeros(R.shape[1]); wB[sel] = 1.0 / len(sel)
    return {"S": wS, "B": wB, "ok": ok}


# =============================================================== C3 PCA 殘差反轉
def c3_select_at(R, pool_row, t, k_pc: int = 5, resid_days: int = 21, frac: float = 0.2) -> np.ndarray | None:
    """回傳選中股票的欄位索引（累積殘差最低的 frac）。只用 R[t-251..t]。"""
    if t < LOOK - 1:
        return None
    Rw_all = R[t - LOOK + 1:t + 1]
    full = np.isfinite(Rw_all).all(axis=0)
    cand = np.nonzero(pool_row & full)[0]
    if len(cand) < 20:
        return None
    Rw = Rw_all[:, cand]
    sd = Rw.std(axis=0, ddof=1)
    keep = sd > 0
    cand, Rw, sd = cand[keep], Rw[:, keep], sd[keep]
    Z = (Rw - Rw.mean(axis=0)) / sd
    U, S, _ = np.linalg.svd(Z, full_matrices=False)
    F = U[:, :k_pc] * S[:k_pc]
    X = np.column_stack([np.ones(LOOK), F])
    beta, *_ = np.linalg.lstsq(X, Rw, rcond=None)
    resid = Rw - X @ beta
    cum = resid[-resid_days:].sum(axis=0)
    n_sel = max(1, int(math.floor(frac * len(cand))))
    order = np.argsort(cum, kind="stable")[:n_sel]
    return cand[order]


# =============================================================== C4 神經網路
FEAT_NAMES = ["ret5", "ret21", "ret63", "ret126", "mom12_1", "vol252", "maxret21", "logamt20", "close_over_high252"]


def c4_features_at(R, CP, AMT, pool_row, t) -> tuple[np.ndarray, np.ndarray]:
    """回傳 (欄位索引, 特徵矩陣 n×9，無效為 NaN)。只用索引 <= t 的資料。
    價格比用含息報酬指數 CP（原始收盤價未還原除權息）。"""
    idx = np.nonzero(pool_row)[0]
    out = np.full((len(idx), len(FEAT_NAMES)), np.nan)
    if t < LOOK or len(idx) == 0:
        return idx, out
    W = CP[t - LOOK:t + 1][:, idx]                      # t-252 .. t，共 253 列
    out[:, 0] = W[-1] / W[-6] - 1.0
    out[:, 1] = W[-1] / W[-22] - 1.0
    out[:, 2] = W[-1] / W[-64] - 1.0
    out[:, 3] = W[-1] / W[-127] - 1.0
    out[:, 4] = W[-22] / W[0] - 1.0                     # t-21 相對 t-252
    Rw = R[t - LOOK + 1:t + 1][:, idx]
    cnt = np.isfinite(Rw).sum(axis=0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        vol = np.nanstd(Rw, axis=0, ddof=1)
        mx = np.nanmax(R[t - 20:t + 1][:, idx], axis=0)
    out[:, 5] = np.where(cnt >= 200, vol, np.nan)
    c21 = np.isfinite(R[t - 20:t + 1][:, idx]).sum(axis=0)
    out[:, 6] = np.where(c21 >= 10, mx, np.nan)
    out[:, 7] = np.log1p(AMT[t - 19:t + 1][:, idx].mean(axis=0))
    out[:, 8] = W[-1] / W[1:].max(axis=0)
    return idx, out


def rank_norm(X: np.ndarray) -> np.ndarray:
    """逐欄截面排名轉 [-0.5, 0.5]。"""
    n = X.shape[0]
    if n < 2:
        return np.zeros_like(X)
    out = np.empty_like(X)
    for j in range(X.shape[1]):
        out[:, j] = (rankdata(X[:, j]) - 1.0) / (n - 1.0) - 0.5
    return out


def mlp_init(d: int, h: int, rng: np.random.Generator) -> dict:
    return {"W1": rng.normal(0, math.sqrt(2.0 / d), (h, d)), "b1": np.zeros(h),
            "W2": rng.normal(0, math.sqrt(1.0 / h), h), "b2": np.zeros(1)}


def mlp_forward(P: dict, X: np.ndarray):
    z1 = X @ P["W1"].T + P["b1"]
    a = np.maximum(z1, 0.0)
    z2 = a @ P["W2"] + P["b2"][0]
    f = 1.0 / (1.0 + np.exp(-z2))
    return f, a, z1


def mlp_loss_grad(P: dict, X: np.ndarray, y: np.ndarray) -> tuple[float, dict]:
    """f(x)=σ(W2·ReLU(W1 x+b1)+b2)，MSE。"""
    n = len(y)
    f, a, z1 = mlp_forward(P, X)
    loss = float(np.mean((f - y) ** 2))
    dz2 = 2.0 * (f - y) * f * (1.0 - f) / n
    da = dz2[:, None] * P["W2"][None, :]
    dz1 = da * (z1 > 0)
    return loss, {"W1": dz1.T @ X, "b1": dz1.sum(axis=0), "W2": a.T @ dz2, "b2": np.array([dz2.sum()])}


def mlp_train(Xtr, ytr, Xva, yva, seed: int, h: int = 32, lr: float = 1e-3, batch: int = 256,
              max_epochs: int = 200, patience: int = 20) -> tuple[dict, dict]:
    rng = np.random.default_rng(seed)
    P = mlp_init(Xtr.shape[1], h, rng)
    m = {k: np.zeros_like(v) for k, v in P.items()}
    v = {k: np.zeros_like(x) for k, x in P.items()}
    b1, b2, eps = 0.9, 0.999, 1e-8
    step = 0
    best = (math.inf, {k: x.copy() for k, x in P.items()}, 0)
    bad = 0
    n = len(ytr)
    ep_done = 0
    for ep in range(1, max_epochs + 1):
        perm = rng.permutation(n)
        for s in range(0, n, batch):
            bi = perm[s:s + batch]
            _, g = mlp_loss_grad(P, Xtr[bi], ytr[bi])
            step += 1
            for k in P:
                m[k] = b1 * m[k] + (1 - b1) * g[k]
                v[k] = b2 * v[k] + (1 - b2) * g[k] ** 2
                P[k] = P[k] - lr * (m[k] / (1 - b1 ** step)) / (np.sqrt(v[k] / (1 - b2 ** step)) + eps)
        vl = float(np.mean((mlp_forward(P, Xva)[0] - yva) ** 2))
        ep_done = ep
        if vl < best[0] - 1e-12:
            best = (vl, {k: x.copy() for k, x in P.items()}, ep)
            bad = 0
        else:
            bad += 1
            if bad >= patience:
                break
    return best[1], {"seed": seed, "best_val_loss": best[0], "best_epoch": best[2], "epochs_run": ep_done}


def c4_training_samples(ctx: dict, train_end: str = "2016-12-31", val_start: str = "2017-01-01",
                        is_end: str = "2018-12-31") -> dict:
    """建立訓練/驗證樣本。目標報酬實現日（下一個月底訊號日的次日 u'）必須 <= 對應截止日。
    訓練：u' <= train_end；驗證：訊號日 >= val_start 且 u' <= is_end。"""
    dates, R, CP, AMT, pool, rt = ctx["dates"], ctx["R"], ctx["CP"], ctx["AMT"], ctx["pool"], ctx["rebal_t"]
    tr_end = int(dates.searchsorted(pd.Timestamp(train_end), side="right") - 1)
    is_e = int(dates.searchsorted(pd.Timestamp(is_end), side="right") - 1)
    v_s = int(dates.searchsorted(pd.Timestamp(val_start)))
    Xt, yt, Xv, yv = [], [], [], []
    max_real = {"train": -1, "val": -1}
    for k in range(len(rt) - 1):
        t, t2 = int(rt[k]), int(rt[k + 1])
        u, u2 = t + 1, t2 + 1
        if t < LOOK or u2 > is_e or not pool[t].any():
            continue
        is_val = t >= v_s
        if not is_val and u2 > tr_end:
            continue
        idx, F = c4_features_at(R, CP, AMT, pool[t], t)
        ok = np.isfinite(F).all(axis=1)
        if ok.sum() < 20:
            continue
        idx, F = idx[ok], F[ok]
        y = (rankdata(CP[u2, idx] / CP[u, idx] - 1.0) - 1.0) / (len(idx) - 1.0)
        (Xv if is_val else Xt).append(rank_norm(F))
        (yv if is_val else yt).append(y)
        key = "val" if is_val else "train"
        max_real[key] = max(max_real[key], u2)
    return {"Xtr": np.vstack(Xt), "ytr": np.concatenate(yt), "Xva": np.vstack(Xv), "yva": np.concatenate(yv),
            "max_realization_idx": max_real, "tr_end": tr_end, "is_end": is_e}


def c4_fit(ctx: dict, n_seeds: int = 5, base_seed: int = SEED, **kw) -> tuple[list, dict]:
    ds = c4_training_samples(ctx)
    models, info = [], []
    for k in range(n_seeds):
        P, inf = mlp_train(ds["Xtr"], ds["ytr"], ds["Xva"], ds["yva"], base_seed + k, **kw)
        models.append(P)
        info.append(inf)
    return models, {"n_train": int(len(ds["ytr"])), "n_val": int(len(ds["yva"])), "seeds": info,
                    "max_realization_date": {k: (str(ctx["dates"][v].date()) if v >= 0 else None)
                                             for k, v in ds["max_realization_idx"].items()}}


def c4_select_at(models, R, CP, AMT, pool_row, t, frac: float = 0.2) -> np.ndarray | None:
    idx, F = c4_features_at(R, CP, AMT, pool_row, t)
    ok = np.isfinite(F).all(axis=1)
    if ok.sum() < 20:
        return None
    idx, F = idx[ok], F[ok]
    X = rank_norm(F)
    pred = np.mean([mlp_forward(P, X)[0] for P in models], axis=0)
    n_sel = max(1, int(math.floor(frac * len(idx))))
    order = np.argsort(-pred, kind="stable")[:n_sel]
    return idx[order]


# =============================================================== 月頻回測（沿用 EXP-001 成交邏輯）
def simulate_w(ctx: dict, targets: dict, ts: list, seg_s: int, seg_e: int, cm: CostModel) -> dict:
    """與 exp001.simulate 相同的成交/成本/下市/漲跌停邏輯，但目標權重由 targets[t] 提供。"""
    R, CP, last_idx, pool = ctx["R"], ctx["CP"], ctx["last_idx"], ctx["pool"]
    T, N = R.shape
    us = [t + 1 for t in ts]
    out = {"periods": [], "u": us, "idx": [], "nav": []}
    if not ts:
        return out
    w = np.zeros(N)
    nav = 1.0
    out["idx"].append(us[0])
    out["nav"].append(1.0)
    for k, (t, u) in enumerate(zip(ts, us)):
        e = us[k + 1] if k + 1 < len(us) else seg_e
        w[(last_idx < u) & (w > 0)] = 0.0
        pool_idx = np.nonzero(pool[t])[0]
        target = targets[t]
        ru = R[u]
        tradable = np.isfinite(ru) & (np.abs(np.nan_to_num(ru, nan=0.0)) < LIMIT)
        tgt = np.where(tradable, target, w)
        d = tgt - w
        dec = float(-d[d < 0].sum())
        inc = float(d[d > 0].sum())
        cash0 = max(0.0, 1.0 - w.sum())
        avail = cash0 + dec * (1.0 - cm.sell_rate)
        need = inc * (1.0 + cm.buy_rate)
        f = min(1.0, avail / need) if need > 0 else 1.0
        wn = w + np.where(d < 0, d, 0.0) + np.where(d > 0, d * f, 0.0)
        inc_eff = inc * f
        c = dec * cm.sell_rate + inc_eff * cm.buy_rate
        wk = wn / (1.0 - c)
        held = np.nonzero(wk > 1e-15)[0]
        Q = CP[u + 1:e + 1][:, held] / CP[u, held] - 1.0
        navs = nav * (1.0 - c) * (1.0 + Q @ wk[held])
        out["idx"].extend(range(u + 1, e + 1))
        out["nav"].extend(navs.tolist())
        Ph = Q[-1]
        gross = float(Ph @ wk[held])
        nav_new = float(navs[-1])
        in_pool = np.zeros(N, bool)
        in_pool[pool_idx] = True
        Ppool = CP[e, pool_idx] / CP[u, pool_idx] - 1.0
        hm = in_pool[held]
        const = float((wk[held][~hm]) @ Ph[~hm])
        out["periods"].append({
            "t": int(t), "u": int(u), "e": int(e), "cost": c, "turnover": 0.5 * (dec + inc_eff),
            "ret": nav_new / nav - 1.0, "gross": gross, "n_hold": int(len(held)), "n_pool": int(len(pool_idx)),
            "n_sel": int((target > 0).sum()), "pool_idx": pool_idx, "Ppool": Ppool, "wpool": wk[pool_idx],
            "const": const})
        w = np.zeros(N)
        w[held] = wk[held] * (1.0 + Ph) / (1.0 + gross)
        nav = nav_new
    return out


def mcpt_excess(pS: list, pB: list, n_perm: int = N_PERM, seed: int = SEED, ppy: int = 12) -> dict:
    """截面置換：每期把股票池各股的持有期報酬隨機重分配，策略與 B1 套用同一個置換、各自權重與成本不變。
    統計量 = (策略期報酬 − B1 期報酬) 的平均 × 12（年化超額）。p = 置換統計量 >= 實際者的比例。"""
    rng = np.random.default_rng(seed)
    K = len(pS)
    ex = np.empty((n_perm, K))
    actual = np.array([a["ret"] - b["ret"] for a, b in zip(pS, pB)])
    for k, (a, b) in enumerate(zip(pS, pB)):
        m = len(a["Ppool"])
        if m == 0:
            ex[:, k] = actual[k]
            continue
        perm = np.argsort(rng.random((n_perm, m)), axis=1)
        Pm = a["Ppool"][perm]
        gS = Pm @ a["wpool"] + a["const"]
        gB = Pm @ b["wpool"] + b["const"]
        ex[:, k] = (1.0 - a["cost"]) * (1.0 + gS) - (1.0 - b["cost"]) * (1.0 + gB)
    stat = ex.mean(axis=1) * ppy
    act = float(actual.mean() * ppy)
    cnt = int((stat >= act - 1e-12).sum())
    return {"actual": act, "perm": stat, "p": cnt / n_perm, "p_plus1": (cnt + 1) / (n_perm + 1),
            "perm_mean": float(stat.mean()), "perm_p95": float(np.quantile(stat, 0.95)), "n_perm": n_perm, "seed": seed}


def etf_buy_hold(ctx: dict, u0: int, seg_e: int) -> pd.Series:
    r = np.nan_to_num(ctx["R"][u0 + 1:seg_e + 1, ctx["col_0050"]], nan=0.0)
    nav = np.concatenate([[1.0], (1 - COST_0050.buy_rate) * np.cumprod(1 + r)])
    return pd.Series(nav, index=ctx["dates"][u0:seg_e + 1])


def seg_bounds(ctx: dict, name: str) -> tuple[int, int]:
    s, e = SEGMENTS[name]
    d = ctx["dates"]
    return int(d.searchsorted(pd.Timestamp(s))), int(d.searchsorted(pd.Timestamp(e), side="right") - 1)


def eval_monthly(ctx: dict, tS: dict, tB: dict, seg: str, info_keys=()) -> dict:
    """tS/tB: {訊號日t: 目標權重向量}（策略 / B1）。回傳指標、MCPT、判定。"""
    dates, pool, rt = ctx["dates"], ctx["pool"], ctx["rebal_t"]
    seg_s, seg_e = seg_bounds(ctx, seg)
    ts = [int(t) for t in rt if seg_s <= t + 1 < seg_e and t in tS and pool[t].any()]
    sims = {}
    for sc, cm in (("base", COST_BASE), ("gross", COST_ZERO)):
        sims[sc] = (simulate_w(ctx, tS, ts, seg_s, seg_e, cm), simulate_w(ctx, tB, ts, seg_s, seg_e, cm))
    S, B = sims["base"]
    nS, nB = E1.nav_series(S, dates), E1.nav_series(B, dates)
    u0 = S["u"][0]
    prS, prB = E1.hold_period_returns(S), E1.hold_period_returns(B)
    grid = [dates[u] for u in S["u"]] + [dates[seg_e]]
    nE = etf_buy_hold(ctx, u0, seg_e)
    prE = E1.period_returns_on_grid(nE, grid)
    mS, mB, mE = E1.seg_metrics(nS, prS, dates), E1.seg_metrics(nB, prB, dates), E1.seg_metrics(nE, prE, dates)
    for m, S_ in ((mS, S), (mB, B)):
        ps = S_["periods"]
        m["turnover_ann"] = float(sum(x["turnover"] for x in ps[1:]) / m["years"])
        m["avg_holdings"] = float(np.mean([x["n_hold"] for x in ps]))
        m["cost_sum_ann"] = float(sum(x["cost"] for x in ps[1:]) / m["years"])
    gS = E1.seg_metrics(E1.nav_series(sims["gross"][0], dates), E1.hold_period_returns(sims["gross"][0]), dates)
    gB = E1.seg_metrics(E1.nav_series(sims["gross"][1], dates), E1.hold_period_returns(sims["gross"][1]), dates)
    mS["cost_drag"], mB["cost_drag"] = gS["cagr"] - mS["cagr"], gB["cagr"] - mB["cagr"]
    act = prS - prB
    mS["excess_mean_ann"] = float(np.mean(act) * 12)
    mS["ir_vs_b1"] = M.sharpe(act, 12)
    mc = mcpt_excess(S["periods"], B["periods"])
    res = {"segment": seg, "first_trade": str(dates[u0].date()), "last_day": str(dates[seg_e].date()),
           "n_rebalances": len(S["u"]), "strategy": mS, "b1": mB, "b2_0050": mE,
           "mcpt": {k: mc[k] for k in ("actual", "p", "p_plus1", "perm_mean", "perm_p95", "n_perm", "seed")},
           "verdict": {"P1_sharpe_gt_b1": {"pass": bool(mS["sharpe"] > mB["sharpe"]), "strat": mS["sharpe"], "b1": mB["sharpe"]},
                       "P2_raw_p": mc["p"],
                       "P3_sharpe_gt_0050": {"pass": bool(mS["sharpe"] > mE["sharpe"]), "strat": mS["sharpe"], "b2": mE["sharpe"]}},
           "_series": {"nS": nS, "nB": nB, "nE": nE, "perm": mc["perm"]}}
    return res


# =============================================================== C2 共整合配對
def eg_pvalues(L: np.ndarray) -> np.ndarray:
    """L: (252, n) 對數價格。對每個 i<j 做 Engle–Granger（statsmodels.coint：OLS 後對殘差做 ADF，AIC 選落後）。"""
    from statsmodels.tsa.stattools import coint
    n = L.shape[1]
    ia, ib = np.triu_indices(n, 1)
    p = np.ones(len(ia))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for k, (i, j) in enumerate(zip(ia, ib)):
            try:
                pv = coint(L[:, i], L[:, j], trend="c", autolag="aic")[1]
                p[k] = pv if np.isfinite(pv) else 1.0
            except Exception:
                p[k] = 1.0
    return p


def pair_params(Ly: np.ndarray, Lx: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """形成期 OLS：y = a + β x + e。回傳 (β, a, 殘差標準差 ddof=1)。輸入為 (252, P)，只含形成期資料。"""
    xm, ym = Lx.mean(axis=0), Ly.mean(axis=0)
    xc = Lx - xm
    beta = (xc * (Ly - ym)).sum(axis=0) / (xc ** 2).sum(axis=0)
    a = ym - beta * xm
    resid = Ly - a - beta * Lx
    return beta, a, resid.std(axis=0, ddof=1)


def sim_pairs(R, LCP, last_idx, t: int, E: int, ca: np.ndarray, cb: np.ndarray,
              beta: np.ndarray, a: np.ndarray, sd: np.ndarray, cm: CostModel,
              z_in: float = 2.0) -> dict:
    """對 P 個配對同時模擬 t+1..E 的交易。訊號日 d=t..E-1（收盤算 z），隔日 d+1 收盤成交；E 日強制平倉。
    y 腿 = ca，x 腿 = cb；pos=+1：多 y 空 x（z<-2 進場），pos=-1：空 y 多 x（z>2 進場）。每腿 0.5 單位（每對本金 1）。
    回傳 inc (E-t, P) 每日損益（占該對本金）、open (E-t, P)、n_entries、notional（成交金額）。"""
    P = len(ca)
    nd = E - t
    Z = (LCP[t:E][:, ca] - beta * LCP[t:E][:, cb] - a) / sd
    pos = np.zeros(P, dtype=np.int8)
    vy = np.zeros(P)
    vx = np.zeros(P)
    inc = np.zeros((nd, P))
    opn = np.zeros((nd, P), dtype=np.int8)
    n_ent = np.zeros(P, dtype=int)
    notional = np.zeros(P)
    short_rate = cm.sell_rate + (SHORT_FEE if cm.sell_rate > 0 else 0.0)
    for k in range(nd):
        u = t + 1 + k
        dl = (last_idx[ca] < u) | (last_idx[cb] < u)
        gone = dl & (pos != 0)
        pos[gone] = 0
        vy[gone] = 0.0
        vx[gone] = 0.0
        ry = np.nan_to_num(R[u, ca], nan=0.0)
        rx = np.nan_to_num(R[u, cb], nan=0.0)
        pnl = vy * ry + vx * rx
        vy = vy * (1.0 + ry)
        vx = vx * (1.0 + rx)
        z = Z[k]
        with np.errstate(invalid="ignore"):
            trad = (np.isfinite(R[u, ca]) & np.isfinite(R[u, cb]) & (np.abs(ry) < LIMIT) & (np.abs(rx) < LIMIT) & ~dl)
            if u == E:
                ex = pos != 0                                   # 期末強制平倉（不看漲跌停）
                en = np.zeros(P, bool)
            else:
                ex = trad & (((pos == 1) & (z >= 0)) | ((pos == -1) & (z <= 0)))
                en = trad & (pos == 0) & (np.abs(z) > z_in)
        cost = np.zeros(P)
        if ex.any():
            cost[ex] += (np.where(vy[ex] > 0, cm.sell_rate, cm.buy_rate) * np.abs(vy[ex])
                         + np.where(vx[ex] > 0, cm.sell_rate, cm.buy_rate) * np.abs(vx[ex]))
            notional[ex] += np.abs(vy[ex]) + np.abs(vx[ex])
            pos[ex] = 0
            vy[ex] = 0.0
            vx[ex] = 0.0
        if en.any():
            sgn = np.where(z[en] < 0, 1, -1).astype(np.int8)
            pos[en] = sgn
            vy[en] = 0.5 * sgn
            vx[en] = -0.5 * sgn
            cost[en] += 0.5 * cm.buy_rate + 0.5 * short_rate
            notional[en] += 1.0
            n_ent[en] += 1
        inc[k] = pnl - cost
        opn[k] = pos != 0
    return {"inc": inc, "open": opn, "n_entries": n_ent, "notional": notional}


def _eg_worker(L):  # 供 ProcessPool 使用
    return eg_pvalues(L)


def pair_formations(ctx: dict) -> list[int]:
    dates = ctx["dates"]
    rt = ctx["rebal_t"]
    return [int(t) for t in rt if dates[t].month in (6, 12)]


def c2_prepare(ctx: dict, segs: list[str], workers: int = 6) -> dict:
    """對各段需要的形成日算 EG p 值（含快取）與配對參數。回傳 {t: formation dict}。"""
    R, AMT, pool, dates = ctx["R"], ctx["AMT"], ctx["pool"], ctx["dates"]
    LCP = np.log(np.maximum(ctx["CP"], 1e-12))
    forms = pair_formations(ctx)
    need = []
    for sname in segs:
        s0, e0 = seg_bounds(ctx, sname)
        need += [t for t in forms if s0 <= t + 1 <= e0]
    need = sorted(set(need))
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    out, todo = {}, []
    for t in need:
        sel = top_liquid(R, AMT, pool[t], t)
        if len(sel) < 12:
            continue
        L = LCP[t - LOOK + 1:t + 1][:, sel]
        cf = CACHE_DIR / f"eg_{dates[t].date()}.npz"
        pv = None
        if cf.exists():
            z = np.load(cf)
            if np.array_equal(z["sel"], sel):
                pv = z["p"]
        out[t] = {"sel": sel, "L": L, "p": pv}
        if pv is None:
            todo.append(t)
    if todo:
        try:
            with ProcessPoolExecutor(max_workers=workers) as ex:
                for t, pv in zip(todo, ex.map(_eg_worker, [out[t]["L"] for t in todo])):
                    out[t]["p"] = pv
                    np.savez(CACHE_DIR / f"eg_{dates[t].date()}.npz", sel=out[t]["sel"], p=pv)
        except Exception as exc:                      # 行程池偶發中斷：其餘改循序計算（結果相同）
            print("process pool failed, falling back to serial:", repr(exc), flush=True)
            for t in todo:
                if out[t]["p"] is None:
                    out[t]["p"] = eg_pvalues(out[t]["L"])
                    np.savez(CACHE_DIR / f"eg_{dates[t].date()}.npz", sel=out[t]["sel"], p=out[t]["p"])
    for t, d in out.items():
        n = len(d["sel"])
        ia, ib = np.triu_indices(n, 1)
        d["ca"], d["cb"] = d["sel"][ia], d["sel"][ib]
        d["beta"], d["a"], d["sd"] = pair_params(d["L"][:, ia], d["L"][:, ib])
        order = np.argsort(d["p"], kind="stable")
        d["chosen"] = np.array([i for i in order[:10] if d["p"][i] < 0.05], dtype=int)
        del d["L"]
    return out


def eval_c2(ctx: dict, forms: dict, seg: str) -> dict:
    R, LCP_, last_idx, dates = ctx["R"], None, ctx["last_idx"], ctx["dates"]
    LCP = np.log(np.maximum(ctx["CP"], 1e-12))
    seg_s, seg_e = seg_bounds(ctx, seg)
    allf = pair_formations(ctx)
    ts = [t for t in allf if seg_s <= t + 1 <= seg_e and t in forms]
    if not ts:
        raise RuntimeError("no formations")
    wins = []
    for t in ts:
        nxt = [x for x in allf if x > t]
        E = min(t + 126, nxt[0] if nxt else 10 ** 9, seg_e)
        wins.append((t, E))
    base = wins[0][0]                                   # NAV 起點 = 第一個形成日收盤
    D = seg_e - base                                     # 日報酬天數：base+1..seg_e
    sims = {}
    for sc, cm in (("base", COST_BASE), ("gross", COST_ZERO)):
        sims[sc] = [sim_pairs(R, LCP, last_idx, t, E, forms[t]["ca"], forms[t]["cb"], forms[t]["beta"],
                              forms[t]["a"], forms[t]["sd"], cm) for t, E in wins]

    def actual_daily(sc):
        r = np.zeros(D)
        for (t, E), s, f in zip(wins, sims[sc], ts):
            ch = forms[f]["chosen"]
            if len(ch):
                r[t - base:E - base] += s["inc"][:, ch].sum(axis=1) / 10.0
        return r

    rb, rg = actual_daily("base"), actual_daily("gross")
    di = dates[base:seg_e + 1]

    def met(r):
        nav = np.concatenate([[1.0], np.cumprod(1 + r)])
        yrs = (di[-1] - di[0]).days / 365.25
        cg = nav[-1] ** (1 / yrs) - 1 if nav[-1] > 0 else -1.0
        mdd = M.max_drawdown(nav)
        return {"cagr": cg, "ann_vol": M.ann_vol(r, 252), "sharpe": M.sharpe(r, 252), "sortino": M.sortino(r, 252),
                "mdd": mdd, "calmar": cg / mdd if mdd > 0 else math.nan, "years": yrs, "n_days": int(len(r)),
                "total_return": float(nav[-1] - 1)}, nav

    mS, navS = met(rb)
    mG, _ = met(rg)
    r0 = np.nan_to_num(R[base + 1:seg_e + 1, ctx["col_0050"]], nan=0.0).copy()
    r0[0] -= COST_0050.buy_rate
    mE, navE = met(r0)
    n_sel = [len(forms[t]["chosen"]) for t in ts]
    open_pairs = np.zeros(D)
    notion = 0.0
    n_trades = 0
    for (t, E), s, f in zip(wins, sims["base"], ts):
        ch = forms[f]["chosen"]
        if len(ch):
            open_pairs[t - base:E - base] += s["open"][:, ch].sum(axis=1)
            notion += float(s["notional"][ch].sum())
            n_trades += int(s["n_entries"][ch].sum())
    mS["cost_drag"] = mG["cagr"] - mS["cagr"]
    mS["cagr_gross"] = mG["cagr"]
    mS["turnover_ann"] = 0.5 * notion / 10.0 / mS["years"]
    mS["avg_open_pairs"] = float(open_pairs.mean())
    mS["avg_selected_pairs"] = float(np.mean(n_sel))
    mS["n_formations"] = len(ts)
    mS["n_trades_total"] = n_trades
    mS["share_days_with_position"] = float((open_pairs > 0).mean())
    mS["mean_pvalue_selected"] = float(np.mean([forms[t]["p"][forms[t]["chosen"]].mean() for t in ts if len(forms[t]["chosen"])]))
    # ---- MCPT：隨機 10 對（同 50 檔），同交易規則，統計量 = 日報酬 Sharpe
    rng = np.random.default_rng(SEED)
    G = np.zeros((N_PERM, D))
    for (t, E), s, f in zip(wins, sims["base"], ts):
        P = s["inc"].shape[1]
        picks = np.argpartition(rng.random((N_PERM, P)), 10, axis=1)[:, :10]
        part = s["inc"][:, picks].sum(axis=2) / 10.0            # (days, N_PERM)
        G[:, t - base:E - base] += part.T
    mu, sdv = G.mean(axis=1), G.std(axis=1, ddof=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        sh = np.where(sdv > 0, mu / sdv * math.sqrt(252), np.nan)
    ok = sh[np.isfinite(sh)]
    a_sh = M.sharpe(rb, 252)
    cnt = int((ok >= a_sh - 1e-12).sum())
    mc = {"actual": a_sh, "p": cnt / len(ok), "p_plus1": (cnt + 1) / (len(ok) + 1), "perm_mean": float(ok.mean()),
          "perm_p95": float(np.quantile(ok, 0.95)), "n_perm": N_PERM, "seed": SEED}
    return {"segment": seg, "first_trade": str(dates[base + 1].date()), "last_day": str(dates[seg_e].date()),
            "strategy": mS, "b2_0050": mE, "mcpt": mc,
            "verdict": {"P1_sharpe_gt_0": {"pass": bool(mS["sharpe"] > 0), "strat": mS["sharpe"]},
                        "P2_raw_p": mc["p"],
                        "P3_sharpe_gt_0050": {"pass": bool(mS["sharpe"] > mE["sharpe"]), "strat": mS["sharpe"], "b2": mE["sharpe"]}},
            "_series": {"nS": pd.Series(navS, index=di), "nE": pd.Series(navE, index=di), "perm": sh}}


# =============================================================== 資料準備與主流程
def prepare_xs(wide: dict) -> dict:
    ctx = E1.prepare(wide)
    ctx["AMT"] = wide["amount"].fillna(0.0).to_numpy(dtype=float)
    return ctx


def build_targets(ctx: dict, models: list) -> dict:
    R, CP, AMT, pool, rt = ctx["R"], ctx["CP"], ctx["AMT"], ctx["pool"], ctx["rebal_t"]
    N = R.shape[1]
    T1S, T1B, T3S, T4S, TB = {}, {}, {}, {}, {}
    c1_ok = []
    for t in rt:
        t = int(t)
        if t < LOOK or not pool[t].any():
            continue
        c1 = c1_target_at(R, AMT, pool[t], t)
        if c1 is not None:
            T1S[t], T1B[t] = c1["S"], c1["B"]
            c1_ok.append(c1["ok"])
        wB = np.zeros(N)
        wB[pool[t]] = 1.0 / pool[t].sum()
        TB[t] = wB
        for fn, store in ((lambda: c3_select_at(R, pool[t], t), T3S),
                          (lambda: c4_select_at(models, R, CP, AMT, pool[t], t) if models else None, T4S)):
            sel = fn()
            if sel is not None and len(sel):
                w = np.zeros(N)
                w[sel] = 1.0 / len(sel)
                store[t] = w
    return {"C1": (T1S, T1B), "C3": (T3S, TB), "C4": (T4S, TB), "c1_ok": c1_ok}


def make_plots(res: dict, out_dir: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    out_dir.mkdir(parents=True, exist_ok=True)
    names = [("C1", "C1 馬可維茲"), ("C2", "C2 共整合配對"), ("C3", "C3 PCA 殘差反轉"), ("C4", "C4 神經網路")]
    for seg in ("OOS", "IS"):
        if not all(seg in res[k] for k, _ in names):
            continue
        fig, ax = plt.subplots(2, 2, figsize=(12, 8))
        for a, (k, lab) in zip(ax.ravel(), names):
            s = res[k][seg]["_series"]
            a.plot(s["nS"], label=lab, color="#1f77b4")
            if "nB" in s:
                a.plot(s["nB"], label="B1（50 檔 1/N）" if k == "C1" else "B1 股票池等權", color="#ff7f0e")
            a.plot(s["nE"], label="0050 買進持有", color="#7f7f7f")
            a.set_yscale("log"); a.set_title(f"{lab}：{seg} 淨值（扣成本，對數軸）"); a.legend(fontsize=8); a.grid(alpha=.3)
        fig.tight_layout(); fig.savefig(out_dir / f"xs_equity_{seg.lower()}.png", dpi=110); plt.close(fig)
        fig, ax = plt.subplots(2, 2, figsize=(12, 8))
        for a, (k, lab) in zip(ax.ravel(), names):
            mc = res[k][seg]["mcpt"]
            perm = res[k][seg]["_series"]["perm"]
            a.hist(perm[np.isfinite(perm)], bins=50, color="#9ecae1")
            a.axvline(mc["actual"], color="red", label=f"實際 {mc['actual']:.3f}")
            unit = "Sharpe" if k == "C2" else "年化超額報酬 vs B1"
            a.set_title(f"{lab}：{seg} MCPT {unit}（p={mc['p']:.4f}）"); a.legend()
        fig.tight_layout(); fig.savefig(out_dir / f"xs_mcpt_{seg.lower()}.png", dpi=110); plt.close(fig)


def _clean(o):
    if isinstance(o, dict):
        return {k: _clean(v) for k, v in o.items() if k != "_series"}
    return o


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--segments", default="IS,OOS")
    ap.add_argument("--models", default="C1,C2,C3,C4")
    a = ap.parse_args()
    segs = a.segments.split(",")
    mods = a.models.split(",")
    from engine.data import blave_tw as bt
    daily, ev = bt.load_raw()
    wide = bt.build_wide(daily, ev)
    ctx = prepare_xs(wide)
    print("data", ctx["R"].shape, ctx["dates"][0].date(), ctx["dates"][-1].date(), flush=True)
    models, c4info = ([], {})
    if "C4" in mods:
        models, c4info = c4_fit(ctx)
        print("C4", json.dumps(c4info, default=float), flush=True)
    tg = build_targets(ctx, models)
    c1_fail = int(len(tg["c1_ok"]) - sum(tg["c1_ok"]))
    print("C1 solver failures", c1_fail, "of", len(tg["c1_ok"]), flush=True)
    forms = c2_prepare(ctx, segs) if "C2" in mods else {}
    res: dict = {k: {} for k in ("C1", "C2", "C3", "C4")}
    for seg in segs:
        for k in mods:
            if k == "C2":
                res[k][seg] = eval_c2(ctx, forms, seg)
            else:
                res[k][seg] = eval_monthly(ctx, *tg[k], seg)
            r = res[k][seg]
            print(seg, k, "sharpe %.3f cagr %.3f mdd %.3f p %.4f" % (r["strategy"]["sharpe"], r["strategy"]["cagr"],
                  r["strategy"]["mdd"], r["mcpt"]["p"]),
                  "b1 %.3f" % r["b1"]["sharpe"] if "b1" in r else "", "0050 %.3f" % r["b2_0050"]["sharpe"], flush=True)
    meta = {"c1_solver_failures": c1_fail, "c1_rebalances": len(tg["c1_ok"]), "c4": c4info,
            "seed": SEED, "n_perm": N_PERM}
    if set(segs) == {"IS", "OOS"} and set(mods) == {"C1", "C2", "C3", "C4"}:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        make_plots(res, OUT_DIR)
        out = {"meta": meta, **{k: _clean(v) for k, v in res.items()}}
        (OUT_DIR / "xs.json").write_text(json.dumps(out, ensure_ascii=False, indent=2, default=float), encoding="utf-8")
        print("written")
    else:
        print(json.dumps({k: {s: _clean(v) for s, v in d.items()} for k, d in res.items() if d},
                         ensure_ascii=False, indent=1, default=float)[:5000])


if __name__ == "__main__":
    main()
