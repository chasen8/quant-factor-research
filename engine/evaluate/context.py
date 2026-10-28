"""評估/回測共用的市場脈絡：價格矩陣、股票池、調倉日、前瞻報酬。IC 與回測共用同一份，口徑一致。

時間約定（04 文件第 1 節）：訊號用 t 日收盤（含）以前資料；t+1 收盤成交；前瞻報酬從 t+1 收盤起算：
    r_{t->t+h} = P[t+1+h] / P[t+1] - 1
價格矩陣 P 為 close_adj 的 forward-fill（下市後凍結=持有人最後價格，下市損失已含在最後一日報酬），
因此下市股不會從樣本中消失（避免存活者偏誤）。程式中不使用任何負向 shift。
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..data.base import MarketData
from ..preprocess import eligibility

OOS_FRACTION = 0.6


def rebalance_positions(dates: pd.DatetimeIndex, freq: str = "M") -> np.ndarray:
    """每月（或每季：3/6/9/12 月）最後一個交易日的位置。"""
    s = pd.Series(np.arange(len(dates)), index=dates)
    last = s.groupby([dates.year, dates.month]).last()
    months = np.array([m for (_, m) in last.index])
    pos = last.to_numpy()
    if freq == "Q":
        pos = pos[np.isin(months, (3, 6, 9, 12))]
    elif freq != "M":
        raise ValueError(freq)
    return pos


class EvalContext:
    def __init__(self, md: MarketData):
        self.md = md
        self.dates = md.dates
        self.cols = md.data["close_adj"].columns
        self.T, self.N = md.data["close_adj"].shape
        self.P = md.data["close_adj"].ffill().to_numpy(dtype=float)
        self.elig = eligibility(md.data["close_raw"], md.min_age_days, md.min_price)
        rb = rebalance_positions(self.dates, "M")
        self.rb = rb[rb + 1 < self.T]  # 需要 t+1 才能成交
        self.rb_dates = self.dates[self.rb]
        self.n_rb = len(self.rb)
        self.oos_idx = int(OOS_FRACTION * self.n_rb)
        self.oos_start = self.rb_dates[self.oos_idx]
        self.elig_rb = self.elig[self.rb]
        self.avg_n_stocks = float(self.elig_rb.sum(axis=1).mean())
        self.n_delisted = int(self.md.meta.get("n_delisted", 0))

    def fwd_return(self, h: int, rows: np.ndarray | None = None) -> np.ndarray:
        """n_rb x N 前瞻 h 日報酬（從 t+1 收盤起算）；超出資料尾端為 NaN。"""
        rb = self.rb if rows is None else rows
        e = rb + 1
        x = rb + 1 + h
        ok = x < self.T
        out = np.full((len(rb), self.N), np.nan)
        out[ok] = self.P[x[ok]] / self.P[e[ok]] - 1.0
        return out

    def hold_return(self, rb_pos: np.ndarray | None = None) -> np.ndarray:
        """從第 k 個調倉日 t_k+1 收盤到 t_{k+1}+1 收盤的持有報酬；最後一列 NaN。"""
        rb = self.rb if rb_pos is None else rb_pos
        e = rb + 1
        out = np.full((len(rb), self.N), np.nan)
        out[:-1] = self.P[e[1:]] / self.P[e[:-1]] - 1.0
        return out
