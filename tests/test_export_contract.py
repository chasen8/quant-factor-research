# -*- coding: utf-8 -*-
"""輸出合約：build 到暫存目錄，逐欄對照 docs/data-contract.md。"""
import json
import re
from pathlib import Path

import pytest

from engine.export import build

DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
COST_KEYS = {"buy_commission", "sell_commission", "sell_tax", "slippage"}
PROV_KEYS = {"data_source", "universe", "avg_n_stocks", "start", "end", "oos_start", "rebalance", "horizon_days",
             "n_quantiles", "cost_model", "n_trials", "engine_version", "params"}
SUMMARY_KEYS = {"ic_mean", "ic_std", "icir", "icir_ann", "ic_tstat_nw", "ic_win_rate", "rank_ic_mean", "rank_ic_std",
                "rank_icir", "rank_icir_ann", "rank_ic_tstat_nw", "rank_ic_win_rate", "is_rank_ic_mean",
                "oos_rank_ic_mean", "oos_rank_ic_tstat_nw", "coverage_mean", "monotonicity", "ls_ann_return_gross",
                "ls_ann_return_net", "ls_sharpe_gross", "ls_sharpe_net", "ls_mdd_net", "top_excess_ann_net",
                "top_sharpe_net", "turnover_ann", "factor_autocorr_1", "dsr"}
METRIC_KEYS = {"cagr", "vol", "sharpe", "sortino", "mdd", "calmar", "win_rate", "turnover_ann", "n_rebalances",
               "n_trades", "cost_drag_ann", "excess_cagr", "beta", "alpha_ann", "info_ratio", "tracking_error",
               "cagr_gross"}
FACTOR_KEYS = ["id", "name_zh", "name_en", "category", "subcategory", "aliases", "formula_latex", "variables",
               "formula_source_type", "direction", "unit", "required_fields", "frequency", "params", "pit_rules",
               "corporate_action_notes", "suggested_markets", "paper_ids", "repo_refs", "known_results",
               "evidence_status", "validation_level", "limitations", "same_name_different_formula",
               "transaction_cost_note", "python"]
PAPER_KEYS = {"id", "title", "authors", "year", "venue", "doi", "doi_url", "free_url", "category", "market",
              "sample_period", "method", "reported_results", "code_availability", "tw_us_suitability", "limitations",
              "verification_status", "fulltext_checked", "factor_ids"}
REPO_KEYS = {"id", "url", "purpose", "factor_count", "formula_explicit", "language", "backtest", "pushed_at", "stars",
             "queried_on", "license", "license_risk", "integration", "limitations", "academic_basis", "recommended",
             "factor_ids"}


def _no_nan(x):
    raise ValueError(f"非法常數 {x}")


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"), parse_constant=_no_nan)


@pytest.fixture(scope="module")
def out(tmp_path_factory):
    d = tmp_path_factory.mktemp("data")
    build(d, demo=True, n_stocks=70, log=lambda *_: None)
    return d


def test_manifest(out):
    m = load(out / "manifest.json")
    assert {"generated_at", "engine_version", "git_commit", "is_demo", "markets", "factor_ids"} <= m.keys()
    assert m["is_demo"] is True and len(m["factor_ids"]) == 36
    assert [x["id"] for x in m["markets"]] == ["DEMO_TW", "DEMO_US"]
    for mk in m["markets"]:
        assert {"id", "label", "is_demo", "n_stocks", "start", "end", "oos_start", "cost_model", "benchmark"} <= mk.keys()
        assert mk["is_demo"] is True and "合成" in mk["label"]
        assert set(mk["cost_model"]) == COST_KEYS
        assert all(DATE.match(mk[k]) for k in ("start", "end", "oos_start"))
    tw = m["markets"][0]["cost_model"]
    assert tw["sell_tax"] == 0.003 and m["markets"][1]["cost_model"]["sell_tax"] == 0


def test_factors_papers_repos_dashboard(out):
    fs = load(out / "factors.json")
    assert len(fs) == 36
    for f in fs:
        assert all(k in f for k in FACTOR_KEYS) and "smoke_test_params" not in f
        assert f["validation_level"] == {"TW": "L0", "US": "L0"}
    papers, repos = load(out / "papers.json"), load(out / "repos.json")
    assert isinstance(papers, list) and isinstance(repos, list)
    for p in papers:
        assert PAPER_KEYS <= p.keys()
    for r in repos:
        assert REPO_KEYS <= r.keys()
    pid = {p["id"]: p for p in papers}
    for f in fs:  # 反查一致
        for x in f["paper_ids"]:
            if x in pid:
                assert f["id"] in pid[x]["factor_ids"]
    d = load(out / "dashboard.json")
    assert d["is_demo"] is True
    assert {"factors", "papers", "repos", "by_category", "by_evidence", "by_level"} <= d["counts"].keys()
    for m in ("TW", "US"):
        assert d["counts"]["by_level"][m]["L0"] == 36
        assert all(d["counts"]["by_level"][m][k] == 0 for k in ("L1", "L2", "L3", "L4"))
    assert d["top_rank_ic"] and all(r["is_demo"] is True for r in d["top_rank_ic"])
    assert all({"type", "id", "title", "date"} <= r.keys() for r in d["recent"])


def test_stats_files(out):
    for mid, n_expected in (("DEMO_TW", 36), ("DEMO_US", 34)):
        files = sorted((out / "stats" / mid).glob("*.json"))
        assert len(files) == n_expected
        for p in files:
            s = load(p)
            assert s["factor_id"] == p.stem and s["market"] == mid
            assert s["is_demo"] is True and s["evidence_label"] == "示範資料"
            assert PROV_KEYS <= s["provenance"].keys() and s["provenance"]["rebalance"] == "M"
            assert set(s["provenance"]["cost_model"]) == COST_KEYS
            assert s["provenance"]["horizon_days"] == 21 and s["provenance"]["n_quantiles"] == 5
            assert s["provenance"]["n_trials"] == 1
            assert set(s["summary"]) == SUMMARY_KEYS
            ic = s["ic_series"]
            n = len(ic["dates"])
            assert n > 0 and all(len(ic[k]) == n for k in ("ic", "rank_ic", "rank_ic_roll12"))
            assert all(DATE.match(d) for d in ic["dates"])
            q = s["quantiles"]
            assert q["n_q"] == 5
            assert set(q["cum"]) == {"Q1", "Q2", "Q3", "Q4", "Q5", "LS", "TOP_EXCESS"}
            assert all(len(v) == len(q["dates"]) and v[0] == 1 for v in q["cum"].values())
            assert set(q["mean_period_return"]) == {"Q1", "Q2", "Q3", "Q4", "Q5"}
            assert s["decay"]["horizons"] == [1, 5, 10, 20, 60, 120] and len(s["decay"]["rank_ic"]) == 6
            dist = s["distribution"]
            assert all(len(dist[k]) == len(dist["dates"]) for k in ("p10", "p25", "p50", "p75", "p90"))
            assert [x["label"] for x in s["subperiods"]] == ["2010-2014", "2015-2019", "2020-2021", "2022-2025"]
            assert all({"label", "start", "end", "rank_ic_mean"} <= x.keys() for x in s["subperiods"])
            assert s["bias_checks"] and all(
                b["status"] in ("pass", "warn", "fail") and {"key", "message"} <= b.keys() for b in s["bias_checks"])


def test_compare(out):
    for mid, n in (("DEMO_TW", 36), ("DEMO_US", 34)):
        c = load(out / "compare" / f"{mid}.json")
        assert c["market"] == mid and c["is_demo"] is True and len(c["factor_ids"]) == n
        for key in ("factor_corr", "ls_return_corr"):
            assert len(c[key]) == n and all(len(r) == n for r in c[key])
        assert all(abs(c["factor_corr"][i][i] - 1) < 1e-5 for i in range(n))


def test_backtests(out):
    idx = load(out / "backtests" / "index.json")
    assert len(idx["presets"]) >= 16
    assert {p["market"] for p in idx["presets"]} == {"DEMO_TW", "DEMO_US"}
    assert {"M", "Q"} <= {p["rebalance"] for p in idx["presets"]}
    for p in idx["presets"]:
        assert {"id", "market", "label", "factors", "rebalance", "top_q"} <= p.keys()
        assert all({"id", "weight"} == set(f) for f in p["factors"])
        r = load(out / "backtests" / p["market"] / f"{p['id']}.json")
        assert r["preset"] == p and r["is_demo"] is True and r["evidence_label"] == "示範資料"
        assert PROV_KEYS <= r["provenance"].keys() and r["provenance"]["rebalance"] == p["rebalance"]
        n = len(r["dates"])
        assert n > 1000 and len(r["nav"]) == n and len(r["bench_nav"]) == n and len(r["drawdown"]) == n
        assert set(r["metrics"]) == METRIC_KEYS
        assert all(set(a) == {"year", "strat", "bench"} for a in r["annual"])
        assert all(set(a) == {"year", "month", "ret"} for a in r["monthly"])
        assert max(r["drawdown"]) <= 1e-9 and r["metrics"]["mdd"] >= 0
        assert r["metrics"]["cost_drag_ann"] >= -1e-9


def test_size_and_no_secret(out):
    total = sum(p.stat().st_size for p in out.rglob("*.json"))
    assert total < 15 * 1024 * 1024
    assert not any(re.search(r"api[_-]?key|secret", p.read_text(encoding="utf-8"), re.I)
                   for p in [out / "manifest.json", out / "dashboard.json"])
