"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { marketKind } from "@/lib/data";
import { safeGet, safeSet } from "@/lib/storage";
import { DARK, LIGHT, UPDOWN_GREEN_UP, UPDOWN_RED_UP, type Palette, type UpDown } from "@/lib/chartTheme";
import { useJson } from "@/lib/hooks";
import { paths } from "@/lib/data";
import type { Manifest, MarketId, MarketInfo, MarketKind } from "@/lib/types";

export type ThemePref = "system" | "light" | "dark";
export type UpDownPref = "auto" | "red-up" | "green-up";

interface Settings {
  themePref: ThemePref;
  setThemePref: (t: ThemePref) => void;
  theme: "light" | "dark";
  palette: Palette;
  updownPref: UpDownPref;
  setUpdownPref: (u: UpDownPref) => void;
  updown: UpDown;
  market: MarketId;
  setMarket: (m: MarketId) => void;
  kind: MarketKind;
  manifest: Manifest | undefined;
  marketInfo: MarketInfo | undefined;
}

const Ctx = createContext<Settings | null>(null);

export function useSettings(): Settings {
  const v = useContext(Ctx);
  if (!v) throw new Error("SettingsProvider missing");
  return v;
}

export function SettingsProvider({ children }: { children: ReactNode }) {
  const [themePref, setThemePrefState] = useState<ThemePref>("system");
  const [systemDark, setSystemDark] = useState(false);
  const [updownPref, setUpdownPrefState] = useState<UpDownPref>("auto");
  const [market, setMarketState] = useState<MarketId>("DEMO_TW");
  const { data: manifest } = useJson<Manifest>(paths.manifest);

  useEffect(() => {
    const t = safeGet("qfr:theme");
    if (t === "light" || t === "dark" || t === "system") setThemePrefState(t);
    const u = safeGet("qfr:updown");
    if (u === "auto" || u === "red-up" || u === "green-up") setUpdownPrefState(u);
    const m = safeGet("qfr:market");
    if (m === "DEMO_TW" || m === "DEMO_US" || m === "TW" || m === "US") setMarketState(m);
  }, []);

  useEffect(() => {
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    setSystemDark(mq.matches);
    const h = (e: MediaQueryListEvent) => setSystemDark(e.matches);
    mq.addEventListener("change", h);
    return () => mq.removeEventListener("change", h);
  }, []);

  const theme: "light" | "dark" = themePref === "system" ? (systemDark ? "dark" : "light") : themePref;
  const kind = marketKind(market);
  const updownMode: "red-up" | "green-up" = updownPref === "auto" ? (kind === "TW" ? "red-up" : "green-up") : updownPref;

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
  }, [theme]);
  useEffect(() => {
    document.documentElement.dataset.updown = updownMode;
  }, [updownMode]);

  const setThemePref = useCallback((t: ThemePref) => {
    setThemePrefState(t);
    safeSet("qfr:theme", t);
  }, []);
  const setUpdownPref = useCallback((u: UpDownPref) => {
    setUpdownPrefState(u);
    safeSet("qfr:updown", u);
  }, []);
  const setMarket = useCallback((m: MarketId) => {
    setMarketState(m);
    safeSet("qfr:market", m);
  }, []);

  const value = useMemo<Settings>(
    () => ({
      themePref,
      setThemePref,
      theme,
      palette: theme === "dark" ? DARK : LIGHT,
      updownPref,
      setUpdownPref,
      updown: updownMode === "red-up" ? UPDOWN_RED_UP : UPDOWN_GREEN_UP,
      market,
      setMarket,
      kind,
      manifest,
      marketInfo: manifest?.markets.find((m) => m.id === market),
    }),
    [themePref, setThemePref, theme, updownPref, setUpdownPref, updownMode, market, setMarket, kind, manifest],
  );

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}
