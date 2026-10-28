# 專案章程：量化 Alpha 因子研究平台

## 目標
建立能持續加入新論文、新因子，並能做實證分析的量化研究平台。原始需求全文見使用者 2026-10-28 訊息（十大節：GitHub 調查、論文調查、因子資料庫、驗證系統、網站規劃、技術評估、MVP、研究規則、交付流程）。

## 目前狀態
- 2026-10-28：Step 1～5 完成並經獨立抽查（有條件通過，2 條必修已修）。總報告 `docs/research/00-summary.md`；因子 36 個在 `factors/factors.yaml`；測試 77 passed。
- 2026-10-28：Step 6 MVP M1～M3 完成。pytest 146＋9 passed、vitest 30 passed、靜態 build（含 basePath）成功；本機 commit 25db55b。
- 2026-10-28：已上線 https://chasen8.github.io/quant-factor-research/（repo chasen8/quant-factor-research，Pages build_type=workflow；部署 run 40642037611 test/build/deploy 全 success，8 個網址實測 200）。
- 2026-10-28：EXP-001（台股低波動）OOS 2019–2026 三條預先登記標準全過（Sharpe 1.24 vs B1 0.94、MCPT p≈0.0005、MDD 25% vs 34%），但 CAGR 13.4% < B1 17.8%，且輸給 0050（CAGR 30%、Sharpe ~1.3）。已知弱點：MCPT 用 Sharpe 對「隨機挑股」的虛無，低波動在機制上就佔優，證據力比 p 值看起來弱。EXP-002 設計要改用更嚴格的統計量（相對 B1 的 alpha 或波動配對的隨機組合）。
- 之後：使用者下載論文 PDF（scripts/fetch_papers.py）→ 逐篇核對公式；M4 台股真資料等使用者看過 MVP。
- 已知待辦：論文全文核對（目前公式多為「標準化定義」、多數樣本期間標「待核對」），上線前必做。

## 決策記錄
格式：日期｜決定｜原因｜何時可推翻

- 2026-10-28｜研究產出用 Markdown＋一份機器可讀因子檔（YAML），存在專案 `docs/research/`｜使用者不用 Artifact；YAML 可直接當 MVP 種子資料｜MVP 改用資料庫為單一真實來源時
- 2026-10-28｜行情與衍生資料放 `C:\trading-data\quant-factors\`｜全域鐵律：大檔不進 OneDrive｜不會推翻
- 2026-10-28｜因子評估與回測引擎自寫；alphalens-reloaded 只當 dev 驗算器；vectorbt 禁用｜需 PIT/台股成本/證據標籤客製；vectorbt 有 Commons Clause｜出現授權乾淨且支援 PIT 的成熟框架時
- 2026-10-28｜MVP 以示範資料為主；台股真資料走 FinMind REST（requests，不裝 FinMind 套件）；美股只做 Ken French＋OSAP 組合報酬對照｜免費源都缺下市股或公告日；FinMind 套件釘 pandas<3；美股免費價格源條款不允許展示｜使用者同意購買 TEJ/CRSP 等合格資料時
- 2026-10-28｜`factors/factors.yaml` 是因子定義的唯一真實來源，直接手改；`C:\trading-data\quant-factors\scratch\` 的生成腳本是一次性工具，**不要重跑**（會覆蓋手改內容）｜避免兩份來源漂移｜不會推翻
- 2026-10-28｜專案 venv：`C:\trading-data\quant-factors\venv`（py 3.13）；測試 `C:\trading-data\quant-factors\venv\Scripts\python.exe -m pytest tests -q`｜venv 不進 OneDrive｜不會推翻
- 2026-10-28｜使用者確認：MVP 做 M1～M3，M4（台股真資料）看過 MVP 再說；只用免費資料；上線成靜態站；36 因子與 5 個推薦 repo 不增刪｜使用者回覆總報告第 7 節｜使用者改變主意時
- 2026-10-28｜論文全文由使用者手動下載，PDF 放 `C:\trading-data\quant-factors\papers\`，**絕不進 git／公開 repo**（版權）｜自動擷取被 403；PDF 有版權｜不會推翻
- 2026-10-28｜web 的 npm 一律走 `bash scripts/web.sh ...`：原始碼在 OneDrive 的 `web/`，node_modules/.next/out 只存在鏡像 `C:\trading-data\quant-factors\web-build`；**禁止在 OneDrive 內直接 npm install / create-next-app**｜node_modules 數百 MB，違反大檔不進 OneDrive｜專案搬出 OneDrive 時
- 2026-10-28｜部署：公開 repo `chasen8/quant-factor-research` ＋ GitHub Pages（Actions：pytest → next build 靜態輸出 → deploy）｜使用者要靜態站；免費 Pages 需公開 repo，與使用者其他站一致｜需要私有時改 Vercel 等
- 2026-10-28｜示範 JSON（web/public/data，約 5MB，決定性種子）提交進 git｜web 不需 Python 即可 build；CI 簡單｜資料量 > 50MB 或改用真資料時
- 2026-10-28｜台股價格資料改用 Blave CDN（download.blave.org，交易所原始 OHLCV＋除權息事件，2010 起、含 332 檔下市股、免金鑰、政府資料開放授權），取代 FinMind 作為價格來源；不安裝 Blave 桌面 app（未簽章、含實盤下單功能）｜使用者推薦；含下市股＝價格類策略無存活者偏誤｜CDN 關閉（manifest enabled=false）或條款改變時
- 2026-10-28｜研究流程改為「一次一個策略、預先登記、OOS 只跑一次、扣成本、MCPT」，撐得住才加下一個因子；實驗記錄在 `docs/experiments/EXP-xxx.md`，結果不得回改登記內容｜使用者要求先別疊因子｜不會推翻
- 2026-10-28｜圖表統一 ECharts 6＋自寫 hook，不用 lightweight-charts/plotly｜一套函式庫涵蓋所有圖型、免署名義務｜需要專業 K 線互動時
