"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import {
  createColumnHelper, createSortedRowModel, rowSortingFeature, sortFn_alphanumeric, sortFn_basic, tableFeatures, useTable,
  type SortingState,
} from "@tanstack/react-table";
import { useSettings } from "./Providers";
import { Btn, Card, DemoNote, ErrorBox, EvidenceTag, LevelBadge, Loading, PageTitle, Pill, cx } from "./ui";
import { useJson, useJsonMap } from "@/lib/hooks";
import { paths } from "@/lib/data";
import { fmtNum } from "@/lib/format";
import {
  CATEGORY_LABEL, EMPTY_FILTERS, buildSearchDocs, categoryLabel, createSearcher, dataNeed, filterFactors, toggle,
  type Availability, type DataNeed, type Filters,
} from "@/lib/filter";
import { loadFavorites, saveFavorites } from "@/lib/storage";
import type { CompareData, Factor, FactorStats, LevelId, MarketId, Paper } from "@/lib/types";

interface Row {
  f: Factor;
  rankIc: number | undefined;
  icir: number | undefined;
  turnover: number | undefined;
  avail: { TW: boolean; US: boolean };
  need: DataNeed;
}

const features = tableFeatures({
  rowSortingFeature,
  sortedRowModel: createSortedRowModel(),
  sortFns: { alphanumeric: sortFn_alphanumeric, basic: sortFn_basic },
});
const helper = createColumnHelper<typeof features, Row>();

const LEVELS: LevelId[] = ["L0", "L1", "L2", "L3", "L4"];
const EVIDENCE = ["文獻實證", "自行回測", "尚未驗證"];
const FREQ: Record<string, string> = { daily: "日頻", monthly: "月頻", quarterly: "季頻" };
const MAX_COMPARE = 5;

function Group({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <fieldset className="mb-4">
      <legend className="mb-1 text-xs font-semibold text-muted">{title}</legend>
      <div className="space-y-1">{children}</div>
    </fieldset>
  );
}

function Check({ checked, onChange, children }: { checked: boolean; onChange: () => void; children: React.ReactNode }) {
  return (
    <label className="flex cursor-pointer items-center gap-2 text-sm">
      <input type="checkbox" checked={checked} onChange={onChange} className="h-4 w-4 accent-[var(--accent)]" />
      <span>{children}</span>
    </label>
  );
}

export function FactorsExplorer() {
  const { market, manifest } = useSettings();
  const { data: factors, error } = useJson<Factor[]>(paths.factors);
  const { data: papers } = useJson<Paper[]>(paths.papers);
  const marketIds = (manifest?.markets ?? []).map((m) => m.id);
  const { data: cmps } = useJsonMap<CompareData>(marketIds.map((m) => paths.compare(m)));
  const ids = manifest?.factor_ids ?? [];
  const { data: stats } = useJsonMap<FactorStats>(manifest ? ids.map((id) => paths.stats(market, id)) : []);

  const [filters, setFilters] = useState<Filters>(EMPTY_FILTERS);
  const [favs, setFavs] = useState<string[]>([]);
  const [onlyFav, setOnlyFav] = useState(false);
  const [selected, setSelected] = useState<string[]>([]);
  const [sorting, setSorting] = useState<SortingState>([]);
  const [showAll, setShowAll] = useState(false);

  useEffect(() => setFavs(loadFavorites()), []);
  const toggleFav = (id: string) =>
    setFavs((cur) => {
      const next = toggle(cur, id);
      saveFavorites(next);
      return next;
    });
  const toggleSel = (id: string) =>
    setSelected((cur) => (cur.includes(id) ? cur.filter((x) => x !== id) : cur.length >= MAX_COMPARE ? cur : [...cur, id]));

  const availability: Availability = useMemo(() => {
    const a: Availability = {};
    for (const m of marketIds) {
      const c = cmps[paths.compare(m)];
      if (c) a[m] = new Set(c.factor_ids);
    }
    return a;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cmps, marketIds.join("|")]);

  const search = useMemo(() => createSearcher(buildSearchDocs(factors ?? [], papers ?? [])), [factors, papers]);

  const rows: Row[] = useMemo(() => {
    const list = filterFactors(factors ?? [], filters, search, availability).filter((f) => !onlyFav || favs.includes(f.id));
    const twId = marketIds.find((m) => m.endsWith("TW"));
    const usId = marketIds.find((m) => m.endsWith("US"));
    return list.map((f) => {
      const st = stats[paths.stats(market, f.id)];
      return {
        f,
        rankIc: st?.summary.rank_ic_mean ?? undefined,
        icir: st?.summary.rank_icir_ann ?? undefined,
        turnover: st?.summary.turnover_ann ?? undefined,
        avail: { TW: !!(twId && availability[twId]?.has(f.id)), US: !!(usId && availability[usId]?.has(f.id)) },
        need: dataNeed(f),
      };
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [factors, filters, search, availability, onlyFav, favs, stats, market]);

  const columns = useMemo(
    () =>
      helper.columns([
        helper.display({
          id: "sel",
          header: "比較",
          cell: ({ row }) => (
            <input
              type="checkbox"
              aria-label={`選取 ${row.original.f.id} 比較`}
              checked={selected.includes(row.original.f.id)}
              disabled={!selected.includes(row.original.f.id) && selected.length >= MAX_COMPARE}
              onChange={() => toggleSel(row.original.f.id)}
              className="h-4 w-4 accent-[var(--accent)]"
            />
          ),
        }),
        helper.display({
          id: "fav",
          header: "★",
          cell: ({ row }) => {
            const on = favs.includes(row.original.f.id);
            return (
              <button
                aria-label={on ? "取消收藏" : "收藏"}
                aria-pressed={on}
                onClick={() => toggleFav(row.original.f.id)}
                className={cx("text-lg leading-none", on ? "text-amber-500" : "text-muted hover:text-amber-500")}
              >
                {on ? "★" : "☆"}
              </button>
            );
          },
        }),
        helper.accessor((r) => r.f.id, {
          id: "id",
          header: "ID",
          sortFn: "alphanumeric",
          cell: ({ row }) => (
            <Link href={`/factors/${row.original.f.id}/`} className="font-mono text-xs text-accent hover:underline">
              {row.original.f.id}
            </Link>
          ),
        }),
        helper.accessor((r) => r.f.name_zh, {
          id: "name",
          header: "名稱",
          sortFn: "alphanumeric",
          cell: ({ row }) => (
            <Link href={`/factors/${row.original.f.id}/`} className="hover:underline">
              <div className="font-medium">{row.original.f.name_zh}</div>
              <div className="text-xs text-muted">{row.original.f.name_en}</div>
            </Link>
          ),
        }),
        helper.accessor((r) => categoryLabel(r.f.category), { id: "category", header: "類別", sortFn: "alphanumeric", cell: (c) => c.getValue() }),
        helper.display({
          id: "markets",
          header: "市場",
          cell: ({ row }) => (
            <span className="flex gap-1">
              <Pill tone={row.original.avail.TW ? "accent" : "neutral"} title={row.original.avail.TW ? "台股有分析結果（示範資料）" : "台股不適用"}>台</Pill>
              <Pill tone={row.original.avail.US ? "accent" : "neutral"} title={row.original.avail.US ? "美股有分析結果（示範資料）" : "美股不適用"}>美</Pill>
            </span>
          ),
        }),
        helper.accessor((r) => r.f.evidence_status, {
          id: "evidence",
          header: "證據標籤",
          sortFn: "alphanumeric",
          cell: ({ row }) => <EvidenceTag label={row.original.f.evidence_status} />,
        }),
        helper.accessor((r) => `${r.f.validation_level.TW}${r.f.validation_level.US}`, {
          id: "level",
          header: "驗證等級（台/美）",
          sortFn: "alphanumeric",
          cell: ({ row }) => (
            <span className="flex gap-1">
              <LevelBadge level={row.original.f.validation_level.TW} />
              <LevelBadge level={row.original.f.validation_level.US} />
            </span>
          ),
        }),
        helper.accessor((r) => r.rankIc, {
          id: "rankIc",
          header: "Rank IC（示範）",
          sortFn: "basic",
          sortUndefined: "last",
          cell: (c) => <span className="num">{fmtNum(c.getValue() ?? null, 4)}</span>,
        }),
        helper.accessor((r) => r.icir, {
          id: "icir",
          header: "ICIR 年化（示範）",
          sortFn: "basic",
          sortUndefined: "last",
          cell: (c) => <span className="num">{fmtNum(c.getValue() ?? null, 2)}</span>,
        }),
        helper.accessor((r) => r.turnover, {
          id: "turnover",
          header: "換手（示範）",
          sortFn: "basic",
          sortUndefined: "last",
          cell: (c) => <span className="num">{fmtNum(c.getValue() ?? null, 2)}</span>,
        }),
        helper.accessor((r) => r.need, {
          id: "need",
          header: "所需資料",
          sortFn: "alphanumeric",
          cell: ({ row }) => (
            <span title={row.original.f.required_fields.join(", ")}>{row.original.need === "price" ? "價量" : "財報／營收"}</span>
          ),
        }),
      ]),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [selected, favs],
  );

  const table = useTable({
    features,
    columns,
    data: rows,
    state: { sorting },
    onSortingChange: setSorting,
  });

  if (error) return <ErrorBox error={error} />;
  if (!factors) return <Loading what="因子資料庫" />;

  const sortedRows = table.getRowModel().rows;
  const shown = showAll ? sortedRows : sortedRows.slice(0, 12);
  const categories = Object.keys(CATEGORY_LABEL);
  const set = (patch: Partial<Filters>) => setFilters((f) => ({ ...f, ...patch }));
  const nFilters =
    filters.categories.length + filters.markets.length + filters.evidence.length + filters.levels.length + filters.dataNeeds.length + filters.frequencies.length;

  const filterPanel = (
    <div>
      <Group title="類別">
        {categories.map((c) => (
          <Check key={c} checked={filters.categories.includes(c)} onChange={() => set({ categories: toggle(filters.categories, c) })}>
            {CATEGORY_LABEL[c]}
          </Check>
        ))}
      </Group>
      <Group title="市場（有分析結果）">
        {(manifest?.markets ?? []).map((m) => (
          <Check key={m.id} checked={filters.markets.includes(m.id)} onChange={() => set({ markets: toggle<MarketId>(filters.markets, m.id) })}>
            {m.id.endsWith("TW") ? "台股" : "美股"}（示範）
          </Check>
        ))}
      </Group>
      <Group title="證據標籤">
        {EVIDENCE.map((e) => (
          <Check key={e} checked={filters.evidence.includes(e)} onChange={() => set({ evidence: toggle(filters.evidence, e) })}>
            {e}
          </Check>
        ))}
      </Group>
      <Group title="驗證等級（任一市場）">
        {LEVELS.map((l) => (
          <Check key={l} checked={filters.levels.includes(l)} onChange={() => set({ levels: toggle(filters.levels, l) })}>
            {l}
          </Check>
        ))}
      </Group>
      <Group title="資料需求">
        <Check checked={filters.dataNeeds.includes("price")} onChange={() => set({ dataNeeds: toggle<DataNeed>(filters.dataNeeds, "price") })}>
          只要價量
        </Check>
        <Check checked={filters.dataNeeds.includes("fundamental")} onChange={() => set({ dataNeeds: toggle<DataNeed>(filters.dataNeeds, "fundamental") })}>
          需財報／營收
        </Check>
      </Group>
      <Group title="計算週期">
        {Object.keys(FREQ).map((k) => (
          <Check key={k} checked={filters.frequencies.includes(k)} onChange={() => set({ frequencies: toggle(filters.frequencies, k) })}>
            {FREQ[k]}
          </Check>
        ))}
      </Group>
      <Btn onClick={() => setFilters({ ...EMPTY_FILTERS, query: filters.query })} className="w-full">
        清除篩選
      </Btn>
    </div>
  );

  return (
    <div>
      <PageTitle title="Alpha 因子資料庫" sub={`共收錄 ${factors.length} 個因子；Rank IC、ICIR、換手欄位皆來自合成示範資料（${market.endsWith("TW") ? "示範台股" : "示範美股"}）。`} />
      <div className="mb-4">
        <DemoNote>Rank IC／ICIR／換手為示範資料計算結果，不代表真實因子表現；驗證等級全部維持 L0。</DemoNote>
      </div>
      <div className="grid gap-4 lg:grid-cols-[15rem_minmax(0,1fr)]">
        <aside>
          <details className="rounded-xl border border-line bg-surface p-3 lg:hidden">
            <summary className="cursor-pointer text-sm font-medium">篩選{nFilters ? `（${nFilters}）` : ""}</summary>
            <div className="mt-3">{filterPanel}</div>
          </details>
          <div className="hidden rounded-xl border border-line bg-surface p-3 lg:block">{filterPanel}</div>
        </aside>

        <div className="min-w-0 space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <input
              type="search"
              value={filters.query}
              onChange={(e) => set({ query: e.target.value })}
              placeholder="搜尋名稱、別名、作者、論文標題…"
              aria-label="搜尋因子"
              className="min-w-0 flex-1 rounded-lg border border-line bg-surface px-3 py-1.5 text-sm"
            />
            <Btn active={onlyFav} onClick={() => setOnlyFav((v) => !v)}>
              ★ 只看收藏（{favs.length}）
            </Btn>
            {selected.length >= 2 ? (
              <Link href={`/compare/?ids=${selected.join(",")}`} className="inline-flex items-center rounded-lg bg-accent px-3 py-1.5 text-sm font-medium text-accentfg">
                比較 {selected.length} 個因子
              </Link>
            ) : (
              <Btn disabled title="勾選 2–5 個因子後可比較">
                比較（已選 {selected.length}）
              </Btn>
            )}
            <label className="flex items-center gap-1 text-sm md:hidden">
              <span className="text-muted">排序</span>
              <select
                className="rounded-lg border border-line bg-surface px-2 py-1.5"
                value={sorting[0] ? `${sorting[0].id}:${sorting[0].desc ? "desc" : "asc"}` : ""}
                onChange={(e) => {
                  const [id, dir] = e.target.value.split(":");
                  setSorting(id ? [{ id, desc: dir === "desc" }] : []);
                }}
              >
                <option value="">預設</option>
                <option value="rankIc:desc">Rank IC 高→低</option>
                <option value="icir:desc">ICIR 高→低</option>
                <option value="turnover:asc">換手 低→高</option>
                <option value="name:asc">名稱</option>
              </select>
            </label>
          </div>
          <div className="text-xs text-muted">
            符合 {sortedRows.length} 個因子{selected.length >= MAX_COMPARE ? "（已達比較上限 5 個）" : ""}
          </div>

          {/* 桌面：表格 */}
          <Card className="hidden p-0 md:block">
            <div className="scroll-x">
              <table className="w-full min-w-[56rem] text-left text-sm">
                <thead className="border-b border-line bg-surface2 text-xs text-muted">
                  {table.getHeaderGroups().map((hg) => (
                    <tr key={hg.id}>
                      {hg.headers.map((h) => {
                        const sortable = h.column.getCanSort();
                        const dir = h.column.getIsSorted();
                        return (
                          <th key={h.id} className="whitespace-nowrap px-2.5 py-2 font-medium" aria-sort={dir === "asc" ? "ascending" : dir === "desc" ? "descending" : "none"}>
                            {sortable ? (
                              <button onClick={h.column.getToggleSortingHandler()} className="inline-flex items-center gap-1 hover:text-fg">
                                <table.FlexRender header={h} />
                                <span aria-hidden>{dir === "asc" ? "▲" : dir === "desc" ? "▼" : "↕"}</span>
                              </button>
                            ) : (
                              <table.FlexRender header={h} />
                            )}
                          </th>
                        );
                      })}
                    </tr>
                  ))}
                </thead>
                <tbody>
                  {shown.map((row) => (
                    <tr key={row.id} className="border-b border-line last:border-0 hover:bg-surface2/60">
                      {row.getAllCells().map((cell) => (
                        <td key={cell.id} className="px-2.5 py-2 align-middle">
                          <table.FlexRender cell={cell} />
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          {/* 手機：卡片 */}
          <div className="space-y-2 md:hidden">
            {shown.map((row) => {
              const r = row.original;
              const on = favs.includes(r.f.id);
              return (
                <Card key={row.id} className="space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <Link href={`/factors/${r.f.id}/`} className="min-w-0">
                      <div className="font-medium">{r.f.name_zh}</div>
                      <div className="font-mono text-xs text-accent">{r.f.id}</div>
                    </Link>
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        aria-label={`選取 ${r.f.id} 比較`}
                        checked={selected.includes(r.f.id)}
                        disabled={!selected.includes(r.f.id) && selected.length >= MAX_COMPARE}
                        onChange={() => toggleSel(r.f.id)}
                        className="h-5 w-5 accent-[var(--accent)]"
                      />
                      <button aria-label={on ? "取消收藏" : "收藏"} aria-pressed={on} onClick={() => toggleFav(r.f.id)} className={cx("text-xl leading-none", on ? "text-amber-500" : "text-muted")}>
                        {on ? "★" : "☆"}
                      </button>
                    </div>
                  </div>
                  <div className="flex flex-wrap items-center gap-1.5">
                    <Pill tone="accent">{categoryLabel(r.f.category)}</Pill>
                    <EvidenceTag label={r.f.evidence_status} />
                    <LevelBadge level={r.f.validation_level.TW} />
                    <LevelBadge level={r.f.validation_level.US} />
                  </div>
                  <div className="num grid grid-cols-3 gap-2 text-xs">
                    <div>
                      <div className="text-muted">Rank IC（示範）</div>
                      {fmtNum(r.rankIc ?? null, 4)}
                    </div>
                    <div>
                      <div className="text-muted">ICIR（示範）</div>
                      {fmtNum(r.icir ?? null, 2)}
                    </div>
                    <div>
                      <div className="text-muted">換手（示範）</div>
                      {fmtNum(r.turnover ?? null, 2)}
                    </div>
                  </div>
                </Card>
              );
            })}
          </div>

          {sortedRows.length === 0 ? <Card className="text-center text-sm text-muted">沒有符合條件的因子。</Card> : null}
          {sortedRows.length > 12 ? (
            <div className="text-center">
              <Btn onClick={() => setShowAll((v) => !v)}>{showAll ? "只顯示前 12 筆" : `顯示全部 ${sortedRows.length} 筆`}</Btn>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
