import type { MarketId, MarketKind } from "./types";

/** 部署在 GitHub Pages 子路徑時為 "/quant-factor-research"，本機為 ""。建置時內嵌。 */
export const BASE_PATH: string = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

export function joinBase(base: string, path: string): string {
  const b = base.replace(/\/+$/, "");
  const p = path.replace(/^\/+/, "");
  return `${b}/${p}`;
}

/** 所有 fetch 都必須走這支，否則子路徑部署後會 404。 */
export function dataUrl(path: string, base: string = BASE_PATH): string {
  return joinBase(base, `data/${path.replace(/^\/+/, "")}`);
}

export const paths = {
  manifest: "manifest.json",
  factors: "factors.json",
  papers: "papers.json",
  repos: "repos.json",
  dashboard: "dashboard.json",
  stats: (market: MarketId, id: string) => `stats/${market}/${id}.json`,
  compare: (market: MarketId) => `compare/${market}.json`,
  backtestIndex: "backtests/index.json",
  backtest: (market: MarketId, preset: string) => `backtests/${market}/${preset}.json`,
};

export function marketKind(id: MarketId): MarketKind {
  return id.endsWith("TW") ? "TW" : "US";
}

const cache = new Map<string, Promise<unknown>>();

export function fetchJson<T>(path: string): Promise<T> {
  const url = dataUrl(path);
  let p = cache.get(url) as Promise<T> | undefined;
  if (!p) {
    p = fetch(url).then((r) => {
      if (!r.ok) throw new Error(`${r.status} ${url}`);
      return r.json() as Promise<T>;
    });
    p.catch(() => cache.delete(url));
    cache.set(url, p);
  }
  return p;
}
