import fs from "node:fs";
import path from "node:path";
import { FactorDetail } from "@/components/FactorDetail";

export const dynamicParams = false;

export function generateStaticParams(): { id: string }[] {
  const raw = fs.readFileSync(path.join(process.cwd(), "public", "data", "manifest.json"), "utf-8");
  const ids = (JSON.parse(raw) as { factor_ids: string[] }).factor_ids;
  return ids.map((id) => ({ id }));
}

export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <FactorDetail id={id} />;
}
