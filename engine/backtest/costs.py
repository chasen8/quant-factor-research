"""交易成本與權重漂移（04 文件第 3、5 節）。

成本 = 買進 sum(dw>0) x (buy_commission + slippage) + 賣出 sum(dw<0) x (sell_commission + sell_tax + slippage)。
證交稅（sell_tax）只在賣出收。空頭腿（只用在多空報酬的成本估計）反向計：增加空單 = 賣出，回補 = 買進；
不計借券費（台股放空受限，見 04 文件第 3 節；LS 僅為學術慣例指標）。
"""
from __future__ import annotations

import numpy as np

from ..data.base import CostModel


def drift_weights(w: np.ndarray, period_ret: np.ndarray) -> np.ndarray:
    """持有一期後權重隨價格漂移（全額投資、歸一化）。period_ret 的 NaN 視為 0。"""
    g = w * (1.0 + np.nan_to_num(period_ret, nan=0.0))
    s = g.sum()
    return g / s if s > 0 else w


def trade_cost(w_old: np.ndarray, w_new: np.ndarray, cm: CostModel, short: bool = False):
    """回傳 (cost_fraction, one_way_turnover, n_trades)。權重以組合淨值為 1 的比例。"""
    d = w_new - w_old
    inc = float(d[d > 0].sum())
    dec = float(-d[d < 0].sum())
    if short:
        cost = inc * cm.sell_rate + dec * cm.buy_rate
    else:
        cost = inc * cm.buy_rate + dec * cm.sell_rate
    return cost, 0.5 * (inc + dec), int((np.abs(d) > 1e-12).sum())
