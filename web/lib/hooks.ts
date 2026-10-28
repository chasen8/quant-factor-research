"use client";

import { useEffect, useState } from "react";
import { fetchJson } from "./data";

export interface Async<T> {
  data: T | undefined;
  error: Error | undefined;
  loading: boolean;
}

/** path 為 null 時不抓。同一路徑在記憶體快取，不重複請求。 */
export function useJson<T>(path: string | null): Async<T> {
  const [state, setState] = useState<{ path: string | null; data?: T; error?: Error }>({ path: null });
  useEffect(() => {
    if (path === null) return;
    let alive = true;
    fetchJson<T>(path).then(
      (data) => alive && setState({ path, data }),
      (error: Error) => alive && setState({ path, error }),
    );
    return () => {
      alive = false;
    };
  }, [path]);
  const fresh = state.path === path;
  return {
    data: fresh ? state.data : undefined,
    error: fresh ? state.error : undefined,
    loading: path !== null && !fresh,
  };
}

/** 一次抓多個路徑；失敗的項目回傳 undefined（例如該市場無此因子）。 */
export function useJsonMap<T>(list: string[]): { data: Record<string, T | undefined>; loading: boolean } {
  const key = list.join("|");
  const [state, setState] = useState<{ key: string; data: Record<string, T | undefined> }>({ key: "", data: {} });
  useEffect(() => {
    let alive = true;
    const paths = key ? key.split("|") : [];
    Promise.all(paths.map((p) => fetchJson<T>(p).then((d) => [p, d] as const, () => [p, undefined] as const))).then(
      (entries) => alive && setState({ key, data: Object.fromEntries(entries) }),
    );
    return () => {
      alive = false;
    };
  }, [key]);
  return { data: state.key === key ? state.data : {}, loading: state.key !== key };
}
