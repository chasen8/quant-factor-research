"""把引擎結果輸出成 docs/data-contract.md 規定的 JSON。

規則：NaN/Inf -> null（allow_nan=False 為保險）；浮點保留 6 位有效數字；UTF-8；緊湊分隔符號。
"""
from __future__ import annotations

import datetime as dt
import json
import math
import subprocess
import time
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from . import ENGINE_VERSION
from .backtest import default_presets, run_backtest
from .data.demo import make_demo_market
from .evaluate import EvalContext, evaluate_factor
from .registry import ROOT, Registry

PAPERS_YAML = ROOT / "factors" / "papers.yaml"
REPOS_YAML = ROOT / "factors" / "repos.yaml"
MAX_BYTES = 15 * 1024 * 1024
DEMO_MARKETS = ("DEMO_TW", "DEMO_US")


def clean(o):
    """遞迴轉成可 JSON 序列化：NaN/Inf -> None，浮點 6 位有效數字。"""
    if o is None or isinstance(o, (bool, str)):
        return o
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, (int, np.integer)):
        return int(o)
    if isinstance(o, (float, np.floating)):
        x = float(o)
        return float(f"{x:.6g}") if math.isfinite(x) else None
    if isinstance(o, (pd.Timestamp, dt.datetime, dt.date)):
        return o.strftime("%Y-%m-%d") if hasattr(o, "strftime") else str(o)
    if isinstance(o, np.ndarray):
        return [clean(v) for v in o.tolist()]
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    return str(o)


def write_json(path: Path, obj) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(clean(obj), ensure_ascii=False, allow_nan=False, separators=(",", ":"))
    path.write_text(text, encoding="utf-8")
    return len(text.encode("utf-8"))


def git_commit() -> str | None:
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, timeout=10)
        out = r.stdout.strip()
        return out if r.returncode == 0 and out else None
    except Exception:  # noqa: BLE001 git 不存在 / 不是 repo
        return None


def _load_list(path: Path, keys: tuple[str, ...], label: str, warn) -> list[dict]:
    if not path.exists():
        warn(f"警告：{path.name} 不存在，{label}.json 輸出空陣列")
        return []
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    if isinstance(doc, dict):
        for k in keys:
            if isinstance(doc.get(k), list):
                return doc[k]
        for v in doc.values():
            if isinstance(v, list):
                return v
        return []
    return doc or []


PAPER_KEYS = ["id", "title", "authors", "year", "venue", "doi", "doi_url", "free_url", "category", "market",
              "sample_period", "method", "reported_results", "code_availability", "tw_us_suitability",
              "limitations", "verification_status", "fulltext_checked"]
REPO_KEYS = ["id", "url", "purpose", "factor_count", "formula_explicit", "language", "backtest", "pushed_at",
             "stars", "queried_on", "license", "license_risk", "integration", "limitations", "academic_basis",
             "recommended"]


def convert_papers(factors: list[dict], warn) -> list[dict]:
    items = _load_list(PAPERS_YAML, ("papers",), "papers", warn)
    rev: dict[str, list[str]] = {}
    for f in factors:
        for pid in f.get("paper_ids", []):
            rev.setdefault(pid, []).append(f["id"])
    out = []
    for it in items:
        p = dict(it)
        for k in PAPER_KEYS:
            p.setdefault(k, [] if k == "authors" else (False if k == "fulltext_checked" else None))
        p["factor_ids"] = sorted(set(rev.get(p["id"], [])))
        out.append(p)
    return out


def convert_repos(factors: list[dict], warn) -> list[dict]:
    items = _load_list(REPOS_YAML, ("repos", "repositories"), "repos", warn)
    rev: dict[str, list[str]] = {}
    for f in factors:
        for r in f.get("repo_refs", []):
            rev.setdefault(str(r["repo"]).lower(), []).append(f["id"])
    out = []
    for it in items:
        r = dict(it)
        if "id" not in r and "repo" in r:
            r["id"] = r["repo"]
        for k in REPO_KEYS:
            r.setdefault(k, False if k == "recommended" else None)
        r["factor_ids"] = sorted(set(rev.get(str(r["id"]).lower(), [])))
        out.append(r)
    return out


def _spearman_mean(zs: list[np.ndarray], ids: list[str]) -> list[list[float]]:
    K = len(ids)
    acc = np.zeros((K, K))
    cnt = np.zeros((K, K))
    n_rb = zs[0].shape[0]
    for k in range(n_rb):
        df = pd.DataFrame({i: z[k] for i, z in enumerate(zs)})
        if df.notna().sum().max() < 30:
            continue
        c = df.corr(method="spearman", min_periods=30).to_numpy()
        m = np.isfinite(c)
        acc[m] += c[m]
        cnt[m] += 1
    with np.errstate(invalid="ignore", divide="ignore"):
        out = acc / cnt
    return out.tolist()


def build(out_dir: Path | str, demo: bool = True, n_stocks: int | None = None,
          markets: tuple[str, ...] = DEMO_MARKETS, log=print) -> dict:
    if not demo:
        raise SystemExit("M1 只支援 --demo（真實資料 adapter 尚未實作）")
    t0 = time.time()
    out = Path(out_dir)
    reg = Registry()
    factors = reg.defs
    sizes: dict[str, int] = {}

    # factors.json：yaml 直接轉換，去掉 smoke_test_params
    fj = [{k: v for k, v in f.items() if k != "smoke_test_params"} for f in factors]
    sizes["factors.json"] = write_json(out / "factors.json", fj)
    papers = convert_papers(factors, log)
    repos = convert_repos(factors, log)
    sizes["papers.json"] = write_json(out / "papers.json", papers)
    sizes["repos.json"] = write_json(out / "repos.json", repos)

    names_zh = {f["id"]: f["name_zh"] for f in factors}
    manifest_markets, all_presets, top_rows = [], [], []
    for mid in markets:
        tm = time.time()
        md = make_demo_market(mid, n_stocks=n_stocks)
        ctx = EvalContext(md)
        ids = [f for f in reg.ids() if reg.available(f, md.data)]
        skipped = [f for f in reg.ids() if f not in ids]
        log(f"[{mid}] 股票 {md.n_stocks}、交易日 {len(md.dates)}、調倉 {ctx.n_rb} 期；"
            f"評估 {len(ids)} 個因子（缺資料略過：{skipped or '無'}）")
        evals = {}
        for fid in ids:
            ev = evaluate_factor(ctx, reg, fid)
            evals[fid] = ev
            sizes[f"stats/{mid}/{fid}.json"] = write_json(out / "stats" / mid / f"{fid}.json", ev.stats)
            s = ev.stats["summary"]
            top_rows.append({"factor_id": fid, "market": mid, "rank_ic_mean": s["rank_ic_mean"],
                             "rank_icir_ann": s["rank_icir_ann"], "is_demo": True})
        # compare
        zs = [evals[f].z for f in ids]
        ls = pd.DataFrame({f: evals[f].ls_net for f in ids})
        comp = {"market": mid, "is_demo": md.is_demo, "factor_ids": ids,
                "factor_corr": _spearman_mean(zs, ids), "ls_return_corr": ls.corr().to_numpy().tolist()}
        sizes[f"compare/{mid}.json"] = write_json(out / "compare" / f"{mid}.json", comp)
        # backtests
        presets = default_presets(mid, names_zh, set(ids))
        zmap = {f: evals[f].z for f in ids}
        for pr in presets:
            res = run_backtest(ctx, reg, zmap, pr)
            sizes[f"backtests/{mid}/{pr.id}.json"] = write_json(out / "backtests" / mid / f"{pr.id}.json", res)
            all_presets.append(pr.as_dict())
        manifest_markets.append({
            "id": mid, "label": md.label, "is_demo": md.is_demo, "n_stocks": md.n_stocks,
            "start": md.dates[0].strftime("%Y-%m-%d"), "end": md.dates[-1].strftime("%Y-%m-%d"),
            "oos_start": ctx.oos_start.strftime("%Y-%m-%d"), "cost_model": md.cost.as_dict(),
            "benchmark": md.benchmark,
        })
        log(f"[{mid}] 完成，耗時 {time.time() - tm:.0f}s")
    sizes["backtests/index.json"] = write_json(out / "backtests" / "index.json", {"presets": all_presets})

    # dashboard
    today = dt.date.today().isoformat()
    top_rows = [r for r in top_rows if r["rank_ic_mean"] is not None]
    top_rows.sort(key=lambda r: -r["rank_ic_mean"])
    by_level = {m: {lv: 0 for lv in ("L0", "L1", "L2", "L3", "L4")} for m in ("TW", "US")}
    for f in factors:
        for m in ("TW", "US"):
            by_level[m][f["validation_level"][m]] += 1
    recent = []
    for p in sorted(papers, key=lambda p: -(p.get("year") or 0))[:5]:
        recent.append({"type": "paper", "id": p["id"], "title": p.get("title") or p["id"],
                       "date": f"{p['year']}-01-01" if p.get("year") else today})
    for r in sorted(repos, key=lambda r: str(r.get("pushed_at") or ""), reverse=True)[:5]:
        recent.append({"type": "repo", "id": r["id"], "title": r["id"], "date": str(r.get("pushed_at") or today)[:10]})
    for f in factors[:5]:
        recent.append({"type": "factor", "id": f["id"], "title": f["name_zh"], "date": today})
    dash = {
        "is_demo": True,
        "counts": {"factors": len(factors), "papers": len(papers), "repos": len(repos),
                   "by_category": dict(Counter(f["category"] for f in factors)),
                   "by_evidence": dict(Counter(f["evidence_status"] for f in factors)),
                   "by_level": by_level},
        "top_rank_ic": top_rows[:10], "recent": recent,
    }
    sizes["dashboard.json"] = write_json(out / "dashboard.json", dash)

    manifest = {"generated_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "engine_version": ENGINE_VERSION, "git_commit": git_commit(), "is_demo": True,
                "markets": manifest_markets, "factor_ids": reg.ids()}
    sizes["manifest.json"] = write_json(out / "manifest.json", manifest)

    total = sum(sizes.values())
    log(f"輸出 {len(sizes)} 個檔，總大小 {total / 1024 / 1024:.2f} MB，總耗時 {time.time() - t0:.0f}s")
    if total >= MAX_BYTES:
        raise RuntimeError(f"輸出 {total} bytes 超過 15MB 上限")
    return {"files": len(sizes), "bytes": total, "seconds": time.time() - t0}
