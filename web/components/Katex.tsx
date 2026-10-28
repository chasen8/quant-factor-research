"use client";

import katex from "katex";
import { useMemo } from "react";

export function Tex({ latex, display = true }: { latex: string; display?: boolean }) {
  const html = useMemo(() => {
    try {
      return katex.renderToString(latex, { displayMode: display, throwOnError: false, output: "htmlAndMathml" });
    } catch {
      return null;
    }
  }, [latex, display]);
  if (html === null) return <code className="break-words text-xs">{latex}</code>;
  return <div className={display ? "overflow-x-auto" : "inline"} dangerouslySetInnerHTML={{ __html: html }} />;
}
