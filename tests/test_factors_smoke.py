# -*- coding: utf-8 -*-
"""Smoke tests for factors/factors.yaml.

Uses exec() ONLY on the code strings that this project wrote itself in factors.yaml
(not user input). Synthetic random data: checks code health, not research results.
"""
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
YAML_PATH = ROOT / "factors" / "factors.yaml"
DOC_A = ROOT / "docs" / "research" / "02a-papers-momentum-reversal-value-risk.md"
DOC_B = ROOT / "docs" / "research" / "02b-papers-quality-liquidity-ml-meta.md"

CATEGORIES = {"momentum", "reversal", "value", "quality", "risk", "liquidity", "composite_ml"}
REQUIRED_KEYS = ["id", "name_zh", "name_en", "category", "subcategory", "aliases", "formula_latex", "variables",
                 "formula_source_type", "direction", "unit", "required_fields", "frequency", "params", "pit_rules",
                 "corporate_action_notes", "suggested_markets", "paper_ids", "repo_refs", "known_results",
                 "evidence_status", "validation_level", "limitations", "same_name_different_formula",
                 "transaction_cost_note", "python"]
N_DAYS, N_STOCKS, TAIL = 300, 50, 20

_DOC = yaml.safe_load(YAML_PATH.read_text(encoding="utf-8"))
FACTORS = _DOC["factors"]


def _paper_ids():
    ids = set()
    for path, pre in ((DOC_A, "02a"), (DOC_B, "02b")):
        for m in re.finditer(r"^## (P-[A-Z]\d+)", path.read_text(encoding="utf-8"), re.M):
            ids.add(f"{pre}:{m.group(1)}")
    return ids


def make_data(seed=0):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2023-01-02", periods=N_DAYS)
    cols = [f"S{i:03d}" for i in range(N_STOCKS)]
    shape = (N_DAYS, N_STOCKS)

    def wide(a):
        return pd.DataFrame(a, index=idx, columns=cols)

    ret = rng.normal(0.0004, 0.02, shape)
    close = 50 * np.exp(np.cumsum(ret, axis=0))
    open_ = close * (1 + rng.normal(0, 0.005, shape))
    high = np.maximum(open_, close) * (1 + np.abs(rng.normal(0, 0.005, shape)))
    low = np.minimum(open_, close) * (1 - np.abs(rng.normal(0, 0.005, shape)))
    vwap = (high + low + close) / 3
    volume = rng.integers(10_000, 5_000_000, shape).astype(float)
    shares = np.full(shape, 1e8) * rng.uniform(0.5, 2, (1, N_STOCKS))

    def acc_series(base_lo, base_hi):
        # quarterly step function (changes every ~63 days) positive values
        base = rng.uniform(base_lo, base_hi, (1, N_STOCKS))
        steps = np.repeat(rng.uniform(0.9, 1.15, (N_DAYS // 63 + 1, N_STOCKS)), 63, axis=0)[:N_DAYS]
        return base * np.cumprod(steps, axis=0) * 1e9

    total_assets = acc_series(5, 20)
    revenue = total_assets * rng.uniform(0.5, 1.2, (1, N_STOCKS))
    cogs = revenue * rng.uniform(0.5, 0.8, (1, N_STOCKS))
    data = {
        "close_adj": wide(close), "close_raw": wide(close), "open": wide(open_), "high": wide(high),
        "low": wide(low), "volume": wide(volume), "vwap": wide(vwap),
        "turnover_value": wide(volume * vwap), "shares_outstanding": wide(shares),
        "market_cap": wide(close * shares),
        "book_equity": wide(total_assets * rng.uniform(0.3, 0.6, (1, N_STOCKS))),
        "net_income": wide(revenue * rng.uniform(0.02, 0.15, (1, N_STOCKS)) * rng.uniform(0.8, 1.2, shape)),
        "operating_cash_flow": wide(revenue * rng.uniform(0.02, 0.2, (1, N_STOCKS)) * rng.uniform(0.8, 1.2, shape)),
        "total_assets": wide(total_assets), "revenue": wide(revenue), "cogs": wide(cogs),
        "gross_profit": wide(revenue - cogs),
        "sga_expense": wide(revenue * 0.1), "interest_expense": wide(revenue * 0.01),
        "long_term_debt": wide(total_assets * rng.uniform(0.05, 0.3, (1, N_STOCKS)) * rng.uniform(0.9, 1.1, shape)),
        "current_assets": wide(total_assets * rng.uniform(0.3, 0.5, (1, N_STOCKS)) * rng.uniform(0.9, 1.1, shape)),
        "current_liabilities": wide(total_assets * rng.uniform(0.15, 0.3, (1, N_STOCKS)) * rng.uniform(0.9, 1.1, shape)),
        "monthly_revenue": wide(revenue / 12 * np.repeat(rng.uniform(0.8, 1.2, (N_DAYS // 21 + 1, N_STOCKS)), 21, axis=0)[:N_DAYS]),
    }
    return data


def load_compute(f):
    ns = {}
    exec(compile(f["python"], f"<factor {f['id']}>", "exec"), ns)  # our own code strings, not user input
    return ns["compute"]


def test_yaml_schema():
    assert _DOC["schema_version"] == 1
    ids = [f["id"] for f in FACTORS]
    assert len(ids) == len(set(ids))
    assert len(FACTORS) >= 30
    paper_ids = _paper_ids()
    from_vocab = None
    for f in FACTORS:
        for k in REQUIRED_KEYS:
            assert k in f, (f["id"], k)
        assert re.fullmatch(r"[A-Z0-9_]+", f["id"]), f["id"]
        assert f["category"] in CATEGORIES
        assert f["direction"] in (1, -1)
        assert f["frequency"] in ("daily", "monthly", "quarterly")
        assert f["evidence_status"] in ("文獻實證", "尚未驗證")
        assert f["formula_source_type"] in ("原文公式", "標準化定義")
        assert f["validation_level"] == {"TW": "L0", "US": "L0"}
        assert set(f["suggested_markets"]) == {"TW", "US"}
        for p in f["paper_ids"]:
            assert p in paper_ids, (f["id"], p)
        if not f["paper_ids"]:
            assert f["evidence_status"] == "尚未驗證" and f.get("paper_ids_note"), f["id"]
        for kr in f["known_results"]:
            assert kr["source"] in paper_ids
            assert kr["evidence"] == "文獻實證"
        for r in f["repo_refs"]:
            assert r["repo"] and r["license"]
        assert f["python"].count("def compute(") == 1


def test_no_self_backtest_label():
    for f in FACTORS:
        assert "自行回測" not in f["evidence_status"]
        assert f["evidence_status"] != "自行回測"


def test_vocab_matches_doc():
    doc = (ROOT / "docs" / "research" / "03-factor-database.md").read_text(encoding="utf-8")
    used = {r for f in FACTORS for r in f["required_fields"]}
    for r in used:
        assert f"`{r}`" in doc, r
    for f in FACTORS:
        assert f["id"] in doc


def test_code_hygiene():
    for f in FACTORS:
        code = f["python"]
        assert "eval(" not in code and "exec(" not in code, f["id"]
        assert not re.search(r"shift\(\s*-", code), f["id"]
        assert not re.search(r"periods\s*=\s*-", code), f["id"]
        assert not re.search(r"\.(?:diff|pct_change)\(\s*-", code), f["id"]
        for line in code.splitlines():
            if line.startswith(("import ", "from ")):
                assert line.split()[1] in ("numpy", "pandas"), (f["id"], line)


@pytest.fixture(scope="module")
def data():
    return make_data()


@pytest.mark.parametrize("f", FACTORS, ids=[f["id"] for f in FACTORS])
def test_compute_shape_and_not_all_nan(f, data):
    compute = load_compute(f)
    out = compute({k: data[k] for k in f["required_fields"]}, **f.get("smoke_test_params", {}))
    assert isinstance(out, pd.DataFrame)
    assert out.shape == data["close_adj"].shape
    assert out.index.equals(data["close_adj"].index)
    assert list(out.columns) == list(data["close_adj"].columns)
    assert not np.isinf(out.to_numpy(dtype=float)).any(), "inf in output"
    tail = out.iloc[-30:]
    assert tail.notna().to_numpy().any(), "all NaN after warm-up"
    assert tail.notna().to_numpy().mean() > 0.5, "mostly NaN after warm-up"


@pytest.mark.parametrize("f", FACTORS, ids=[f["id"] for f in FACTORS])
def test_no_lookahead(f, data):
    compute = load_compute(f)
    params = f.get("smoke_test_params", {})
    base_in = {k: data[k] for k in f["required_fields"]}
    out1 = compute(base_in, **params)

    rng = np.random.default_rng(123)
    mod = {}
    for k, df in base_in.items():
        df2 = df.copy()
        # scale-aware random garbage (strictly positive) for the last TAIL days
        scale = float(np.nanmean(df.to_numpy()))
        df2.iloc[-TAIL:] = rng.uniform(0.2, 3.0, df2.iloc[-TAIL:].shape) * scale
        mod[k] = df2
    out2 = compute(mod, **params)

    cut = N_DAYS - TAIL  # rows [0, cut) must be unchanged
    a, b = out1.iloc[:cut], out2.iloc[:cut]
    assert a.isna().equals(b.isna()), "NaN pattern changed -> look-ahead"
    pd.testing.assert_frame_equal(a, b, check_exact=True)


def test_lookahead_test_is_not_vacuous(data):
    """Most factors must react to the modified tail (a few legitimately do not, e.g. skip>=21 momentum)."""
    rng = np.random.default_rng(7)
    reacted = 0
    for f in FACTORS:
        compute = load_compute(f)
        params = f.get("smoke_test_params", {})
        base_in = {k: data[k] for k in f["required_fields"]}
        mod = {}
        for k, df in base_in.items():
            df2 = df.copy()
            df2.iloc[-TAIL:] = rng.uniform(0.2, 3.0, df2.iloc[-TAIL:].shape) * float(np.nanmean(df.to_numpy()))
            mod[k] = df2
        o1, o2 = compute(base_in, **params), compute(mod, **params)
        if not o1.iloc[-TAIL:].fillna(0).equals(o2.iloc[-TAIL:].fillna(0)):
            reacted += 1
    assert reacted >= int(0.8 * len(FACTORS))
