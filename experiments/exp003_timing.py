"""EXP-003 擇時類 T1 GARCH／T2 HMM／T3 凱利，與描述性檢定 D1 GBM 假設／D2 Copula 尾部。
規格權威：docs/experiments/EXP-003-ten-models-tw.md（參數不得改）。

用法：
  python experiments/exp003_timing.py --segments IS     # 只跑 IS（除錯用，不寫檔）
  python experiments/exp003_timing.py                   # IS + OOS 完整（輸出 timing.json / png）
  python experiments/exp003_timing.py --write-md        # 由 timing.json 產生 timing.md
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import optimize, signal
from scipy import stats as sps

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine import metrics as M  # noqa: E402
from engine.data.base import CostModel  # noqa: E402

OUT_DIR = ROOT / "docs" / "experiments" / "exp003"
SEED = 20261029
N_PERM = 2000
SEGMENTS = {"IS": ("2011-01-01", "2018-12-31"), "OOS": ("2019-01-01", "2026-09-30")}
COST_0050 = CostModel(0.001425, 0.001425, 0.001, 0.0005)   # 買 0.1925%、賣 0.2925%
COST_ZERO = CostModel(0.0, 0.0, 0.0, 0.0)
ID_RE = re.compile(r"^[1-9]\d{3}$")

GARCH_WIN = 1000
GARCH_MIN = 250          # 歷史不足 1000 日時的最少日數（見偏離清單）
TARGET_VOL = 0.15
HMM_START = "2010-01-01"
KELLY_WIN = 252


# ================================================================ 日曆
def week_end_idx(dates: pd.DatetimeIndex) -> np.ndarray:
    iso = dates.isocalendar()
    s = pd.Series(np.arange(len(dates)), index=dates)
    return s.groupby([iso["year"].to_numpy(), iso["week"].to_numpy()]).max().sort_values().to_numpy()


def month_end_idx(dates: pd.DatetimeIndex) -> np.ndarray:
    s = pd.Series(np.arange(len(dates)), index=dates)
    return s.groupby([dates.year, dates.month]).max().sort_values().to_numpy()


# ================================================================ GARCH(1,1) 高斯 MLE（x 為百分比報酬，已去均值）
def _garch_var(params: np.ndarray, x: np.ndarray, s0: float) -> np.ndarray:
    """回傳 sigma2[0..n]，sigma2[t] 為以 x[:t] 預測 x[t] 的條件變異（sigma2[n] = 下一日預測）。"""
    w, a, b = params
    z = w + a * x ** 2                       # z[t] -> sigma2[t+1] 的非遞迴項
    y, _ = signal.lfilter([1.0], [1.0, -b], z, zi=[b * s0])
    return np.concatenate([[s0], y])


def garch_nll(params: np.ndarray, x: np.ndarray) -> float:
    s0 = float(np.var(x))
    s2 = _garch_var(params, x, s0)[:-1]
    if not np.all(np.isfinite(s2)) or np.any(s2 <= 0):
        return 1e18
    return 0.5 * float(np.sum(np.log(s2) + x ** 2 / s2))


def fit_garch(x: np.ndarray) -> np.ndarray:
    """高斯 MLE，ω>0, α,β>=0, α+β<1。回傳 (ω, α, β)。多組起點取最佳。"""
    v = float(np.var(x))
    best, bv = None, np.inf
    for a0, b0 in ((0.05, 0.90), (0.10, 0.80), (0.15, 0.50)):
        x0 = np.array([v * (1 - a0 - b0), a0, b0])
        r = optimize.minimize(
            garch_nll, x0, args=(x,), method="SLSQP",
            bounds=[(1e-8, None), (0.0, 0.999), (0.0, 0.999)],
            constraints=[{"type": "ineq", "fun": lambda p: 0.9995 - p[1] - p[2]}],
            options={"maxiter": 300, "ftol": 1e-10})
        if r.fun < bv and np.all(np.isfinite(r.x)):
            best, bv = r.x, r.fun
    return best


def garch_next_sigma2(params: np.ndarray, x: np.ndarray, s0: float) -> float:
    return float(_garch_var(params, x, s0)[-1])


def signals_garch(lr: np.ndarray, week_idx: np.ndarray, month_idx: np.ndarray,
                  win: int = GARCH_WIN, min_n: int = GARCH_MIN, target: float = TARGET_VOL,
                  start_idx: int = 0) -> np.ndarray:
    """每個週訊號日 t：用 t 以前最近的月底 m 的估計參數（視窗 = lr[m-win+1..m]，不足取 min_n 以上的可得資料），
    以視窗均值去均值，濾波到 t，預測 t+1 日波動 -> e = min(1, target / (σ̂√252))。資料不足回 NaN。"""
    e = np.full(len(week_idx), np.nan)
    cache: dict[int, tuple] = {}
    for k, t in enumerate(week_idx):
        ms = month_idx[month_idx <= t]
        if len(ms) == 0:
            continue
        m = int(ms[-1])
        lo = max(start_idx, m - win + 1)
        if m - lo + 1 < min_n:
            continue
        if m not in cache:
            seg = lr[lo:m + 1]
            mu = float(seg.mean())
            x = (seg - mu) * 100.0
            cache[m] = (fit_garch(x), mu, float(np.var(x)), lo)
        par, mu, s0, lo = cache[m]
        x_all = (lr[lo:t + 1] - mu) * 100.0
        s2 = garch_next_sigma2(par, x_all, s0)
        sig_ann = math.sqrt(s2) / 100.0 * math.sqrt(252)
        e[k] = min(1.0, target / sig_ann)
    return e


# ================================================================ HMM（statsmodels MarkovRegression，只用濾波機率）
def signals_hmm(lr: np.ndarray, week_idx: np.ndarray, month_idx: np.ndarray, start_idx: int,
                min_n: int = 200, return_probs: bool = False):
    """對每個月底 m：用 lr[start_idx..m] 重估 2 狀態（均值、變異數皆切換）高斯 HMM；
    該月之後（到下個月底前）的週訊號日 t，用該組參數對 lr[start_idx..t] 做前向濾波，
    取「均值較高狀態」在 t 的濾波機率 p；p>0.5 -> e=1，否則 0。濾波只餵 <= t 的資料。"""
    from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression
    e = np.full(len(week_idx), np.nan)
    probs = np.full(len(week_idx), np.nan)
    prev = None
    n_fail = 0
    for j, m in enumerate(month_idx):
        if m - start_idx + 1 < min_n:
            continue
        nxt = month_idx[j + 1] if j + 1 < len(month_idx) else np.inf
        ks = np.nonzero((week_idx >= m) & (week_idx < nxt))[0]
        if len(ks) == 0:
            continue
        y = lr[start_idx:m + 1] * 100.0
        par = None
        try:
            mod = MarkovRegression(y, k_regimes=2, switching_variance=True)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                v = float(np.var(y))
                sp = np.array([0.95, 0.05, float(y.mean()) + 0.1 * math.sqrt(v), float(y.mean()) - 0.1 * math.sqrt(v),
                               0.5 * v, 2.0 * v])         # 固定、由資料決定的起點（不用隨機搜尋，結果可重現）
                res = mod.fit(start_params=sp, disp=False)
            par = np.asarray(res.params, float)
            if not np.all(np.isfinite(par)):
                par = None
        except Exception:
            par = None
        if par is None:
            n_fail += 1
            par = prev
            if par is None:
                continue
        prev = par
        hi = int(np.argmax(par[2:4]))                      # const[0], const[1]
        t_last = int(week_idx[ks[-1]])
        mod2 = MarkovRegression(lr[start_idx:t_last + 1] * 100.0, k_regimes=2, switching_variance=True)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            fr = mod2.filter(par)
        fp = np.asarray(fr.filtered_marginal_probabilities)[:, hi]
        for k in ks:
            p = float(fp[week_idx[k] - start_idx])
            probs[k] = p
            e[k] = 1.0 if p > 0.5 else 0.0
    signals_hmm.n_fail = n_fail
    return (e, probs) if return_probs else e


# ================================================================ 凱利
def signals_kelly(lr: np.ndarray, week_idx: np.ndarray, win: int = KELLY_WIN, scale: float = 1.0) -> np.ndarray:
    e = np.full(len(week_idx), np.nan)
    for k, t in enumerate(week_idx):
        if t - win + 1 < 0:
            continue
        seg = lr[t - win + 1:t + 1]
        v = float(seg.var(ddof=1))
        e[k] = float(np.clip(scale * seg.mean() / v, 0.0, 1.0)) if v > 0 else 0.0
    return e


# ================================================================ 持倉 -> 日報酬
def build_path(T: int, week_idx: np.ndarray, e: np.ndarray, seg_s: int, seg_e: int, cm: CostModel) -> dict | None:
    """訊號日 t 的目標 e 於 t+1 收盤成交。h[d] = 第 d 日持有的比例（d 日報酬賺到的曝險）；
    cost[d] = 第 d 日收盤調倉的成本（佔淨值比例）。段內第一個有效訊號之成交日 u0 起算（先前為現金）。"""
    ok = np.isfinite(e) & (week_idx + 1 >= seg_s) & (week_idx + 1 <= seg_e)
    ts, es = week_idx[ok], e[ok]
    if len(ts) == 0:
        return None
    us = ts + 1
    h = np.zeros(T)
    cost = np.zeros(T)
    prev = 0.0
    for k, (u, ek) in enumerate(zip(us, es)):
        d = ek - prev
        cost[u] = d * cm.buy_rate if d > 0 else -d * cm.sell_rate
        nxt = us[k + 1] if k + 1 < len(us) else seg_e
        h[u + 1:nxt + 1] = ek
        prev = ek
    u0 = int(us[0])
    return {"u0": u0, "seg_e": seg_e, "h": h, "cost": cost, "e": es, "us": us}


def daily_net(path: dict, r: np.ndarray) -> np.ndarray:
    a, b = path["u0"], path["seg_e"]
    return path["h"][a:b + 1] * r[a:b + 1] - path["cost"][a:b + 1]


def bh_path(T: int, u0: int, seg_e: int, cm: CostModel) -> dict:
    h = np.zeros(T)
    h[u0 + 1:seg_e + 1] = 1.0
    cost = np.zeros(T)
    cost[u0] = cm.buy_rate
    return {"u0": u0, "seg_e": seg_e, "h": h, "cost": cost, "e": np.array([1.0]), "us": np.array([u0])}


def path_metrics(path: dict, r: np.ndarray, dates: pd.DatetimeIndex, gross_cm: CostModel = COST_ZERO,
                 cm: CostModel = COST_0050) -> dict:
    net = daily_net(path, r)
    nav = np.concatenate([[1.0], np.cumprod(1.0 + net)])
    a = path["u0"]
    yrs = (dates[path["seg_e"]] - dates[a - 1]).days / 365.25
    cagr = nav[-1] ** (1 / yrs) - 1 if nav[-1] > 0 else -1.0
    es = path["e"]
    prev = np.concatenate([[0.0], es[:-1]])
    dE = np.abs(es - prev)
    turn_ann = float(0.5 * dE[1:].sum() / yrs)       # 單邊換手（不含首次建倉），與 EXP-001 同義
    # 毛報酬（成本 0）
    gross = path["h"][a:path["seg_e"] + 1] * r[a:path["seg_e"] + 1]
    gnav = np.cumprod(1.0 + gross)[-1]
    gcagr = gnav ** (1 / yrs) - 1 if gnav > 0 else -1.0
    mdd = M.max_drawdown(nav)
    return {
        "cagr": float(cagr), "ann_vol": M.ann_vol(net, 252), "sharpe": M.sharpe(net, 252),
        "mdd": float(mdd), "calmar": float(cagr / mdd) if mdd > 0 else math.nan,
        "avg_position": float(path["h"][a + 1:path["seg_e"] + 1].mean()),
        "turnover_ann": turn_ann, "cost_drag": float(gcagr - cagr), "cagr_gross": float(gcagr),
        "n_days": int(len(net)), "years": float(yrs), "n_trades": int(len(es)),
        "first_trade": str(dates[a].date()), "last_day": str(dates[path["seg_e"]].date()),
    }


# ================================================================ MCPT
def mcpt(path: dict, r: np.ndarray, n_perm: int = N_PERM, seed: int = SEED) -> dict:
    """持倉序列與成本固定，把該段 0050 日報酬隨機打亂；統計量 = 扣成本日頻年化 Sharpe。"""
    a, b = path["u0"], path["seg_e"]
    h = path["h"][a:b + 1]
    c = path["cost"][a:b + 1]
    seg = r[a:b + 1]
    rng = np.random.default_rng(seed)
    perm = np.argsort(rng.random((n_perm, len(seg))), axis=1)
    net = h[None, :] * seg[perm] - c[None, :]
    mu, sd = net.mean(axis=1), net.std(axis=1, ddof=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        sh = np.where(sd > 0, mu / sd * math.sqrt(252), np.nan)
    actual = M.sharpe(h * seg - c, 252)
    ok = sh[np.isfinite(sh)]
    cnt = int((ok >= actual - 1e-12).sum())
    return {"actual": float(actual), "perm": sh, "p": cnt / len(ok), "p_plus1": (cnt + 1) / (len(ok) + 1),
            "perm_mean": float(ok.mean()), "perm_p95": float(np.quantile(ok, 0.95)), "n_perm": n_perm, "seed": seed}


def seg_bounds(dates: pd.DatetimeIndex, name: str) -> tuple[int, int]:
    s, e = SEGMENTS[name]
    return int(dates.searchsorted(pd.Timestamp(s))), int(dates.searchsorted(pd.Timestamp(e), side="right") - 1)


# ================================================================ 描述性檢定 D1
def kupiec(n_exc: int, n: int, p: float = 0.01) -> float:
    if n_exc == 0:
        lr = -2 * n * math.log(1 - p)
    else:
        ph = n_exc / n
        lr = -2 * ((n - n_exc) * math.log(1 - p) + n_exc * math.log(p)
                   - (n - n_exc) * math.log(1 - ph) - n_exc * math.log(ph))
    return float(1 - sps.chi2.cdf(lr, 1))


def d1_gbm(lr_is: np.ndarray, lr_oos: np.ndarray) -> dict:
    from statsmodels.stats.diagnostic import acorr_ljungbox
    out = {}
    z99 = sps.norm.ppf(0.01)
    mu_i, sd_i = lr_is.mean(), lr_is.std(ddof=1)
    for name, x in (("IS", lr_is), ("OOS", lr_oos)):
        jb = sps.jarque_bera(x)
        lb_r = acorr_ljungbox(x, lags=[10]).iloc[0]
        lb_r2 = acorr_ljungbox(x ** 2, lags=[10]).iloc[0]
        mu, sd = x.mean(), x.std(ddof=1)
        var_own = mu + z99 * sd
        n = len(x)
        exc_own = int((x < var_own).sum())
        exc_is = int((x < mu_i + z99 * sd_i).sum())
        emp1 = float(np.quantile(x, 0.01))
        # 滾動 252 日常態 VaR（只用過去資料）
        roll_mu = pd.Series(x).rolling(252).mean().shift(1).to_numpy()
        roll_sd = pd.Series(x).rolling(252).std().shift(1).to_numpy()
        valid = np.isfinite(roll_sd)
        exc_roll = int((x[valid] < roll_mu[valid] + z99 * roll_sd[valid]).sum())
        out[name] = {
            "n": n, "mean_daily": float(mu), "std_daily": float(sd),
            "skew": float(sps.skew(x)), "excess_kurtosis": float(sps.kurtosis(x)),
            "jb_stat": float(jb.statistic), "jb_p": float(jb.pvalue),
            "lb10_ret_stat": float(lb_r["lb_stat"]), "lb10_ret_p": float(lb_r["lb_pvalue"]),
            "lb10_sq_stat": float(lb_r2["lb_stat"]), "lb10_sq_p": float(lb_r2["lb_pvalue"]),
            "var1_normal_own": float(var_own), "var1_empirical": emp1,
            "expected_exceed": 0.01 * n,
            "exceed_normal_own_fit": exc_own, "kupiec_p_own": kupiec(exc_own, n),
            "exceed_normal_is_params": exc_is, "kupiec_p_is_params": kupiec(exc_is, n),
            "exceed_normal_rolling252": exc_roll, "n_rolling": int(valid.sum()),
            "expected_exceed_rolling": 0.01 * int(valid.sum()),
            "kupiec_p_rolling": kupiec(exc_roll, int(valid.sum())),
        }
    return out


# ================================================================ D2 Copula
def _pseudo(x: np.ndarray) -> np.ndarray:
    return sps.rankdata(x) / (len(x) + 1.0)


def ll_gaussian(rho: float, u: np.ndarray, v: np.ndarray) -> float:
    a, b = sps.norm.ppf(u), sps.norm.ppf(v)
    return float(np.sum(-0.5 * np.log(1 - rho ** 2) - (rho ** 2 * (a ** 2 + b ** 2) - 2 * rho * a * b) / (2 * (1 - rho ** 2))))


def ll_clayton(th: float, u: np.ndarray, v: np.ndarray) -> float:
    A = u ** -th + v ** -th - 1.0
    return float(np.sum(np.log1p(th) - (th + 1) * (np.log(u) + np.log(v)) - (2 + 1 / th) * np.log(A)))


def ll_gumbel(th: float, u: np.ndarray, v: np.ndarray) -> float:
    lu, lv = -np.log(u), -np.log(v)
    A = lu ** th + lv ** th
    C = -(A ** (1 / th))
    return float(np.sum(C - np.log(u) - np.log(v) + (th - 1) * (np.log(lu) + np.log(lv))
                        + (-2 + 2 / th) * np.log(A) + np.log1p((th - 1) * A ** (-1 / th))))


def fit_copulas(u: np.ndarray, v: np.ndarray) -> dict:
    out = {}
    r = optimize.minimize_scalar(lambda x: -ll_gaussian(x, u, v), bounds=(-0.99, 0.99), method="bounded")
    out["gaussian"] = {"param": float(r.x), "ll": -float(r.fun)}
    r = optimize.minimize_scalar(lambda x: -ll_clayton(x, u, v), bounds=(1e-4, 30.0), method="bounded")
    out["clayton"] = {"param": float(r.x), "ll": -float(r.fun)}
    r = optimize.minimize_scalar(lambda x: -ll_gumbel(x, u, v), bounds=(1.0001, 30.0), method="bounded")
    out["gumbel"] = {"param": float(r.x), "ll": -float(r.fun)}
    for k in out:
        out[k]["aic"] = 2 * 1 - 2 * out[k]["ll"]
    return out


def copula_lower(model: str, par: float, q: float = 0.05) -> float:
    """條件機率 P(U<q | V<q) = C(q,q)/q（模型值）。"""
    if model == "gaussian":
        z = sps.norm.ppf(q)
        c = sps.multivariate_normal(mean=[0, 0], cov=[[1, par], [par, 1]]).cdf([z, z])
    elif model == "clayton":
        c = (2 * q ** -par - 1) ** (-1 / par)
    else:
        c = math.exp(-((2 * (-math.log(q)) ** par) ** (1 / par)))
    return float(c / q)


def emp_lower(u: np.ndarray, v: np.ndarray, q: float = 0.05) -> float:
    m = v < q
    return float(((u < q) & m).sum() / max(1, m.sum()))


def d2_copula(wide: dict, dates: pd.DatetimeIndex, is_end_idx: int, is_range: tuple[int, int], oos_range: tuple[int, int],
              top_n: int = 10, q: float = 0.05) -> dict:
    close, amt, ret = wide["close_raw"], wide["amount"], wide["ret"]
    idm = np.array([bool(ID_RE.match(str(c))) for c in close.columns])
    amt20 = amt.fillna(0.0).rolling(20, min_periods=20).mean().iloc[is_end_idx].to_numpy()
    traded = close.notna().iloc[is_end_idx].to_numpy()
    cand = np.nonzero(idm & traded)[0]
    cand = cand[np.argsort(-amt20[cand], kind="stable")][:top_n]
    names = [close.columns[j] for j in cand]
    a, b = is_range
    c, d = oos_range
    R = ret.iloc[:, cand]
    Ris, Roos = R.iloc[a:b + 1].to_numpy(), R.iloc[c:d + 1].to_numpy()
    pairs = []
    for i in range(top_n):
        for j in range(i + 1, top_n):
            ok = np.isfinite(Ris[:, i]) & np.isfinite(Ris[:, j])
            u, v = _pseudo(Ris[ok, i]), _pseudo(Ris[ok, j])
            fit = fit_copulas(u, v)
            model_l = {m: copula_lower(m, fit[m]["param"], q) for m in fit}
            ok2 = np.isfinite(Roos[:, i]) & np.isfinite(Roos[:, j])
            u2, v2 = _pseudo(Roos[ok2, i]), _pseudo(Roos[ok2, j])
            pairs.append({
                "pair": f"{names[i]}-{names[j]}", "n_is": int(ok.sum()), "n_oos": int(ok2.sum()),
                "fit": fit, "best_aic": min(fit, key=lambda m: fit[m]["aic"]),
                "model_lower": model_l, "emp_is": emp_lower(u, v, q), "emp_oos": emp_lower(u2, v2, q),
                "emp_oos_sym": float(0.5 * (emp_lower(u2, v2, q) + emp_lower(v2, u2, q))),
            })
    mae = {}
    for m in ("gaussian", "clayton", "gumbel"):
        mae[m] = float(np.mean([abs(p["model_lower"][m] - p["emp_oos"]) for p in pairs]))
    mae["best_aic_model_per_pair"] = float(np.mean([abs(p["model_lower"][p["best_aic"]] - p["emp_oos"]) for p in pairs]))
    mae["naive_is_empirical"] = float(np.mean([abs(p["emp_is"] - p["emp_oos"]) for p in pairs]))
    aic_sum = {m: float(sum(p["fit"][m]["aic"] for p in pairs)) for m in ("gaussian", "clayton", "gumbel")}
    wins = {m: int(sum(p["best_aic"] == m for p in pairs)) for m in ("gaussian", "clayton", "gumbel")}
    return {
        "stocks": names, "n_pairs": len(pairs), "q": q, "aic_sum": aic_sum, "aic_wins": wins, "mae_vs_oos_emp": mae,
        "mean_model_lower": {m: float(np.mean([p["model_lower"][m] for p in pairs])) for m in ("gaussian", "clayton", "gumbel")},
        "mean_emp_is": float(np.mean([p["emp_is"] for p in pairs])),
        "mean_emp_oos": float(np.mean([p["emp_oos"] for p in pairs])),
        "pairs": pairs,
    }


# ================================================================ 主流程
def build_signals(lr: np.ndarray, dates: pd.DatetimeIndex, first_idx: int) -> dict:
    """所有週訊號（從 first_idx 起）。HMM 起點 = 2010-01 起的資料（整份資料即從 2010-01-04 開始）。"""
    wk = week_end_idx(dates)
    wk = wk[wk >= first_idx]
    mo = month_end_idx(dates)
    hs = int(dates.searchsorted(pd.Timestamp(HMM_START)))
    sig = {"week_idx": wk}
    sig["T1"] = signals_garch(lr, wk, mo)
    sig["T2"], sig["T2_prob"] = signals_hmm(lr, wk, mo, hs, return_probs=True)
    sig["T2_fail"] = int(getattr(signals_hmm, "n_fail", 0))
    sig["T3"] = signals_kelly(lr, wk)
    sig["T3_half"] = signals_kelly(lr, wk, scale=0.5)
    return sig


def run_segment(name: str, dates, r: np.ndarray, sig: dict) -> dict:
    T = len(dates)
    seg_s, seg_e = seg_bounds(dates, name)
    wk = sig["week_idx"]
    res: dict = {"segment": name, "start": SEGMENTS[name][0], "end": SEGMENTS[name][1]}
    paths = {k: build_path(T, wk, sig[k], seg_s, seg_e, COST_0050) for k in ("T1", "T2", "T3", "T3_half")}
    u0 = max(p["u0"] for p in paths.values())
    # 所有策略與 0050 買進持有用同一個起點（理論上相同；不同時取最晚者）
    for k in paths:
        if paths[k]["u0"] != u0:
            paths[k] = build_path(T, wk[wk + 1 >= u0], sig[k][wk + 1 >= u0], seg_s, seg_e, COST_0050)
    bh = bh_path(T, u0, seg_e, COST_0050)
    mb = path_metrics(bh, r, dates)
    res["bh_0050"] = mb
    series = {"bh": pd.Series(np.cumprod(1.0 + daily_net(bh, r)), index=dates[u0:seg_e + 1])}
    for k, p in paths.items():
        m = path_metrics(p, r, dates)
        mc = mcpt(p, r)
        m["excess_sharpe_vs_bh"] = m["sharpe"] - mb["sharpe"]
        res[k] = {"metrics": m,
                  "mcpt": {x: mc[x] for x in ("actual", "p", "p_plus1", "perm_mean", "perm_p95", "n_perm", "seed")},
                  "P1": {"pass": bool(m["sharpe"] > mb["sharpe"]), "strat": m["sharpe"], "bh": mb["sharpe"]}}
        series[k] = pd.Series(np.cumprod(1.0 + daily_net(p, r)), index=dates[u0:seg_e + 1])
        series[k + "_h"] = pd.Series(p["h"][u0:seg_e + 1], index=dates[u0:seg_e + 1])
        series[k + "_perm"] = mc["perm"]
    res["_series"] = series
    return res


# ================================================================ 圖
def make_plots(results: dict, out_dir: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    out_dir.mkdir(parents=True, exist_ok=True)
    lab = {"T1": "T1 GARCH 波動目標", "T2": "T2 HMM 牛市持有", "T3": "T3 凱利", "bh": "0050 買進持有"}
    col = {"T1": "#1f77b4", "T2": "#d62728", "T3": "#2ca02c", "bh": "#7f7f7f"}
    for seg in [s for s in ("OOS", "IS") if s in results]:
        ser = results[seg]["_series"]
        fig, ax = plt.subplots(2, 1, figsize=(10, 7), sharex=True, gridspec_kw={"height_ratios": [2, 1]})
        for k in ("bh", "T1", "T2", "T3"):
            ax[0].plot(ser[k], label=lab[k], color=col[k], lw=1.3)
        ax[0].set_yscale("log"); ax[0].set_title(f"{seg} 淨值（扣成本，起點=1，對數軸）"); ax[0].legend(); ax[0].grid(alpha=.3)
        for k in ("T1", "T2", "T3"):
            ax[1].plot(ser[k + "_h"], label=lab[k], color=col[k], lw=0.9, alpha=.85)
        ax[1].set_ylim(-0.05, 1.05); ax[1].set_title(f"{seg} 持倉比例（0050）"); ax[1].legend(ncol=3, fontsize=8); ax[1].grid(alpha=.3)
        fig.tight_layout(); fig.savefig(out_dir / f"timing_{seg.lower()}.png", dpi=120); plt.close(fig)
    if "OOS" in results:
        fig, ax = plt.subplots(1, 3, figsize=(14, 3.8))
        for a, k in zip(ax, ("T1", "T2", "T3")):
            perm = results["OOS"]["_series"][k + "_perm"]
            mc = results["OOS"][k]["mcpt"]
            a.hist(perm[np.isfinite(perm)], bins=50, color="#9ecae1")
            a.axvline(mc["actual"], color="red", label=f"實際 {mc['actual']:.2f}")
            a.set_title(f"{lab[k]} OOS MCPT（p={mc['p']:.3f}）"); a.legend()
        fig.tight_layout(); fig.savefig(out_dir / "timing_mcpt.png", dpi=120); plt.close(fig)


# ================================================================ 報告（數字取自 timing.json；解讀文字依 2026-10-29 該次結果撰寫）
def _pc(x, d=1):
    return "n/a" if x is None or not np.isfinite(x) else f"{x * 100:.{d}f}%"


def write_md(d: dict, path: Path) -> None:
    L = []
    A = L.append
    A("# EXP-003 擇時類（T1～T3）與描述性檢定（D1、D2）結果\n")
    A("> 規格：`docs/experiments/EXP-003-ten-models-tw.md`（預先登記，未改動）。標的 0050，基準 = 0050 買進持有（同起點、同成本）。"
      "成本：買 0.1925%、賣 0.2925%（含手續費、證交稅 0.1%、滑價 0.05%）。無風險利率 0。"
      "Sharpe／波動用日報酬、年化因子 252。MCPT 2000 次、seed 20261029。")
    A("> **MCPT 原始 p 值未做 Holm 校正**（T1～T3 與 C1～C4 共 7 個，由主對話統一校正）；下表只寫原始 p。\n")
    for seg in ("OOS", "IS"):
        s = d[seg]
        A(f"## {seg}（{s['start']} ~ {s['end']}）\n")
        A("| 指標 | 0050 買進持有 | T1 GARCH | T2 HMM | T3 凱利 | T3 半凱利（只報告） |\n|---|---|---|---|---|---|")
        keys = [("CAGR", "cagr", True), ("年化波動", "ann_vol", True), ("Sharpe", "sharpe", False), ("最大回撤", "mdd", True),
                ("平均持倉比例", "avg_position", True), ("年換手（單邊，不含建倉）", "turnover_ann", False),
                ("成本拖累（CAGR，毛-淨）", "cost_drag", True)]
        cols = [s["bh_0050"]] + [s[k]["metrics"] for k in ("T1", "T2", "T3", "T3_half")]
        for lab, k, pct in keys:
            A(f"| {lab} | " + " | ".join(_pc(c[k], 2) if pct else f"{c[k]:.2f}" for c in cols) + " |")
        A("| 原始 MCPT p（P(置換 Sharpe ≥ 實際)） | - | " + " | ".join(f"{s[k]['mcpt']['p']:.4f}" for k in ("T1", "T2", "T3", "T3_half")) + " |")
        A("| P1：Sharpe > 0050 | - | " + " | ".join("PASS" if s[k]["P1"]["pass"] else "FAIL" for k in ("T1", "T2", "T3", "T3_half")) + " |")
        A(f"\n首次成交 {s['bh_0050']['first_trade']}，結束 {s['bh_0050']['last_day']}；每週調倉一次（共 {s['T1']['metrics']['n_trades']} 次訊號）。\n")
    A("圖：`timing_oos.png`、`timing_is.png`（淨值＋持倉比例）、`timing_mcpt.png`（OOS 置換分布）。原始數字：`timing.json`。\n")
    A("## 合格判定（OOS；P2 待 Holm 校正，此處只給原始 p）\n")
    A("| ID | P1 Sharpe>0050 | 原始 p | 備註 |\n|---|---|---|---|")
    for k, nm in (("T1", "T1 GARCH"), ("T2", "T2 HMM"), ("T3", "T3 凱利")):
        o = d["OOS"][k]
        A(f"| {nm} | **{'PASS' if o['P1']['pass'] else 'FAIL'}**（{o['P1']['strat']:.3f} vs {o['P1']['bh']:.3f}） | {o['mcpt']['p']:.4f} | 原始 p 已 > 0.05，Holm 後只會更大；P1 不過，整體不合格 |")
    A("")
    o, i = d["OOS"], d["IS"]
    A("## 解讀\n")
    A(f"**T1 GARCH 波動目標。** OOS Sharpe {o['T1']['metrics']['sharpe']:.2f}（0050 {o['bh_0050']['sharpe']:.2f}），CAGR {_pc(o['T1']['metrics']['cagr'])}（0050 {_pc(o['bh_0050']['cagr'])}），"
      f"MDD {_pc(o['T1']['metrics']['mdd'])}（{_pc(o['bh_0050']['mdd'])}）。平均持倉 {_pc(o['T1']['metrics']['avg_position'], 0)}，換手低、成本拖累僅 {_pc(o['T1']['metrics']['cost_drag'], 2)}，"
      f"但降波動等於降曝險：在 0050 一路走多的樣本裡，少持有的部分就是少賺的部分，Sharpe 沒有改善；回撤只小幅改善，因為急跌時波動是突然放大，"
      f"GARCH 反應落後（此為推測，未另行驗證）。原始 p = {o['T1']['mcpt']['p']:.3f}，與隨機打亂報酬無法區分。IS 也沒贏 0050（{i['T1']['metrics']['sharpe']:.2f} vs {i['bh_0050']['sharpe']:.2f}）。\n")
    A(f"**T2 HMM 牛熊濾波。** OOS Sharpe {o['T2']['metrics']['sharpe']:.2f}、CAGR {_pc(o['T2']['metrics']['cagr'])}，是三者中最差。"
      f"濾波機率在震盪市頻繁越過 0.5，年換手 {o['T2']['metrics']['turnover_ann']:.1f} 倍（單邊），成本拖累 {_pc(o['T2']['metrics']['cost_drag'], 2)}／年；"
      f"毛報酬 CAGR 也只有 {_pc(o['T2']['metrics']['cagr_gross'])}（0050 {_pc(o['bh_0050']['cagr_gross'])}），即使無成本也輸，退場時點偏晚、回補也偏晚。"
      f"IS 幾乎零報酬（Sharpe {i['T2']['metrics']['sharpe']:.2f}）。原始 p = {o['T2']['mcpt']['p']:.3f}。\n")
    A(f"**T3 凱利。** OOS Sharpe {o['T3']['metrics']['sharpe']:.2f}、CAGR {_pc(o['T3']['metrics']['cagr'])}、MDD {_pc(o['T3']['metrics']['mdd'])}（三者中回撤最小，低於 0050 {_pc(o['bh_0050']['mdd'])}），"
      f"但 Sharpe 仍低於 0050。252 日 μ̂ 轉負時（圖上約 2022 年中至 2023 年中）空手，躲過空頭卻也錯過之後的反彈；μ̂/σ̂² 常 > 1 而被 clip 在 1，多數時間等於滿倉。"
      f"半凱利（只報告）OOS Sharpe {o['T3_half']['metrics']['sharpe']:.2f}、CAGR {_pc(o['T3_half']['metrics']['cagr'])}，在這段上升趨勢樣本中曝險較低的版本表現較差，不代表半凱利一般較差。"
      f"原始 p = {o['T3']['mcpt']['p']:.3f}。\n")
    A("**共同觀察。** 三個模型 OOS 都沒有贏 0050 買進持有，MCPT 原始 p 都遠大於 0.05：把它們的持倉序列套在隨機打亂的報酬上，得到同樣好的 Sharpe 是常態。"
      "OOS 這段 0050 年化約 30%（含台積電行情），任何持倉比例 < 1 的方法都先天吃虧；誠實聲明：這段 OOS 與 EXP-001 相同，並不完全乾淨。\n")
    d1 = d["D1"]
    A("## D1：GBM 假設檢定（0050 日對數報酬）\n")
    A("| 項目 | IS | OOS |\n|---|---|---|")
    A(f"| 樣本日數 | {d1['IS']['n']} | {d1['OOS']['n']} |")
    A(f"| 偏態／超額峰度 | {d1['IS']['skew']:.2f} / {d1['IS']['excess_kurtosis']:.2f} | {d1['OOS']['skew']:.2f} / {d1['OOS']['excess_kurtosis']:.2f} |")
    A(f"| Jarque–Bera p（常態） | {d1['IS']['jb_p']:.2e} | {d1['OOS']['jb_p']:.2e} |")
    A(f"| Ljung–Box(10) 報酬 p（獨立） | {d1['IS']['lb10_ret_p']:.3f} | {d1['OOS']['lb10_ret_p']:.3f} |")
    A(f"| Ljung–Box(10) 報酬平方 p（波動固定） | {d1['IS']['lb10_sq_p']:.2e} | {d1['OOS']['lb10_sq_p']:.2e} |")
    A(f"| 1% VaR 預期破線次數 | {d1['IS']['expected_exceed']:.1f} | {d1['OOS']['expected_exceed']:.1f} |")
    A(f"| 常態 VaR（該段自身 μ、σ）實際破線 / Kupiec p | {d1['IS']['exceed_normal_own_fit']} / {d1['IS']['kupiec_p_own']:.4f} | {d1['OOS']['exceed_normal_own_fit']} / {d1['OOS']['kupiec_p_own']:.4f} |")
    A(f"| 常態 VaR（IS 參數用於該段）實際破線 / Kupiec p | {d1['IS']['exceed_normal_is_params']} / {d1['IS']['kupiec_p_is_params']:.4f} | {d1['OOS']['exceed_normal_is_params']} / {d1['OOS']['kupiec_p_is_params']:.2e} |")
    A(f"| 常態 VaR（滾動 252 日，只用過去）實際破線 / 預期 / Kupiec p | {d1['IS']['exceed_normal_rolling252']} / {d1['IS']['expected_exceed_rolling']:.1f} / {d1['IS']['kupiec_p_rolling']:.4f} | {d1['OOS']['exceed_normal_rolling252']} / {d1['OOS']['expected_exceed_rolling']:.1f} / {d1['OOS']['kupiec_p_rolling']:.2e} |")
    A(f"| 1% 分位：常態 vs 經驗 | {_pc(d1['IS']['var1_normal_own'], 2)} vs {_pc(d1['IS']['var1_empirical'], 2)} | {_pc(d1['OOS']['var1_normal_own'], 2)} vs {_pc(d1['OOS']['var1_empirical'], 2)} |")
    A("\n**結論：** GBM 的「報酬常態」被拒絕（兩段皆厚尾、JB p≈0），「波動固定」被拒絕（報酬平方有極強自相關，即波動聚集）；"
      "「報酬彼此獨立」在 5% 水準下未被拒絕（Ljung–Box(10) p：IS 0.40、OOS 0.08，OOS 偏弱但未達顯著）。"
      "因為厚尾，常態 VaR 在 1% 水準的破線次數是預期的 1.6～3.5 倍，Kupiec 檢定全部拒絕。\n")
    d2 = d["D2"]
    A("## D2：Copula 下尾相依\n")
    A(f"IS 期末（2018-12-28）20 日平均成交金額前 10 名普通股：{'、'.join(d2['stocks'])}；45 個配對。")
    A("\n| 項目 | Gaussian | Clayton | Gumbel |\n|---|---|---|---|")
    A(f"| AIC 加總（越小越好） | {d2['aic_sum']['gaussian']:.0f} | {d2['aic_sum']['clayton']:.0f} | {d2['aic_sum']['gumbel']:.0f} |")
    A(f"| 各配對 AIC 最佳次數 | {d2['aic_wins']['gaussian']} | {d2['aic_wins']['clayton']} | {d2['aic_wins']['gumbel']} |")
    A(f"| 模型推算 P(U<5% 且 V<5%)/5% 平均 | {d2['mean_model_lower']['gaussian']:.3f} | {d2['mean_model_lower']['clayton']:.3f} | {d2['mean_model_lower']['gumbel']:.3f} |")
    mae = d2["mae_vs_oos_emp"]
    A(f"| 對 OOS 經驗值的平均絕對誤差（MAE） | {mae['gaussian']:.3f} | {mae['clayton']:.3f} | {mae['gumbel']:.3f} |")
    A(f"\n經驗值：IS 平均 {d2['mean_emp_is']:.3f}、OOS 平均 {d2['mean_emp_oos']:.3f}（獨立時應為 0.05）。依各配對 AIC 最佳模型推算的 MAE {mae['best_aic_model_per_pair']:.3f}；"
      f"「直接拿 IS 經驗值當預測」的 MAE {mae['naive_is_empirical']:.3f}。")
    A("\n**結論：** AIC 明顯偏好 Clayton（45 對中 35 對最佳、加總最小），Gumbel 最差，符合「下尾相依強於上尾」。"
      "三個模型的 5% 下尾值都低於 OOS 實際值（OOS 的同步崩盤比 IS 更強），Clayton MAE 最小（0.082）但只略優於直接沿用 IS 經驗值（0.097）；"
      "Gaussian 與 Gumbel 嚴重低估（理論下尾相依為 0）。結論：Clayton 的形狀較合適，但「樣本外預測崩盤同步程度」只有有限改善，且仍低估 OOS。\n")
    A("## 偏離與實作選擇\n")
    A("""1. **GARCH 歷史不足 1000 日**：資料自 2010-01-04 起，2011～2013 年可用歷史不足 1000 個交易日。規格要求「過去 1000 日」，本實作取 min(1000, 可得日數)，至少 250 日才產生訊號（2011-01 起才有）；2014-01 之後皆為完整 1000 日。OOS 全為完整視窗。
2. **GARCH 細節**：以視窗樣本均值去均值（均值固定為該視窗均值），報酬以百分比單位估計；自寫高斯 MLE（SLSQP、3 組起點取最佳，約束 ω≥1e-8、α,β≥0、α+β≤0.9995）；初始條件變異 = 視窗樣本變異。每週訊號日用最近月底估的參數，對「視窗起點到 t」的資料遞迴濾波，預測 t+1 日變異。測試含已知參數回收，以及遞迴與樸素迴圈一致。
3. **HMM**：statsmodels `MarkovRegression(k_regimes=2, switching_variance=True)`（均值與變異數皆隨狀態切換的 2 狀態高斯模型，等價於高斯 HMM；statsmodels 以 EM＋準牛頓最佳化求 MLE，並非單純 Baum–Welch）。使用 2010-01 起至月底的全部日對數報酬（以 % 為單位），**每個月底獨立重估，起點為固定的資料決定值**（不用隨機搜尋；早期曾用上月參數暖啟動，發現結果有 1e-5 級不可重現，改掉。此修改發生在任何 IS／OOS 績效之前）。每週訊號日 t 用該月參數對「2010-01 到 t」的資料做前向濾波（只用濾波機率），「均值較高狀態」機率 > 0.5 → e=1。無擬合失敗。第一個月底需至少 200 個觀測。
4. **凱利**：μ̂、σ̂² 為過去 252 日對數報酬的日均值與日樣本變異數（ddof=1）；e=clip(μ̂/σ̂², 0, 1)。半凱利 = 0.5·μ̂/σ̂²，只報告。
5. **週訊號日**：每個 ISO 週最後一個交易日收盤算，下一交易日收盤成交（t+1），從 t+2 日起賺報酬。IS 首次成交 2011-01-10；OOS 2019-01-02。各段獨立從現金起算並付首次買進成本；0050 買進持有同起點、同付一次買進成本。
6. **曝險與成本近似**：持倉期間視為固定曝險比例 e（等同每日再平衡、不計漂移再平衡成本），成本只在訊號調倉日依 |Δe| 計（增加按買進成本率、減少按賣出成本率）。對連續持倉的 T1、T3 略有簡化；T2（0 或 1）不受影響。
7. **指標**：Sharpe／波動用日淨報酬×√252；CAGR、MDD 用日淨值；換手 = Σ|Δe|÷2÷年數（單邊，與 EXP-001 同義，不含首次建倉）；成本拖累 = 零成本 CAGR − 淨 CAGR；平均持倉 = 段內每日持倉比例平均。
8. **MCPT**：固定持倉序列與每日成本，對該段（含起點日）0050 日報酬做 2000 次隨機排列，統計量為扣成本日頻年化 Sharpe；p = 置換 Sharpe ≥ 實際的比例（JSON 另附 (k+1)/(n+1)）。IS、OOS 各自獨立做；T3 半凱利也做了但只報告。
9. **D1**：用對數報酬。破線檢定三種：常態以該段自身 μ、σ（樣本內）、以 IS 的 μ、σ（用於 OOS 為樣本外）、以滾動 252 日只用過去的參數；皆附 Kupiec 無條件覆蓋檢定。
10. **D2**：成交金額 = 20 日平均（停牌日計 0，與 EXP-001 一致），限 4 位數代號普通股（排除 ETF）、IS 期末有成交者；此 10 檔中有數檔在 IS 後段才上市（配對 IS 最少 724 日），各配對取兩檔皆有報酬的重疊日。虛擬觀測值 = 秩/(n+1)（同值取平均秩）。三種 copula 皆自寫對數似然、單參數（AIC = 2 − 2ℓ）、純量有界最佳化。5% 下尾係數 = 條件機率 C(q,q)/q：Gaussian 用二元常態 CDF，Clayton (2q^−θ−1)^(−1/θ)/q，Gumbel exp(−(2(−ln q)^θ)^(1/θ))/q。OOS 經驗值用 OOS 自身的秩，U<q 且 V<q 的比例除以 V<q 的比例（順序依代號排序；對稱化版本見 JSON `emp_oos_sym`）。
11. 缺少 U+2212 字型的警告來自對數軸刻度的 mathtext，圖面不受影響（`axes.unicode_minus=False` 已設）。""")
    A("\n## 已知限制\n")
    A("- 0050 單一標的、單一路徑；OOS 與 EXP-001 重疊且期間 0050 年化約 30%，擇時類先天處於劣勢，不應外推到其他標的或期間。\n"
      "- 週頻調倉；無融資、無稅務細節；0050 含息報酬由資料還原。")
    path.write_text("\n".join(L) + "\n", encoding="utf-8")


# ================================================================ 載入資料
def load_0050() -> tuple[dict, pd.DatetimeIndex, np.ndarray]:
    from engine.data import blave_tw as bt
    daily, ev = bt.load_raw()
    wide = bt.build_wide(daily, ev)
    dates = wide["ret"].index
    r = wide["ret"]["0050"].fillna(0.0).to_numpy(dtype=float)
    return wide, dates, r


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--segments", default="IS,OOS")
    ap.add_argument("--no-d2", action="store_true")
    ap.add_argument("--write-md", action="store_true", help="由 timing.json 產生 timing.md（不重跑）")
    a = ap.parse_args()
    if a.write_md:
        write_md(json.loads((OUT_DIR / "timing.json").read_text(encoding="utf-8")), OUT_DIR / "timing.md")
        return
    wide, dates, r = load_0050()
    lr = np.log1p(r)
    first_idx = int(dates.searchsorted(pd.Timestamp(SEGMENTS["IS"][0]))) - 10
    sig = build_signals(lr, dates, first_idx)
    print("signals built; HMM fit failures:", sig["T2_fail"])
    results = {}
    for s in a.segments.split(","):
        results[s] = run_segment(s, dates, r, sig)
        for k in ("T1", "T2", "T3"):
            x = results[s][k]
            print(s, k, "sharpe %.3f bh %.3f cagr %.3f mdd %.3f p %.4f" % (
                x["metrics"]["sharpe"], results[s]["bh_0050"]["sharpe"], x["metrics"]["cagr"], x["metrics"]["mdd"], x["mcpt"]["p"]))
    if set(results) != {"IS", "OOS"}:
        return
    iS, iE = seg_bounds(dates, "IS")
    oS, oE = seg_bounds(dates, "OOS")
    d1 = d1_gbm(lr[iS:iE + 1], lr[oS:oE + 1])
    d2 = None if a.no_d2 else d2_copula(wide, dates, iE, (iS, iE), (oS, oE))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    make_plots(results, OUT_DIR)
    clean = {s: {k: v for k, v in rr.items() if k != "_series"} for s, rr in results.items()}
    clean["D1"] = d1
    clean["D2"] = d2
    clean["meta"] = {"seed": SEED, "n_perm": N_PERM, "hmm_fit_failures": sig["T2_fail"],
                     "cost_0050": {"buy": COST_0050.buy_rate, "sell": COST_0050.sell_rate}}
    (OUT_DIR / "timing.json").write_text(json.dumps(clean, ensure_ascii=False, indent=2, default=float), encoding="utf-8")
    print("written timing.json")


if __name__ == "__main__":
    main()
