"""逐截面 IC / Rank IC（Pearson / Spearman）。"""
from __future__ import annotations

import warnings

import numpy as np
from scipy import stats as sps

MIN_N = 30


def _rank_rows(a: np.ndarray) -> np.ndarray:
    out = np.full(a.shape, np.nan)
    for i in range(a.shape[0]):
        m = np.isfinite(a[i])
        if m.any():
            out[i, m] = sps.rankdata(a[i, m], method="average")
    return out


def rowwise_pearson(x: np.ndarray, y: np.ndarray, min_n: int = MIN_N) -> np.ndarray:
    """每列（截面）的 Pearson 相關；成對有效樣本 < min_n 回 NaN。"""
    m = np.isfinite(x) & np.isfinite(y)
    n = m.sum(axis=1)
    xm = np.where(m, x, 0.0)
    ym = np.where(m, y, 0.0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        mx = xm.sum(axis=1, keepdims=True) / n[:, None]
        my = ym.sum(axis=1, keepdims=True) / n[:, None]
        dx = np.where(m, x - mx, 0.0)
        dy = np.where(m, y - my, 0.0)
        c = (dx * dy).sum(axis=1) / np.sqrt((dx ** 2).sum(axis=1) * (dy ** 2).sum(axis=1))
    c = np.where(n >= min_n, c, np.nan)
    return np.where(np.isfinite(c), c, np.nan)


def rowwise_rank_ic(x: np.ndarray, y: np.ndarray, min_n: int = MIN_N) -> np.ndarray:
    """Spearman：先取成對有效樣本，再各自排名，再 Pearson。"""
    m = np.isfinite(x) & np.isfinite(y)
    xr = _rank_rows(np.where(m, x, np.nan))
    yr = _rank_rows(np.where(m, y, np.nan))
    return rowwise_pearson(xr, yr, min_n)
