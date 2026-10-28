# -*- coding: utf-8 -*-
"""指標對手算：Sharpe、Sortino、MDD、CAGR、Rank IC、Newey-West t、DSR。"""
import math
import statistics

import numpy as np
import pytest
import statsmodels.api as sm
from scipy import stats as sps

from engine import metrics as M
from engine.evaluate.ic import rowwise_pearson, rowwise_rank_ic

R = [0.01, 0.03, -0.01, 0.02]


def test_sharpe_hand():
    mu, sd = statistics.mean(R), statistics.stdev(R)  # 獨立實作（樣本標準差）
    assert M.sharpe(R, 12) == pytest.approx(mu / sd * math.sqrt(12))
    assert M.sharpe(R, 12) == pytest.approx(2.5354, abs=1e-3)
    assert M.sharpe(R, 12, rf=0.0125) == pytest.approx(0.0, abs=1e-12)


def test_sortino_hand():
    # MAR=0：只有 -0.01 一筆下行；DD = sqrt(0.01^2 / 4) = 0.005；mean = 0.0125
    assert M.sortino(R, 12) == pytest.approx(0.0125 / 0.005 * math.sqrt(12))


def test_mdd_and_drawdown():
    nav = np.cumprod([1.10, 0.90, 0.95, 1.20])  # 1.1, .99, .9405, 1.1286
    assert M.max_drawdown(nav) == pytest.approx(1 - 0.9405 / 1.1)
    dd = M.drawdown_series(nav)
    assert dd[0] == 0 and dd.min() == pytest.approx(-(1 - 0.9405 / 1.1))
    assert M.max_drawdown([1.0, 1.1, 1.2]) == 0.0


def test_cagr_and_calmar():
    r = [0.10, -0.10, -0.05, 0.20]
    nav_end = 1.1 * 0.9 * 0.95 * 1.2
    assert M.cagr(r, 12) == pytest.approx(nav_end ** (12 / 4) - 1)
    assert M.cagr([0.01] * 12, 12) == pytest.approx(1.01 ** 12 - 1)
    mdd = 1 - 0.9405 / 1.1
    assert M.calmar(r, 12) == pytest.approx(M.cagr(r, 12) / mdd)


def test_rank_ic_hand():
    x = np.array([[1, 2, 3, 4, 5.0]])
    y = np.array([[2, 1, 4, 3, 5.0]])
    # Spearman = 1 - 6*sum(d^2)/(n(n^2-1)) = 1 - 6*4/120 = 0.8
    assert rowwise_rank_ic(x, y, min_n=3)[0] == pytest.approx(0.8)
    assert rowwise_rank_ic(x, y, min_n=6)[0] != rowwise_rank_ic(x, y, min_n=6)[0]  # 樣本不足 -> NaN


def test_rank_ic_matches_scipy_with_nan_and_ties():
    rng = np.random.default_rng(1)
    x = rng.normal(size=(5, 80))
    y = 0.3 * x + rng.normal(size=(5, 80))
    x[:, ::7] = np.nan
    y[:, 3::11] = np.nan
    x[0, :20] = 1.0  # 並列
    ic = rowwise_rank_ic(x, y, min_n=10)
    pc = rowwise_pearson(x, y, min_n=10)
    for i in range(5):
        m = np.isfinite(x[i]) & np.isfinite(y[i])
        assert ic[i] == pytest.approx(sps.spearmanr(x[i, m], y[i, m])[0])
        assert pc[i] == pytest.approx(sps.pearsonr(x[i, m], y[i, m])[0])


@pytest.mark.parametrize("lag", [0, 1, 3])
def test_newey_west_matches_statsmodels(lag):
    rng = np.random.default_rng(7)
    e = rng.normal(size=200)
    x = 0.1 + e + 0.5 * np.concatenate([[0], e[:-1]])  # MA(1)
    res = sm.OLS(x, np.ones_like(x)).fit(cov_type="HAC", cov_kwds={"maxlags": lag})
    assert M.newey_west_tstat(x, lag) == pytest.approx(float(res.tvalues[0]), rel=1e-9)


def test_nw_lag_rule():
    assert M.nw_lag_for_horizon(1) == 0
    assert M.nw_lag_for_horizon(21) == 1
    assert M.nw_lag_for_horizon(60) == 3


def test_dsr_known_value_and_monotonicity():
    # n=1 -> SR0=0 -> PSR；sr=0.1, T=250, 常態：z = 0.1*sqrt(249)/sqrt(1+0.5*0.01)
    z = 0.1 * math.sqrt(249) / math.sqrt(1 + 0.5 * 0.01)
    assert M.deflated_sharpe(0.1, 250, 0.0, 3.0, 1) == pytest.approx(sps.norm.cdf(z))
    assert M.deflated_sharpe(0.0, 250, 0.0, 3.0, 1) == pytest.approx(0.5)
    base = [M.deflated_sharpe(0.12, 250, 0.0, 3.0, n, sr_var=0.01) for n in (1, 5, 20, 100, 1000)]
    assert all(a > b for a, b in zip(base, base[1:]))  # 試驗越多越低
    srs = [M.deflated_sharpe(s, 250, 0.0, 3.0, 20, sr_var=0.01) for s in (0.05, 0.1, 0.2, 0.4)]
    assert all(a < b for a, b in zip(srs, srs[1:]))  # Sharpe 越高越高
    t = [M.deflated_sharpe(0.3, T, 0.0, 3.0, 10, sr_var=0.01) for T in (60, 120, 500)]
    assert t[0] < t[1] < t[2]
    # 負偏態 / 肥尾 -> 較低
    assert M.deflated_sharpe(0.1, 250, -1.0, 6.0, 1) < M.deflated_sharpe(0.1, 250, 0.0, 3.0, 1)
    # SR0 公式手算
    n, v = 10, 0.01
    g = 0.5772156649015329
    sr0 = math.sqrt(v) * ((1 - g) * sps.norm.ppf(1 - 1 / n) + g * sps.norm.ppf(1 - 1 / (n * math.e)))
    exp = sps.norm.cdf((0.2 - sr0) * math.sqrt(249) / math.sqrt(1 + 0.5 * 0.04))
    assert M.deflated_sharpe(0.2, 250, 0.0, 3.0, n, sr_var=v) == pytest.approx(exp)
