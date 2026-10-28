"""EXP-001 台股低波動選股。規格權威：docs/experiments/EXP-001-lowvol-tw.md（參數不得改）。

用法：
  python experiments/exp001_lowvol.py --segments IS        # 只跑 IS（除錯用）
  python experiments/exp001_lowvol.py                      # IS + OOS 完整（輸出 results.json/md/png）
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine import metrics as M  # noqa: E402
from engine.data.base import CostModel  # noqa: E402

OUT_DIR = ROOT / "docs" / "experiments" / "exp001"
SEED = 20261028
N_PERM = 2000
ID_RE = re.compile(r"^[1-9]\d{3}$")


@dataclass(frozen=True)
class Params:
    """預設值 = 規格值。測試可縮小，正式執行一律用預設。"""
    lookback: int = 252
    min_valid: int = 200
    min_hist: int = 252
    min_price: float = 10.0
    amt_win: int = 20
    min_amt: float = 5_000_000.0
    top_frac: float = 0.2
    limit: float = 0.095


COST_BASE = CostModel(0.001425, 0.001425, 0.003, 0.001)
COST_SLIP3 = CostModel(0.001425, 0.001425, 0.003, 0.003)
COST_ZERO = CostModel(0.0, 0.0, 0.0, 0.0)

SEGMENTS = {"IS": ("2011-01-01", "2018-12-31"), "OOS": ("2019-01-01", "2026-09-30")}


# ---------------------------------------------------------------- 訊號 / 股票池
def compute_signals(wide: dict, p: Params = Params()) -> dict:
    """回傳 pool(T×N bool)、vol(T×N float)。每個 t 只用 <= t 的資料（rolling 皆為後向）。"""
    close = wide["close_raw"]
    amt = wide["amount"]
    ret = wide["ret"]
    traded = close.notna()
    idm = np.array([bool(ID_RE.match(str(c))) for c in close.columns])
    hist = traded.cumsum()
    amt_avg = amt.fillna(0.0).rolling(p.amt_win, min_periods=p.amt_win).mean()   # 停牌日計 0（保守）
    vol = ret.rolling(p.lookback, min_periods=p.min_valid).std()
    T = len(close)
    full_window = np.arange(T) >= p.lookback - 1
    pool = (traded.to_numpy() & idm[None, :] & (hist.to_numpy() >= p.min_hist)
            & (close.to_numpy() >= p.min_price) & (amt_avg.to_numpy() >= p.min_amt)
            & full_window[:, None])
    return {"pool": pool, "vol": vol.to_numpy(dtype=float)}


def month_end_idx(dates: pd.DatetimeIndex) -> np.ndarray:
    s = pd.Series(np.arange(len(dates)), index=dates)
    return s.groupby([dates.year, dates.month]).max().to_numpy()


def select_lowvol(pool_row: np.ndarray, vol_row: np.ndarray, top_frac: float) -> np.ndarray:
    cand = np.nonzero(pool_row & np.isfinite(vol_row))[0]
    if len(cand) == 0:
        return cand
    n = max(1, int(math.floor(top_frac * len(cand))))
    order = np.argsort(vol_row[cand], kind="stable")
    return cand[order[:n]]


# ---------------------------------------------------------------- 回測
def simulate(R: np.ndarray, CP: np.ndarray, last_idx: np.ndarray, pool: np.ndarray, vol: np.ndarray,
             rebal_t: np.ndarray, seg_s: int, seg_e: int, cm: CostModel, mode: str,
             p: Params = Params()) -> dict:
    """R: 含息日報酬(NaN=無成交)；CP: cumprod(1+R.fillna(0))。
    rebal_t: 訊號日索引（月底）；成交日 u=t+1 收盤。段內第一個合格訊號日起建倉。
    mode: 'lowvol'（策略）或 'all'（B1：股票池等權）。"""
    T, N = R.shape
    ts = [t for t in rebal_t if seg_s <= t + 1 < seg_e and pool[t].any()
          and (mode == "all" or np.isfinite(vol[t][pool[t]]).any())]
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
        w[(last_idx < u) & (w > 0)] = 0.0              # 已下市：以最後收盤結算成現金（免費）
        pool_idx = np.nonzero(pool[t])[0]
        sel = pool_idx if mode == "all" else select_lowvol(pool[t], vol[t], p.top_frac)
        target = np.zeros(N)
        target[sel] = 1.0 / len(sel)
        ru = R[u]
        tradable = np.isfinite(ru) & (np.abs(np.nan_to_num(ru, nan=0.0)) < p.limit)
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
        # MCPT 用資料
        in_pool = np.zeros(N, bool)
        in_pool[pool_idx] = True
        Ppool = CP[e, pool_idx] / CP[u, pool_idx] - 1.0
        hm = in_pool[held]
        const = float((wk[held][~hm]) @ Ph[~hm])
        out["periods"].append({
            "t": int(t), "u": int(u), "e": int(e), "cost": c, "turnover": 0.5 * (dec + inc_eff),
            "ret": nav_new / nav - 1.0, "gross": gross, "n_hold": int(len(held)), "n_pool": int(len(pool_idx)),
            "n_sel": int(len(sel)), "pool_idx": pool_idx, "Ppool": Ppool, "wpool": wk[pool_idx], "const": const,
        })
        w = np.zeros(N)
        w[held] = wk[held] * (1.0 + Ph) / (1.0 + gross)
        nav = nav_new
    return out


# ---------------------------------------------------------------- MCPT
def mcpt(periods: list[dict], n_perm: int = N_PERM, seed: int = SEED) -> dict:
    """截面置換：每期把股票池中各股票的持有期報酬隨機重分配給股票，權重序列與成本不變。
    統計量 = 扣成本後月頻年化 Sharpe。"""
    rng = np.random.default_rng(seed)
    K = len(periods)
    Rm = np.empty((n_perm, K))
    actual = np.array([pr["ret"] for pr in periods])
    for k, pr in enumerate(periods):
        m = len(pr["Ppool"])
        if m == 0 or not np.any(pr["wpool"]):
            gross = np.full(n_perm, pr["const"])
        else:
            perm = np.argsort(rng.random((n_perm, m)), axis=1)
            gross = pr["Ppool"][perm] @ pr["wpool"] + pr["const"]
        Rm[:, k] = (1.0 - pr["cost"]) * (1.0 + gross) - 1.0
    mu = Rm.mean(axis=1)
    sd = Rm.std(axis=1, ddof=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        sh = np.where(sd > 0, mu / sd * math.sqrt(12), np.nan)
    a = M.sharpe(actual, 12)
    ok = sh[np.isfinite(sh)]
    cnt = int((ok >= a - 1e-12).sum())
    return {"actual": float(a), "perm": sh, "p": cnt / len(ok), "p_plus1": (cnt + 1) / (len(ok) + 1),
            "perm_mean": float(ok.mean()), "perm_p95": float(np.quantile(ok, 0.95))}


# ---------------------------------------------------------------- 指標
def seg_metrics(nav: pd.Series, pr: np.ndarray, dates: pd.DatetimeIndex) -> dict:
    yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    end = float(nav.iloc[-1])
    cg = end ** (1 / yrs) - 1 if end > 0 else -1.0
    mdd = M.max_drawdown(nav.to_numpy())
    return {
        "cagr": cg, "ann_vol": M.ann_vol(pr, 12), "sharpe": M.sharpe(pr, 12), "sortino": M.sortino(pr, 12),
        "mdd": mdd, "calmar": cg / mdd if mdd > 0 else math.nan,
        "win_rate": float(np.mean(np.asarray(pr) > 0)), "years": yrs, "n_periods": int(len(pr)),
        "total_return": end - 1.0,
        "sharpe_daily": M.sharpe(nav.pct_change().dropna().to_numpy(), 252),
    }


def annual_returns(nav: pd.Series) -> dict:
    ye = nav.groupby(nav.index.year).last()
    prev = pd.concat([pd.Series([nav.iloc[0]]), ye.iloc[:-1]]).to_numpy()
    return {int(y): float(v / b - 1) for y, v, b in zip(ye.index, ye.to_numpy(), prev)}


def nav_series(sim: dict, dates: pd.DatetimeIndex) -> pd.Series:
    return pd.Series(sim["nav"], index=dates[sim["idx"]])


def hold_period_returns(sim: dict) -> np.ndarray:
    return np.array([x["ret"] for x in sim["periods"]])


def buy_hold_etf(R: np.ndarray, col: int, u0: int, seg_e: int, cm: CostModel, dates) -> tuple[pd.Series, pd.Series]:
    r = np.nan_to_num(R[u0 + 1:seg_e + 1, col], nan=0.0)
    nav = np.concatenate([[1.0], (1 - cm.buy_rate) * np.cumprod(1 + r)])
    return pd.Series(nav, index=dates[u0:seg_e + 1]), None


def period_returns_on_grid(nav: pd.Series, grid_dates: list) -> np.ndarray:
    v = nav.reindex(grid_dates).to_numpy()
    return v[1:] / v[:-1] - 1.0


def run_segment(name: str, ctx: dict, p: Params = Params()) -> dict:
    s_date, e_date = SEGMENTS[name]
    dates = ctx["dates"]
    seg_s = int(dates.searchsorted(pd.Timestamp(s_date)))
    seg_e = int(dates.searchsorted(pd.Timestamp(e_date), side="right") - 1)
    args = (ctx["R"], ctx["CP"], ctx["last_idx"], ctx["pool"], ctx["vol"], ctx["rebal_t"], seg_s, seg_e)
    res: dict = {"segment": name, "start": s_date, "end": e_date}
    sims = {}
    for sc, cm in (("base", COST_BASE), ("slip30", COST_SLIP3), ("gross", COST_ZERO)):
        sims[sc] = {"strat": simulate(*args, cm, "lowvol", p), "b1": simulate(*args, cm, "all", p)}
    S, B = sims["base"]["strat"], sims["base"]["b1"]
    nS, nB = nav_series(S, dates), nav_series(B, dates)
    u0 = S["u"][0]
    # 期間報酬：策略沿用持有期；B1 同一調倉日網格
    prS = hold_period_returns(S)
    prB = hold_period_returns(B)
    grid = [dates[u] for u in S["u"]] + [dates[seg_e]]
    nE, _ = buy_hold_etf(ctx["R"], ctx["col_0050"], u0, seg_e, COST_BASE, dates)
    prE = period_returns_on_grid(nE, grid)
    res["first_trade"] = str(dates[u0].date())
    res["last_day"] = str(dates[seg_e].date())
    res["n_rebalances"] = len(S["u"])
    mS, mB, mE = seg_metrics(nS, prS, dates), seg_metrics(nB, prB, dates), seg_metrics(nE, prE, dates)
    ppy = 12
    act = prS - prB
    beta = float(np.cov(prS, prB, ddof=1)[0, 1] / np.var(prB, ddof=1))
    for m, S_ in ((mS, S), (mB, B)):
        ps = S_["periods"]
        m["turnover_ann"] = float(sum(x["turnover"] for x in ps[1:]) / m["years"])   # 不含首次建倉
        m["avg_holdings"] = float(np.mean([x["n_hold"] for x in ps]))
        m["avg_pool"] = float(np.mean([x["n_pool"] for x in ps]))
        m["cost_sum_ann"] = float(sum(x["cost"] for x in ps[1:]) / m["years"])
    gS = seg_metrics(nav_series(sims["gross"]["strat"], dates), hold_period_returns(sims["gross"]["strat"]), dates)
    gB = seg_metrics(nav_series(sims["gross"]["b1"], dates), hold_period_returns(sims["gross"]["b1"]), dates)
    mS["cost_drag"] = gS["cagr"] - mS["cagr"]
    mB["cost_drag"] = gB["cagr"] - mB["cagr"]
    mS["cagr_gross"], mB["cagr_gross"] = gS["cagr"], gB["cagr"]
    mS["excess_cagr_vs_b1"] = mS["cagr"] - mB["cagr"]
    mS["excess_mean_ann"] = float(np.mean(act) * ppy)
    mS["ir_vs_b1"] = M.sharpe(act, ppy)
    mS["beta_vs_b1"] = beta
    res.update({"strategy": mS, "b1": mB, "b2_0050": mE})
    # 滑價 0.30% 敏感度
    sl = {}
    for key in ("strat", "b1"):
        sm = sims["slip30"][key]
        sl[key] = seg_metrics(nav_series(sm, dates), hold_period_returns(sm), dates)
    sl["sharpe_gt_b1"] = bool(sl["strat"]["sharpe"] > sl["b1"]["sharpe"])
    sl["mdd_lt_b1"] = bool(sl["strat"]["mdd"] < sl["b1"]["mdd"])
    res["slip30"] = sl
    # MCPT
    mc = mcpt(S["periods"], N_PERM, SEED)
    res["mcpt"] = {k: mc[k] for k in ("actual", "p", "p_plus1", "perm_mean", "perm_p95")}
    res["mcpt"]["n_perm"] = N_PERM
    res["mcpt"]["seed"] = SEED
    res["verdict"] = {
        "P1": {"pass": bool(mS["sharpe"] > mB["sharpe"]), "strat": mS["sharpe"], "b1": mB["sharpe"]},
        "P2": {"pass": bool(mc["p"] < 0.05 and mc["p_plus1"] < 0.05), "p": mc["p"], "p_plus1": mc["p_plus1"]},
        "P3": {"pass": bool(mS["mdd"] < mB["mdd"]), "strat": mS["mdd"], "b1": mB["mdd"]},
    }
    res["annual"] = {"strat": annual_returns(nS), "b1": annual_returns(nB), "b2": annual_returns(nE)}
    res["_series"] = {"nS": nS, "nB": nB, "nE": nE, "perm": mc["perm"]}
    return res


# ---------------------------------------------------------------- 資料準備
def prepare(wide: dict) -> dict:
    dates = wide["close_raw"].index
    ret = wide["ret"]
    R = ret.to_numpy(dtype=float)
    CP = np.cumprod(1.0 + np.nan_to_num(R, nan=0.0), axis=0)
    traded = wide["close_raw"].notna().to_numpy()
    T = len(dates)
    last_idx = np.where(traded.any(axis=0), T - 1 - np.argmax(traded[::-1], axis=0), -1)
    sig = compute_signals(wide)
    cols = list(wide["close_raw"].columns)
    return {"dates": dates, "R": R, "CP": CP, "last_idx": last_idx, "pool": sig["pool"], "vol": sig["vol"],
            "rebal_t": month_end_idx(dates), "col_0050": cols.index("0050"), "cols": cols}


def data_stats(wide: dict, ctx: dict) -> dict:
    dates = ctx["dates"]
    pool = ctx["pool"]
    rt = ctx["rebal_t"]
    per_year = {}
    for y in sorted(set(dates[rt].year)):
        sizes = [int(pool[t].sum()) for t in rt if dates[t].year == y]
        if sizes and max(sizes) > 0:
            per_year[int(y)] = {"mean": float(np.mean(sizes)), "min": int(min(sizes)), "max": int(max(sizes))}
    cols = ctx["cols"]
    last = ctx["last_idx"]
    end_cut = len(dates) - 1 - 10
    delist = {}
    for j, c in enumerate(cols):
        if ID_RE.match(c) and 0 <= last[j] < end_cut:
            y = int(dates[last[j]].year)
            delist[y] = delist.get(y, 0) + 1
    r = wide["ret"]
    big = r.abs().stack()
    big = big[big > 0.5]
    return {"pool_per_year": per_year, "delisted_common_per_year": dict(sorted(delist.items())),
            "n_common_stocks_total": int(sum(bool(ID_RE.match(c)) for c in cols)),
            "n_all_ids": len(cols), "n_days": len(dates),
            "n_extreme_ret_gt50pct": int(len(big)),
            "extreme_examples": [f"{i[1]} {i[0].date()} {r.loc[i[0], i[1]]:+.1%}" for i in big.sort_values(ascending=False).index[:8]]}


def sanity(wide: dict) -> dict:
    r = wide["ret"]
    out = {}
    for s in ("0050", "2330"):
        x = r[s].loc["2011-01-01":"2025-12-31"].fillna(0.0)
        yrs = (x.index[-1] - x.index[0]).days / 365.25
        out[s] = {"cagr_2011_2025": float((1 + x).prod() ** (1 / yrs) - 1),
                  "total_multiple": float((1 + x).prod()), "first": str(r[s].first_valid_index().date())}
    return out


# ---------------------------------------------------------------- 圖與報告
def make_plots(results: dict, out_dir: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    out_dir.mkdir(parents=True, exist_ok=True)
    segs = [s for s in ("IS", "OOS") if s in results]
    col = {"s": "#1f77b4", "b1": "#ff7f0e", "b2": "#7f7f7f"}
    fig, ax = plt.subplots(len(segs), 1, figsize=(9, 4 * len(segs)), squeeze=False)
    for a, s in zip(ax[:, 0], segs):
        ser = results[s]["_series"]
        a.plot(ser["nS"], label="低波動策略", color=col["s"])
        a.plot(ser["nB"], label="B1 股票池等權", color=col["b1"])
        a.plot(ser["nE"], label="B2 0050", color=col["b2"])
        a.set_yscale("log"); a.set_title(f"{s} 淨值（扣成本，起點=1，對數軸）"); a.legend(); a.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(out_dir / "equity.png", dpi=120); plt.close(fig)

    fig, ax = plt.subplots(len(segs), 1, figsize=(9, 3.2 * len(segs)), squeeze=False)
    for a, s in zip(ax[:, 0], segs):
        ser = results[s]["_series"]
        for k, lab, c in (("nS", "低波動策略", col["s"]), ("nB", "B1", col["b1"]), ("nE", "B2 0050", col["b2"])):
            a.plot(ser[k].index, M.drawdown_series(ser[k].to_numpy()), label=lab, color=c, lw=1)
        a.set_title(f"{s} 回撤"); a.legend(); a.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(out_dir / "drawdown.png", dpi=120); plt.close(fig)

    fig, ax = plt.subplots(1, len(segs), figsize=(6 * len(segs), 4), squeeze=False)
    for a, s in zip(ax[0], segs):
        mc = results[s]["mcpt"]
        perm = results[s]["_series"]["perm"]
        a.hist(perm[np.isfinite(perm)], bins=50, color="#9ecae1")
        a.axvline(mc["actual"], color="red", label=f"實際 {mc['actual']:.2f}")
        a.set_title(f"{s} MCPT 置換 Sharpe（p={mc['p']:.4f}）"); a.legend()
    fig.tight_layout(); fig.savefig(out_dir / "mcpt.png", dpi=120); plt.close(fig)

    fig, ax = plt.subplots(len(segs), 1, figsize=(10, 3.6 * len(segs)), squeeze=False)
    for a, s in zip(ax[:, 0], segs):
        an = results[s]["annual"]
        yrs = sorted(an["strat"])
        x = np.arange(len(yrs)); wd = 0.27
        for i, (k, lab, c) in enumerate((("strat", "策略", col["s"]), ("b1", "B1", col["b1"]), ("b2", "0050", col["b2"]))):
            a.bar(x + (i - 1) * wd, [an[k][y] * 100 for y in yrs], wd, label=lab, color=c)
        a.set_xticks(x); a.set_xticklabels(yrs); a.set_ylabel("%"); a.set_title(f"{s} 年度報酬"); a.legend(); a.grid(alpha=.3, axis="y")
    fig.tight_layout(); fig.savefig(out_dir / "annual.png", dpi=120); plt.close(fig)


def _f(x, pct=True, d=2):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "n/a"
    return f"{x * 100:.{d}f}%" if pct else f"{x:.{d}f}"


def write_md(results: dict, stats: dict, san: dict, path: Path) -> None:
    L = []
    A = L.append
    A("# EXP-001 結果：台股低波動選股\n")
    A("> 規格：`EXP-001-lowvol-tw.md`（預先登記，未改動）。無風險利率 = 0。Sharpe/Sortino/波動/IR 皆用「持有期（調倉日到下一調倉日，約月頻）」報酬、年化因子 12；"
      "CAGR、最大回撤、Calmar 用日淨值。")
    A("> 資料來源：臺灣證券交易所、證券櫃檯買賣中心（政府資料開放授權 https://data.gov.tw/license；經 Blave CDN 整理）。\n")
    if "OOS" in results:
        v = results["OOS"]["verdict"]
        A("## 合格判定（OOS，滑價 0.10%）\n")
        A("| # | 條件 | 數字 | 判定 |\n|---|---|---|---|")
        A(f"| P1 | Sharpe 策略 > B1 | 策略 {v['P1']['strat']:.3f} vs B1 {v['P1']['b1']:.3f} | **{'PASS' if v['P1']['pass'] else 'FAIL'}** |")
        A(f"| P2 | MCPT p < 0.05（n=2000, seed=20261028） | p = {v['P2']['p']:.4f}（(k+1)/(n+1) = {v['P2']['p_plus1']:.4f}） | **{'PASS' if v['P2']['pass'] else 'FAIL'}** |")
        A(f"| P3 | 最大回撤 策略 < B1 | 策略 {_f(v['P3']['strat'])} vs B1 {_f(v['P3']['b1'])} | **{'PASS' if v['P3']['pass'] else 'FAIL'}** |")
        allp = all(v[k]["pass"] for k in ("P1", "P2", "P3"))
        A(f"\n**總判定：{'三條全過（撐得住）' if allp else '未全過（不合格），依規格不調參重跑'}**\n")
    A("## 結果表（IS / OOS 並排；扣成本，滑價 0.10%）\n")
    segs = [s for s in ("IS", "OOS") if s in results]
    rows = [("CAGR", "cagr", True), ("年化波動", "ann_vol", True), ("Sharpe", "sharpe", False), ("Sortino", "sortino", False),
            ("最大回撤", "mdd", True), ("Calmar", "calmar", False), ("月勝率", "win_rate", True),
            ("年化單邊換手", "turnover_ann", True), ("成本拖累（CAGR 年化，毛-淨）", "cost_drag", True),
            ("平均持股數", "avg_holdings", False), ("平均股票池檔數", "avg_pool", False)]
    hdr = "| 指標 | " + " | ".join(f"{s} 策略 | {s} B1 | {s} B2(0050)" for s in segs) + " |"
    A(hdr); A("|---|" + "---|" * (3 * len(segs)))
    for lab, k, pct in rows:
        cells = []
        for s in segs:
            for g in ("strategy", "b1", "b2_0050"):
                val = results[s][g].get(k)
                cells.append(_f(val, pct, 2) if val is not None else "-")
        A(f"| {lab} | " + " | ".join(cells) + " |")
    A("")
    A("| 相對 B1 | " + " | ".join(segs) + " |\n|---|" + "---|" * len(segs))
    for lab, k, pct in (("超額 CAGR", "excess_cagr_vs_b1", True), ("超額報酬（期間均值×12）", "excess_mean_ann", True),
                        ("IR", "ir_vs_b1", False), ("beta", "beta_vs_b1", False)):
        A(f"| {lab} | " + " | ".join(_f(results[s]["strategy"][k], pct, 3 if not pct else 2) for s in segs) + " |")
    A("")
    A("| MCPT | " + " | ".join(segs) + " |\n|---|" + "---|" * len(segs))
    A("| 實際 Sharpe | " + " | ".join(f"{results[s]['mcpt']['actual']:.3f}" for s in segs) + " |")
    A("| 置換均值 / 95 分位 | " + " | ".join(f"{results[s]['mcpt']['perm_mean']:.3f} / {results[s]['mcpt']['perm_p95']:.3f}" for s in segs) + " |")
    A("| p 值（≥ 實際的比例） | " + " | ".join(f"{results[s]['mcpt']['p']:.4f}" for s in segs) + " |")
    A("")
    A("各段起訖（績效各自從該段第一個持有日起算、重新建倉）：" + "；".join(
        f"{s}：首次成交 {results[s]['first_trade']}，結束 {results[s]['last_day']}，調倉 {results[s]['n_rebalances']} 次" for s in segs) + "\n")
    if "OOS" in results:
        o = results["OOS"]
        A("## 解讀提醒（客觀事實，非調參依據）\n")
        A(f"- P1~P3 依規格全數以 B1 為對照；OOS 策略 CAGR {_f(o['strategy']['cagr'])} 低於 B1 {_f(o['b1']['cagr'])}"
          f"（超額 CAGR {_f(o['strategy']['excess_cagr_vs_b1'])}、IR {o['strategy']['ir_vs_b1']:.2f}），Sharpe 與回撤的優勢來自波動較低（beta {o['strategy']['beta_vs_b1']:.2f}），不是報酬較高。")
        A(f"- 參考基準 B2（0050）OOS Sharpe {o['b2_0050']['sharpe']:.2f}、CAGR {_f(o['b2_0050']['cagr'])}，皆高於策略；B2 不列入判定。")
        A("- MCPT 虛無是「同權重、隨機挑股」，策略勝過它主要反映「低波動股本身風險較低」，並非能預測較高報酬。")
        A("")
    A("## 滑價 0.30% 敏感度（只報告，不作判定）\n")
    A("| 段 | 策略 CAGR | 策略 Sharpe | 策略 MDD | B1 CAGR | B1 Sharpe | B1 MDD | Sharpe>B1 | MDD<B1 |\n|---|---|---|---|---|---|---|---|---|")
    for s in segs:
        x = results[s]["slip30"]
        A(f"| {s} | {_f(x['strat']['cagr'])} | {x['strat']['sharpe']:.3f} | {_f(x['strat']['mdd'])} | {_f(x['b1']['cagr'])} | "
          f"{x['b1']['sharpe']:.3f} | {_f(x['b1']['mdd'])} | {x['sharpe_gt_b1']} | {x['mdd_lt_b1']} |")
    A("")
    A("## 年度報酬\n")
    for s in segs:
        an = results[s]["annual"]
        A(f"**{s}**\n\n| 年 | 策略 | B1 | 0050 |\n|---|---|---|---|")
        for y in sorted(an["strat"]):
            A(f"| {y} | {_f(an['strat'][y])} | {_f(an['b1'][y])} | {_f(an['b2'][y])} |")
        A("")
    A("圖檔：`exp001/equity.png`、`drawdown.png`、`mcpt.png`、`annual.png`；原始數字 `exp001/results.json`。\n")
    A("## 資料健全性檢查\n")
    A(f"- 含息報酬（事件日用 C/ref_price−1）2011-01-01~2025-12-31：0050 年化 **{_f(san['0050']['cagr_2011_2025'])}**（累積 {san['0050']['total_multiple']:.2f} 倍）；"
      f"2330 年化 **{_f(san['2330']['cagr_2011_2025'])}**（累積 {san['2330']['total_multiple']:.2f} 倍）。")
    A(f"- 資料共 {stats['n_days']} 個交易日、{stats['n_all_ids']} 個代號（其中 4 位數普通股代號 {stats['n_common_stocks_total']} 檔）。")
    A(f"- 單日 |報酬| > 50% 的觀測共 {stats['n_extreme_ret_gt50pct']} 筆（未做任何修正；規格未授權）。最大者：" + "；".join(stats["extreme_examples"]))
    A("\n**每年股票池檔數（月底調倉日的池大小）**\n\n| 年 | 平均 | 最小 | 最大 | 該年最後交易日在該年的 4 位數代號股（下市/終止）檔數 |\n|---|---|---|---|---|")
    for y, d in stats["pool_per_year"].items():
        A(f"| {y} | {d['mean']:.0f} | {d['min']} | {d['max']} | {stats['delisted_common_per_year'].get(y, 0)} |")
    A("")
    A("## 保守解讀與實作選擇（規格模稜兩可處）\n")
    A("""1. **暖身期不足 252 日**：2010 年僅約 247 個交易日，規格股票池規則 2 要求 ≥252 日資料，故 IS 第一個合格訊號日為 2011 年 1 月底（2011-02 初首次成交），而非 2011-01-03。
2. **股票池 vs 訊號有效報酬數**：股票池 = 規則 1~4（含 252 日視窗須完整）；「有效報酬 ≥200」只用於選股，B1 的池不再套用此條。
3. **成交額平均**：過去 20 個交易日平均，停牌日（無成交）以 0 計入，使均值偏低（較保守）。
4. **波動度**：252 個「市場交易日」視窗內有效日報酬的樣本標準差（ddof=1，不年化）；停牌日不計入。
5. **挑 20%**：池中有有效訊號者數 ×0.2 無條件捨去（至少 1 檔），同值以代號順序決勝。
6. **漲跌停判定**：以含息報酬（C/ref_price−1，事件日為正確漲跌幅）絕對值 ≥9.5%、或成交日無成交（停牌）→ 該股買賣皆不成交，權重維持。買、賣兩方向皆以此一律封鎖（較保守）。
7. **賣出不足以支應買進（因不成交）**：買進按比例縮減；剩餘為現金（報酬 0）直到下次調倉。
8. **下市**：最後有成交日之後，部位視為最後收盤價結算的現金（免交易成本，報酬 0），下次調倉再投入。以資料中該股最後成交日判斷下市（含少數「長期停牌後才下市」情形，此時停牌期間同樣以現金計；停牌期間不能賣出本就等同如此）。
9. **同日多事件**：events 表實測無同股同日重複；若有則取第一筆。**停牌跨事件**：恢復日報酬基準採「上一有成交日至今」區間內最早事件的 ref_price（避免重複計中間事件）。
10. **指標頻率**：Sharpe/Sortino/波動/IR/勝率用持有期報酬（調倉日→下一調倉日，最後一期到段末）、年化因子 12；與 MCPT 統計量一致。換手率不含首次建倉；成本拖累 = 零成本 CAGR − 含成本 CAGR。
11. **IS / OOS 各自獨立建倉**：OOS 以 2018 年底最後交易日的訊號、2019-01-02 成交建倉（不承接 IS 持倉），並付首次買進成本；B2 同樣在該段首次成交日買進並付一次買進成本。
12. **P2 判定**：同時要求 p（比例）與 (k+1)/(n+1) 皆 <0.05。
13. **MCPT 置換範圍**：只置換「該期股票池內」股票的持有期報酬；池外但仍持有的部位（例如不成交殘留）保持其實際報酬。
14. 4 位數字且首位 1~9 的代號含少數 91xx 台灣存託憑證（TDR）；規格字面納入，未額外排除。""")
    A("\n## 已知限制\n")
    A("""- 股票池與下市判斷以資料中最後成交日為準，無法區分「下市」與「資料缺漏」。
- 日資料無法模擬盤中漲跌停鎖死與實際可成交量；成交額門檻（500 萬/日平均）下的持倉規模以小額資金為前提。
- 無財報與處置/注意股、全額交割股等旗標。
- 事件表的 ref_price 為交易所公告之參考價，現金股利與股票股利、減資等皆以 C/ref_price−1 處理，不另做稅務（股利所得稅）調整。
- 成本以比例近似；未計融資融券、借券、股利所得稅。
- 區間 2011–2026 僅涵蓋一個完整長多頭＋2020/2022 的回檔，樣本有限。""")
    path.write_text("\n".join(L) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--segments", default="IS,OOS")
    a = ap.parse_args()
    from engine.data import blave_tw as bt
    bt.download()
    daily, ev = bt.load_raw()
    wide = bt.build_wide(daily, ev)
    ctx = prepare(wide)
    san = sanity(wide)
    stats = data_stats(wide, ctx)
    print("sanity", json.dumps(san))
    results = {}
    for s in a.segments.split(","):
        results[s] = run_segment(s, ctx)
        v = results[s]["verdict"]
        print(s, {k: (x["pass"]) for k, x in v.items()}, "sharpe", results[s]["strategy"]["sharpe"], results[s]["b1"]["sharpe"],
              "mdd", results[s]["strategy"]["mdd"], results[s]["b1"]["mdd"], "p", results[s]["mcpt"]["p"])
    if set(results) == {"IS", "OOS"}:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        make_plots(results, OUT_DIR)
        clean = {s: {k: v for k, v in r.items() if k != "_series"} for s, r in results.items()}
        clean["data_stats"] = stats
        clean["sanity"] = san
        (OUT_DIR / "results.json").write_text(json.dumps(clean, ensure_ascii=False, indent=2, default=float), encoding="utf-8")
        write_md(results, stats, san, ROOT / "docs" / "experiments" / "EXP-001-results.md")
        print("written")
    else:
        print(json.dumps({s: {k: v for k, v in r.items() if k not in ("_series",)} for s, r in results.items()},
                         ensure_ascii=False, indent=1, default=float)[:6000])


if __name__ == "__main__":
    main()
