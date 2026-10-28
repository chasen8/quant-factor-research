"""前處理（04 文件第 1 節）：每期截面 winsorize 1%/99% -> z-score -> 乘 direction；覆蓋率；股票池過濾。

全部以「列 = 一個截面（某調倉日）、欄 = 股票」的 numpy 陣列運作，NaN 代表缺漏/不在池內。
"""
from __future__ import annotations

import warnings

import numpy as np
import pandas as pd

MIN_CROSS_SECTION = 30  # 有效樣本 < 30 檔 -> 該期記為缺漏（04 文件）


def eligibility(close_raw: pd.DataFrame, min_age_days: int = 60, min_price: float | None = None,
                seasoned_at_start: bool = True) -> np.ndarray:
    """T x N 布林：當日可交易且在股票池內。

    * 有未還原收盤價才算「存在」（下市後、上市前為 NaN）。
    * 上市未滿 min_age_days 個交易日排除。上市日以資料中第一個有價格的日子推定；
      資料第一列就已有價格的股票視為早已上市（seasoned_at_start），不排除。
    * min_price：用「未還原」收盤價過濾（美股 $5 慣例），避免還原價造成人為過濾。
    * 下市股在下市前都在池內（含下市損失），所以沒有存活者偏誤。
    """
    px = close_raw.to_numpy(dtype=float)
    alive = np.isfinite(px)
    age = np.cumsum(alive, axis=0)  # 第 1 天=1
    if seasoned_at_start:
        age = age + np.where(alive[0:1, :], 10 ** 6, 0)
    ok = alive & (age > min_age_days)
    if min_price is not None:
        with np.errstate(invalid="ignore"):
            ok &= px >= min_price
    return ok


def winsorize_rows(a: np.ndarray, lo: float = 0.01, hi: float = 0.99) -> np.ndarray:
    """每列（截面）把值夾在 [lo, hi] 分位數之間。"""
    out = a.copy()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        ql = np.nanquantile(a, lo, axis=1, keepdims=True)
        qh = np.nanquantile(a, hi, axis=1, keepdims=True)
    out = np.where(np.isfinite(out), np.minimum(np.maximum(out, ql), qh), np.nan)
    return out


def zscore_rows(a: np.ndarray) -> np.ndarray:
    """z = (f - mean)/std（樣本標準差 ddof=1）；std=0 的截面回全 NaN。"""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        m = np.nanmean(a, axis=1, keepdims=True)
        s = np.nanstd(a, axis=1, ddof=1, keepdims=True)
    s = np.where(s > 0, s, np.nan)
    return (a - m) / s


def preprocess_rows(raw: np.ndarray, elig: np.ndarray, direction: int,
                    min_n: int = MIN_CROSS_SECTION, winsor=(0.01, 0.99)):
    """raw, elig: n_rb x N。回傳 (z, winsorized_raw, coverage, n_valid)。

    1. 只保留股票池內且有限的值（缺漏不補 0、不補均值）
    2. 截面 winsorize -> z-score -> 乘 direction（z 越大 = 預期報酬越高）
    3. 有效樣本 < min_n 的截面整列設 NaN
    coverage = 有效因子值股票數 / 股票池股票數
    """
    x = np.where(elig & np.isfinite(raw), raw, np.nan)
    n_valid = np.isfinite(x).sum(axis=1)
    n_elig = elig.sum(axis=1)
    cov = np.where(n_elig > 0, n_valid / np.maximum(n_elig, 1), np.nan)
    bad = n_valid < min_n
    xw = winsorize_rows(x, *winsor)
    z = zscore_rows(xw) * direction
    z[bad] = np.nan
    xw[bad] = np.nan
    return z, xw, cov, n_valid
