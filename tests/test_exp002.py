"""EXP-002 單元測試：合成資料，不連網。"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))

import exp002_xsmom_crypto as E  # noqa: E402
from engine.data import binance_spot as bs  # noqa: E402
from engine.data.base import CostModel  # noqa: E402


def _long(sym_dates: dict, seed=0, vol=1e6):
    rng = np.random.default_rng(seed)
    rows = []
    for sym, ds in sym_dates.items():
        px = 100.0
        for d in ds:
            px *= 1 + rng.normal(0, 0.02)
            rows.append((sym, pd.Timestamp(d), px, vol))
    return pd.DataFrame(rows, columns=["symbol", "date", "close", "quote_volume"])


def test_gap_split():
    d0 = pd.Timestamp("2020-01-01")
    # A: 缺 6 天（差 7）不切；B: 缺 7 天（差 8）切成兩個資產
    a = list(pd.date_range(d0, periods=10)) + list(pd.date_range(d0 + pd.Timedelta(days=16), periods=5))
    b = list(pd.date_range(d0, periods=10)) + list(pd.date_range(d0 + pd.Timedelta(days=17), periods=5))
    df = _long({"AAAUSDT": a, "BBBUSDT": b})
    s = E.split_gaps(df)
    assert s[s.symbol == "AAAUSDT"]["asset"].nunique() == 1
    assert sorted(s[s.symbol == "BBBUSDT"]["asset"].unique()) == ["BBBUSDT", "BBBUSDT#2"]
    w = E.build_wide(df)
    cols = w["assets"]
    j2 = cols.index("BBBUSDT#2")
    first = w["first"][j2]
    assert np.isnan(w["R"][first, j2])                      # 跨缺口報酬不計算
    j1 = cols.index("BBBUSDT")
    assert w["last"][j1] == 9
    assert np.isnan(w["P"][12, j1])                          # 舊資產下架後無價格
    ja = cols.index("AAAUSDT")
    assert np.isfinite(w["R"][12, ja]) and w["R"][12, ja] == 0.0   # 短缺口填補日報酬 0


def test_leverage_rule():
    syms = ["BTCUSDT", "BTCUPUSDT", "BTCDOWNUSDT", "ETHUSDT", "ETHBULLUSDT", "ETHBEARUSDT", "JUPUSDT", "SUPERUSDT", "UPUSDT"]
    ex = E.leverage_excluded(syms)
    assert ex == {"BTCUP", "BTCDOWN", "ETHBULL", "ETHBEAR"}
    assert "JUP" not in ex and "BTC" not in ex and "UP" not in ex
    # J 若恰好是交易對則 JUP 會被排除（規格字面行為）
    assert "JUP" in E.leverage_excluded(syms + ["JUSDT"])


def _wide_random(T=200, N=8, seed=1):
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2020-01-01", periods=T)
    rows = []
    for j in range(N):
        px = 100.0
        for d in dates:
            px *= 1 + rng.normal(0, 0.03)
            rows.append((f"C{j}USDT", d, px, 1e6 * (j + 1)))
    rows.append(("BTCUSDT", dates[0], 1.0, 1.0))      # 讓 prepare 取得 BTC 欄位
    df = pd.DataFrame(rows, columns=["symbol", "date", "close", "quote_volume"])
    bt = [("BTCUSDT", d, 100 * (1 + 0.001 * i), 5e6) for i, d in enumerate(dates)]
    df = df[df.symbol != "BTCUSDT"]
    return pd.concat([df, pd.DataFrame(bt, columns=df.columns)], ignore_index=True)


SMALL = E.Params(min_hist=20, vol_win=10, top_n=6, min_hold=2)


def test_no_lookahead_signals():
    df = _wide_random()
    full = E.prepare(df, SMALL)
    t = 150
    cut = df[df.date <= full["dates"][t]]
    part = E.prepare(cut, SMALL)
    # 同欄位順序以名稱對齊
    for name in part["cols"]:
        jf, jp = full["cols"].index(name), part["cols"].index(name)
        assert full["pool"][t, jf] == part["pool"][t, jp]
        a, b = full["sig"][t, jf], part["sig"][t, jp]
        assert (np.isnan(a) and np.isnan(b)) or abs(a - b) < 1e-12


def test_no_lookahead_simulation():
    """改動第一期成交日 u 之後的所有價格，第一期的選股與持有權重不得改變。"""
    df = _wide_random()
    ctx = E.prepare(df, SMALL)
    seg_s, seg_e = 60, 180

    def run(c):
        return E.simulate(c["CP"], c["traded"], c["last_idx"], c["pool"], c["sig"], c["rebal_t"], seg_s, seg_e,
                          E.COST_BASE, "mom", SMALL)
    base = run(ctx)
    u = base["u"][0]
    df2 = df.copy()
    m = df2.date > ctx["dates"][u]
    df2.loc[m, "close"] = df2.loc[m, "close"] * np.random.default_rng(5).uniform(0.5, 2.0, m.sum())
    ctx2 = E.prepare(df2, SMALL)
    alt = run(ctx2)
    p1, p2 = base["periods"][0], alt["periods"][0]
    assert sorted(p1["pool_idx"]) == sorted(p2["pool_idx"])
    assert p1["n_hold"] == p2["n_hold"] and abs(p1["cost"] - p2["cost"]) < 1e-12
    assert np.allclose(p1["wpool"], p2["wpool"])


def test_cost_calculation():
    # 第一期從現金買入：成本 = buy_rate * 買入金額（含成本後權重正規化）
    df = _wide_random()
    ctx = E.prepare(df, SMALL)
    cm = CostModel(0.001, 0.001, 0.0, 0.001)
    sim = E.simulate(ctx["CP"], ctx["traded"], ctx["last_idx"], ctx["pool"], ctx["sig"], ctx["rebal_t"], 60, 120, cm, "mom", SMALL)
    pr = sim["periods"][0]
    # 以 1 單位現金買進：花費 inc*(1+buy_rate)=1 -> inc = 1/1.002，成本 = inc*0.002
    assert abs(pr["cost"] - 0.002 / 1.002) < 1e-12
    assert abs(pr["turnover"] - 0.5 * (1 / 1.002)) < 1e-12
    # 零成本時成本為 0
    sim0 = E.simulate(ctx["CP"], ctx["traded"], ctx["last_idx"], ctx["pool"], ctx["sig"], ctx["rebal_t"], 60, 120, E.COST_ZERO, "mom", SMALL)
    assert all(p["cost"] == 0.0 for p in sim0["periods"])
    # 滑價 0.25% 的成本較高
    simh = E.simulate(ctx["CP"], ctx["traded"], ctx["last_idx"], ctx["pool"], ctx["sig"], ctx["rebal_t"], 60, 120, E.COST_SLIP25, "mom", SMALL)
    assert sum(p["cost"] for p in simh["periods"]) > sum(p["cost"] for p in sim["periods"])


def test_delisted_position_settles_to_cash():
    d = pd.date_range("2020-01-01", periods=120)
    rows = []
    rng = np.random.default_rng(3)
    for sym, n, drift in (("AAAUSDT", 120, 0.002), ("BBBUSDT", 120, 0.0), ("CCCUSDT", 120, 0.0), ("BTCUSDT", 120, 0.0)):
        px = 100.0
        for i in range(n):
            px *= 1 + drift + rng.normal(0, 0.005)
            rows.append((sym, d[i], px, 1e6))
    df = pd.DataFrame(rows, columns=["symbol", "date", "close", "quote_volume"])
    df = df[~((df.symbol == "AAAUSDT") & (df.date > d[70]))]      # AAA 在 d[70] 下架
    ctx = E.prepare(df, E.Params(min_hist=20, vol_win=10, top_n=6, min_hold=1, frac=0.34))
    sim = E.simulate(ctx["CP"], ctx["traded"], ctx["last_idx"], ctx["pool"], ctx["sig"], ctx["rebal_t"], 50, 110,
                     E.COST_ZERO, "mom", E.Params(min_hist=20, vol_win=10, top_n=6, min_hold=1, frac=0.34))
    assert np.isfinite(sim["nav"]).all() and min(sim["nav"]) > 0


def test_mcpt_null_not_significant():
    """無訊號合成資料：隨機選股，p 值不應顯著（多個 seed 的 p 不應大量 <0.05）。"""
    ps = []
    for seed in range(6):
        df = _wide_random(T=420, N=12, seed=seed + 10)
        prm = E.Params(min_hist=20, vol_win=10, top_n=12, min_hold=3)
        ctx = E.prepare(df, prm)
        args = (ctx["CP"], ctx["traded"], ctx["last_idx"], ctx["pool"], ctx["sig"], ctx["rebal_t"], 40, 410)
        S = E.simulate(*args, E.COST_BASE, "mom", prm)
        B = E.simulate(*args, E.COST_BASE, "all", prm)
        mc = E.mcpt(S["periods"], np.array([x["ret"] for x in B["periods"]]), n_perm=500, seed=E.SEED)
        ps.append(mc["p"])
        assert 0.0 <= mc["p"] <= 1.0 and mc["p_plus1"] >= mc["p"]
    assert np.mean(np.array(ps) < 0.05) <= 1 / 3
    assert 0.1 < np.mean(ps) < 0.9


def test_mcpt_runs_on_trending_data():
    """有趨勢的合成資料：流程可跑並回傳有限值。"""
    rng = np.random.default_rng(0)
    T, N = 900, 12
    dates = pd.date_range("2020-01-01", periods=T)
    base = rng.normal(0, 0.02, (T, N))
    rows = []
    for j in range(N):
        px, trend = 100.0, 0.0
        for i, dt in enumerate(dates):
            if i % 7 == 0:
                trend = rng.normal(0, 0.01)
            px *= 1 + trend + rng.normal(0, 0.003)
            rows.append((f"C{j}USDT", dt, px, 1e6))
    df = pd.DataFrame(rows, columns=["symbol", "date", "close", "quote_volume"])
    df = pd.concat([df, df[df.symbol == "C0USDT"].assign(symbol="BTCUSDT")], ignore_index=True)
    prm = E.Params(min_hist=20, vol_win=10, top_n=12, min_hold=3, lookback=7)
    ctx = E.prepare(df, prm)
    args = (ctx["CP"], ctx["traded"], ctx["last_idx"], ctx["pool"], ctx["sig"], ctx["rebal_t"], 40, 890)
    S = E.simulate(*args, E.COST_BASE, "mom", prm)
    B = E.simulate(*args, E.COST_BASE, "all", prm)
    mc = E.mcpt(S["periods"], np.array([x["ret"] for x in B["periods"]]), n_perm=500, seed=E.SEED)
    assert np.isfinite(mc["actual"])           # 趨勢每 7 天重抽，動能訊號強度不保證；只驗證流程可跑並回傳有限值


def test_select_mom_rounding():
    pool = np.ones(9, bool)
    sig = np.arange(9, dtype=float)
    assert list(E.select_mom(pool, sig)) == [8, 7, 6]            # 9/3=3
    pool = np.ones(10, bool)
    assert len(E.select_mom(pool, np.arange(10.0))) == 3          # round(3.33)=3
    pool = np.ones(5, bool)
    assert len(E.select_mom(pool, np.arange(5.0))) == 3           # round(1.67)=2 -> 至少 3
    pool = np.ones(2, bool)
    assert len(E.select_mom(pool, np.arange(2.0))) == 2           # 不足 3 個：全拿
    sig = np.array([np.nan, 1.0, 2.0, 3.0, 4.0, 5.0])
    assert list(E.select_mom(np.ones(6, bool), sig)) == [5, 4, 3]  # NaN 不入選


def test_pool_rules():
    d = pd.date_range("2020-01-01", periods=100)
    rows = []
    rng = np.random.default_rng(2)
    spec = {"AAAUSDT": 5e6, "BBBUSDT": 4e6, "CCCUSDT": 3e6, "USDCUSDT": 9e9, "BTCUPUSDT": 9e9, "BTCUSDT": 1e8}
    for sym, v in spec.items():
        px = 100.0
        for dt in d:
            px *= 1 + rng.normal(0, 0.02)
            rows.append((sym, dt, px, v))
    # 新幣：只有最後 30 天 -> 歷史 < 60 天，不入池
    px = 10.0
    for dt in d[-30:]:
        px *= 1.01
        rows.append(("NEWUSDT", dt, px, 1e10))
    df = pd.DataFrame(rows, columns=["symbol", "date", "close", "quote_volume"])
    ctx = E.prepare(df, E.Params(top_n=3))
    t = 99
    names = {ctx["w"]["base"][j] for j in np.nonzero(ctx["pool"][t])[0]}
    assert names == {"BTC", "AAA", "BBB"}          # USDC/BTCUP 被排除、NEW 歷史不足、只取前 3


def test_timestamp_units_and_header(tmp_path):
    ms = 1735689600000                  # 2025-01-01 00:00:00 UTC（毫秒）
    us = 1735689600000000               # 同一時間（微秒）
    assert bs.parse_open_time(pd.Series([ms, us])).tolist() == [pd.Timestamp("2025-01-01")] * 2
    hdr = "open_time,open,high,low,close,volume,close_time,quote_asset_volume,count,taker_buy_base,taker_buy_quote,ignore\n"
    row = f"{us},1,2,0.5,1.5,10,{us + 86399999999},15.0,5,1,1,0\n"
    for name, body in (("h.zip", hdr + row), ("n.zip", row)):
        p = tmp_path / name
        with zipfile.ZipFile(p, "w") as z:
            z.writestr("x.csv", body)
        out = bs.read_zip(p)
        assert len(out) == 1 and out["date"].iloc[0] == pd.Timestamp("2025-01-01")
        assert out["close"].iloc[0] == 1.5 and out["quote_volume"].iloc[0] == 15.0
