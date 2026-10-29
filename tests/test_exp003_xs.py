"""EXP-003 C1~C4 單元測試：合成資料，不連網。"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))

import exp001_lowvol as E1  # noqa: E402
import exp003_xs as X  # noqa: E402


# ---------------------------------------------------------------- C1
def _cov_mu(n, seed=0, T=300):
    rng = np.random.default_rng(seed)
    f = rng.normal(0, 0.01, (T, 1))
    Rw = f * rng.uniform(0.5, 1.5, (1, n)) + rng.normal(0, 0.01, (T, n)) + rng.uniform(-0.0005, 0.002, n)
    return Rw.mean(0), np.cov(Rw, rowvar=False, ddof=1)


def test_c1_weight_constraints():
    for seed in range(5):
        mu, cov = _cov_mu(50, seed)
        w, ok = X.max_sharpe_long_only(mu, cov)
        assert ok
        assert abs(w.sum() - 1) < 1e-6
        assert w.min() >= -1e-9 and w.max() <= 0.10 + 1e-9
        # 最大 Sharpe 不應比 1/N 差
        sh = lambda v: (mu * 252) @ v / np.sqrt(v @ (cov * 252) @ v)  # noqa: E731
        assert sh(w) >= sh(np.full(50, 1 / 50)) - 1e-6


def test_c1_fallback_equal_weight():
    mu, cov = _cov_mu(5)                      # 5 檔 × 10% < 100%：不可行
    w, ok = X.max_sharpe_long_only(mu, cov)
    assert not ok and np.allclose(w, 0.2)
    mu, cov = _cov_mu(20)
    cov[0, 0] = np.nan
    w, ok = X.max_sharpe_long_only(mu, cov)
    assert not ok and np.allclose(w, 1 / 20)


def test_c1_target_no_lookahead():
    rng = np.random.default_rng(1)
    T, N = 400, 70
    R = rng.normal(0.0005, 0.02, (T, N))
    AMT = rng.uniform(1e7, 1e9, (T, N))
    pool = np.ones(N, bool)
    t = 320
    a = X.c1_target_at(R, AMT, pool, t)
    b = X.c1_target_at(R[:t + 1], AMT[:t + 1], pool, t)
    assert np.allclose(a["S"], b["S"]) and np.allclose(a["B"], b["B"])
    assert (a["B"] > 0).sum() == 50 and abs(a["S"].sum() - 1) < 1e-6 and a["S"].max() <= 0.1 + 1e-9


# ---------------------------------------------------------------- C2
def _ou_pair(T=500, seed=0, theta=0.15, sig=0.02):
    rng = np.random.default_rng(seed)
    x = np.cumsum(rng.normal(0, 0.01, T))
    s = np.zeros(T)
    for i in range(1, T):
        s[i] = s[i - 1] * (1 - theta) + rng.normal(0, sig)
    y = 0.5 + 1.2 * x + s
    return np.column_stack([y, x])


def _arrays(L):
    T, n = L.shape
    CP = np.exp(L)
    R = np.vstack([np.full((1, n), np.nan), CP[1:] / CP[:-1] - 1.0])
    R[0] = 0.0
    return R, L, np.full(n, T - 1)


def test_c2_params_use_formation_only_and_trade_profits():
    L = _ou_pair()
    R, LCP, last = _arrays(L)
    t = 260
    b1, a1, s1 = X.pair_params(L[t - 251:t + 1, :1], L[t - 251:t + 1, 1:])
    L2 = L.copy()
    L2[t + 1:] += 5.0                                         # 形成日之後的資料被改動
    b2, a2, s2 = X.pair_params(L2[t - 251:t + 1, :1], L2[t - 251:t + 1, 1:])
    assert np.allclose(b1, b2) and np.allclose(a1, a2) and np.allclose(s1, s2)
    assert abs(b1[0] - 1.2) < 0.3
    ca, cb = np.array([0]), np.array([1])
    E = t + 126
    g = X.sim_pairs(R, LCP, last, t, E, ca, cb, b1, a1, s1, X.COST_ZERO)
    n = X.sim_pairs(R, LCP, last, t, E, ca, cb, b1, a1, s1, X.COST_BASE)
    assert g["n_entries"][0] >= 1
    assert g["inc"].sum() > 0                                 # 均值回歸的合成價差：毛損益為正
    assert n["inc"].sum() < g["inc"].sum()                    # 成本使損益下降
    assert g["open"][-1, 0] == 0                              # 期末強制平倉


def test_c2_signals_causal():
    """截斷（改動）第 k0 天之後的價格，k0 之前的每日損益不變。"""
    L = _ou_pair(seed=3)
    R, LCP, last = _arrays(L)
    t, E, k0 = 260, 386, 60
    b, a, s = X.pair_params(L[t - 251:t + 1, :1], L[t - 251:t + 1, 1:])
    ca, cb = np.array([0]), np.array([1])
    base = X.sim_pairs(R, LCP, last, t, E, ca, cb, b, a, s, X.COST_BASE)
    L2 = L.copy()
    L2[t + k0 + 1:] += np.random.default_rng(9).normal(0, 0.3, (len(L) - t - k0 - 1, 2))
    R2, LCP2, _ = _arrays(L2)
    alt = X.sim_pairs(R2, LCP2, last, t, E, ca, cb, b, a, s, X.COST_BASE)
    assert np.allclose(base["inc"][:k0], alt["inc"][:k0])


def test_c2_limit_blocks_entry_and_costs():
    L = _ou_pair(seed=0)
    R, LCP, last = _arrays(L)
    t, E = 260, 386
    b, a, s = X.pair_params(L[t - 251:t + 1, :1], L[t - 251:t + 1, 1:])
    ca, cb = np.array([0]), np.array([1])
    base = X.sim_pairs(R, LCP, last, t, E, ca, cb, b, a, s, X.COST_BASE)
    # 在每個非期末日把 x 腿設為漲停（不成交）：不可能開倉
    R2 = R.copy()
    R2[t + 1:E, 1] = 0.099
    alt = X.sim_pairs(R2, LCP, last, t, E, ca, cb, b, a, s, X.COST_BASE)
    assert base["n_entries"][0] >= 1 and alt["n_entries"][0] == 0
    # 一次完整來回的成本（每對本金 1，每腿 0.5）
    cm = X.COST_BASE
    rt = 0.5 * (cm.buy_rate + cm.sell_rate + (cm.sell_rate + X.SHORT_FEE) + cm.buy_rate)
    assert abs(rt - 0.5 * (0.002425 + 0.005425 + 0.006225 + 0.002425)) < 1e-12


def test_c2_mcpt_not_significant_on_random_walks():
    rng = np.random.default_rng(7)
    n, T, t = 12, 520, 270
    sig = 0
    for world in range(6):
        L = np.cumsum(rng.normal(0, 0.015, (T, n)), axis=0)
        R, LCP, last = _arrays(L)
        ia, ib = np.triu_indices(n, 1)
        p = X.eg_pvalues(L[t - 251:t + 1])
        b, a, s = X.pair_params(L[t - 251:t + 1][:, ia], L[t - 251:t + 1][:, ib])
        E = t + 126
        inc = X.sim_pairs(R, LCP, last, t, E, ia, ib, b, a, s, X.COST_BASE)["inc"]
        ch = np.argsort(p)[:10]
        act = inc[:, ch].sum(axis=1) / 10
        sh_act = act.mean() / act.std(ddof=1)
        r2 = np.random.default_rng(100 + world)
        cnt = 0
        for _ in range(500):
            pk = r2.choice(len(ia), 10, replace=False)
            x = inc[:, pk].sum(axis=1) / 10
            cnt += (x.mean() / x.std(ddof=1) >= sh_act) if x.std() > 0 else 0
        sig += (cnt / 500) < 0.05
    assert sig <= 1                                            # 6 個無訊號世界至多 1 個 p<0.05


# ---------------------------------------------------------------- C3
def test_c3_no_lookahead_and_selection_size():
    rng = np.random.default_rng(2)
    T, N = 400, 120
    fac = rng.normal(0, 0.01, (T, 5))
    R = fac @ rng.normal(0, 1, (5, N)) + rng.normal(0, 0.01, (T, N))
    pool = np.ones(N, bool)
    t = 330
    a = X.c3_select_at(R, pool, t)
    b = X.c3_select_at(R[:t + 1], pool, t)
    assert a is not None and np.array_equal(a, b)
    assert len(a) == int(0.2 * N)
    # 改動 t 之後的資料不影響
    R2 = R.copy()
    R2[t + 1:] = rng.normal(0, 0.05, R2[t + 1:].shape)
    assert np.array_equal(a, X.c3_select_at(R2, pool, t))


def test_c3_selects_most_negative_residual():
    """最近 21 日被人為壓低的股票，應在累積殘差最低組。"""
    rng = np.random.default_rng(5)
    T, N = 300, 100
    R = rng.normal(0, 0.01, (T, N)) + rng.normal(0, 0.01, (T, 1))
    R[-21:, 7] -= 0.02
    sel = X.c3_select_at(R, np.ones(N, bool), T - 1)
    assert 7 in sel


# ---------------------------------------------------------------- C4
def _syn_ctx(T_end="2020-06-30", N=60, seed=0):
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2010-01-01", T_end)
    T = len(dates)
    R = rng.normal(0.0003, 0.02, (T, N))
    CP = np.cumprod(1 + R, axis=0)
    AMT = rng.uniform(1e7, 1e9, (T, N))
    pool = np.ones((T, N), bool)
    pool[:LOOKBACK] = False
    return {"dates": dates, "R": R, "CP": CP, "AMT": AMT, "pool": pool, "rebal_t": E1.month_end_idx(dates)}


LOOKBACK = 252


def test_c4_features_no_lookahead():
    ctx = _syn_ctx()
    t = 1000
    pr = np.ones(ctx["R"].shape[1], bool)
    i1, F1 = X.c4_features_at(ctx["R"], ctx["CP"], ctx["AMT"], pr, t)
    R = ctx["R"][:t + 1]
    CP = np.cumprod(1 + R, axis=0)
    i2, F2 = X.c4_features_at(R, CP, ctx["AMT"][:t + 1], pr, t)
    assert np.allclose(F1, F2, equal_nan=True) and np.isfinite(F1).all()


def test_c4_selection_no_lookahead():
    ctx = _syn_ctx()
    rng = np.random.default_rng(0)
    models = [X.mlp_init(9, 32, rng) for _ in range(2)]
    t = 1000
    pr = np.ones(ctx["R"].shape[1], bool)
    a = X.c4_select_at(models, ctx["R"], ctx["CP"], ctx["AMT"], pr, t)
    R = ctx["R"][:t + 1]
    b = X.c4_select_at(models, R, np.cumprod(1 + R, axis=0), ctx["AMT"][:t + 1], pr, t)
    assert np.array_equal(a, b) and len(a) == int(0.2 * len(pr))


def test_c4_training_cutoff():
    ctx = _syn_ctx()
    ds = X.c4_training_samples(ctx)
    d = ctx["dates"]
    assert ds["max_realization_idx"]["train"] <= ds["tr_end"] <= int(d.searchsorted(pd.Timestamp("2016-12-31"), side="right") - 1)
    assert ds["max_realization_idx"]["val"] <= ds["is_end"] == int(d.searchsorted(pd.Timestamp("2018-12-31"), side="right") - 1)
    assert d[ds["max_realization_idx"]["val"]] <= pd.Timestamp("2018-12-31")
    # 改動 2019-01-01 之後的所有資料，訓練/驗證樣本完全不變
    ctx2 = {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in ctx.items()}
    cut = int(d.searchsorted(pd.Timestamp("2019-01-01")))
    rng = np.random.default_rng(99)
    ctx2["R"][cut:] = rng.normal(0, 0.1, ctx2["R"][cut:].shape)
    ctx2["CP"] = np.cumprod(1 + ctx2["R"], axis=0)
    ctx2["AMT"][cut:] *= 7
    ds2 = X.c4_training_samples(ctx2)
    for k in ("Xtr", "ytr", "Xva", "yva"):
        assert np.array_equal(ds[k], ds2[k])


def test_mlp_gradient_check():
    rng = np.random.default_rng(0)
    P = X.mlp_init(9, 32, rng)
    P["b1"] = rng.normal(0, 0.1, 32)
    P["b2"] = rng.normal(0, 0.1, 1)
    Xb = rng.uniform(-0.5, 0.5, (40, 9))
    y = rng.uniform(0, 1, 40)
    _, g = X.mlp_loss_grad(P, Xb, y)
    eps = 1e-6
    for k in P:
        flat = P[k].reshape(-1)
        gflat = g[k].reshape(-1)
        for i in rng.choice(len(flat), min(6, len(flat)), replace=False):
            old = flat[i]
            flat[i] = old + eps
            lp, _ = X.mlp_loss_grad(P, Xb, y)
            flat[i] = old - eps
            lm, _ = X.mlp_loss_grad(P, Xb, y)
            flat[i] = old
            assert abs((lp - lm) / (2 * eps) - gflat[i]) < 1e-6 + 1e-4 * abs(gflat[i])


def test_mlp_learns_simple_signal():
    rng = np.random.default_rng(3)
    Xa = rng.uniform(-0.5, 0.5, (3000, 9))
    ya = np.clip(Xa[:, 0] + 0.5 + rng.normal(0, 0.05, 3000), 0, 1)
    P, info = X.mlp_train(Xa[:2400], ya[:2400], Xa[2400:], ya[2400:], seed=1, max_epochs=60)
    base = float(np.mean((ya[2400:] - ya[:2400].mean()) ** 2))
    assert info["best_val_loss"] < 0.5 * base


# ---------------------------------------------------------------- MCPT 無訊號
def _periods(seed, K=60, m=100, k_sel=20):
    rng = np.random.default_rng(seed)
    S, B = [], []
    for _ in range(K):
        P = rng.normal(0, 0.05, m)
        wS = np.zeros(m); wS[rng.choice(m, k_sel, replace=False)] = 1 / k_sel
        wB = np.full(m, 1 / m)
        for lst, w, c in ((S, wS, 0.002), (B, wB, 0.0005)):
            g = float(P @ w)
            lst.append({"Ppool": P, "wpool": w, "const": 0.0, "cost": c, "ret": (1 - c) * (1 + g) - 1})
    return S, B


def test_mcpt_not_significant_without_signal():
    ps = []
    for seed in range(20):
        S, B = _periods(seed)
        ps.append(X.mcpt_excess(S, B, n_perm=400, seed=11)["p"])
    assert sum(p < 0.05 for p in ps) <= 4              # 虛無下期望約 1 個
    assert 0.2 < np.mean(ps) < 0.8


def test_mcpt_significant_with_signal():
    rng = np.random.default_rng(0)
    S, B = [], []
    for _ in range(60):
        m = 100
        P = rng.normal(0, 0.05, m)
        w = np.zeros(m); w[np.argsort(-P)[:20]] = 1 / 20            # 偷看未來的選股
        for lst, ww in ((S, w), (B, np.full(m, 1 / m))):
            g = float(P @ ww)
            lst.append({"Ppool": P, "wpool": ww, "const": 0.0, "cost": 0.002, "ret": 0.998 * (1 + g) - 1})
    assert X.mcpt_excess(S, B, n_perm=400, seed=3)["p"] < 0.01
