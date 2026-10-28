"""決定性「合成示範資料」產生器（固定種子）。**全部是假資料，不是任何真實行情**，
只為展示介面與驗證引擎；網站上所有由它產生的結果一律標 `示範資料`、validation_level 維持 L0。

兩個市場：DEMO_TW（約 250 檔、台股成本、台股法定財報截止日）、DEMO_US（約 400 檔、美股成本）。
交易日為 2010-01-04 ~ 2025-12-31 的營業日（不含各國假日，這是合成日曆）。

內嵌的合成溢酬（刻意很弱；每月月初用「上月底以前」的資訊決定，所以產生器本身沒有前視）：
  * 動能 12-1：預期月報酬 +0.25% x z(12-1 動能)
  * 規模：    -0.20% x z(log 市值)
  * 帳面市值比：+0.25% x z(log B/M，用潛在帳面價值)
  * 短期反轉： -0.10% x z(上月報酬)
  * 獲利品質（毛利/資產）：+0.15% x z(q)，q 為個股固定潛在品質
個股特異波動日度約 2%（月度約 9%），所以 Rank IC 約 0.01~0.03，圖表有訊號但不是純雜訊。
低波動、流動性（ILLIQ）、營收類因子在這個資料中沒有被刻意植入溢酬。

資料結構重點：
  * 價格：市場因子(波動 regime) + 10 個產業因子 + 個股雜訊；close_adj 為含息還原（以最後交易日為錨），
    close_raw = close_adj / f_t（f_t 為股息累積還原因子）；open/high/low/vwap 與 close_adj 同還原口徑。
  * 台股漲跌幅限制：2015-06-01 前 ±7%，之後 ±10%。
  * 存活者偏誤：約 18% 個股中途新上市、約 12% 中途下市（其中一半最後一日 -30% 當作下市損失），
    下市/未上市的格子為 NaN，股票池由 preprocess 的「上市未滿 60 日排除」處理。
  * 會計欄位：季頻潛在值 -> 流量取 TTM、存量取期末 -> 依 PIT 規則落後後 forward-fill。
    台股用法定截止日（Q1 5/15、Q2 8/14、Q3 11/14、年報次年 3/31，截止日「之後」第一個交易日生效）；
    美股季報落後 45 天、年報落後 90 天。簡化：新上市股在上市日之前已公告的最近一季數字會被 ffill 帶入。
  * monthly_revenue 只有 DEMO_TW（美股無月營收揭露）；每月 10 日之後第一個交易日生效。
  * shares_outstanding 有少量增資事件（階梯式上調），market_cap = close_raw x shares_outstanding。
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .base import COST_TW, COST_US, MarketData

START, END = "2010-01-04", "2025-12-31"
SEEDS = {"DEMO_TW": 20100104, "DEMO_US": 20250101}
DEFAULT_N = {"DEMO_TW": 250, "DEMO_US": 400}

PREMIA = {  # 月預期報酬 / 1 個標準差
    "mom_12_1": 0.0025, "size": -0.0020, "bm": 0.0025, "rev_1m": -0.0010, "quality_gpoa": 0.0015,
}
LABELS = {
    "DEMO_TW": "示範台股（合成資料，非真實行情）",
    "DEMO_US": "示範美股（合成資料，非真實行情）",
}
BENCH = "股票池等權（示範資料）"


def _z(x: np.ndarray, mask: np.ndarray) -> np.ndarray:
    v = np.where(mask, x, np.nan)
    m, s = np.nanmean(v), np.nanstd(v)
    z = (v - m) / (s if s > 0 else 1.0)
    return np.where(mask, z, 0.0)


def _place(vals_q: np.ndarray, eff_pos: np.ndarray, T: int, mask: np.ndarray, idx, cols) -> pd.DataFrame:
    """把季（月）值放在生效日列再 forward-fill；上市前/下市後設 NaN。"""
    arr = np.full((T, vals_q.shape[1]), np.nan)
    for q in range(vals_q.shape[0]):
        if eff_pos[q] < T:
            arr[eff_pos[q]] = vals_q[q]
    df = pd.DataFrame(arr, index=idx, columns=cols).ffill()
    return df.where(mask)


def make_demo_market(market_id: str, n_stocks: int | None = None, seed: int | None = None,
                     start: str = START, end: str = END) -> MarketData:
    if market_id not in SEEDS:
        raise ValueError(market_id)
    tw = market_id == "DEMO_TW"
    N = n_stocks or DEFAULT_N[market_id]
    rng = np.random.default_rng(SEEDS[market_id] if seed is None else seed)
    dates = pd.bdate_range(start, end)
    T = len(dates)
    cols = [f"{'T' if tw else 'U'}{i:04d}" for i in range(N)]

    # ---- 上市 / 下市 ----
    first = np.zeros(N, dtype=int)
    late = rng.random(N) < 0.18
    if T > 1100:
        first[late] = rng.integers(260, T - 800, late.sum())
    last = np.full(N, T - 1, dtype=int)
    dl = rng.random(N) < 0.12
    if T > 1100:
        for i in np.where(dl)[0]:
            lo, hi = first[i] + 300, T - 60
            if hi > lo:
                last[i] = rng.integers(lo, hi)
    delisted = last < T - 1
    drop30 = delisted & (rng.random(N) < 0.5)
    pos = np.arange(T)[:, None]
    alive = (pos >= first[None, :]) & (pos <= last[None, :])

    # ---- 日報酬（不含溢酬）----
    K = 10
    lv = np.zeros(T)
    eps = rng.normal(size=T)
    for t in range(1, T):
        lv[t] = 0.98 * lv[t - 1] + 0.12 * eps[t]
    mkt = 0.0003 + 0.009 * np.exp(lv) * rng.normal(size=T)
    ind_ret = 0.005 * rng.normal(size=(T, K))
    ind_i = rng.integers(0, K, N)
    beta = np.clip(rng.normal(1.0, 0.25, N), 0.3, 1.8)
    sig = np.exp(rng.normal(np.log(0.022 if tw else 0.018), 0.25, N))
    tdraw = rng.standard_t(5, size=(T, N)) / np.sqrt(5.0 / 3.0)
    logr = beta[None, :] * mkt[:, None] + ind_ret[:, ind_i] + sig[None, :] * tdraw
    if tw:
        lim = np.where(dates < pd.Timestamp("2015-06-01"), 0.068, 0.095)[:, None]
    else:
        lim = np.full((T, 1), 0.35)

    price0 = np.clip(np.exp(rng.normal(np.log(35.0 if tw else 45.0), 0.6, N)), 3.0, 500.0)
    mcap0 = np.exp(rng.normal(np.log(2e10 if tw else 3e9), 1.3, N))
    shares0 = mcap0 / price0
    logsh = np.log(shares0)
    lm0 = np.log(price0) + logsh
    lb0 = lm0 + rng.normal(0.0, 0.5, N)
    g_book = rng.normal(0.05, 0.03, N)
    qual = rng.normal(size=N)

    logp = np.zeros((T, N))
    month_key = dates.year * 12 + dates.month
    starts = np.r_[0, np.where(np.diff(month_key) != 0)[0] + 1, T]
    P = PREMIA
    for bi in range(len(starts) - 1):
        a, b = starts[bi], starts[bi + 1]
        block = logr[a:b].copy()
        if a >= 1:
            p = a - 1
            mask = alive[p]
            prem = np.zeros(N)
            lmc = logp[p] + logsh
            prem += P["size"] * _z(lmc, mask)
            bm = lb0 + 0.5 * g_book * p / 252.0 + 0.5 * (lmc - lm0) - lmc
            prem += P["bm"] * _z(bm, mask)
            prem += P["quality_gpoa"] * _z(qual, mask)
            if p >= 252:
                prem += P["mom_12_1"] * _z(logp[p - 21] - logp[p - 252], mask)
            if p >= 21:
                prem += P["rev_1m"] * _z(logp[p] - logp[p - 21], mask)
            block += prem[None, :] / (b - a)
        block = np.clip(block, -lim[a:b], lim[a:b])
        for i in np.where(drop30 & (last >= a) & (last < b))[0]:
            block[last[i] - a, i] = np.log(0.7)
        logr[a:b] = block
        if a == 0:
            logp[:b] = np.log(price0)[None, :] + np.cumsum(block, axis=0)
        else:
            logp[a:b] = logp[a - 1] + np.cumsum(block, axis=0)
    close_adj = np.exp(logp)

    # 還原口徑
    dy = rng.uniform(0.01, 0.05, N) if tw else rng.uniform(0.0, 0.04, N)
    f_t = np.exp(-dy[None, :] * (last[None, :] - pos) / 252.0)
    close_raw = close_adj / f_t

    prev = np.vstack([close_adj[:1], close_adj[:-1]])
    open_ = prev * np.exp(0.35 * logr + 0.004 * rng.normal(size=(T, N)))
    high = np.maximum(open_, close_adj) * np.exp(np.abs(rng.normal(0, 0.006, (T, N))))
    low = np.minimum(open_, close_adj) * np.exp(-np.abs(rng.normal(0, 0.006, (T, N))))
    vwap = (open_ + high + low + close_adj) / 4.0 * np.exp(rng.normal(0, 0.001, (T, N)))

    # 股本：階梯式增資
    mult = np.ones((T, N))
    n_ev = rng.poisson(0.4, N)
    for i in np.where(n_ev > 0)[0]:
        for d in rng.integers(0, T, n_ev[i]):
            mult[d:, i] *= rng.uniform(1.03, 1.15)
    shares = shares0[None, :] * mult
    turn_base = np.exp(rng.normal(np.log(0.004), 0.5, N))
    volume = (shares * turn_base[None, :] * np.exp(0.3 * lv)[:, None]
              * np.exp(rng.normal(0, 0.35, (T, N))) * (1.0 + 8.0 * np.abs(logr)))
    volume = np.round(volume)
    turnover_value = volume * vwap / f_t
    market_cap = close_raw * shares

    def W(a, mask=alive):
        return pd.DataFrame(np.where(mask, a, np.nan), index=dates, columns=cols)

    data = {
        "close_adj": W(close_adj), "close_raw": W(close_raw), "open": W(open_), "high": W(high),
        "low": W(low), "vwap": W(vwap), "volume": W(volume), "turnover_value": W(turnover_value),
        "shares_outstanding": W(shares), "market_cap": W(market_cap),
    }

    # ---- 季頻會計（2008Q1 起，讓 2010 年初就有 TTM）----
    qends = pd.date_range("2008-03-31", end, freq="QE")
    Q = len(qends)
    ty = np.array([(q - dates[0]).days / 365.0 for q in qends])
    pq = np.clip(np.searchsorted(dates.values, qends.values, side="right") - 1, 0, T - 1)
    lmc_q = logp[pq] + logsh[None, :]
    # 基本面潛在規模 fund（與價格無關的成長 + 隨機漫步）；帳面價值另含 0.5 倍價格變動（讓 B/M 有橫斷面意義）
    walk = np.cumsum(rng.normal(0, 0.03, (Q, N)), axis=0)
    fund = np.exp(lb0[None, :] + 0.5 * g_book[None, :] * ty[:, None] + walk)
    book = fund * np.exp(0.5 * (lmc_q - lm0[None, :]) + rng.normal(0, 0.02, (Q, N)))
    eqr = rng.uniform(0.15, 0.30, N)
    ta = fund / eqr[None, :] * np.exp(rng.normal(0, 0.02, (Q, N)))
    ta = np.maximum(ta, book / 0.95)
    turn = rng.uniform(0.5, 1.2, N)
    rev_q = ta * turn[None, :] / 4.0 * np.exp(rng.normal(0, 0.08, (Q, N)))
    gm = np.clip((0.30 + 0.08 * qual) / turn, 0.05, 0.8)
    gp_q = rev_q * gm[None, :] * np.exp(rng.normal(0, 0.03, (Q, N)))
    cogs_q = rev_q - gp_q
    sga_q = rev_q * rng.uniform(0.05, 0.15, N)[None, :] * np.exp(rng.normal(0, 0.05, (Q, N)))
    ltd = ta * rng.uniform(0.05, 0.3, N)[None, :] * np.exp(rng.normal(0, 0.05, (Q, N)))
    int_q = ltd * 0.03 / 4.0
    ni_q = (gp_q - sga_q - int_q) * 0.75 * np.exp(rng.normal(0, 0.05, (Q, N)))
    ocf_q = ni_q * rng.uniform(0.9, 1.3, N)[None, :] + ta * rng.normal(0, 0.003, (Q, N))
    ca = ta * rng.uniform(0.3, 0.5, N)[None, :] * np.exp(rng.normal(0, 0.03, (Q, N)))
    cl = ta * rng.uniform(0.15, 0.3, N)[None, :] * np.exp(rng.normal(0, 0.03, (Q, N)))

    def ttm(x):
        out = np.full_like(x, np.nan)
        for q in range(3, Q):
            out[q] = x[q - 3:q + 1].sum(axis=0)
        return out

    # 生效日（PIT）
    deadlines = []
    for qe in qends:
        if tw:
            dd = {3: (qe.year, 5, 15), 6: (qe.year, 8, 14), 9: (qe.year, 11, 14), 12: (qe.year + 1, 3, 31)}[qe.month]
            deadlines.append(pd.Timestamp(*dd))
        else:
            deadlines.append(qe + pd.Timedelta(days=90 if qe.month == 12 else 45))
    eff_pos = np.searchsorted(dates.values, np.array(deadlines, dtype="datetime64[ns]"), side="right")
    fields = {
        "revenue": ttm(rev_q), "cogs": ttm(cogs_q), "gross_profit": ttm(gp_q), "sga_expense": ttm(sga_q),
        "interest_expense": ttm(int_q), "net_income": ttm(ni_q), "operating_cash_flow": ttm(ocf_q),
        "book_equity": book, "total_assets": ta, "long_term_debt": ltd, "current_assets": ca,
        "current_liabilities": cl,
    }
    for k, v in fields.items():
        data[k] = _place(v, eff_pos, T, alive, dates, cols)

    if tw:  # 月營收：每月 10 日後第一個交易日生效
        mends = pd.date_range("2008-01-31", end, freq="ME")
        qi = np.clip(np.searchsorted(qends.values, mends.values, side="left"), 0, Q - 1)
        season = 0.15 * np.sin(2 * np.pi * (mends.month.values - 1) / 12.0)
        mrev = rev_q[qi] / 3.0 * np.exp(season)[:, None] * np.exp(rng.normal(0, 0.12, (len(mends), N)))
        eff_m = np.searchsorted(dates.values, (mends + pd.Timedelta(days=10)).values, side="right")
        data["monthly_revenue"] = _place(mrev, eff_m, T, alive, dates, cols)

    return MarketData(
        market_id=market_id, label=LABELS[market_id], data=data,
        cost=COST_TW if tw else COST_US, benchmark=BENCH, is_demo=True,
        data_source="合成示範資料（固定種子，非真實行情）",
        universe_desc=("合成台股池，含中途上市/下市股；上市未滿 60 交易日排除" if tw
                       else "合成美股池，含中途上市/下市股；上市未滿 60 交易日、股價 < $5 排除"),
        min_price=None if tw else 5.0, min_age_days=60, pit_estimated=True,
        meta={"n_delisted": int(delisted.sum()), "n_late_listed": int(late.sum()),
              "premia": PREMIA, "first": first, "last": last, "latent_quality": qual},
    )
