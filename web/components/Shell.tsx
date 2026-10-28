"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useSettings, type ThemePref, type UpDownPref } from "./Providers";
import { cx } from "./ui";
import type { MarketId, MarketKind } from "@/lib/types";
import { marketKind } from "@/lib/data";

const NAV = [
  { href: "/", label: "儀表板" },
  { href: "/factors/", label: "因子資料庫" },
  { href: "/compare/", label: "因子比較" },
  { href: "/backtest/", label: "策略回測" },
  { href: "/sources/", label: "論文與 GitHub" },
];

export function DemoBanner() {
  return (
    <div role="note" className="border-b border-demoline bg-demobg px-4 py-1 text-center text-xs text-demo">
      目前所有績效為<strong>合成示範資料</strong>，非真實研究結果
    </div>
  );
}

function Segmented<T extends string>({
  value, options, onChange, label,
}: { value: T; options: { id: T; label: string; title?: string }[]; onChange: (v: T) => void; label: string }) {
  return (
    <div role="group" aria-label={label} className="inline-flex overflow-hidden rounded-lg border border-line text-xs">
      {options.map((o) => (
        <button
          key={o.id}
          title={o.title}
          aria-pressed={value === o.id}
          onClick={() => onChange(o.id)}
          className={cx("px-2.5 py-1 transition-colors", value === o.id ? "bg-accent text-accentfg" : "bg-surface hover:bg-surface2")}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}

export function Header() {
  const pathname = usePathname() ?? "/";
  const s = useSettings();
  const markets = s.manifest?.markets ?? [];
  const pick = (kind: MarketKind): MarketId | undefined => markets.find((m) => marketKind(m.id) === kind)?.id;

  return (
    <header className="sticky top-0 z-30 border-b border-line bg-surface/95 backdrop-blur">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-x-4 gap-y-2 px-4 py-2">
        <Link href="/" className="text-base font-bold tracking-tight">
          量化 Alpha 因子研究平台
        </Link>
        <nav aria-label="主選單" className="scroll-x order-3 -mx-1 flex w-full gap-1 md:order-none md:w-auto">
          {NAV.map((n) => {
            const active = n.href === "/" ? pathname === "/" : pathname.startsWith(n.href);
            return (
              <Link
                key={n.href}
                href={n.href}
                aria-current={active ? "page" : undefined}
                className={cx(
                  "whitespace-nowrap rounded-md px-2.5 py-1 text-sm",
                  active ? "bg-accentsoft font-semibold text-accent" : "text-muted hover:bg-surface2 hover:text-fg",
                )}
              >
                {n.label}
              </Link>
            );
          })}
        </nav>
        <div className="ml-auto flex flex-wrap items-center gap-2">
          <Segmented<MarketKind>
            label="市場"
            value={s.kind}
            onChange={(k) => {
              const m = pick(k);
              if (m) s.setMarket(m);
            }}
            options={[
              { id: "TW", label: "台股", title: s.manifest?.markets.find((m) => marketKind(m.id) === "TW")?.label },
              { id: "US", label: "美股", title: s.manifest?.markets.find((m) => marketKind(m.id) === "US")?.label },
            ]}
          />
          <Segmented<UpDownPref>
            label="漲跌色"
            value={s.updownPref}
            onChange={s.setUpdownPref}
            options={[
              { id: "auto", label: "自動", title: "跟隨市場：台股紅漲綠跌、美股綠漲紅跌" },
              { id: "red-up", label: "紅漲", title: "紅漲綠跌（台股慣例）" },
              { id: "green-up", label: "綠漲", title: "綠漲紅跌（美股慣例）" },
            ]}
          />
          <Segmented<ThemePref>
            label="主題"
            value={s.themePref}
            onChange={s.setThemePref}
            options={[
              { id: "system", label: "跟隨" },
              { id: "light", label: "淺" },
              { id: "dark", label: "深" },
            ]}
          />
        </div>
      </div>
    </header>
  );
}

export function Footer() {
  return (
    <footer className="mt-12 border-t border-line bg-surface px-4 py-6 text-xs text-muted">
      <div className="mx-auto max-w-7xl space-y-1">
        <p>
          <strong>免責聲明：</strong>非投資建議；歷史回測不代表未來報酬。
        </p>
        <p>
          本站所有績效數字目前皆為合成示範資料。證據標籤：文獻實證＝論文原始報告；自行回測＝本平台以自有資料重算；尚未驗證＝僅收錄公式；示範資料＝合成資料，僅展示介面。
        </p>
        <p>圖表使用 Apache ECharts（Apache-2.0）、公式使用 KaTeX（MIT）。</p>
      </div>
    </footer>
  );
}
