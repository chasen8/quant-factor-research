import type { Metadata } from "next";
import { Sources } from "@/components/Sources";

export const metadata: Metadata = { title: "論文與 GitHub｜量化 Alpha 因子研究平台" };

export default function Page() {
  return <Sources />;
}
