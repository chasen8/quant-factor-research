import type { Metadata } from "next";
import { Backtest } from "@/components/Backtest";

export const metadata: Metadata = { title: "策略回測｜量化 Alpha 因子研究平台" };

export default function Page() {
  return <Backtest />;
}
