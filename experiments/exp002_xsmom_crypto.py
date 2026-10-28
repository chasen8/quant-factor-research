"""EXP-002 加密貨幣橫斷面動能（Binance 現貨、只做多）。規格權威：docs/experiments/EXP-002-xsmom-crypto.md（參數不得改）。

用法：
  python experiments/exp002_xsmom_crypto.py --segments IS     # 只跑 IS（除錯用）
  python experiments/exp002_xsmom_crypto.py                   # IS + OOS 完整（輸出 results.json/md/png）
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine import metrics as M  # noqa: E402
from engine.data.base import CostModel  # noqa: E402

OUT_DIR = ROOT / "docs" / "experiments" / "exp002"
SEED = 20261028
N_PERM = 2000
PPY = 52

EXCLUDE_BASES = set("""USDC BUSD TUSD PAX USDP USDS USDSB DAI FDUSD UST USTC AEUR EUR EURI GBP AUD TRY BRL RUB BIDR IDRT NGN UAH ZAR
BKRW PAXG XUSD USD1 USDE RLUSD BFUSD WBTC WBETH BETH""".split())
LEV_SUFFIX = ("UP", "DOWN", "BULL", "BEAR")


@dataclass(frozen=True)
class Params:
    """預設值 = 規格值。測試可縮小，正式執行一律用預設。"""
    lookback: int = 21
    min_hist: int = 60
    vol_win: int = 30
    top_n: int = 30
    frac: float = 1 / 3
    min_hold: int = 3
    gap_missing: int = 7        # 連續 >= 7 天沒有日 K -> 缺口切成新資產


def mk_cost(slip: float) -> CostModel:
    return CostModel(0.001, 0.001, 0.0, slip)


COST_BASE = mk_cost(0.001)
COST_SLIP25 = mk_cost(0.0025)
COST_ZERO = CostModel(0.0, 0.0, 0.0, 0.0)

SEGMENTS = {"IS": ("2018-07-01", "2021-12-31"), "OOS": ("2022-01-01", "2026-09-30")}


# ---------------------------------------------------------------- 資料整形
def leverage_excluded(symbols: list[str]) -> set[str]:
    """槓桿代幣：base 以 UP/DOWN/BULL/BEAR 結尾，且去掉後綴的部分本身也是某個 USDT 交易對的 base。"""
    bases = {s[:-4] for s in symbols if s.endswith("USDT")}
    out = set()
    for b in bases:
        for suf in LEV_SUFFIX:
            if b.endswith(suf) and len(b) > len(suf) and b[:-len(suf)] in bases:
                out.add(b)
                break
    return out


def split_gaps(df: pd.DataFrame, gap_missing: int = 7) -> pd.DataFrame:
    """df: [symbol, date, close, quote_volume]。連續 >= gap_missing 天沒有日 K（相鄰日 K 日期差 >= gap_missing+1）
    即在缺口後視為新資產。新增欄位 asset（第一段=symbol，其後 symbol#2、#3…）。"""
    df = df.sort_values(["symbol", "date"]).reset_index(drop=True)
    d = df["date"].diff().dt.days
    new_sym = df["symbol"] != df["symbol"].shift()
    brk = new_sym | (d >= gap_missing + 1)
    seg = brk.groupby(df["symbol"]).cumsum()            # 每個 symbol 內的段號（1 起算）
    df["asset"] = np.where(seg == 1, df["symbol"], df["symbol"] + "#" + seg.astype(str))
    return df


def build_wide(df: pd.DataFrame, p: Params = Params()) -> dict:
    """回傳 numpy 寬表。traded=該日有日 K；P=資產存續期間內向前填補的收盤（短缺口用）；
    R=日報酬（首日、缺口前後新資產首日為 NaN；短缺口內填補日為 0）；CP=cumprod(1+R)。"""
    df = split_gaps(df, p.gap_missing)
    dates = pd.date_range(df["date"].min(), df["date"].max(), freq="D")
    assets = list(dict.fromkeys(df["asset"]))
    col = {a: i for i, a in enumerate(assets)}
    T, N = len(dates), len(assets)
    C = np.full((T, N), np.nan)
    Q = np.full((T, N), np.nan)
    ti = dates.get_indexer(df["date"])
    ci = df["asset"].map(col).to_numpy()
    ok = (df["close"].to_numpy() > 0)
    C[ti[ok], ci[ok]] = df["close"].to_numpy()[ok]
    Q[ti[ok], ci[ok]] = df["quote_volume"].to_numpy()[ok]
    traded = np.isfinite(C)
    first = np.where(traded.any(0), traded.argmax(0), -1)
    last = np.where(traded.any(0), T - 1 - traded[::-1].argmax(0), -1)
    P = pd.DataFrame(C).ffill().to_numpy().copy()
    after = np.arange(T)[:, None] > last[None, :]
    P[after] = np.nan                                    # 下架後不再有價格
    R = np.full((T, N), np.nan)
    R[1:] = P[1:] / P[:-1] - 1.0                         # 首日（前一日 NaN）自動為 NaN
    CP = np.cumprod(1.0 + np.nan_to_num(R, nan=0.0), axis=0)
    sym = np.array([a.split("#")[0] for a in assets])
    base = np.array([s[:-4] for s in sym])
    return {"dates": dates, "assets": assets, "sym": sym, "base": base, "C": C, "Q": Q, "traded": traded, "P": P,
            "R": R, "CP": CP, "first": first, "last": last}


def compute_signals(w: dict, lev: set[str], p: Params = Params()) -> dict:
    """pool(T×N bool)、sig(T×N float)。第 t 列只用 <= t 的資料。"""
    traded = w["traded"]
    P = w["P"]
    T, N = traded.shape
    excl = np.array([(b in EXCLUDE_BASES) or (b in lev) for b in w["base"]])
    hist = np.cumsum(traded, axis=0)
    qv = np.nan_to_num(w["Q"], nan=0.0)
    cs = np.vstack([np.zeros((1, N)), np.cumsum(qv, axis=0)])
    avg = np.full((T, N), np.nan)
    k = p.vol_win
    avg[k - 1:] = (cs[k:] - cs[:-k]) / k                 # 過去 30 天（含當日）；缺 K 日計 0（保守）
    elig = traded & (hist >= p.min_hist) & ~excl[None, :] & np.isfinite(avg)
    pool = np.zeros((T, N), bool)
    for t in range(T):
        idx = np.nonzero(elig[t])[0]
        if len(idx) == 0:
            continue
        order = np.argsort(-avg[t, idx], kind="stable")
        pool[t, idx[order[:p.top_n]]] = True
    L = p.lookback
    win = np.vstack([np.zeros((1, N), int), np.cumsum(traded.astype(int), axis=0)])
    full = np.full((T, N), False)
    full[L:] = (win[L + 1:T + 1] - win[:T - L]) == L + 1    # t-L..t 共 L+1 根都有 K
    sig = np.full((T, N), np.nan)
    sig[L:] = P[L:] / P[:-L] - 1.0
    sig[~full] = np.nan
    sig[~traded] = np.nan
    return {"pool": pool, "sig": sig, "excluded": excl, "avg_qv": avg}


def sunday_idx(dates: pd.DatetimeIndex) -> np.ndarray:
    return np.nonzero(dates.day_of_week == 6)[0]


def select_mom(pool_row: np.ndarray, sig_row: np.ndarray, p: Params = Params()) -> np.ndarray:
    cand = np.nonzero(pool_row & np.isfinite(sig_row))[0]
    if len(cand) == 0:
        return cand
    n = max(p.min_hold, int(math.floor(len(cand) * p.frac + 0.5)))
    n = min(n, len(cand))
    order = np.argsort(-sig_row[cand], kind="stable")
    return cand[order[:n]]


# ---------------------------------------------------------------- 回測
def simulate(CP: np.ndarray, traded: np.ndarray, last_idx: np.ndarray, pool: np.ndarray, sig: np.ndarray,
             rebal_t: np.ndarray, seg_s: int, seg_e: int, cm: CostModel, mode: str, p: Params = Params()) -> dict:
    """rebal_t: 訊號日（週日）索引；成交日 u=t+1（週一）收盤。mode 'mom'（策略）或 'all'（B1：股票池等權）。
    策略與 B1 的調倉日網格一致（皆要求池內至少一檔有有效訊號）。"""
    T, N = CP.shape
    ts = [int(t) for t in rebal_t if seg_s <= t + 1 < seg_e and (pool[t] & np.isfinite(sig[t])).any()]
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
        w[(last_idx < u) & (w > 0)] = 0.0              # 已下架：以最後收盤結算成現金（免費）
        pool_idx = np.nonzero(pool[t])[0]
        sel = pool_idx if mode == "all" else select_mom(pool[t], sig[t], p)
        target = np.zeros(N)
        target[sel] = 1.0 / len(sel)
        tgt = np.where(traded[u], target, w)           # 成交日無日 K：不成交，維持原部位
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
        Qm = CP[u + 1:e + 1][:, held] / CP[u, held] - 1.0
        navs = nav * (1.0 - c) * (1.0 + Qm @ wk[held])
        out["idx"].extend(range(u + 1, e + 1))
        out["nav"].extend(navs.tolist())
        Ph = Qm[-1]
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
            "n_sel": int(len(sel)), "pool_idx": pool_idx, "Ppool": Ppool, "wpool": wk[pool_idx], "const": const,
        })
        w = np.zeros(N)
        w[held] = wk[held] * (1.0 + Ph) / (1.0 + gross)
        nav = nav_new
    return out


# ---------------------------------------------------------------- MCPT
def mcpt(periods: list[dict], b1_ret: np.ndarray, n_perm: int = N_PERM, seed: int = SEED) -> dict:
    """截面置換：每期把股票池中各幣的持有期報酬隨機重分配給各幣，權重序列與成本不變。
    統計量 = 扣成本後、相對 B1 的週超額報酬平均 × 52（B1 的報酬固定為實際值）。"""
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
    stat = (Rm - b1_ret[None, :]).mean(axis=1) * PPY
    a = float((actual - b1_ret).mean() * PPY)
    cnt = int((stat >= a - 1e-12).sum())
    return {"actual": a, "perm": stat, "p": cnt / n_perm, "p_plus1": (cnt + 1) / (n_perm + 1),
            "perm_mean": float(stat.mean()), "perm_p95": float(np.quantile(stat, 0.95)), "k": cnt}


# ---------------------------------------------------------------- 指標
def seg_metrics(nav: pd.Series, pr: np.ndarray) -> dict:
    yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    end = float(nav.iloc[-1])
    cg = end ** (1 / yrs) - 1 if end > 0 else -1.0
    mdd = M.max_drawdown(nav.to_numpy())
    return {
        "cagr": cg, "ann_vol": M.ann_vol(pr, PPY), "sharpe": M.sharpe(pr, PPY), "sortino": M.sortino(pr, PPY),
        "mdd": mdd, "calmar": cg / mdd if mdd > 0 else math.nan,
        "win_rate": float(np.mean(np.asarray(pr) > 0)), "years": yrs, "n_periods": int(len(pr)),
        "total_return": end - 1.0,
    }


def annual_returns(nav: pd.Series) -> dict:
    ye = nav.groupby(nav.index.year).last()
    prev = pd.concat([pd.Series([nav.iloc[0]]), ye.iloc[:-1]]).to_numpy()
    return {int(y): float(v / b - 1) for y, v, b in zip(ye.index, ye.to_numpy(), prev)}


def nav_series(sim: dict, dates: pd.DatetimeIndex) -> pd.Series:
    return pd.Series(sim["nav"], index=dates[sim["idx"]])


def hold_period_returns(sim: dict) -> np.ndarray:
    return np.array([x["ret"] for x in sim["periods"]])


def buy_hold(R: np.ndarray, col: int, u0: int, seg_e: int, cm: CostModel, dates) -> pd.Series:
    r = np.nan_to_num(R[u0 + 1:seg_e + 1, col], nan=0.0)
    nav = np.concatenate([[1.0], (1 - cm.buy_rate) * np.cumprod(1 + r)])
    return pd.Series(nav, index=dates[u0:seg_e + 1])


def period_returns_on_grid(nav: pd.Series, grid_dates: list) -> np.ndarray:
    v = nav.reindex(grid_dates).to_numpy()
    return v[1:] / v[:-1] - 1.0


def prepare(df: pd.DataFrame, p: Params = Params()) -> dict:
    w = build_wide(df, p)
    lev = leverage_excluded(sorted(set(df["symbol"])))
    sg = compute_signals(w, lev, p)
    cols = w["assets"]
    return {"w": w, "dates": w["dates"], "R": w["R"], "CP": w["CP"], "traded": w["traded"], "last_idx": w["last"],
            "pool": sg["pool"], "sig": sg["sig"], "rebal_t": sunday_idx(w["dates"]), "col_btc": cols.index("BTCUSDT"),
            "cols": cols, "lev": lev, "excluded": sg["excluded"], "avg_qv": sg["avg_qv"]}


def run_segment(name: str, ctx: dict, p: Params = Params()) -> dict:
    s_date, e_date = SEGMENTS[name]
    dates = ctx["dates"]
    seg_s = int(dates.searchsorted(pd.Timestamp(s_date)))
    seg_e = int(dates.searchsorted(pd.Timestamp(e_date), side="right") - 1)
    args = (ctx["CP"], ctx["traded"], ctx["last_idx"], ctx["pool"], ctx["sig"], ctx["rebal_t"], seg_s, seg_e)
    res: dict = {"segment": name, "start": s_date, "end": e_date}
    sims = {}
    for sc, cm in (("base", COST_BASE), ("slip25", COST_SLIP25), ("gross", COST_ZERO)):
        sims[sc] = {"strat": simulate(*args, cm, "mom", p), "b1": simulate(*args, cm, "all", p)}
    S, B = sims["base"]["strat"], sims["base"]["b1"]
    nS, nB = nav_series(S, dates), nav_series(B, dates)
    u0 = S["u"][0]
    prS, prB = hold_period_returns(S), hold_period_returns(B)
    grid = [dates[u] for u in S["u"]] + [dates[seg_e]]
    nBTC = buy_hold(ctx["R"], ctx["col_btc"], u0, seg_e, COST_BASE, dates)
    prE = period_returns_on_grid(nBTC, grid)
    res["first_trade"] = str(dates[u0].date())
    res["last_day"] = str(dates[seg_e].date())
    res["n_rebalances"] = len(S["u"])
    mS, mB, mE = seg_metrics(nS, prS), seg_metrics(nB, prB), seg_metrics(nBTC, prE)
    act = prS - prB
    actE = prS - prE
    beta = float(np.cov(prS, prB, ddof=1)[0, 1] / np.var(prB, ddof=1))
    for m, S_ in ((mS, S), (mB, B)):
        ps = S_["periods"]
        m["turnover_ann"] = float(sum(x["turnover"] for x in ps[1:]) / m["years"])    # 不含首次建倉
        m["avg_holdings"] = float(np.mean([x["n_hold"] for x in ps]))
        m["avg_pool"] = float(np.mean([x["n_pool"] for x in ps]))
        m["cost_sum_ann"] = float(sum(x["cost"] for x in ps[1:]) / m["years"])
    gS = seg_metrics(nav_series(sims["gross"]["strat"], dates), hold_period_returns(sims["gross"]["strat"]))
    gB = seg_metrics(nav_series(sims["gross"]["b1"], dates), hold_period_returns(sims["gross"]["b1"]))
    mS["cost_drag"], mB["cost_drag"] = gS["cagr"] - mS["cagr"], gB["cagr"] - mB["cagr"]
    mS["cagr_gross"], mB["cagr_gross"] = gS["cagr"], gB["cagr"]
    mS["excess_cagr_vs_b1"] = mS["cagr"] - mB["cagr"]
    mS["excess_cagr_vs_b2"] = mS["cagr"] - mE["cagr"]
    mS["excess_mean_ann_vs_b1"] = float(np.mean(act) * PPY)
    mS["excess_mean_ann_vs_b2"] = float(np.mean(actE) * PPY)
    mS["ir_vs_b1"] = M.sharpe(act, PPY)
    mS["ir_vs_b2"] = M.sharpe(actE, PPY)
    mS["beta_vs_b1"] = beta
    res.update({"strategy": mS, "b1": mB, "b2_btc": mE})
    sl = {}
    for key in ("strat", "b1"):
        sm = sims["slip25"][key]
        sl[key] = seg_metrics(nav_series(sm, dates), hold_period_returns(sm))
    sl["sharpe_gt_b1"] = bool(sl["strat"]["sharpe"] > sl["b1"]["sharpe"])
    sl["sharpe_gt_b2"] = bool(sl["strat"]["sharpe"] > mE["sharpe"])
    res["slip25"] = sl
    mc = mcpt(S["periods"], prB, N_PERM, SEED)
    res["mcpt"] = {k: mc[k] for k in ("actual", "p", "p_plus1", "perm_mean", "perm_p95", "k")}
    res["mcpt"]["n_perm"] = N_PERM
    res["mcpt"]["seed"] = SEED
    res["verdict"] = {
        "P1": {"pass": bool(mS["sharpe"] > mB["sharpe"]), "strat": mS["sharpe"], "b1": mB["sharpe"]},
        "P2": {"pass": bool(mc["p"] < 0.05 and mc["p_plus1"] < 0.05), "p": mc["p"], "p_plus1": mc["p_plus1"]},
        "P3": {"pass": bool(mS["sharpe"] > mE["sharpe"]), "strat": mS["sharpe"], "b2": mE["sharpe"]},
    }
    res["annual"] = {"strat": annual_returns(nS), "b1": annual_returns(nB), "b2": annual_returns(nBTC)}
    # 每年股票池代表幣（調倉日出現次數最多的 base）與穩定幣 CV 檢查
    res["pool_top_bases"] = pool_representatives(ctx, S, dates)
    res["cv_flags"] = cv_check(ctx, S, dates)
    res["_series"] = {"nS": nS, "nB": nB, "nE": nBTC, "perm": mc["perm"]}
    return res


def pool_representatives(ctx: dict, sim: dict, dates, topk: int = 8) -> dict:
    cnt: dict[int, dict[str, int]] = {}
    n: dict[int, int] = {}
    base = ctx["w"]["base"]
    for pr in sim["periods"]:
        y = int(dates[pr["t"]].year)
        n[y] = n.get(y, 0) + 1
        for j in pr["pool_idx"]:
            cnt.setdefault(y, {})
            cnt[y][base[j]] = cnt[y].get(base[j], 0) + 1
    return {y: [f"{b}({c}/{n[y]})" for b, c in sorted(d.items(), key=lambda kv: (-kv[1], kv[0]))[:topk]] for y, d in sorted(cnt.items())}


def cv_check(ctx: dict, sim: dict, dates, win: int = 60, thr: float = 0.01) -> dict:
    """股票池中，過去 60 天收盤價變異係數 < 1% 的 base（報告用，不影響選股）。"""
    C = ctx["w"]["C"]
    base = ctx["w"]["base"]
    flags: dict[str, dict] = {}
    for pr in sim["periods"]:
        t = pr["t"]
        for j in pr["pool_idx"]:
            x = C[max(0, t - win + 1):t + 1, j]
            x = x[np.isfinite(x)]
            if len(x) >= 30 and x.mean() > 0 and x.std(ddof=0) / x.mean() < thr:
                d = flags.setdefault(base[j], {"weeks": 0, "first": str(dates[t].date()), "last": str(dates[t].date())})
                d["weeks"] += 1
                d["last"] = str(dates[t].date())
    return flags


def data_stats(df: pd.DataFrame, ctx: dict) -> dict:
    w = ctx["w"]
    dates = ctx["dates"]
    assets = w["assets"]
    last = w["last"]
    end_cut = len(dates) - 1 - 10
    delist = {}
    for j in range(len(assets)):
        if 0 <= last[j] < end_cut:
            y = int(dates[last[j]].year)
            delist[y] = delist.get(y, 0) + 1
    n_sym = int(df["symbol"].nunique())
    n_split = sum(1 for a in assets if "#" in a)
    # 異常：單日報酬 > +300% 或 < -80%（只對有成交的連續兩日；列出供人工檢查，不做修正）
    R = w["R"]
    tr = w["traded"].copy()
    prev = np.vstack([np.zeros((1, tr.shape[1]), bool), tr[:-1]])
    ext = np.isfinite(R) & tr & prev & ((R > 3.0) | (R < -0.8))
    ti, ci = np.nonzero(ext)
    anomalies = [{"asset": assets[c], "date": str(dates[t].date()), "ret": float(R[t, c])} for t, c in zip(ti, ci)]
    anomalies.sort(key=lambda x: -abs(x["ret"]))
    pool = ctx["pool"]
    per_year = {}
    for y in sorted(set(dates[ctx["rebal_t"]].year)):
        sizes = [int(pool[t].sum()) for t in ctx["rebal_t"] if dates[t].year == y and pool[t].any()]
        if sizes:
            per_year[int(y)] = {"mean": float(np.mean(sizes)), "min": int(min(sizes)), "max": int(max(sizes))}
    return {"n_symbols": n_sym, "n_assets_after_split": len(assets), "n_assets_from_gap_split": n_split,
            "n_rows": int(len(df)), "first_date": str(dates[0].date()), "last_date": str(dates[-1].date()),
            "n_days": int(len(dates)), "delisted_assets_per_year": dict(sorted(delist.items())),
            "leverage_excluded_bases": sorted(ctx["lev"]), "n_anomalies": len(anomalies), "anomalies": anomalies,
            "pool_per_year": per_year}


def sanity(ctx: dict) -> dict:
    w = ctx["w"]
    j = ctx["col_btc"]
    r = np.nan_to_num(w["R"][:, j], nan=0.0)
    dates = ctx["dates"]
    yrs = (dates[-1] - dates[0]).days / 365.25
    return {"BTC": {"first": str(dates[w["first"][j]].date()), "total_multiple": float(np.prod(1 + r)),
                    "cagr_full": float(np.prod(1 + r) ** (1 / yrs) - 1)}}


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
        a.plot(ser["nS"], label="動能策略", color=col["s"])
        a.plot(ser["nB"], label="B1 股票池等權", color=col["b1"])
        a.plot(ser["nE"], label="B2 BTC 買進持有", color=col["b2"])
        a.set_yscale("log"); a.set_title(f"{s} 淨值（扣成本，起點=1，對數軸）"); a.legend(); a.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(out_dir / "equity.png", dpi=120); plt.close(fig)

    fig, ax = plt.subplots(len(segs), 1, figsize=(9, 3.2 * len(segs)), squeeze=False)
    for a, s in zip(ax[:, 0], segs):
        ser = results[s]["_series"]
        for k, lab, c in (("nS", "動能策略", col["s"]), ("nB", "B1", col["b1"]), ("nE", "B2 BTC", col["b2"])):
            a.plot(ser[k].index, M.drawdown_series(ser[k].to_numpy()), label=lab, color=c, lw=1)
        a.set_title(f"{s} 回撤"); a.legend(); a.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(out_dir / "drawdown.png", dpi=120); plt.close(fig)

    fig, ax = plt.subplots(1, len(segs), figsize=(6 * len(segs), 4), squeeze=False)
    for a, s in zip(ax[0], segs):
        mc = results[s]["mcpt"]
        perm = results[s]["_series"]["perm"]
        a.hist(perm, bins=50, color="#9ecae1")
        a.axvline(mc["actual"], color="red", label=f"實際 {mc['actual']:.2f}")
        a.set_title(f"{s} MCPT 相對 B1 年化週超額報酬（p={mc['p']:.4f}）"); a.legend()
    fig.tight_layout(); fig.savefig(out_dir / "mcpt.png", dpi=120); plt.close(fig)

    fig, ax = plt.subplots(len(segs), 1, figsize=(10, 3.6 * len(segs)), squeeze=False)
    for a, s in zip(ax[:, 0], segs):
        an = results[s]["annual"]
        yrs = sorted(an["strat"])
        x = np.arange(len(yrs)); wd = 0.27
        for i, (k, lab, c) in enumerate((("strat", "策略", col["s"]), ("b1", "B1", col["b1"]), ("b2", "BTC", col["b2"]))):
            a.bar(x + (i - 1) * wd, [an[k][y] * 100 for y in yrs], wd, label=lab, color=c)
        a.set_xticks(x); a.set_xticklabels(yrs); a.set_ylabel("%"); a.set_title(f"{s} 年度報酬"); a.legend(); a.grid(alpha=.3, axis="y")
    fig.tight_layout(); fig.savefig(out_dir / "annual.png", dpi=120); plt.close(fig)


def _f(x, pct=True, d=2):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "n/a"
    return f"{x * 100:.{d}f}%" if pct else f"{x:.{d}f}"


def write_md(results: dict, stats: dict, san: dict, dl: dict, path: Path) -> None:
    L = []
    A = L.append
    A("# EXP-002 結果：加密貨幣橫斷面動能（只做多）\n")
    A("> 規格：`EXP-002-xsmom-crypto.md`（預先登記，合格標準與參數未改動；模稜兩可處見文末與規格「偏離記錄」）。無風險利率 = 0。"
      "Sharpe/Sortino/波動/IR 皆用持有期（週一收盤到下週一收盤）報酬、年化因子 52；CAGR、最大回撤、Calmar 用日淨值。")
    A("> 資料來源：Binance Public Data（data.binance.vision，現貨月檔日 K，sha256 驗證）。\n")
    o = results.get("OOS")
    if o:
        v = o["verdict"]
        A("## 合格判定（OOS，滑價 0.10%）\n")
        A("| # | 條件 | 數字 | 判定 |\n|---|---|---|---|")
        A(f"| P1 | Sharpe 策略 > B1 | 策略 {v['P1']['strat']:.3f} vs B1 {v['P1']['b1']:.3f} | **{'PASS' if v['P1']['pass'] else 'FAIL'}** |")
        A(f"| P2 | MCPT p < 0.05（n=2000, seed=20261028） | p = {v['P2']['p']:.4f}（(k+1)/(n+1) = {v['P2']['p_plus1']:.4f}） | **{'PASS' if v['P2']['pass'] else 'FAIL'}** |")
        A(f"| P3 | Sharpe 策略 > B2（BTC 買進持有） | 策略 {v['P3']['strat']:.3f} vs B2 {v['P3']['b2']:.3f} | **{'PASS' if v['P3']['pass'] else 'FAIL'}** |")
        allp = all(v[k]["pass"] for k in ("P1", "P2", "P3"))
        A(f"\n**總判定：{'三條全過（撐得住）' if allp else '未全過（不合格），依規格不調參重跑'}**\n")
    A("## 結果表（IS / OOS 並排；扣成本，滑價 0.10%）\n")
    segs = [s for s in ("IS", "OOS") if s in results]
    rows = [("CAGR", "cagr", True), ("年化波動", "ann_vol", True), ("Sharpe", "sharpe", False), ("Sortino", "sortino", False),
            ("最大回撤", "mdd", True), ("Calmar", "calmar", False), ("週勝率", "win_rate", True),
            ("年化單邊換手", "turnover_ann", True), ("成本拖累（CAGR，毛-淨）", "cost_drag", True),
            ("平均持有數", "avg_holdings", False), ("平均股票池數", "avg_pool", False)]
    A("| 指標 | " + " | ".join(f"{s} 策略 | {s} B1 | {s} B2(BTC)" for s in segs) + " |")
    A("|---|" + "---|" * (3 * len(segs)))
    for lab, k, pct in rows:
        cells = []
        for s in segs:
            for g in ("strategy", "b1", "b2_btc"):
                val = results[s][g].get(k)
                cells.append(_f(val, pct, 2) if val is not None else "-")
        A(f"| {lab} | " + " | ".join(cells) + " |")
    A("")
    A("| 相對基準 | " + " | ".join(segs) + " |\n|---|" + "---|" * len(segs))
    for lab, k, pct in (("超額 CAGR vs B1", "excess_cagr_vs_b1", True), ("超額 CAGR vs B2", "excess_cagr_vs_b2", True),
                        ("超額週報酬均值×52 vs B1", "excess_mean_ann_vs_b1", True), ("超額週報酬均值×52 vs B2", "excess_mean_ann_vs_b2", True),
                        ("IR vs B1", "ir_vs_b1", False), ("IR vs B2", "ir_vs_b2", False), ("beta vs B1", "beta_vs_b1", False)):
        A(f"| {lab} | " + " | ".join(_f(results[s]["strategy"][k], pct, 3 if not pct else 2) for s in segs) + " |")
    A("")
    A("| MCPT（統計量＝相對 B1 週超額報酬均值×52） | " + " | ".join(segs) + " |\n|---|" + "---|" * len(segs))
    A("| 實際值 | " + " | ".join(f"{_f(results[s]['mcpt']['actual'])}" for s in segs) + " |")
    A("| 置換均值 / 95 分位 | " + " | ".join(f"{_f(results[s]['mcpt']['perm_mean'])} / {_f(results[s]['mcpt']['perm_p95'])}" for s in segs) + " |")
    A("| p 值（≥ 實際的比例） | " + " | ".join(f"{results[s]['mcpt']['p']:.4f}（k={results[s]['mcpt']['k']}）" for s in segs) + " |")
    A("")
    A("各段起訖（績效各自從該段第一個成交日起算、從現金建倉）：" + "；".join(
        f"{s}：首次成交 {results[s]['first_trade']}，結束 {results[s]['last_day']}，調倉 {results[s]['n_rebalances']} 次" for s in segs) + "\n")
    A("## 滑價 0.25% 敏感度（只報告，不作判定）\n")
    A("| 段 | 策略 CAGR | 策略 Sharpe | 策略 MDD | B1 CAGR | B1 Sharpe | B1 MDD | Sharpe>B1 | Sharpe>B2 |\n|---|---|---|---|---|---|---|---|---|")
    for s in segs:
        x = results[s]["slip25"]
        A(f"| {s} | {_f(x['strat']['cagr'])} | {x['strat']['sharpe']:.3f} | {_f(x['strat']['mdd'])} | {_f(x['b1']['cagr'])} | "
          f"{x['b1']['sharpe']:.3f} | {_f(x['b1']['mdd'])} | {x['sharpe_gt_b1']} | {x['sharpe_gt_b2']} |")
    A("")
    A("## 年度報酬\n")
    for s in segs:
        an = results[s]["annual"]
        A(f"**{s}**\n\n| 年 | 策略 | B1 | BTC |\n|---|---|---|---|")
        for y in sorted(an["strat"]):
            A(f"| {y} | {_f(an['strat'][y])} | {_f(an['b1'][y])} | {_f(an['b2'][y])} |")
        A("")
    A("圖檔：`exp002/equity.png`、`drawdown.png`、`mcpt.png`、`annual.png`；原始數字 `exp002/results.json`。\n")
    A("## 每年股票池代表幣（調倉日出現次數最多的 8 個 base，括號為出現週數/該年調倉週數）\n")
    for s in segs:
        A(f"**{s}**\n")
        for y, lst in results[s]["pool_top_bases"].items():
            A(f"- {y}：{', '.join(lst)}")
        A("")
    A("## 穩定幣 CV 檢查（股票池中過去 60 天收盤價變異係數 < 1% 的 base；不影響選股）\n")
    for s in segs:
        fl = results[s]["cv_flags"]
        if fl:
            A(f"- {s}：" + "；".join(f"{b}（{d['weeks']} 週，{d['first']}~{d['last']}）" for b, d in fl.items()))
        else:
            A(f"- {s}：無")
    A("")
    A("## 資料檢查\n")
    A(f"- 下載：{dl.get('symbols', 'n/a')} 個 USDT 交易對、{dl.get('files', 'n/a')} 個月檔，checksum 失敗 {dl.get('bad', 'n/a')}。")
    A(f"- 載入：{stats['n_symbols']} 個交易對 -> 缺口切分後 {stats['n_assets_after_split']} 個資產（其中 {stats['n_assets_from_gap_split']} 個為缺口後新資產）；"
      f"{stats['n_rows']} 列日 K，{stats['first_date']} ~ {stats['last_date']}。")
    A(f"- BTCUSDT 全期：{san['BTC']['first']} 起累積 {san['BTC']['total_multiple']:.2f} 倍（年化 {_f(san['BTC']['cagr_full'])}）。")
    A(f"- 被槓桿代幣規則排除的 base（{len(stats['leverage_excluded_bases'])} 個，供人工檢查有無誤殺）：" + ", ".join(stats["leverage_excluded_bases"]))
    A(f"- 單日報酬 > +300% 或 < −80% 的資料點共 {stats['n_anomalies']} 筆（未做任何修正；規格未授權）。前 25 筆：")
    for a in stats["anomalies"][:25]:
        A(f"  - {a['asset']} {a['date']} {a['ret']:+.1%}")
    A("\n**每年股票池檔數（調倉日池大小）與當年最後一根日 K 落在該年的資產數（下架/停止）**\n\n| 年 | 平均 | 最小 | 最大 | 下架資產數 |\n|---|---|---|---|---|")
    for y, d in stats["pool_per_year"].items():
        A(f"| {y} | {d['mean']:.1f} | {d['min']} | {d['max']} | {stats['delisted_assets_per_year'].get(y, 0)} |")
    A("")
    A("## 保守解讀與實作選擇（規格模稜兩可處；亦追加於規格「偏離記錄」）\n")
    A(IMPL_NOTES)
    A("\n## 已知限制\n")
    A("""- Binance 現貨日 K 的收盤價是單一交易所價格，下架前最後數日常有流動性枯竭與極端價；以「最後收盤價結算成現金」假設可以在該價出場，實際不一定成交。
- 成本以比例近似，未模擬市場衝擊；股票池以 30 日成交額前 30 名為限，但小額資金之外的容量未評估。
- 2018–2026 只含少數完整週期（2018、2022 熊市）；結果對時期高度敏感，且 OOS 內事件（LUNA、FTX）屬極端樣本。
- 本實驗只做多、不做空，無資金費率、無借貸利息；現金報酬 0。
- 交易對清單來自 Binance 月檔目錄；未列在目錄內的交易對（例如從未產出月檔者）不在樣本內。""")
    path.write_text("\n".join(L) + "\n", encoding="utf-8")


IMPL_NOTES = """1. **缺口判定**：「連續 ≥ 7 天沒有日 K」解讀為缺了 7 天以上，即相鄰兩根日 K 日期差 ≥ 8 天才切成新資產（日期差 7 天＝缺 6 天，不切）。新資產第一天沒有報酬，歷史天數與成交額重新累積。
2. **短缺口（< 7 天）**：同一資產；缺 K 日價格向前填補（日報酬 0），資料恢復日報酬為跨短缺口的實際漲跌。訊號窗口內有缺 K 則該資產當週不入選；成交日缺 K 則不成交。
3. **股票池規則 2 的「≥ 60 天日 K」**：指該資產累積有日 K 的天數（含訊號日）≥ 60，不是日曆天。
4. **30 日平均成交額**：訊號日（含）往前 30 個日曆日，缺 K 日以 0 計入再除以 30（較保守）；不足 30 日曆日的歷史不具資格。排名同值以資產欄位順序決勝。
5. **槓桿代幣規則**：stem 是否為 USDT 交易對 base，以「目錄內全部 USDT 交易對（含已下架、不分時間）」判定，不是當日已知清單；這是靜態清單，不影響報酬資料的時序，但嚴格說不是 point-in-time。被排除的 base 全列於上方供人工檢查。
6. **訊號有效性**：訊號日往前 21 天（t−21 … t 共 22 根）都必須有日 K。前 1/3 的「1/3」以「池內有有效訊號的資產數」為基數，四捨五入（0.5 進位）、至少 3 個、不超過有效數；有效數 < 3 時全部持有。B1 是整個股票池（含無有效訊號者）等權。策略與 B1 要求相同的調倉日網格（池內至少一檔有有效訊號）。
7. **成交與權重**：週日收盤算訊號、週一收盤成交；成交日無日 K 的資產不成交、維持原權重；賣出不足以支應買進時買進按比例縮減，剩餘為現金（報酬 0）。已下架資產以最後收盤結算成現金（免成本）。
8. **成本**：手續費 0.10% + 滑價 0.10% 單邊（買賣皆是），無印花稅。敏感度為滑價 0.25%。
9. **指標頻率**：Sharpe/Sortino/波動/IR/週勝率用持有期報酬（週一→下週一；最後一期到段末，可能不足一週）、年化 52；換手率不含首次建倉（單邊＝買賣金額平均）；成本拖累＝零成本 CAGR − 含成本 CAGR。CAGR 以日曆日/365.25 換算年數。
10. **IS / OOS 各自獨立建倉**：不承接 IS 持倉；第一個成交日付首次買進成本。IS 首筆訊號為 2018-07-01（週日），成交 2018-07-02；OOS 首筆訊號為 2022-01-02，成交 2022-01-03。B2 同日買進並付一次買進成本。
11. **P2 判定**：同時要求 p（比例）與 (k+1)/(n+1) 皆 < 0.05。MCPT 中 B1 的週報酬固定為實際值，只置換策略；置換範圍是調倉日股票池內的資產（含當週無法成交者），池外殘留部位維持實際報酬。
12. **P3**：規格寫「Sharpe 策略 > B2」，B2 的週報酬使用與策略相同的調倉網格（週一→週一）計算 Sharpe。
13. **時間戳**：位數 ≥ 16 視為微秒（2025-01 起），否則毫秒；CSV 首欄非數字時視為 header 略過；日期取 UTC 日。同一 (交易對, 日期) 重複時取第一筆。
14. **穩定幣 CV 檢查**：對 IS/OOS 各自調倉日的股票池成員計算（至少 30 筆有 K 的觀測），僅報告。"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--segments", default="IS,OOS")
    a = ap.parse_args()
    from engine.data import binance_spot as bs
    df = bs.load_all()
    ctx = prepare(df)
    san = sanity(ctx)
    stats = data_stats(df, ctx)
    print("sanity", json.dumps(san), "assets", stats["n_assets_after_split"], "last", stats["last_date"], flush=True)
    results = {}
    for s in a.segments.split(","):
        results[s] = run_segment(s, ctx)
        v = results[s]["verdict"]
        r = results[s]
        print(s, {k: x["pass"] for k, x in v.items()}, "sharpe", r["strategy"]["sharpe"], r["b1"]["sharpe"], r["b2_btc"]["sharpe"],
              "p", r["mcpt"]["p"], flush=True)
    if set(results) == {"IS", "OOS"}:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        make_plots(results, OUT_DIR)
        dlp = bs.DATA_DIR / "download-summary.json"
        dl = json.loads(dlp.read_text(encoding="utf-8")) if dlp.exists() else {}
        dl.pop("bad_keys", None)
        dstat = bs.dir_stats()
        lp = bs.DATA_DIR / "load-stats.json"
        lstat = json.loads(lp.read_text(encoding="utf-8")) if lp.exists() else {}
        clean = {s: {k: v for k, v in r.items() if k != "_series"} for s, r in results.items()}
        clean["data_stats"] = {k: v for k, v in stats.items() if k != "anomalies"}
        clean["data_stats"]["anomalies_top100"] = stats["anomalies"][:100]
        clean["download"] = {"summary": dl, "dir": dstat, "load": lstat}
        clean["sanity"] = san
        (OUT_DIR / "results.json").write_text(json.dumps(clean, ensure_ascii=False, indent=2, default=float), encoding="utf-8")
        write_md(results, stats, san, dl, ROOT / "docs" / "experiments" / "EXP-002-results.md")
        print("written")
    else:
        print(json.dumps({s: {k: v for k, v in r.items() if k not in ("_series",)} for s, r in results.items()},
                         ensure_ascii=False, indent=1, default=float)[:6000])


if __name__ == "__main__":
    main()
