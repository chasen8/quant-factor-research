import type { Metadata } from "next";
import { FactorsExplorer } from "@/components/FactorsExplorer";

export const metadata: Metadata = { title: "因子資料庫｜量化 Alpha 因子研究平台" };

export default function Page() {
  return <FactorsExplorer />;
}
