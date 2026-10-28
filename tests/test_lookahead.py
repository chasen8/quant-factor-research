# -*- coding: utf-8 -*-
"""防前視：竄改評估截點之後的所有資料，截點之前（含其前瞻視窗）的 IC 不變。"""
import copy

import numpy as np
import pytest

from engine.data.demo import make_demo_market
from engine.evaluate import EvalContext, evaluate_factor
from engine.evaluate.factor_eval import H_IC
from engine.registry import Registry

FACTORS = ["MOM_12_1", "REV_1M", "BM", "GPOA", "VOL_252", "ILLIQ", "REV_YOY", "ALPHA101_002", "BETA_BAB"]


@pytest.fixture(scope="module")
def base():
    md = make_demo_market("DEMO_TW", n_stocks=70)
    return md, EvalContext(md), Registry()


def _tamper(md, cut_pos):
    md2 = copy.copy(md)
    rng = np.random.default_rng(99)
    new = {}
    for k, df in md.data.items():
        d2 = df.copy()
        tail = d2.iloc[cut_pos + 1:]
        scale = float(np.nanmean(df.to_numpy()))
        garbage = rng.uniform(0.2, 3.0, tail.shape) * scale
        d2.iloc[cut_pos + 1:] = np.where(tail.notna().to_numpy(), garbage, np.nan)
        new[k] = d2
    md2.data = new
    return md2


def test_ic_before_cutoff_unchanged(base):
    md, ctx, reg = base
    cut_pos = int(len(md.dates) * 0.6)
    ctx2 = EvalContext(_tamper(md, cut_pos))
    assert ctx.n_rb == ctx2.n_rb
    # 該期的前瞻視窗（t+1+h）完全落在截點之前
    safe = ctx.rb + 1 + H_IC <= cut_pos
    assert safe.sum() > 50
    for fid in FACTORS:
        a = evaluate_factor(ctx, reg, fid)
        b = evaluate_factor(ctx2, reg, fid)
        assert np.array_equal(a.ric[safe], b.ric[safe], equal_nan=True), fid
        # 因子值本身：t <= cutoff 的截面完全相同（不需要任何前瞻）
        pre = ctx.rb <= cut_pos
        assert np.array_equal(a.z[pre], b.z[pre], equal_nan=True), fid


def test_tamper_test_is_not_vacuous(base):
    md, ctx, reg = base
    cut_pos = int(len(md.dates) * 0.6)
    ctx2 = EvalContext(_tamper(md, cut_pos))
    after = ctx.rb > cut_pos + 30
    changed = 0
    for fid in FACTORS:
        a = evaluate_factor(ctx, reg, fid)
        b = evaluate_factor(ctx2, reg, fid)
        if not np.array_equal(a.ric[after], b.ric[after], equal_nan=True):
            changed += 1
    assert changed >= len(FACTORS) - 1


def test_no_negative_shift_in_engine_sources():
    import re
    from pathlib import Path
    root = Path(__file__).resolve().parents[1] / "engine"
    for p in root.rglob("*.py"):
        txt = p.read_text(encoding="utf-8")
        assert not re.search(r"shift\(\s*-", txt), p
        assert not re.search(r"periods\s*=\s*-", txt), p
