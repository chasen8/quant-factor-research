import Fuse from "fuse.js";
import type { Factor, LevelId, MarketId, Paper } from "./types";

export const CATEGORY_LABEL: Record<string, string> = {
  momentum: "動能 Momentum",
  reversal: "反轉 Reversal",
  value: "價值 Value",
  quality: "品質 Quality",
  risk: "風險 Risk",
  liquidity: "流動性 Liquidity",
  composite_ml: "複合／ML Composite",
};

export function categoryLabel(c: string): string {
  return CATEGORY_LABEL[c] ?? c;
}

/** 純價量欄位；其餘（財報、月營收等）視為需財報。 */
export const PRICE_FIELDS = new Set([
  "close_adj", "close_raw", "open", "high", "low", "volume", "vwap", "turnover_value", "market_cap", "shares_outstanding",
]);

export type DataNeed = "price" | "fundamental";

export function dataNeed(f: Pick<Factor, "required_fields">): DataNeed {
  return f.required_fields.every((x) => PRICE_FIELDS.has(x)) ? "price" : "fundamental";
}

export interface Filters {
  query: string;
  categories: string[];
  /** 該因子在所選市場「有分析結果」才通過；空陣列 = 不限 */
  markets: MarketId[];
  evidence: string[];
  levels: LevelId[];
  dataNeeds: DataNeed[];
  frequencies: string[];
}

export const EMPTY_FILTERS: Filters = {
  query: "",
  categories: [],
  markets: [],
  evidence: [],
  levels: [],
  dataNeeds: [],
  frequencies: [],
};

interface SearchDoc {
  id: string;
  name_zh: string;
  name_en: string;
  aliases: string[];
  authors: string[];
  papers: string[];
}

export function buildSearchDocs(factors: Factor[], papers: Paper[]): SearchDoc[] {
  const byId = new Map(papers.map((p) => [p.id, p]));
  return factors.map((f) => {
    const ps = f.paper_ids.map((id) => byId.get(id)).filter((p): p is Paper => !!p);
    return {
      id: f.id,
      name_zh: f.name_zh,
      name_en: f.name_en,
      aliases: f.aliases,
      authors: ps.flatMap((p) => p.authors),
      papers: ps.map((p) => p.title),
    };
  });
}

export function createSearcher(docs: SearchDoc[]): (query: string) => Set<string> | null {
  const fuse = new Fuse(docs, {
    keys: [
      { name: "id", weight: 2 },
      { name: "name_zh", weight: 2 },
      { name: "name_en", weight: 2 },
      { name: "aliases", weight: 1.5 },
      { name: "authors", weight: 1 },
      { name: "papers", weight: 1 },
    ],
    threshold: 0.3,
    ignoreLocation: true,
    minMatchCharLength: 2,
  });
  return (query: string) => {
    const q = query.trim();
    if (!q) return null;
    return new Set(fuse.search(q).map((r) => r.item.id));
  };
}

export type Availability = Partial<Record<MarketId, Set<string>>>;

export function filterFactors(
  factors: Factor[],
  filters: Filters,
  search: (q: string) => Set<string> | null,
  availability: Availability,
): Factor[] {
  const hit = search(filters.query);
  return factors.filter((f) => {
    if (hit && !hit.has(f.id)) return false;
    if (filters.categories.length && !filters.categories.includes(f.category)) return false;
    if (filters.evidence.length && !filters.evidence.includes(f.evidence_status)) return false;
    if (filters.markets.length && !filters.markets.some((m) => availability[m]?.has(f.id))) return false;
    if (filters.levels.length) {
      const lv = [f.validation_level.TW, f.validation_level.US];
      if (!filters.levels.some((l) => lv.includes(l))) return false;
    }
    if (filters.dataNeeds.length && !filters.dataNeeds.includes(dataNeed(f))) return false;
    if (filters.frequencies.length && !filters.frequencies.includes(f.frequency)) return false;
    return true;
  });
}

export function toggle<T>(arr: T[], v: T): T[] {
  return arr.includes(v) ? arr.filter((x) => x !== v) : [...arr, v];
}

export function parseIds(raw: string | null | undefined, valid?: Set<string>, max = 5): string[] {
  if (!raw) return [];
  const out: string[] = [];
  for (const s of raw.split(",")) {
    const id = s.trim();
    if (!id || out.includes(id)) continue;
    if (valid && !valid.has(id)) continue;
    out.push(id);
    if (out.length >= max) break;
  }
  return out;
}
