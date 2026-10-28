"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { useJson } from "@/lib/hooks";
import { paths } from "@/lib/data";
import type { Factor, LicenseRisk, Paper, Repo } from "@/lib/types";
import { Btn, Card, ErrorBox, Loading, PageTitle, Pill, Tabs } from "./ui";
import { PaperCard, RepoCard } from "./SourceCards";

type TabId = "papers" | "repos" | "map";

export function Sources() {
  const { data: papers, error: e1 } = useJson<Paper[]>(paths.papers);
  const { data: repos, error: e2 } = useJson<Repo[]>(paths.repos);
  const { data: factors } = useJson<Factor[]>(paths.factors);
  const [tab, setTab] = useState<TabId>("papers");
  const [q, setQ] = useState("");
  const [risk, setRisk] = useState<LicenseRisk | "all">("all");
  const [onlyRec, setOnlyRec] = useState(false);

  const ql = q.trim().toLowerCase();
  const fp = useMemo(
    () =>
      (papers ?? []).filter(
        (p) => !ql || [p.title, p.authors.join(" "), p.venue, p.factor_ids.join(" "), String(p.year)].join(" ").toLowerCase().includes(ql),
      ),
    [papers, ql],
  );
  const fr = useMemo(
    () =>
      (repos ?? []).filter(
        (r) =>
          (risk === "all" || r.license_risk === risk) &&
          (!onlyRec || r.recommended) &&
          (!ql || [r.id, r.purpose, r.language, r.license, r.factor_ids.join(" ")].join(" ").toLowerCase().includes(ql)),
      ),
    [repos, ql, risk, onlyRec],
  );

  if (e1 || e2) return <ErrorBox error={(e1 ?? e2) as Error} />;
  if (!papers || !repos) return <Loading what="論文與專案" />;

  const nUnchecked = papers.filter((p) => !p.fulltext_checked).length;

  return (
    <div>
      <PageTitle title="論文與 GitHub 研究中心" sub="每個因子的來源追溯：論文（文獻實證）與開源專案（含授權風險）。" />
      <Tabs<TabId>
        tabs={[
          { id: "papers", label: `論文（${papers.length}）` },
          { id: "repos", label: `GitHub（${repos.length}）` },
          { id: "map", label: "因子 ↔ 來源對照" },
        ]}
        value={tab}
        onChange={setTab}
      />
      <div className="mt-4 space-y-3">
        {tab !== "map" ? (
          <div className="flex flex-wrap items-center gap-2">
            <input
              type="search"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder={tab === "papers" ? "搜尋標題、作者、期刊、因子 ID…" : "搜尋專案、用途、語言、授權、因子 ID…"}
              aria-label="搜尋"
              className="min-w-0 flex-1 rounded-lg border border-line bg-surface px-3 py-1.5 text-sm"
            />
            {tab === "repos" ? (
              <>
                {(["all", "ok", "copyleft", "none", "restricted"] as const).map((r) => (
                  <Btn key={r} active={risk === r} onClick={() => setRisk(r)}>
                    {{ all: "全部授權", ok: "寬鬆", copyleft: "Copyleft", none: "無授權", restricted: "附限制" }[r]}
                  </Btn>
                ))}
                <Btn active={onlyRec} onClick={() => setOnlyRec((v) => !v)}>
                  只看推薦
                </Btn>
              </>
            ) : null}
          </div>
        ) : null}

        {tab === "papers" ? (
          <>
            <p className="text-xs text-muted">
              共 {fp.length} 篇。{nUnchecked} / {papers.length} 篇尚未核對全文，文獻數字僅供參考；以論文原文為準。
            </p>
            <div className="grid gap-3 lg:grid-cols-2">
              {fp.map((p) => (
                <PaperCard key={p.id} paper={p} />
              ))}
            </div>
          </>
        ) : null}

        {tab === "repos" ? (
          <>
            <p className="text-xs text-muted">
              共 {fr.length} 個。星數為「查詢日」當天的數字，之後會變動。Copyleft／無授權／附限制的專案只可做概念參考，不得複製程式碼。
            </p>
            <div className="grid gap-3 lg:grid-cols-2">
              {fr.map((r) => (
                <RepoCard key={r.id} repo={r} />
              ))}
            </div>
          </>
        ) : null}

        {tab === "map" ? (
          <Card className="p-0">
            <div className="scroll-x">
              <table className="w-full min-w-[40rem] text-left text-sm">
                <thead className="border-b border-line bg-surface2 text-xs text-muted">
                  <tr>
                    <th className="px-3 py-2 font-medium">因子</th>
                    <th className="px-3 py-2 font-medium">論文</th>
                    <th className="px-3 py-2 font-medium">GitHub 參考專案</th>
                  </tr>
                </thead>
                <tbody>
                  {(factors ?? []).map((f) => (
                    <tr key={f.id} className="border-b border-line align-top last:border-0">
                      <td className="px-3 py-2">
                        <Link href={`/factors/${f.id}/`} className="text-accent hover:underline">
                          {f.name_zh}
                        </Link>
                        <div className="font-mono text-[11px] text-muted">{f.id}</div>
                      </td>
                      <td className="px-3 py-2">
                        <div className="flex flex-wrap gap-1">
                          {f.paper_ids.length === 0 ? <span className="text-xs text-muted">—</span> : null}
                          {f.paper_ids.map((id) => {
                            const p = papers.find((x) => x.id === id);
                            return (
                              <Pill key={id} title={p?.title}>
                                {p ? `${p.authors[0]?.split(" ").pop() ?? ""} ${p.year}` : id}
                              </Pill>
                            );
                          })}
                        </div>
                      </td>
                      <td className="px-3 py-2">
                        <div className="flex flex-wrap gap-1">
                          {f.repo_refs.length === 0 ? <span className="text-xs text-muted">—</span> : null}
                          {f.repo_refs.map((r) => (
                            <Pill key={r.repo} tone={/GPL|None|無授權|Commons/i.test(r.license) ? "warn" : "ok"} title={`${r.license}：${r.usage}`}>
                              {r.repo}
                            </Pill>
                          ))}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        ) : null}
      </div>
    </div>
  );
}
