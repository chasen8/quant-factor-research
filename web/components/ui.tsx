"use client";

import { useState, type ReactNode } from "react";
import type { LevelId, LicenseRisk, Provenance } from "@/lib/types";
import { costToText, fmtInt, fmtStr } from "@/lib/format";

export function cx(...a: (string | false | null | undefined)[]): string {
  return a.filter(Boolean).join(" ");
}

export function Card({ children, className }: { children: ReactNode; className?: string }) {
  return <section className={cx("min-w-0 rounded-xl border border-line bg-surface p-4", className)}>{children}</section>;
}

export function PageTitle({ title, sub }: { title: string; sub?: ReactNode }) {
  return (
    <div className="mb-5">
      <h1 className="text-2xl font-bold tracking-tight">{title}</h1>
      {sub ? <p className="mt-1 text-sm text-muted">{sub}</p> : null}
    </div>
  );
}

export function SectionTitle({ children, right }: { children: ReactNode; right?: ReactNode }) {
  return (
    <div className="mb-2 mt-6 flex items-center justify-between gap-2">
      <h2 className="text-base font-semibold">{children}</h2>
      {right}
    </div>
  );
}

const EVIDENCE_STYLE: Record<string, string> = {
  文獻實證: "border-sky-500/40 bg-sky-500/10 text-sky-700 dark:text-sky-300",
  自行回測: "border-emerald-500/40 bg-emerald-500/10 text-emerald-700 dark:text-emerald-300",
  尚未驗證: "border-line bg-surface2 text-muted",
  示範資料: "border-demoline bg-demobg text-demo",
};

/** 證據標籤：全站統一（見 04 文件第 0 節）。 */
export function EvidenceTag({ label, className }: { label: string; className?: string }) {
  return (
    <span
      className={cx(
        "inline-flex items-center whitespace-nowrap rounded-md border px-1.5 py-0.5 text-[11px] font-medium leading-4",
        EVIDENCE_STYLE[label] ?? EVIDENCE_STYLE["尚未驗證"],
        className,
      )}
    >
      {label}
    </span>
  );
}

const LEVEL_TITLE: Record<LevelId, string> = {
  L0: "L0 尚未驗證",
  L1: "L1 樣本內顯著",
  L2: "L2 樣本外確認",
  L3: "L3 扣成本後有效",
  L4: "L4 跨市場／跨期間穩健",
};

export function LevelBadge({ level }: { level: LevelId }) {
  return (
    <span
      title={LEVEL_TITLE[level]}
      className={cx(
        "inline-flex min-w-7 justify-center rounded-md border px-1.5 py-0.5 text-[11px] font-semibold tabular",
        level === "L0" ? "border-line bg-surface2 text-muted" : "border-emerald-500/40 bg-emerald-500/10 text-emerald-700 dark:text-emerald-300",
      )}
    >
      {level}
    </span>
  );
}

export function Pill({ children, tone = "neutral", title }: { children: ReactNode; tone?: "neutral" | "ok" | "warn" | "bad" | "accent"; title?: string }) {
  const t = {
    neutral: "border-line bg-surface2 text-muted",
    ok: "border-transparent bg-okbg text-ok",
    warn: "border-transparent bg-warnbg text-warn",
    bad: "border-transparent bg-badbg text-bad",
    accent: "border-transparent bg-accentsoft text-accent",
  }[tone];
  return (
    <span title={title} className={cx("inline-flex items-center whitespace-nowrap rounded-full border px-2 py-0.5 text-[11px] font-medium", t)}>
      {children}
    </span>
  );
}

const LICENSE_TONE: Record<LicenseRisk, "ok" | "warn" | "bad"> = { ok: "ok", copyleft: "warn", none: "bad", restricted: "bad" };
const LICENSE_NOTE: Record<LicenseRisk, string> = {
  ok: "寬鬆授權",
  copyleft: "Copyleft：不可複製程式碼進本平台",
  none: "無授權：預設保留所有權利，不可複製",
  restricted: "附帶限制：不可引入",
};

export function LicenseBadge({ license, risk }: { license: string; risk: LicenseRisk }) {
  return (
    <Pill tone={LICENSE_TONE[risk]} title={LICENSE_NOTE[risk]}>
      {risk !== "ok" ? "⚠ " : ""}
      {license}
    </Pill>
  );
}

export function Btn({
  children, onClick, active, disabled, title, className, type = "button",
}: {
  children: ReactNode; onClick?: () => void; active?: boolean; disabled?: boolean; title?: string; className?: string; type?: "button" | "submit";
}) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      title={title}
      className={cx(
        "inline-flex items-center justify-center gap-1 rounded-lg border px-3 py-1.5 text-sm transition-colors disabled:cursor-not-allowed disabled:opacity-45",
        active ? "border-accent bg-accent text-accentfg" : "border-line bg-surface hover:bg-surface2",
        className,
      )}
    >
      {children}
    </button>
  );
}

export function Tabs<T extends string>({
  tabs, value, onChange, className,
}: { tabs: { id: T; label: string }[]; value: T; onChange: (v: T) => void; className?: string }) {
  return (
    <div role="tablist" className={cx("scroll-x -mx-1 flex gap-1 border-b border-line px-1", className)}>
      {tabs.map((t) => (
        <button
          key={t.id}
          role="tab"
          aria-selected={value === t.id}
          onClick={() => onChange(t.id)}
          className={cx(
            "whitespace-nowrap border-b-2 px-3 py-2 text-sm font-medium transition-colors",
            value === t.id ? "border-accent text-accent" : "border-transparent text-muted hover:text-fg",
          )}
        >
          {t.label}
        </button>
      ))}
    </div>
  );
}

export function Loading({ what = "資料" }: { what?: string }) {
  return <div className="animate-pulse rounded-xl border border-line bg-surface p-6 text-sm text-muted">載入{what}中…</div>;
}

export function ErrorBox({ error }: { error: Error | string }) {
  return (
    <div className="rounded-xl border border-transparent bg-badbg p-4 text-sm text-bad">
      資料載入失敗：{typeof error === "string" ? error : error.message}
    </div>
  );
}

export function NotApplicable({ children }: { children?: ReactNode }) {
  return (
    <div className="rounded-xl border border-dashed border-line bg-surface p-6 text-center text-sm text-muted">
      {children ?? "此市場不適用：該因子在此市場沒有分析結果。"}
    </div>
  );
}

export function DemoNote({ children }: { children?: ReactNode }) {
  return (
    <div className="rounded-lg border border-demoline bg-demobg px-3 py-2 text-xs text-demo">
      <strong>示範資料</strong>　{children ?? "以下數字由合成資料產生，只為展示介面與流程，不是研究結論。"}
    </div>
  );
}

/** 單一指標卡：可展開「出生證明」。 */
export function MetricCard({
  label, value, sub, tone, provenance, evidence, hint,
}: {
  label: string;
  value: string;
  sub?: string;
  tone?: "up" | "down" | "none";
  provenance?: Provenance;
  evidence?: string;
  hint?: string;
}) {
  const [open, setOpen] = useState(false);
  return (
    <div className="min-w-0 rounded-xl border border-line bg-surface p-3" title={hint}>
      <div className="flex items-start justify-between gap-2">
        <div className="text-xs text-muted">{label}</div>
        {evidence ? <EvidenceTag label={evidence} /> : null}
      </div>
      <div className={cx("num mt-1 text-xl font-semibold", tone === "up" && "text-up", tone === "down" && "text-down")}>{value}</div>
      {sub ? <div className="num text-xs text-muted">{sub}</div> : null}
      {provenance ? (
        <>
          <button
            onClick={() => setOpen((o) => !o)}
            aria-expanded={open}
            className="mt-2 text-[11px] text-accent underline-offset-2 hover:underline"
          >
            {open ? "收合出生證明 ▲" : "出生證明 ▼"}
          </button>
          {open ? <BirthCertificate p={provenance} evidence={evidence} /> : null}
        </>
      ) : null}
    </div>
  );
}

export function BirthCertificate({ p, evidence }: { p: Provenance; evidence?: string }) {
  const rows: [string, string][] = [
    ["證據標籤", fmtStr(evidence)],
    ["資料源", p.data_source],
    ["股票池", p.universe],
    ["平均檔數", p.avg_n_stocks.toFixed(1)],
    ["期間", `${p.start} ~ ${p.end}`],
    ["樣本外起點", p.oos_start],
    ["調倉", p.rebalance === "M" ? "月" : "季"],
    ["成本", costToText(p.cost_model)],
    ["試驗次數 n_trials", fmtInt(p.n_trials)],
    ["引擎版本", p.engine_version],
  ];
  return (
    <dl className="mt-2 grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 rounded-lg bg-surface2 p-2 text-[11px] leading-snug">
      {rows.map(([k, v]) => (
        <div key={k} className="contents">
          <dt className="whitespace-nowrap text-muted">{k}</dt>
          <dd className="break-words">{v}</dd>
        </div>
      ))}
    </dl>
  );
}
