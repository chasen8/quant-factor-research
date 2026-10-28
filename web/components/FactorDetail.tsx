"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useJson } from "@/lib/hooks";
import { paths } from "@/lib/data";
import { highlightPython } from "@/lib/highlight";
import { categoryLabel } from "@/lib/filter";
import type { Factor, Paper, Repo } from "@/lib/types";
import { Btn, Card, ErrorBox, EvidenceTag, LevelBadge, LicenseBadge, Loading, Pill, Tabs } from "./ui";
import { Tex } from "./Katex";
import { FactorAnalysis } from "./FactorAnalysis";
import { PaperCard, RepoCard, guessRisk } from "./SourceCards";

type TabId = "concept" | "formula" | "code" | "sources" | "analysis" | "limits";
const TABS: { id: TabId; label: string }[] = [
  { id: "concept", label: "概念" },
  { id: "formula", label: "公式" },
  { id: "code", label: "程式碼" },
  { id: "sources", label: "來源" },
  { id: "analysis", label: "分析" },
  { id: "limits", label: "限制" },
];

function Field({ k, children }: { k: string; children: React.ReactNode }) {
  return (
    <div className="grid gap-0.5 py-2 sm:grid-cols-[9rem_1fr] sm:gap-3">
      <dt className="text-xs font-medium text-muted">{k}</dt>
      <dd className="min-w-0 break-words text-sm">{children}</dd>
    </div>
  );
}

export function FactorDetail({ id }: { id: string }) {
  const { data: factors, error } = useJson<Factor[]>(paths.factors);
  const { data: papers } = useJson<Paper[]>(paths.papers);
  const { data: repos } = useJson<Repo[]>(paths.repos);
  const [tab, setTabState] = useState<TabId>("concept");
  useEffect(() => {
    const h = window.location.hash.slice(1);
    if (TABS.some((t) => t.id === h)) setTabState(h as TabId);
  }, []);
  const setTab = (t: TabId) => {
    setTabState(t);
    try {
      window.history.replaceState(null, "", `#${t}`);
    } catch {
      /* ignore */
    }
  };

  const factor = factors?.find((f) => f.id === id);
  if (error) return <ErrorBox error={error} />;
  if (!factors) return <Loading what="因子" />;
  if (!factor) return <ErrorBox error={`找不到因子 ${id}`} />;

  return (
    <div>
      <div className="mb-1 text-xs text-muted">
        <Link href="/factors/" className="text-accent hover:underline">
          ← 因子資料庫
        </Link>
      </div>
      <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <h1 className="text-2xl font-bold tracking-tight">{factor.name_zh}</h1>
          <p className="text-sm text-muted">
            {factor.name_en}　·　<span className="font-mono">{factor.id}</span>
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Pill tone="accent">{categoryLabel(factor.category)}</Pill>
          <EvidenceTag label={factor.evidence_status} />
          <span className="text-xs text-muted">台股</span>
          <LevelBadge level={factor.validation_level.TW} />
          <span className="text-xs text-muted">美股</span>
          <LevelBadge level={factor.validation_level.US} />
          <Link href={`/compare/?ids=${factor.id}`} className="rounded-lg border border-line bg-surface px-3 py-1 text-sm hover:bg-surface2">
            加入比較
          </Link>
        </div>
      </div>

      <Tabs tabs={TABS} value={tab} onChange={setTab} />
      <div className="mt-4">
        {tab === "concept" ? <Concept f={factor} /> : null}
        {tab === "formula" ? <Formula f={factor} /> : null}
        {tab === "code" ? <Code f={factor} repos={repos} /> : null}
        {tab === "sources" ? <Sources f={factor} papers={papers} repos={repos} /> : null}
        {tab === "analysis" ? <FactorAnalysis factor={factor} /> : null}
        {tab === "limits" ? <Limits f={factor} /> : null}
      </div>
    </div>
  );
}

function Concept({ f }: { f: Factor }) {
  return (
    <Card>
      {f.same_name_different_formula ? (
        <div className="mb-3 rounded-lg bg-warnbg px-3 py-2 text-sm text-warn">
          <strong>⚠ 相同名稱、不同公式：</strong>
          {f.same_name_different_formula}
        </div>
      ) : null}
      <dl className="divide-y divide-line">
        <Field k="類別">{categoryLabel(f.category)}　／　{f.subcategory}</Field>
        <Field k="方向">
          {f.direction === 1 ? "因子值越大，預期報酬越高（做多高分組）" : "因子值越小，預期報酬越高（做多低分組）"}
        </Field>
        <Field k="單位">{f.unit}</Field>
        <Field k="更新頻率">{f.frequency === "daily" ? "日頻" : f.frequency === "monthly" ? "月頻" : f.frequency === "quarterly" ? "季頻（財報）" : f.frequency}</Field>
        <Field k="所需資料欄位">
          <span className="flex flex-wrap gap-1">
            {f.required_fields.map((x) => (
              <code key={x} className="rounded bg-surface2 px-1.5 py-0.5 text-xs">
                {x}
              </code>
            ))}
          </span>
        </Field>
        <Field k="別名">{f.aliases.length ? f.aliases.join("、") : "—"}</Field>
        <Field k="市場適用性（台股）">{f.suggested_markets.TW ?? "—"}</Field>
        <Field k="市場適用性（美股）">{f.suggested_markets.US ?? "—"}</Field>
        <Field k="證據狀態">
          <EvidenceTag label={f.evidence_status} />
          <span className="ml-2 text-xs text-muted">
            {f.evidence_status === "文獻實證" ? "有論文報告，但尚未經本平台以真實資料重算；驗證等級仍為 L0。" : "公式已收錄，尚未重算。"}
          </span>
        </Field>
      </dl>
    </Card>
  );
}

function Formula({ f }: { f: Factor }) {
  return (
    <div className="space-y-4">
      <Card>
        <div className="mb-1 flex items-center justify-between gap-2">
          <h3 className="text-sm font-semibold">公式</h3>
          <Pill tone={f.formula_source_type === "原文公式" ? "ok" : "neutral"} title="原文公式＝取自論文原文；標準化定義＝由領域常見定義整理，非原文">
            {f.formula_source_type}
          </Pill>
        </div>
        <Tex latex={f.formula_latex} />
        {f.formula_original ? (
          <div className="mt-2 text-xs">
            <span className="text-muted">原文表達式：</span>
            <code className="break-all">{f.formula_original}</code>
            {f.location_in_source ? <span className="text-muted">（{f.location_in_source}）</span> : null}
          </div>
        ) : null}
      </Card>
      <Card>
        <h3 className="mb-2 text-sm font-semibold">變數定義</h3>
        <div className="scroll-x">
          <table className="w-full text-left text-sm">
            <thead className="text-xs text-muted">
              <tr>
                <th className="py-1 pr-3 font-medium">符號</th>
                <th className="py-1 pr-3 font-medium">意義</th>
                <th className="py-1 font-medium">單位</th>
              </tr>
            </thead>
            <tbody>
              {f.variables.map((v) => (
                <tr key={v.symbol} className="border-t border-line align-top">
                  <td className="py-1.5 pr-3">
                    <Tex latex={v.symbol} display={false} />
                  </td>
                  <td className="py-1.5 pr-3">{v.meaning}</td>
                  <td className="py-1.5 text-muted">{v.unit}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
      <Card>
        <h3 className="mb-2 text-sm font-semibold">PIT（Point-in-Time）規則</h3>
        <ul className="list-disc space-y-1 pl-5 text-sm">
          {f.pit_rules.map((r, i) => (
            <li key={i}>{r}</li>
          ))}
        </ul>
        <h4 className="mb-1 mt-3 text-sm font-semibold">公司行動處理</h4>
        <p className="text-sm">{f.corporate_action_notes}</p>
      </Card>
    </div>
  );
}

function Code({ f, repos }: { f: Factor; repos: Repo[] | undefined }) {
  const [copied, setCopied] = useState(false);
  const html = useMemo(() => highlightPython(f.python), [f.python]);
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(f.python);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      setCopied(false);
    }
  };
  return (
    <div className="space-y-4">
      <Card>
        <div className="mb-2 flex items-center justify-between">
          <h3 className="text-sm font-semibold">Python 實作（pandas）</h3>
          <Btn onClick={copy}>{copied ? "已複製" : "複製"}</Btn>
        </div>
        <pre className="scroll-x rounded-lg bg-surface2 p-3 text-xs leading-relaxed">
          <code dangerouslySetInnerHTML={{ __html: html }} />
        </pre>
      </Card>
      <Card>
        <h3 className="mb-2 text-sm font-semibold">授權說明</h3>
        <p className="text-sm">
          上方程式碼為本平台依公式自行撰寫，未複製下列任何第三方專案的程式碼。參考專案的授權如下；標示警示的專案（Copyleft、無授權、附帶限制）只能做概念參考，不得複製其程式碼。
        </p>
        <ul className="mt-2 space-y-2">
          {f.repo_refs.length === 0 ? <li className="text-sm text-muted">沒有對應的參考專案。</li> : null}
          {f.repo_refs.map((r) => {
            const known = repos?.find((x) => x.id === r.repo);
            return (
              <li key={r.repo} className="flex flex-wrap items-center gap-2 text-sm">
                <LicenseBadge license={r.license} risk={known?.license_risk ?? guessRisk(r.license)} />
                <span className="font-mono text-xs">{r.repo}</span>
                <span className="text-xs text-muted">{r.usage}</span>
              </li>
            );
          })}
        </ul>
      </Card>
    </div>
  );
}

function Sources({ f, papers, repos }: { f: Factor; papers: Paper[] | undefined; repos: Repo[] | undefined }) {
  const myPapers = f.paper_ids.map((id) => papers?.find((p) => p.id === id)).filter((p): p is Paper => !!p);
  return (
    <div className="space-y-6">
      <section>
        <h3 className="mb-2 text-sm font-semibold">原始論文與文獻實證數據</h3>
        {f.paper_ids_note ? <p className="mb-2 text-xs text-muted">{f.paper_ids_note}</p> : null}
        {!papers ? <Loading what="論文" /> : null}
        <div className="grid gap-3 lg:grid-cols-2">
          {myPapers.map((p) => {
            const kr = f.known_results.filter((k) => k.source === p.id);
            return (
              <div key={p.id} className="space-y-2">
                <PaperCard paper={p} />
                {kr.map((k, i) => (
                  <div key={i} className="rounded-lg border border-line bg-surface2 p-3 text-xs">
                    <div className="mb-1 flex flex-wrap items-center gap-2">
                      <EvidenceTag label={k.evidence} />
                      <span className="text-muted">
                        {k.market}｜{k.period}｜位置：{k.location}
                      </span>
                    </div>
                    <div>{k.result}</div>
                  </div>
                ))}
              </div>
            );
          })}
        </div>
        {papers && myPapers.length === 0 ? <p className="text-sm text-muted">沒有對應論文。</p> : null}
      </section>
      <section>
        <h3 className="mb-2 text-sm font-semibold">GitHub 參考專案</h3>
        {!repos ? <Loading what="專案" /> : null}
        <div className="grid gap-3 lg:grid-cols-2">
          {f.repo_refs.map((r) => {
            const full = repos?.find((x) => x.id === r.repo);
            return full ? (
              <div key={r.repo} className="space-y-1">
                <RepoCard repo={full} />
                <p className="px-1 text-xs text-muted">於本因子的用途：{r.usage}</p>
              </div>
            ) : (
              <Card key={r.repo}>
                <div className="flex flex-wrap items-center gap-2">
                  <LicenseBadge license={r.license} risk={guessRisk(r.license)} />
                  <span className="font-mono text-sm">{r.repo}</span>
                </div>
                <p className="mt-1 text-xs text-muted">{r.usage}</p>
              </Card>
            );
          })}
        </div>
        {f.repo_refs.length === 0 ? <p className="text-sm text-muted">沒有對應專案。</p> : null}
      </section>
    </div>
  );
}

function Limits({ f }: { f: Factor }) {
  return (
    <Card>
      <dl className="divide-y divide-line">
        <Field k="已知研究限制">{f.limitations}</Field>
        <Field k="交易成本備註">{f.transaction_cost_note}</Field>
        <Field k="台股差異提醒">{f.suggested_markets.TW ?? "—"}</Field>
        <Field k="美股差異提醒">{f.suggested_markets.US ?? "—"}</Field>
        <Field k="同名不同公式">{f.same_name_different_formula || "—"}</Field>
      </dl>
    </Card>
  );
}
