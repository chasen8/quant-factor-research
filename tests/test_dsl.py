# -*- coding: utf-8 -*-
"""DSL：合法式子與 pandas 手寫一致；惡意/過大式子被拒絕。"""
import numpy as np
import pandas as pd
import pytest

from engine.dsl import DSLError, compile_formula


@pytest.fixture(scope="module")
def data():
    rng = np.random.default_rng(3)
    idx = pd.bdate_range("2022-01-03", periods=120)
    cols = [f"S{i}" for i in range(15)]

    def w(a):
        return pd.DataFrame(a, index=idx, columns=cols)

    close = 50 * np.exp(np.cumsum(rng.normal(0, 0.02, (120, 15)), axis=0))
    return {"close_adj": w(close), "open": w(close * (1 + rng.normal(0, 0.01, (120, 15)))),
            "volume": w(rng.integers(1000, 9000, (120, 15)).astype(float)), "high": w(close * 1.01),
            "low": w(close * 0.99), "vwap": w(close)}


def eq(a, b):
    pd.testing.assert_frame_equal(a, b, check_exact=False, rtol=1e-12)


def test_main_example(data):
    f = compile_formula("rank(ts_mean(close, 5)) - rank(volume)")
    exp = (data["close_adj"].rolling(5).mean().rank(axis=1, pct=True)
           - data["volume"].rank(axis=1, pct=True))
    eq(f.evaluate(data), exp)
    assert f.variables == {"close", "volume"}


def test_more_operators(data):
    c, o, v = data["close_adj"], data["open"], data["volume"]
    eq(compile_formula("delta(close, 3) / delay(close, 3)").evaluate(data), (c - c.shift(3)) / c.shift(3))
    eq(compile_formula("-log(close) + abs(open - close) ** 2").evaluate(data), -np.log(c) + (o - c).abs() ** 2)
    eq(compile_formula("ts_corr(close, volume, 10)").evaluate(data), c.rolling(10).corr(v))
    eq(compile_formula("zscore(returns)").evaluate(data),
       (lambda r: r.sub(r.mean(axis=1), axis=0).div(r.std(axis=1, ddof=1), axis=0))(c.pct_change(fill_method=None)))
    eq(compile_formula("where(close > open, 1, -1) * ts_std(close, 5)").evaluate(data),
       pd.DataFrame(np.where(c > o, 1.0, -1.0), index=c.index, columns=c.columns) * c.rolling(5).std())
    eq(compile_formula("ts_rank(close, 7)").evaluate(data), c.rolling(7).rank(pct=True))
    eq(compile_formula("max2(close, open) - min2(close, open)").evaluate(data), (c - o).abs())
    out = compile_formula("1 / (close - close)").evaluate(data)  # inf -> NaN
    assert not np.isinf(out.to_numpy()).any()


def test_no_lookahead_in_dsl(data):
    f = compile_formula("rank(delta(close, 5)) + ts_mean(volume, 10)")
    a = f.evaluate(data)
    d2 = {k: v.copy() for k, v in data.items()}
    for v in d2.values():
        v.iloc[-10:] = 12345.0
    b = f.evaluate(d2)
    pd.testing.assert_frame_equal(a.iloc[:-10], b.iloc[:-10])


@pytest.mark.parametrize("bad", [
    "__import__('os')",
    "__import__('os').system('echo hi')",
    "close.__class__",
    "close.shift(1)",
    "(lambda: 1)()",
    "close[0]",
    "close['x']",
    "[c for c in close]",
    "ts_mean(close, 1000)",
    "ts_mean(close, 253)",
    "ts_mean(close, 0)",
    "ts_mean(close, volume)",
    "ts_mean(close, 5.5)",
    "ts_mean(x=close, d=5)",
    "eval('1')",
    "open_",
    "__builtins__",
    "'abc'",
    "None",
    "close if open else volume",
    "close and open",
    "close ** volume",
    "close ** 50",
    "close @ open",
    "close // open",
    "close % open",
    "rank(close, 3)",
    "",
    "close +",
    "abs(" * 12 + "close" + ")" * 12,          # 巢狀過深
    "-" * 600 + "close",                       # 過長
    " + ".join(["close"] * 120),               # 節點過多
])
def test_rejected(bad):
    with pytest.raises(DSLError):
        compile_formula(bad)


def test_boundary_accepts():
    compile_formula("ts_mean(close, 252)")
    compile_formula("abs(" * 8 + "close" + ")" * 8)
    compile_formula("close ** 2")
    compile_formula("close ** -1")
