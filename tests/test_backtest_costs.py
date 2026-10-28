# -*- coding: utf-8 -*-
"""回測成本會計：2 檔 2 期手算案例；台股證交稅只在賣出收。"""
import numpy as np
import pytest

from engine.backtest import simulate, trade_cost, drift_weights
from engine.data.base import COST_TW, COST_US, CostModel

BUY = 0.001425 + 0.0010          # 0.002425
SELL = 0.001425 + 0.003 + 0.0010  # 0.005425


def test_rates():
    assert COST_TW.buy_rate == pytest.approx(BUY)
    assert COST_TW.sell_rate == pytest.approx(SELL)
    assert COST_US.sell_rate == pytest.approx(0.0005)


def test_trade_cost_tax_only_on_sell():
    c, to, n = trade_cost(np.array([0.0, 0.0]), np.array([1.0, 0.0]), COST_TW)
    assert c == pytest.approx(BUY) and to == pytest.approx(0.5) and n == 1  # 純買進：無稅
    c, to, n = trade_cost(np.array([1.0, 0.0]), np.array([0.0, 1.0]), COST_TW)
    assert c == pytest.approx(SELL + BUY) and to == pytest.approx(1.0) and n == 2
    no_tax = CostModel(0.001425, 0.001425, 0.0, 0.0010)
    c0, _, _ = trade_cost(np.array([1.0, 0.0]), np.array([0.0, 1.0]), no_tax)
    assert c - c0 == pytest.approx(0.003)  # 差額恰為證交稅 x 賣出 1.0
    # 空頭腿相反：新增空單=賣出
    cs, _, _ = trade_cost(np.zeros(2), np.array([1.0, 0.0]), COST_TW, short=True)
    assert cs == pytest.approx(SELL)


def test_two_stock_two_period_hand_case():
    # 日 0..4；A: 100,110,121,121,121；B: 50,50,55,66,66
    P = np.array([[100, 50], [110, 50], [121, 55], [121, 66], [121, 66.0]])
    events = [(0, np.array([1.0, 0.0])), (2, np.array([0.0, 1.0]))]  # 期 1 持 A，期 2 換成 B
    sim = simulate(P, events, COST_TW)
    r = sim["ret_net"]
    c0, c1 = BUY, SELL + BUY
    exp = [-c0, 0.10, (1.10) * (1 - c1) - 1.0, 0.20, 0.0]
    assert r == pytest.approx(exp)
    assert sim["costs"] == pytest.approx([c0, c1])
    assert sim["n_trades"] == 3 and sim["turnover"] == pytest.approx([1.0])
    nav = np.prod(1 + r)
    assert nav == pytest.approx((1 - c0) * 1.1 * 1.1 * (1 - c1) * 1.2)
    # 毛報酬無成本
    assert np.prod(1 + sim["ret_gross"]) == pytest.approx(1.1 * 1.1 * 1.2)
    # 美股同一案例：只有滑價 0.0005 單邊
    r_us = simulate(P, events, COST_US)["ret_net"]
    assert r_us[0] == pytest.approx(-0.0005)
    assert r_us[2] == pytest.approx(1.1 * (1 - 0.001) - 1)


def test_weight_drift_partial_rebalance():
    # 兩檔各半；A 翻倍、B 不變 -> 漂移成 2/3, 1/3；再平衡回 50/50：賣 A 1/6、買 B 1/6
    P = np.array([[100, 100], [200, 100], [200, 100.0]])
    w = np.array([0.5, 0.5])
    sim = simulate(P, [(0, w), (1, w)], COST_TW)
    assert drift_weights(w, np.array([1.0, 0.0])) == pytest.approx([2 / 3, 1 / 3])
    assert sim["costs"][1] == pytest.approx(SELL / 6 + BUY / 6)
    assert sim["turnover"] == pytest.approx([1 / 6])
    expected_day1 = (1.0 + 0.5) * (1 - (SELL + BUY) / 6) - 1.0  # 毛報酬 +50%
    assert sim["ret_net"][1] == pytest.approx(expected_day1)
