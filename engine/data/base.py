"""市場資料容器與成本模型。真資料 adapter 只要回傳 MarketData 即可接上整個引擎。"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict

import pandas as pd


@dataclass(frozen=True)
class CostModel:
    """單邊比例成本（見 docs/data-contract.md）。"""
    buy_commission: float
    sell_commission: float
    sell_tax: float
    slippage: float

    def as_dict(self) -> dict:
        return asdict(self)

    @property
    def buy_rate(self) -> float:
        return self.buy_commission + self.slippage

    @property
    def sell_rate(self) -> float:
        return self.sell_commission + self.sell_tax + self.slippage


COST_TW = CostModel(0.001425, 0.001425, 0.003, 0.0010)
COST_US = CostModel(0.0, 0.0, 0.0, 0.0005)


@dataclass
class MarketData:
    """data: 欄位詞彙表（03 文件第 2 節）的寬表字典，index=交易日、columns=股票。
    已下市/未上市的格子為 NaN。min_price 用未還原收盤價過濾（None=不過濾）。"""
    market_id: str
    label: str
    data: dict[str, pd.DataFrame]
    cost: CostModel
    benchmark: str
    is_demo: bool = True
    data_source: str = ""
    universe_desc: str = ""
    min_price: float | None = None
    min_age_days: int = 60
    pit_estimated: bool = True
    meta: dict = field(default_factory=dict)

    @property
    def dates(self) -> pd.DatetimeIndex:
        return self.data["close_adj"].index

    @property
    def n_stocks(self) -> int:
        return self.data["close_adj"].shape[1]
