"""EXP-001 單元測試：小型手造資料，不連網。"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))

import exp001_lowvol as E  # noqa: E402
from engine.data import blave_tw as bt  # noqa: E402
from engine.data.base import CostModel  # noqa: E402


def _daily(rows):
    return pd.DataFrame(rows, columns=["stock_id", "date", "close", "volume", "amount"]).assign(
        date=lambda d: pd.to_datetime(d["date"]), market="twse")


def test_event_day_return_uses_ref_price():
    days = pd.bdate_range("2024-01-01", periods=6).strftime("%Y-%m-%d")
    closes = [100, 100, 95, 96, 97, 98]
    rows = [("1111", d, c, 1000, 1e7) for d, c in zip(days, closes)]
    ev = pd.DataFrame({"date": [days[2]], "stock_id": ["1111"], "prev_close": [100.0], "ref_price": [90.0], "kind": ["twse_exright"]})
    w = bt.build_wide(_daily(rows), ev.assign(date=pd.to_datetime(ev["date"])))
    r = w["ret"]["1111"]
    assert np.isnan(r.iloc[0])
    assert abs(r.iloc[1] - 0.0) < 1e-12
    assert abs(r.iloc[2] - (95 / 90 - 1)) < 1e-12          # 事件日
    assert abs(r.iloc[3] - (96 / 95 - 1)) < 1e-12          # 一般日


def test_halt_and_event_during_halt():
    days = pd.bdate_range("2024-01-01", periods=6).strftime("%Y-%m-%d")
    vols = [1000, 1000, 0, 0, 1000, 1000]
    closes = [100, 100, 100, 100, 60, 61]
    rows = [("1111", d, c, v, 1e7 if v else 0) for d, c, v in zip(days, closes, vols)]
    ev = pd.DataFrame({"date": pd.to_datetime([days[3]]), "stock_id": ["1111"], "prev_close": [100.0],
                       "ref_price": [50.0], "kind": ["twse_exright"]})
    r = bt.build_wide(_daily(rows), ev)["ret"]["1111"]
    assert np.isnan(r.iloc[2]) and np.isnan(r.iloc[3])      # 停牌日 NaN
    assert abs(r.iloc[4] - (60 / 50 - 1)) < 1e-12           # 恢復日：基準為期間事件 ref_price
    assert abs(r.iloc[5] - (61 / 60 - 1)) < 1e-12
    # 無事件的停牌：以上一有成交日收盤為基準
    r2 = bt.build_wide(_daily(rows), ev.iloc[0:0])["ret"]["1111"]
    assert abs(r2.iloc[4] - (60 / 100 - 1)) < 1e-12


def _small_wide(T=40, N=6, seed=0):
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2020-01-01", periods=T)
    cols = [f"{1100 + i}" for i in range(N)]
    ret = pd.DataFrame(rng.normal(0, 0.01, (T, N)) * np.linspace(1, 3, N), index=dates, columns=cols)
    ret.iloc[0] = np.nan
    close = 50 * (1 + ret.fillna(0)).cumprod()
    amt = pd.DataFrame(1e7, index=dates, columns=cols)
    vol = pd.DataFrame(1000, index=dates, columns=cols)
    return {"close_raw": close, "volume": vol, "amount": amt, "ret": ret}


SMALL = E.Params(lookback=10, min_valid=8, min_hist=10, min_price=1.0, amt_win=3, min_amt=0.0, top_frac=0.5)


def test_no_lookahead_in_signal_and_selection():
    w = _small_wide()
    t = 25
    s1 = E.compute_signals(w, SMALL)
    sel1 = E.select_lowvol(s1["pool"][t], s1["vol"][t], SMALL.top_frac)
    w2 = {k: v.copy() for k, v in w.items()}
    for k in ("close_raw", "ret", "amount", "volume"):
        w2[k].iloc[t + 1:] = w2[k].iloc[t + 1:] * 7.3 + 5          # 竄改 t 之後所有資料
    s2 = E.compute_signals(w2, SMALL)
    assert np.array_equal(s1["pool"][:t + 1], s2["pool"][:t + 1])
    assert np.allclose(s1["vol"][:t + 1], s2["vol"][:t + 1], equal_nan=True)
    sel2 = E.select_lowvol(s2["pool"][t], s2["vol"][t], SMALL.top_frac)
    assert np.array_equal(sel1, sel2) and len(sel1) > 0


def _sim_inputs(R, sel_by_t):
    """手造：pool 全真、vol 讓 sel_by_t 指定的股票最小。"""
    T, N = R.shape
    CP = np.cumprod(1 + np.nan_to_num(R, nan=0.0), axis=0)
    pool = np.ones((T, N), bool)
    vol = np.ones((T, N))
    for t, j in sel_by_t.items():
        vol[t, j] = 0.0
    last = np.full(N, T - 1)
    return CP, pool, vol, last


CM = CostModel(0.001, 0.001, 0.003, 0.0)
P1 = E.Params(top_frac=1.0 / 3)       # 3 檔選 1 檔


def test_sell_tax_only_on_sell():
    R = np.zeros((12, 3))
    CP, pool, vol, last = _sim_inputs(R, {2: 0, 6: 1})
    sim = E.simulate(R, CP, last, pool, vol, np.array([2, 6]), 0, 11, CM, "lowvol", P1)
    c0, c1 = sim["periods"][0]["cost"], sim["periods"][1]["cost"]
    assert abs(c0 - 0.001 / 1.001) < 1e-9                    # 首次只買：無證交稅
    assert c1 > 0.0039                                       # 賣出含 0.3% 稅 + 買進佣金
    # 第二期成本 = 賣 1 的 (0.001+0.003) 加買進
    assert c1 < 0.0055


def test_limit_lock_keeps_weight():
    R = np.zeros((12, 3))
    R[7, 0] = 0.10          # 第二次成交日(t=6 → u=7) 股票 0 漲停：賣不掉；股票 1 買不到資金
    CP, pool, vol, last = _sim_inputs(R, {2: 0, 6: 1})
    sim = E.simulate(R, CP, last, pool, vol, np.array([2, 6]), 0, 11, CM, "lowvol", P1)
    p1 = sim["periods"][1]
    assert p1["cost"] == 0.0
    assert p1["wpool"][0] > 0.99 and p1["wpool"][1] < 1e-9
    # 目標股漲停買不到：舊股照賣（收賣出成本），新股買不到 → 全現金
    R2 = np.zeros((12, 3)); R2[7, 1] = 0.095
    CP2, pool, vol, last = _sim_inputs(R2, {2: 0, 6: 1})
    sim2 = E.simulate(R2, CP2, last, pool, vol, np.array([2, 6]), 0, 11, CM, "lowvol", P1)
    assert sim2["periods"][1]["wpool"].sum() < 1e-9 and sim2["periods"][1]["cost"] > 0.003


def _periods(K=24, m=30, seed=1, kind="ew"):
    rng = np.random.default_rng(seed)
    ps = []
    for _ in range(K):
        P = rng.normal(0.005, 0.05, m)
        if kind == "ew":
            w = np.full(m, 1.0 / m)
        else:                                   # 完美預知：全押報酬最高的 3 檔
            w = np.zeros(m); w[np.argsort(P)[-3:]] = 1 / 3
        c = 0.002
        ret = (1 - c) * (1 + w @ P) - 1
        ps.append({"Ppool": P, "wpool": w, "const": 0.0, "cost": c, "ret": ret})
    return ps


def test_mcpt_equal_weight_no_edge():
    r = E.mcpt(_periods(kind="ew"), n_perm=200, seed=E.SEED)
    assert r["p"] >= 0.5                       # 等權全池：置換不改變報酬（也不改變成本）→ p=1


def test_mcpt_perfect_foresight_p_zero():
    r = E.mcpt(_periods(kind="oracle"), n_perm=500, seed=E.SEED)
    assert r["p"] <= 1 / 501 + 1e-12


def test_mcpt_costs_unchanged_by_permutation():
    ps = _periods(kind="oracle")
    for pr in ps:                               # 報酬全相同 → 置換前後一致，唯一差異可能來自成本
        v = float(pr["Ppool"][0])
        pr["Ppool"] = np.full_like(pr["Ppool"], v)
        pr["ret"] = (1 - pr["cost"]) * (1 + v) - 1
    r = E.mcpt(ps, n_perm=50, seed=E.SEED)
    assert np.allclose(r["perm"][np.isfinite(r["perm"])], r["actual"]) or not np.isfinite(r["perm"]).any()
