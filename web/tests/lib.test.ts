import fs from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { dataUrl, joinBase, marketKind } from "@/lib/data";
import { fmtInt, fmtNum, fmtPct, fmtSigned, fmtSignedPct, fmtStr, isNum, costToText, sign } from "@/lib/format";
import { EMPTY_FILTERS, buildSearchDocs, createSearcher, dataNeed, filterFactors, parseIds, toggle } from "@/lib/filter";
import { parseFavorites, safeGet, safeSet } from "@/lib/storage";
import { highlightPython } from "@/lib/highlight";
import { toCsv } from "@/lib/csv";
import type {
  BacktestResult, CompareData, Dashboard, Factor, FactorStats, Manifest, Paper, Repo,
} from "@/lib/types";

const DATA = path.resolve(import.meta.dirname, "..", "public", "data");
const read = <T,>(p: string): T => JSON.parse(fs.readFileSync(path.join(DATA, p), "utf-8")) as T;

describe("format：null / NaN 一律顯示「—」", () => {
  it("fmtNum", () => {
    expect(fmtNum(null)).toBe("—");
    expect(fmtNum(undefined)).toBe("—");
    expect(fmtNum(NaN)).toBe("—");
    expect(fmtNum(Infinity)).toBe("—");
    expect(fmtNum(1.23456, 3)).toBe("1.235");
    expect(fmtNum(0)).toBe("0.00");
  });
  it("fmtPct / fmtSigned / fmtSignedPct", () => {
    expect(fmtPct(0.012)).toBe("1.2%");
    expect(fmtPct(null)).toBe("—");
    expect(fmtPct(-0.05, 0)).toBe("-5%");
    expect(fmtSigned(0.5)).toBe("+0.50");
    expect(fmtSigned(-0.5)).toBe("-0.50");
    expect(fmtSigned(null)).toBe("—");
    expect(fmtSignedPct(0.02, 2)).toBe("+2.00%");
    expect(fmtSignedPct(NaN)).toBe("—");
  });
  it("fmtInt / fmtStr / isNum / sign", () => {
    expect(fmtInt(9308)).toBe("9,308");
    expect(fmtInt(null)).toBe("—");
    expect(fmtStr("")).toBe("—");
    expect(fmtStr(null)).toBe("—");
    expect(fmtStr("x")).toBe("x");
    expect(isNum(NaN)).toBe(false);
    expect(isNum(0)).toBe(true);
    expect(sign(null)).toBe(0);
    expect(sign(-1)).toBe(-1);
  });
  it("輸出不含 NaN 字樣", () => {
    for (const v of [null, undefined, NaN, Infinity, -Infinity]) {
      expect(fmtNum(v)).not.toContain("NaN");
      expect(fmtPct(v)).not.toContain("NaN");
      expect(fmtSignedPct(v)).not.toContain("NaN");
    }
  });
  it("costToText", () => {
    const t = costToText({ buy_commission: 0.001425, sell_commission: 0.001425, sell_tax: 0.003, slippage: 0.001 });
    expect(t).toContain("0.1425%");
    expect(t).toContain("0.3%");
  });
});

describe("dataUrl（basePath）", () => {
  it("無 basePath", () => {
    expect(dataUrl("manifest.json", "")).toBe("/data/manifest.json");
    expect(dataUrl("/stats/DEMO_TW/BM.json", "")).toBe("/data/stats/DEMO_TW/BM.json");
  });
  it("有 basePath", () => {
    expect(dataUrl("manifest.json", "/quant-factor-research")).toBe("/quant-factor-research/data/manifest.json");
    expect(dataUrl("factors.json", "/quant-factor-research/")).toBe("/quant-factor-research/data/factors.json");
  });
  it("joinBase", () => {
    expect(joinBase("", "a/b")).toBe("/a/b");
    expect(joinBase("/x", "/a")).toBe("/x/a");
  });
  it("marketKind", () => {
    expect(marketKind("DEMO_TW")).toBe("TW");
    expect(marketKind("US")).toBe("US");
  });
});

describe("storage", () => {
  it("沒有 window 時不丟例外", () => {
    expect(safeGet("x")).toBeNull();
    expect(() => safeSet("x", "1")).not.toThrow();
  });
  it("parseFavorites 容錯", () => {
    expect(parseFavorites(null)).toEqual([]);
    expect(parseFavorites("not json")).toEqual([]);
    expect(parseFavorites('{"a":1}')).toEqual([]);
    expect(parseFavorites('["A",1,"B"]')).toEqual(["A", "B"]);
  });
});

describe("搜尋與篩選（真實 factors.json）", () => {
  const factors = read<Factor[]>("factors.json");
  const papers = read<Paper[]>("papers.json");
  const manifest = read<Manifest>("manifest.json");
  const search = createSearcher(buildSearchDocs(factors, papers));
  const availability = {
    DEMO_TW: new Set(read<CompareData>("compare/DEMO_TW.json").factor_ids),
    DEMO_US: new Set(read<CompareData>("compare/DEMO_US.json").factor_ids),
  };
  const run = (patch: Partial<typeof EMPTY_FILTERS>) => filterFactors(factors, { ...EMPTY_FILTERS, ...patch }, search, availability).map((f) => f.id);

  it("無條件回傳全部 36 個", () => {
    expect(run({})).toHaveLength(36);
    expect(factors).toHaveLength(manifest.factor_ids.length);
  });
  it("依英文名／別名搜尋", () => {
    expect(run({ query: "momentum" })).toContain("MOM_12_1");
    expect(run({ query: "UMD" })).toContain("MOM_12_1");
  });
  it("依中文名搜尋", () => {
    expect(run({ query: "動能" })).toContain("MOM_12_1");
  });
  it("依論文作者搜尋", () => {
    expect(run({ query: "Jegadeesh" })).toContain("MOM_12_1");
  });
  it("類別篩選", () => {
    const ids = run({ categories: ["momentum"] });
    expect(ids).toHaveLength(5);
    expect(ids).toContain("MOM_12_1");
  });
  it("市場篩選：營收因子在美股不存在", () => {
    expect(run({ markets: ["DEMO_US"] })).not.toContain("REV_YOY");
    expect(run({ markets: ["DEMO_TW"] })).toContain("REV_YOY");
  });
  it("證據標籤與驗證等級篩選", () => {
    expect(run({ evidence: ["尚未驗證"] }).length).toBeGreaterThan(0);
    expect(run({ levels: ["L1"] })).toHaveLength(0);
    expect(run({ levels: ["L0"] })).toHaveLength(36);
  });
  it("資料需求：價量 vs 財報", () => {
    const price = run({ dataNeeds: ["price"] });
    const fund = run({ dataNeeds: ["fundamental"] });
    expect(price).toContain("MOM_12_1");
    expect(fund).toContain("ROE");
    expect(price.length + fund.length).toBe(36);
    expect(dataNeed({ required_fields: ["close_adj", "volume"] })).toBe("price");
  });
  it("toggle / parseIds", () => {
    expect(toggle(["a"], "b")).toEqual(["a", "b"]);
    expect(toggle(["a", "b"], "a")).toEqual(["b"]);
    expect(parseIds("A,B,A, C,,")).toEqual(["A", "B", "C"]);
    expect(parseIds("A,B,C,D,E,F", undefined, 5)).toHaveLength(5);
    expect(parseIds("A,X", new Set(["A"]))).toEqual(["A"]);
    expect(parseIds(null)).toEqual([]);
  });
});

describe("highlight / csv", () => {
  it("跳脫 HTML 並上色", () => {
    const h = highlightPython('def f(x):\n    return x < 1  # <b>');
    expect(h).toContain('<span class="tok-kw">def</span>');
    expect(h).toContain('<span class="tok-fn">f</span>');
    expect(h).toContain("&lt;");
    expect(h).not.toContain("<b>");
  });
  it("toCsv 處理 null 與逗號", () => {
    expect(toCsv([{ name: "a", values: ["x,y", "z"] }, { name: "b", values: [1, null] }])).toBe('a,b\n"x,y",1\nz,');
  });
});

describe("合約型別對真實 JSON 的抽樣檢查", () => {
  const manifest = read<Manifest>("manifest.json");

  it("manifest", () => {
    expect(manifest.is_demo).toBe(true);
    expect(manifest.markets.map((m) => m.id)).toEqual(["DEMO_TW", "DEMO_US"]);
    expect(manifest.factor_ids).toHaveLength(36);
    for (const m of manifest.markets) {
      expect(typeof m.cost_model.sell_tax).toBe("number");
      expect(m.is_demo).toBe(true);
    }
  });

  it("factors：關鍵欄位且 validation_level 皆為 L0", () => {
    const factors = read<Factor[]>("factors.json");
    for (const f of factors) {
      expect(typeof f.id).toBe("string");
      expect(typeof f.name_zh).toBe("string");
      expect(typeof f.formula_latex).toBe("string");
      expect(Array.isArray(f.variables)).toBe(true);
      expect(Array.isArray(f.pit_rules)).toBe(true);
      expect([1, -1]).toContain(f.direction);
      expect(f.validation_level.TW).toBe("L0");
      expect(f.validation_level.US).toBe("L0");
      expect(["文獻實證", "尚未驗證"]).toContain(f.evidence_status);
    }
  });

  it("papers / repos", () => {
    const papers = read<Paper[]>("papers.json");
    const repos = read<Repo[]>("repos.json");
    expect(papers.length).toBeGreaterThan(0);
    expect(typeof papers[0].fulltext_checked).toBe("boolean");
    expect(Array.isArray(papers[0].factor_ids)).toBe(true);
    expect(["ok", "copyleft", "none", "restricted"]).toContain(repos[0].license_risk);
    for (const r of repos) expect(typeof r.queried_on).toBe("string");
  });

  it("stats：示範資料標籤、mdd 為正、欄式序列等長", () => {
    for (const mk of ["DEMO_TW", "DEMO_US"] as const) {
      const s = read<FactorStats>(`stats/${mk}/MOM_12_1.json`);
      expect(s.is_demo).toBe(true);
      expect(s.evidence_label).toBe("示範資料");
      expect(s.evidence_label).not.toBe("文獻實證");
      expect(s.evidence_label).not.toBe("自行回測");
      expect(s.provenance.n_trials).toBeGreaterThanOrEqual(1);
      expect(s.summary.ls_mdd_net ?? 0).toBeGreaterThanOrEqual(0);
      const n = s.ic_series.dates.length;
      expect(s.ic_series.rank_ic).toHaveLength(n);
      expect(s.ic_series.rank_ic_roll12).toHaveLength(n);
      for (const k of ["Q1", "Q5", "LS", "TOP_EXCESS"]) expect(s.quantiles.cum[k]).toHaveLength(s.quantiles.dates.length);
      expect(s.decay.horizons).toHaveLength(s.decay.rank_ic.length);
      expect(s.bias_checks.length).toBeGreaterThan(0);
    }
  });

  it("每個市場的 stats 檔數與 compare.factor_ids 一致，缺的因子沒有檔案", () => {
    for (const mk of ["DEMO_TW", "DEMO_US"]) {
      const c = read<CompareData>(`compare/${mk}.json`);
      const files = fs.readdirSync(path.join(DATA, "stats", mk)).map((f) => f.replace(".json", ""));
      expect(new Set(files)).toEqual(new Set(c.factor_ids));
      expect(c.factor_corr).toHaveLength(c.factor_ids.length);
      expect(c.ls_return_corr).toHaveLength(c.factor_ids.length);
    }
    expect(read<CompareData>("compare/DEMO_US.json").factor_ids).not.toContain("REV_YOY");
  });

  it("backtest：drawdown ≤ 0、mdd 為正、日頻序列等長", () => {
    const idx = read<{ presets: { id: string; market: string }[] }>("backtests/index.json");
    expect(idx.presets.length).toBeGreaterThan(0);
    const p = idx.presets[0];
    const b = read<BacktestResult>(`backtests/${p.market}/${p.id}.json`);
    expect(b.is_demo).toBe(true);
    expect(b.nav).toHaveLength(b.dates.length);
    expect(b.bench_nav).toHaveLength(b.dates.length);
    expect(Math.max(...b.drawdown.filter(isNum))).toBeLessThanOrEqual(0);
    expect(b.metrics.mdd ?? 0).toBeGreaterThanOrEqual(0);
    expect(b.monthly[0]).toHaveProperty("month");
  });

  it("dashboard", () => {
    const d = read<Dashboard>("dashboard.json");
    expect(d.is_demo).toBe(true);
    expect(d.counts.factors).toBe(36);
    expect(d.top_rank_ic.every((x) => x.is_demo)).toBe(true);
    expect(Object.keys(d.counts.by_level.TW)).toEqual(["L0", "L1", "L2", "L3", "L4"]);
  });

  it("所有 JSON 檔可解析且不含 NaN 字面值（NaN 字面值會使 JSON.parse 失敗）", () => {
    const walk = (dir: string): string[] =>
      fs.readdirSync(dir, { withFileTypes: true }).flatMap((e) => (e.isDirectory() ? walk(path.join(dir, e.name)) : [path.join(dir, e.name)]));
    const files = walk(DATA).filter((f) => f.endsWith(".json"));
    expect(files.length).toBeGreaterThanOrEqual(90);
    for (const f of files) {
      const txt = fs.readFileSync(f, "utf-8");
      expect(() => JSON.parse(txt)).not.toThrow();
    }
  });
});
