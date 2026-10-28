// 建置後檢查：確認 out/ 內容完整。用法：npm run check:out（需先 npm run build）
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const out = path.join(root, "out");
const errors = [];
const must = (rel, why) => {
  if (!fs.existsSync(path.join(out, rel))) errors.push(`缺少 ${rel}（${why}）`);
};

if (!fs.existsSync(out)) {
  console.error("找不到 out/，請先執行 npm run build");
  process.exit(1);
}

for (const page of ["index.html", "factors/index.html", "compare/index.html", "backtest/index.html", "sources/index.html"]) must(page, "頁面");

const manifest = JSON.parse(fs.readFileSync(path.join(root, "public", "data", "manifest.json"), "utf-8"));
for (const id of manifest.factor_ids) must(`factors/${id}/index.html`, "因子詳細頁");

for (const f of ["manifest.json", "factors.json", "papers.json", "repos.json", "dashboard.json", "backtests/index.json", "compare/DEMO_TW.json", "compare/DEMO_US.json"]) must(`data/${f}`, "資料檔");

const countJson = (dir) =>
  fs.readdirSync(dir, { withFileTypes: true }).reduce((n, e) => n + (e.isDirectory() ? countJson(path.join(dir, e.name)) : e.name.endsWith(".json") ? 1 : 0), 0);
const src = countJson(path.join(root, "public", "data"));
const dst = fs.existsSync(path.join(out, "data")) ? countJson(path.join(out, "data")) : 0;
if (src !== dst) errors.push(`data/ JSON 數量不符：public ${src} vs out ${dst}`);

// basePath 檢查：若設定了 NEXT_PUBLIC_BASE_PATH，首頁資源路徑必須以它開頭
const bp = process.env.NEXT_PUBLIC_BASE_PATH ?? "";
const html = fs.existsSync(path.join(out, "index.html")) ? fs.readFileSync(path.join(out, "index.html"), "utf-8") : "";
const assetRefs = [...html.matchAll(/(?:src|href)="(\/_next\/[^"]+)"/g)].map((m) => m[1]);
const prefixed = [...html.matchAll(/(?:src|href)="([^"]*\/_next\/[^"]+)"/g)].map((m) => m[1]);
if (bp) {
  if (assetRefs.length) errors.push(`index.html 有 ${assetRefs.length} 個資源路徑未加 ${bp}（例：${assetRefs[0]}）`);
  if (!prefixed.length || !prefixed.every((u) => u.startsWith(`${bp}/_next/`))) errors.push(`index.html 的資源路徑未全部以 ${bp}/ 開頭`);
}

if (errors.length) {
  console.error(errors.join("\n"));
  process.exit(1);
}
console.log(`check:out OK：5 個頁面、${manifest.factor_ids.length} 個因子頁、data/ ${dst} 個 JSON${bp ? `、basePath=${bp}` : ""}`);
