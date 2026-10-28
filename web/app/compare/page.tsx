import { Suspense } from "react";
import type { Metadata } from "next";
import { Compare } from "@/components/Compare";
import { Loading } from "@/components/ui";

export const metadata: Metadata = { title: "因子比較｜量化 Alpha 因子研究平台" };

export default function Page() {
  return (
    <Suspense fallback={<Loading what="比較頁" />}>
      <Compare />
    </Suspense>
  );
}
