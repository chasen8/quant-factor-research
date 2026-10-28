import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";
import "./globals.css";
import "katex/dist/katex.min.css";
import { SettingsProvider } from "@/components/Providers";
import { DemoBanner, Footer, Header } from "@/components/Shell";

export const metadata: Metadata = {
  title: "量化 Alpha 因子研究平台（示範版）",
  description: "每個數字都標示證據來源的 Alpha 因子研究平台。目前所有績效皆為合成示範資料。",
};

export const viewport: Viewport = { width: "device-width", initialScale: 1 };

// 在 React 水合前先套用主題，避免閃白。
const THEME_SCRIPT = `try{var t=localStorage.getItem('qfr:theme');var d=t==='dark'||((!t||t==='system')&&window.matchMedia('(prefers-color-scheme: dark)').matches);document.documentElement.dataset.theme=d?'dark':'light';var m=localStorage.getItem('qfr:market');document.documentElement.dataset.updown=(localStorage.getItem('qfr:updown')==='green-up'||(m&&m.indexOf('US')>=0&&localStorage.getItem('qfr:updown')!=='red-up'))?'green-up':'red-up';}catch(e){document.documentElement.dataset.theme='light';document.documentElement.dataset.updown='red-up';}`;

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="zh-Hant" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_SCRIPT }} />
      </head>
      <body>
        <SettingsProvider>
          <DemoBanner />
          <Header />
          <main className="mx-auto min-h-[60vh] max-w-7xl px-4 py-6">{children}</main>
          <Footer />
        </SettingsProvider>
      </body>
    </html>
  );
}
