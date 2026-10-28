// localStorage 的所有讀寫都包 try/catch（私密視窗、被封鎖時不可炸掉）。
export function safeGet(key: string): string | null {
  try {
    return typeof window === "undefined" ? null : window.localStorage.getItem(key);
  } catch {
    return null;
  }
}

export function safeSet(key: string, value: string): void {
  try {
    if (typeof window !== "undefined") window.localStorage.setItem(key, value);
  } catch {
    /* ignore */
  }
}

export function parseFavorites(raw: string | null): string[] {
  if (!raw) return [];
  try {
    const v: unknown = JSON.parse(raw);
    return Array.isArray(v) ? v.filter((x): x is string => typeof x === "string") : [];
  } catch {
    return [];
  }
}

export function loadFavorites(): string[] {
  return parseFavorites(safeGet("qfr:favorites"));
}

export function saveFavorites(ids: string[]): void {
  safeSet("qfr:favorites", JSON.stringify(ids));
}
