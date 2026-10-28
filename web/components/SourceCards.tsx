"use client";

import Link from "next/link";
import { useState } from "react";
import { Card, LicenseBadge, Pill, cx } from "./ui";
import { fmtInt } from "@/lib/format";
import type { LicenseRisk, Paper, Repo } from "@/lib/types";

export function FactorLinks({ ids }: { ids: string[] }) {
  if (!ids.length) return <span className="text-xs text-muted">尚無對應因子</span>;
  return (
    <span className="flex flex-wrap gap-1">
      {ids.map((id) => (
        <Link key={id} href={`/factors/${id}/`} className="rounded-md border border-line bg-surface2 px-1.5 py-0.5 font-mono text-[11px] text-accent hover:underline">
          {id}
        </Link>
      ))}
    </span>
  );
}

function More({ rows }: { rows: [string, string][] }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="mt-2">
      <button onClick={() => setOpen((o) => !o)} aria-expanded={open} className="text-xs text-accent hover:underline">
        {open ? "收合細節 ▲" : "展開細節 ▼"}
      </button>
      {open ? (
        <dl className="mt-2 space-y-1.5 text-xs">
          {rows.map(([k, v]) => (
            <div key={k}>
              <dt className="font-medium text-muted">{k}</dt>
              <dd className="whitespace-pre-line break-words">{v}</dd>
            </div>
          ))}
        </dl>
      ) : null}
    </div>
  );
}

export function PaperCard({ paper, highlight }: { paper: Paper; highlight?: boolean }) {
  return (
    <Card className={cx("space-y-2", highlight && "border-accent")}>
      <div className="flex flex-wrap items-center gap-1.5">
        <Pill tone="accent">{paper.category}</Pill>
        {paper.fulltext_checked ? <Pill tone="ok">已核對全文</Pill> : <Pill tone="warn" title="目前僅核對 DOI 與摘要；數字未與全文逐項比對">未核對全文</Pill>}
        <Pill>{paper.verification_status}</Pill>
      </div>
      <h3 className="text-sm font-semibold leading-snug">{paper.title}</h3>
      <div className="text-xs text-muted">
        {paper.authors.join(", ")}　·　{paper.year}　·　{paper.venue}
      </div>
      <div className="flex flex-wrap gap-3 text-xs">
        {paper.doi_url ? (
          <a href={paper.doi_url} target="_blank" rel="noopener noreferrer" className="text-accent hover:underline">
            DOI：{paper.doi}
          </a>
        ) : (
          <span className="text-muted">無 DOI</span>
        )}
        {paper.free_url ? (
          <a href={paper.free_url} target="_blank" rel="noopener noreferrer" className="text-accent hover:underline">
            免費全文
          </a>
        ) : null}
      </div>
      <div className="text-xs">
        <span className="text-muted">市場與期間：</span>
        {paper.market}；{paper.sample_period}
      </div>
      <div className="text-xs">
        <span className="text-muted">文獻報告結果：</span>
        {paper.reported_results}
      </div>
      <div className="flex flex-wrap items-center gap-2 text-xs">
        <span className="text-muted">對應因子：</span>
        <FactorLinks ids={paper.factor_ids} />
      </div>
      <More
        rows={[
          ["方法", paper.method],
          ["程式碼可得性", paper.code_availability],
          ["台股／美股適用性", paper.tw_us_suitability],
          ["限制", paper.limitations],
        ]}
      />
    </Card>
  );
}

const RISK_NOTE: Record<LicenseRisk, string | null> = {
  ok: null,
  copyleft: "Copyleft 授權（GPL/AGPL 類）：只能做概念參考，不得複製程式碼進本平台。",
  none: "沒有授權條款：預設保留所有權利，不得複製或再散布其程式碼。",
  restricted: "授權附帶使用限制：不得引入，也不得做為以其功能為主體的收費服務之基礎。",
};

export function RepoCard({ repo, highlight }: { repo: Repo; highlight?: boolean }) {
  const note = RISK_NOTE[repo.license_risk];
  return (
    <Card className={cx("space-y-2", highlight && "border-accent")}>
      <div className="flex flex-wrap items-center gap-1.5">
        <LicenseBadge license={repo.license} risk={repo.license_risk} />
        {repo.recommended ? <Pill tone="ok">推薦</Pill> : null}
        <Pill title="與本平台整合難易度">整合 {repo.integration}</Pill>
        <Pill>{repo.language}</Pill>
      </div>
      <h3 className="text-sm font-semibold">
        <a href={repo.url} target="_blank" rel="noopener noreferrer" className="break-all text-accent hover:underline">
          {repo.id}
        </a>
      </h3>
      <p className="text-xs">{repo.purpose}</p>
      <div className="num flex flex-wrap gap-x-4 gap-y-0.5 text-xs text-muted">
        <span>
          ★ {fmtInt(repo.stars)}（查詢日 {repo.queried_on}）
        </span>
        <span>最後 push：{repo.pushed_at}</span>
      </div>
      {note ? <div className="rounded-lg bg-warnbg px-2 py-1.5 text-xs text-warn">⚠ {note}</div> : null}
      <div className="flex flex-wrap items-center gap-2 text-xs">
        <span className="text-muted">對應因子：</span>
        <FactorLinks ids={repo.factor_ids} />
      </div>
      <More
        rows={[
          ["因子數量", repo.factor_count],
          ["公式是否明確", repo.formula_explicit],
          ["回測功能", repo.backtest],
          ["學術依據", repo.academic_basis ?? "—"],
          ["限制", repo.limitations],
        ]}
      />
    </Card>
  );
}

/** 由授權字串推估風險（僅在 repos.json 查不到該 repo 時使用）。 */
export function guessRisk(license: string): LicenseRisk {
  if (/AGPL|GPL/i.test(license)) return "copyleft";
  if (/^none|無授權/i.test(license)) return "none";
  if (/Commons Clause/i.test(license)) return "restricted";
  return "ok";
}
