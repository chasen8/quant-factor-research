# -*- coding: utf-8 -*-
"""Consistency tests for factors/papers.yaml and factors/repos.yaml."""
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
PAPERS_YAML = ROOT / "factors" / "papers.yaml"
REPOS_YAML = ROOT / "factors" / "repos.yaml"
FACTORS_YAML = ROOT / "factors" / "factors.yaml"

PAPER_FIELDS = [
    "id", "title", "authors", "year", "venue", "doi", "doi_url", "free_url",
    "category", "market", "sample_period", "method", "reported_results",
    "code_availability", "tw_us_suitability", "limitations",
    "verification_status", "fulltext_checked",
]
REPO_FIELDS = [
    "id", "url", "purpose", "factor_count", "formula_explicit", "language",
    "backtest", "pushed_at", "stars", "queried_on", "license", "license_risk",
    "integration", "limitations", "academic_basis", "recommended",
]
LICENSE_RISKS = {"ok", "copyleft", "none", "restricted"}
INTEGRATIONS = {"高", "中高", "中", "低"}


def _load(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def papers():
    d = _load(PAPERS_YAML)
    assert d["schema_version"] == 1
    return d["papers"]


@pytest.fixture(scope="module")
def repos():
    d = _load(REPOS_YAML)
    assert d["schema_version"] == 1
    return d["repos"]


def test_yaml_loadable():
    assert isinstance(_load(PAPERS_YAML), dict)
    assert isinstance(_load(REPOS_YAML), dict)


def test_paper_ids_unique(papers):
    ids = [p["id"] for p in papers]
    assert len(ids) == len(set(ids))
    assert len(ids) == 39


def test_repo_ids_unique(repos):
    ids = [r["id"] for r in repos]
    assert len(ids) == len(set(ids))
    assert len(ids) == 22


def test_paper_required_fields(papers):
    for p in papers:
        for k in PAPER_FIELDS:
            assert k in p, f"{p.get('id')} missing {k}"
        assert isinstance(p["authors"], list) and p["authors"]
        assert all(isinstance(a, str) for a in p["authors"])
        assert isinstance(p["year"], int)
        assert isinstance(p["fulltext_checked"], bool)
        assert p["id"].startswith(("02a:P-", "02b:P-"))


def test_repo_required_fields(repos):
    for r in repos:
        for k in REPO_FIELDS:
            assert k in r, f"{r.get('id')} missing {k}"
        assert r["integration"] in INTEGRATIONS
        assert isinstance(r["recommended"], bool)
        assert r["queried_on"] == "2026-10-28"
        assert isinstance(r["stars"], int)


def test_factor_paper_ids_exist(papers):
    ids = {p["id"] for p in papers}
    factors = _load(FACTORS_YAML)["factors"]
    missing = {pid for f in factors for pid in f.get("paper_ids", [])} - ids
    assert not missing, f"factors.yaml references unknown papers: {sorted(missing)}"


def test_repos_exactly_five_recommended(repos):
    rec = sorted(r["id"] for r in repos if r["recommended"])
    assert len(rec) == 5, rec
    assert set(rec) == {
        "microsoft/qlib", "wukan1986/ta_cn", "stefan-jansen/alphalens-reloaded",
        "OpenSourceAP/CrossSection", "trevorstephens/gplearn",
    }


def test_license_risk_valid(repos):
    for r in repos:
        assert r["license_risk"] in LICENSE_RISKS, r["id"]


def test_doi_url_prefix(papers):
    for p in papers:
        if p["doi_url"] is not None:
            assert p["doi_url"].startswith("https://doi.org/"), p["id"]
            assert p["doi_url"] == "https://doi.org/" + p["doi"], p["id"]
        else:
            assert p["doi"] is None, p["id"]
