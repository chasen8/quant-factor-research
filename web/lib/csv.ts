import type { Num } from "./types";

function cell(v: string | Num | undefined): string {
  if (v === null || v === undefined) return "";
  if (typeof v === "number") return Number.isFinite(v) ? String(v) : "";
  return /[",\n]/.test(v) ? `"${v.replace(/"/g, '""')}"` : v;
}

/** 欄式資料轉 CSV（第一欄通常是日期） */
export function toCsv(columns: { name: string; values: (string | Num)[] }[]): string {
  const n = Math.max(0, ...columns.map((c) => c.values.length));
  const lines = [columns.map((c) => cell(c.name)).join(",")];
  for (let i = 0; i < n; i++) lines.push(columns.map((c) => cell(c.values[i])).join(","));
  return lines.join("\n");
}
