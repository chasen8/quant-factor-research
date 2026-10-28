"""績效與統計指標（公式對照 docs/research/04-validation-methodology.md 第 2、3、4.5 節）。

所有函式輸入為 1 維序列（每期報酬 / IC 序列），回傳 float（資料不足回 nan）。
"""
from __future__ import annotations

import math

import numpy as np
from scipy import stats as sps

EULER_GAMMA = 0.5772156649015329


def _a(x) -> np.ndarray:
    a = np.asarray(x, dtype=float)
    return a[np.isfinite(a)]


def nav_from_returns(r) -> np.ndarray:
    return np.cumprod(1.0 + np.asarray(r, dtype=float))


def cagr(r, periods_per_year: float) -> float:
    """CAGR = NAV_T^(P/T) - 1。"""
    r = _a(r)
    if len(r) == 0:
        return math.nan
    nav = float(np.prod(1.0 + r))
    if nav <= 0:
        return -1.0
    return nav ** (periods_per_year / len(r)) - 1.0


def ann_vol(r, periods_per_year: float) -> float:
    r = _a(r)
    return float(np.std(r, ddof=1) * math.sqrt(periods_per_year)) if len(r) > 1 else math.nan


def sharpe(r, periods_per_year: float, rf: float = 0.0) -> float:
    """mean(r-rf)/std(r-rf) * sqrt(P)；rf 為每期無風險利率（預設 0，須在文件註明）。"""
    r = _a(r) - rf
    if len(r) < 2:
        return math.nan
    s = np.std(r, ddof=1)
    return float(np.mean(r) / s * math.sqrt(periods_per_year)) if s > 0 else math.nan


def sortino(r, periods_per_year: float, mar: float = 0.0) -> float:
    """mean(r-MAR)/DD * sqrt(P)，DD = sqrt(mean(min(0, r-MAR)^2))。"""
    r = _a(r)
    if len(r) < 2:
        return math.nan
    dd = math.sqrt(float(np.mean(np.minimum(0.0, r - mar) ** 2)))
    return float(np.mean(r - mar) / dd * math.sqrt(periods_per_year)) if dd > 0 else math.nan


def drawdown_series(nav) -> np.ndarray:
    """NAV/running_max - 1（<=0）。"""
    nav = np.asarray(nav, dtype=float)
    return nav / np.maximum.accumulate(nav) - 1.0


def max_drawdown(nav) -> float:
    """MDD = max_t(1 - NAV_t / max_{s<=t} NAV_s)，回傳正數。"""
    nav = np.asarray(nav, dtype=float)
    nav = nav[np.isfinite(nav)]
    if len(nav) == 0:
        return math.nan
    return float(-drawdown_series(nav).min())


def calmar(r, periods_per_year: float) -> float:
    r = _a(r)
    if len(r) == 0:
        return math.nan
    m = max_drawdown(nav_from_returns(r))
    return cagr(r, periods_per_year) / m if m > 0 else math.nan


def newey_west_tstat(x, lag: int) -> float:
    """對均值的 Newey-West t 值：t = mean / sqrt(S/T)，
    S = g0 + 2*sum_{j=1..L}(1 - j/(L+1)) * g_j，g_j = (1/T) sum e_t e_{t-j}（Bartlett 核，無小樣本修正）。
    與 statsmodels OLS(const).fit(cov_type='HAC', cov_kwds={'maxlags': L}) 的 t 值一致。"""
    x = _a(x)
    T = len(x)
    if T < 3:
        return math.nan
    e = x - x.mean()
    L = int(min(max(lag, 0), T - 1))
    s = float(np.dot(e, e) / T)
    for j in range(1, L + 1):
        s += 2.0 * (1.0 - j / (L + 1.0)) * float(np.dot(e[j:], e[:-j]) / T)
    if s <= 0:
        return math.nan
    return float(x.mean() / math.sqrt(s / T))


def nw_lag_for_horizon(h_days: int, rebalance_days: int = 21) -> int:
    """04 文件：lag = h-1（以「日」計的重疊）。我們的 IC 序列是月頻（每 ~21 日一點），
    相鄰兩點的前瞻視窗只重疊 max(0, h - 間隔) 日，換算成「樣本」單位為 ceil((h-1)/rebalance_days)；
    h=21 時為 1（月長 20~23 日不一，保守留 1 期）。"""
    return int(math.ceil(max(h_days - 1, 0) / rebalance_days))


def sharpe_se(sr: float, T: int, skew: float, kurt: float) -> float:
    """Lo(2002)/Mertens(2002)：SE(SR) = sqrt((1 - g3*SR + (g4-1)/4*SR^2)/(T-1))，SR 為每期、kurt 為非超額。"""
    v = (1.0 - skew * sr + (kurt - 1.0) / 4.0 * sr ** 2) / (T - 1)
    return math.sqrt(v) if v > 0 else math.nan


def deflated_sharpe(sr: float, T: int, skew: float, kurt: float,
                    n_trials: int = 1, sr_var: float | None = None) -> float:
    """Deflated Sharpe Ratio（Bailey & Lopez de Prado 2014；04 文件 4.5）。

    sr: 每期（非年化）Sharpe；kurt: 非超額峰度（常態=3）。
    SR0 = sqrt(V) * ((1-g)*Phi^-1(1-1/N) + g*Phi^-1(1-1/(N*e)))；N=1 時 SR0=0（退化成 PSR）。
    sr_var（N 次試驗 Sharpe 的變異數）未提供時，用虛無假設下的 1/(T-1)（SR 估計誤差的量級）近似，
    並在 bias_checks 說明；之後有真正的多參數試驗時應傳入實際變異數。"""
    if not np.isfinite(sr) or T < 3:
        return math.nan
    n = max(int(n_trials), 1)
    if n == 1:
        sr0 = 0.0
    else:
        v = sr_var if sr_var is not None else 1.0 / (T - 1)
        sr0 = math.sqrt(v) * ((1 - EULER_GAMMA) * sps.norm.ppf(1 - 1.0 / n)
                              + EULER_GAMMA * sps.norm.ppf(1 - 1.0 / (n * math.e)))
    denom = 1.0 - skew * sr + (kurt - 1.0) / 4.0 * sr ** 2
    if denom <= 0:
        return math.nan
    return float(sps.norm.cdf((sr - sr0) * math.sqrt(T - 1) / math.sqrt(denom)))


def skew_kurt(r) -> tuple[float, float]:
    """(偏態, 非超額峰度)。"""
    r = _a(r)
    if len(r) < 4 or np.std(r) == 0:
        return 0.0, 3.0
    return float(sps.skew(r)), float(sps.kurtosis(r, fisher=False))


def annual_return_from_nav(nav_end: float, n: int, periods_per_year: float) -> float:
    if n <= 0 or not np.isfinite(nav_end) or nav_end <= 0:
        return math.nan
    return float(nav_end ** (periods_per_year / n) - 1.0)
