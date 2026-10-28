import type { CostModel, Num } from "./types";

export const DASH = "—";

export function isNum(v: unknown): v is number {
  return typeof v === "number" && Number.isFinite(v);
}

/** null / undefined / NaN / Infinity 一律顯示「—」，不可出現 NaN。 */
export function fmtNum(v: Num | undefined, digits = 2): string {
  return isNum(v) ? v.toFixed(digits) : DASH;
}

/** 0.012 → "1.2%" */
export function fmtPct(v: Num | undefined, digits = 1): string {
  return isNum(v) ? `${(v * 100).toFixed(digits)}%` : DASH;
}

export function fmtSigned(v: Num | undefined, digits = 2): string {
  if (!isNum(v)) return DASH;
  const s = v.toFixed(digits);
  return v > 0 ? `+${s}` : s;
}

export function fmtSignedPct(v: Num | undefined, digits = 1): string {
  if (!isNum(v)) return DASH;
  const s = (v * 100).toFixed(digits);
  return v > 0 ? `+${s}%` : `${s}%`;
}

export function fmtInt(v: Num | undefined): string {
  return isNum(v) ? Math.round(v).toLocaleString("en-US") : DASH;
}

export function fmtStr(v: string | null | undefined): string {
  return v === null || v === undefined || v === "" ? DASH : v;
}

/** 正負號語意：1 / -1 / 0（null → 0） */
export function sign(v: Num | undefined): 1 | -1 | 0 {
  if (!isNum(v) || v === 0) return 0;
  return v > 0 ? 1 : -1;
}

function pctText(x: number): string {
  return `${parseFloat((x * 100).toFixed(4))}%`;
}

export function costToText(c: CostModel): string {
  return `買進手續費 ${pctText(c.buy_commission)}｜賣出手續費 ${pctText(c.sell_commission)}｜證交稅 ${pctText(c.sell_tax)}｜滑價 ${pctText(c.slippage)}（皆為單邊）`;
}
