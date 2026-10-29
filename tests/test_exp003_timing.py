"""EXP-003 擇時類與 D1/D2 的單元測試（合成資料）。"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT))

import exp003_timing as X  # noqa: E402


def sim_garch(n, w, a, b, seed):
    rng = np.random.default_rng(seed)
    x = np.empty(n)
    s2 = w / (1 - a - b)
    for t in range(n):
        x[t] = math_sqrt(s2) * rng.standard_normal()
        s2 = w + a * x[t] ** 2 + b * s2
    return x


def math_sqrt(v):
    return float(np.sqrt(v))


def test_garch_param_recovery():
    x = sim_garch(6000, 0.05, 0.10, 0.85, 1)
    w, a, b = X.fit_garch(x)
    assert abs(a - 0.10) < 0.04
    assert abs(b - 0.85) < 0.06
    assert abs((a + b) - 0.95) < 0.03
    assert w > 0 and a >= 0 and b >= 0 and a + b < 1


def test_garch_nll_matches_naive_loop():
    x = sim_garch(300, 0.05, 0.1, 0.8, 2)
    p = np.array([0.04, 0.12, 0.8])
    s2 = [np.var(x)]
    for t in range(1, len(x)):
        s2.append(p[0] + p[1] * x[t - 1] ** 2 + p[2] * s2[-1])
    s2 = np.array(s2)
    ref = 0.5 * np.sum(np.log(s2) + x ** 2 / s2)
    assert X.garch_nll(p, x) == pytest.approx(ref, rel=1e-10)
    nxt = p[0] + p[1] * x[-1] ** 2 + p[2] * s2[-1]
    assert X.garch_next_sigma2(p, x, np.var(x)) == pytest.approx(nxt, rel=1e-10)


def _fake_calendar(n=900):
    return pd.bdate_range("2010-01-04", periods=n)


def test_garch_signal_bounds_and_no_lookahead():
    dates = _fake_calendar(900)
    rng = np.random.default_rng(3)
    lr = rng.standard_normal(900) * 0.01
    wk, mo = X.week_end_idx(dates), X.month_end_idx(dates)
    e = X.signals_garch(lr, wk, mo, win=400, min_n=250)
    ok = np.isfinite(e)
    assert ok.sum() > 10 and np.all((e[ok] > 0) & (e[ok] <= 1))
    cut = 700
    lr2 = lr.copy()
    lr2[cut + 1:] = rng.standard_normal(len(lr) - cut - 1) * 0.05      # 改掉未來
    e2 = X.signals_garch(lr2, wk, mo, win=400, min_n=250)
    past = wk <= cut
    np.testing.assert_allclose(e[past], e2[past], equal_nan=True)


def test_hmm_no_lookahead_truncation():
    dates = _fake_calendar(500)
    rng = np.random.default_rng(4)
    state = (np.arange(500) // 120) % 2
    lr = np.where(state == 0, 0.001 + 0.006 * rng.standard_normal(500), -0.002 + 0.02 * rng.standard_normal(500))
    wk, mo = X.week_end_idx(dates), X.month_end_idx(dates)
    e_full, p_full = X.signals_hmm(lr, wk, mo, 0, min_n=150, return_probs=True)
    cut = 380
    dt, lt = dates[:cut + 1], lr[:cut + 1]
    wk2, mo2 = X.week_end_idx(dt), X.month_end_idx(dt)
    e_cut, p_cut = X.signals_hmm(lt, wk2, mo2, 0, min_n=150, return_probs=True)
    lim = cut - 25                                    # 避開截斷處多出的「假月底」
    a = wk[wk <= lim]
    b = wk2[wk2 <= lim]
    assert len(a) == len(b) and np.all(a == b)
    np.testing.assert_allclose(p_full[:len(a)], p_cut[:len(a)], atol=1e-8, equal_nan=True)
    np.testing.assert_array_equal(e_full[:len(a)], e_cut[:len(a)])
    assert np.isfinite(p_full).sum() > 10
    # 與「截至該週才餵資料」的濾波一致：亂改未來資料，過去訊號不變
    lr3 = lr.copy()
    lr3[cut + 1:] += 0.05
    e3, p3 = X.signals_hmm(lr3, wk, mo, 0, min_n=150, return_probs=True)
    np.testing.assert_allclose(p_full[:len(a)], p3[:len(a)], atol=1e-8, equal_nan=True)


def test_kelly_clip_and_formula():
    rng = np.random.default_rng(5)
    lr = rng.standard_normal(600) * 0.01 + 0.002          # mu/var = 20 -> clip 到 1
    wk = np.array([300, 400, 599])
    e = X.signals_kelly(lr, wk)
    assert np.all(e == 1.0)
    lr2 = rng.standard_normal(600) * 0.01 - 0.002          # 負 -> 0
    assert np.all(X.signals_kelly(lr2, wk) == 0.0)
    lr3 = rng.standard_normal(600) * 0.05 + 0.0005         # mu/var = 0.2
    seg = lr3[300 - 251:301]
    exp = seg.mean() / seg.var(ddof=1)
    assert X.signals_kelly(lr3, np.array([300]))[0] == pytest.approx(np.clip(exp, 0, 1))
    assert X.signals_kelly(lr3, np.array([300]), scale=0.5)[0] == pytest.approx(np.clip(0.5 * exp, 0, 1))
    assert np.isnan(X.signals_kelly(lr, np.array([100]))[0])


def test_path_costs_and_timing():
    T = 12
    r = np.full(T, 0.01)
    cm = X.COST_0050
    p = X.build_path(T, np.array([2, 5]), np.array([1.0, 0.0]), 0, 11, cm)
    assert p["u0"] == 3
    assert p["cost"][3] == pytest.approx(cm.buy_rate) and p["cost"][6] == pytest.approx(cm.sell_rate)
    assert p["h"][3] == 0 and p["h"][4] == 1 and p["h"][6] == 1 and p["h"][7] == 0   # t+1 成交，隔日起賺報酬
    net = X.daily_net(p, r)
    assert net[0] == pytest.approx(-cm.buy_rate)


def test_mcpt_random_positions_not_significant():
    rng = np.random.default_rng(6)
    T = 800
    r = rng.standard_normal(T) * 0.01 + 0.0003
    ps = []
    for s in range(6):
        g = np.random.default_rng(100 + s)
        wk = np.arange(5, T - 1, 5)
        e = g.integers(0, 2, len(wk)).astype(float)       # 與報酬無關的隨機持倉
        path = X.build_path(T, wk, e, 0, T - 1, X.COST_0050)
        ps.append(X.mcpt(path, r, n_perm=500, seed=7)["p"])
    assert np.mean(ps) > 0.2 and min(ps) > 0.01        # 不應系統性顯著
    # 完美前瞻持倉（在漲日持有）-> 顯著
    h_cheat = (r[2:] > 0).astype(float)      # t 日訊號 -> t+1 成交 -> 賺 t+2 日報酬
    wk = np.arange(0, T - 2)
    path = X.build_path(T, wk, h_cheat, 0, T - 1, X.CostModel(0, 0, 0, 0))
    assert X.mcpt(path, r, n_perm=500, seed=7)["p"] < 0.01


def test_copula_loglik_and_lower_tail():
    rng = np.random.default_rng(8)
    n = 4000
    th = 2.0
    # Clayton 抽樣
    u = rng.random(n)
    w = rng.random(n)
    v = ((w ** (-th / (1 + th)) - 1) * u ** (-th) + 1) ** (-1 / th)
    fit = X.fit_copulas(u, v)
    assert abs(fit["clayton"]["param"] - th) < 0.3
    assert min(fit, key=lambda m: fit[m]["aic"]) == "clayton"
    assert X.copula_lower("clayton", th, 0.05) == pytest.approx((2 * 0.05 ** -th - 1) ** (-1 / th) / 0.05)
    # 獨立：下尾條件機率 = q；Gaussian rho=0
    assert X.copula_lower("gaussian", 0.0, 0.05) == pytest.approx(0.05, abs=1e-4)
    assert X.copula_lower("gumbel", 1.0, 0.05) == pytest.approx(0.05, abs=1e-9)
    # Gaussian 抽樣 -> Gaussian 贏過 Clayton/Gumbel 的對數似然機會高；至少 rho 回收
    z = rng.multivariate_normal([0, 0], [[1, 0.6], [0.6, 1]], size=n)
    uu, vv = X._pseudo(z[:, 0]), X._pseudo(z[:, 1])
    f2 = X.fit_copulas(uu, vv)
    assert abs(f2["gaussian"]["param"] - 0.6) < 0.05
    assert f2["gaussian"]["aic"] < f2["gumbel"]["aic"]


def test_d1_returns_keys():
    rng = np.random.default_rng(9)
    x = rng.standard_t(4, 1500) * 0.01
    out = X.d1_gbm(x[:700], x[700:])
    for s in ("IS", "OOS"):
        assert out[s]["excess_kurtosis"] > 0 and out[s]["jb_p"] < 0.05
        assert 0 <= out[s]["lb10_sq_p"] <= 1
