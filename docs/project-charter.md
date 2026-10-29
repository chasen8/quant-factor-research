# 專案章程：量化 Alpha 因子研究平台

## 目標
建立能持續加入新論文、新因子，並能做實證分析的量化研究平台。原始需求全文見使用者 2026-10-28 訊息（十大節：GitHub 調查、論文調查、因子資料庫、驗證系統、網站規劃、技術評估、MVP、研究規則、交付流程）。

## 目前狀態
- 2026-10-28：Step 1～5 完成並經獨立抽查（有條件通過，2 條必修已修）。總報告 `docs/research/00-summary.md`；因子 36 個在 `factors/factors.yaml`；測試 77 passed。
- 2026-10-28：Step 6 MVP M1～M3 完成。pytest 146＋9 passed、vitest 30 passed、靜態 build（含 basePath）成功；本機 commit 25db55b。
- 2026-10-28：已上線 https://chasen8.github.io/quant-factor-research/（repo chasen8/quant-factor-research，Pages build_type=workflow；部署 run 40642037611 test/build/deploy 全 success，8 個網址實測 200）。
- 2026-10-28：EXP-001（台股低波動）OOS 2019–2026 三條預先登記標準全過（Sharpe 1.24 vs B1 0.94、MCPT p≈0.0005、MDD 25% vs 34%），但 CAGR 13.4% < B1 17.8%，且輸給 0050（CAGR 30%、Sharpe ~1.3）。已知弱點：MCPT 用 Sharpe 對「隨機挑股」的虛無，低波動在機制上就佔優，證據力比 p 值看起來弱。EXP-002 設計要改用更嚴格的統計量（相對 B1 的 alpha 或波動配對的隨機組合）。
- 2026-10-28：EXP-002（幣圈 3 週動能，Binance 成交額前 30、只做多、週調倉）OOS 2022–2026 三條全沒過：策略 CAGR −58%／Sharpe −0.68，B1（前 30 等權）−48%／−0.44，BTC 買進持有 +13%／0.50；MCPT p=0.93。IS 有過 P1、P2，但仍輸 BTC。主導結論：成交額前 30 的山寨幣籃子 2022–2026 跌約 95%，BTC 漲 80%，選幣因子救不了籃子本身。B1 逐年報酬已用原始 zip 獨立重算吻合。已知瑕疵：穩定幣 U（UUSDT）不在排除清單，2026 年有 29 週進池（不影響結論）。
- 2026-10-29：EXP-003（使用者給的「十大量化模型」影片截圖，在 `new/`，不進 git）台股實測：7 個策略在 Holm 校正後全部沒過（原始 p 最小 0.136）。擇時類（GARCH、HMM、凱利）只降低回撤，Sharpe 都輸 0050。馬可維茲輸 1/N。配對交易扣成本後為負。PCA 反轉被成本吃掉。神經網路 Sharpe 1.50 但超額報酬 −0.9%，本質上是重新發現低波動。D1、D2 證實肥尾、波動群聚、崩盤同步被低估。BSM 未測。凱利已用原始資料獨立重算吻合。
- 2026-10-29：新增 `AGENTS.md`，給 Codex 等其他 AI 用。
- 目前唯一通過預先登記標準的是 EXP-001 低波動，但它仍輸 0050。
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
- 2026-10-28｜加密貨幣實驗資料用 Binance 公開歷史檔（data.binance.vision 現貨日 K，免金鑰、含已下架幣、CHECKSUM 驗證），存 `C:\trading-data\quant-factors\binance-spot\`；Blave CDN 只有台股｜使用者要「先試試加密貨幣」；免費且無存活者偏誤（限 Binance 上架過的幣）｜Binance 停止提供或條款禁止研究用途時
- 2026-10-28｜EXP-002 起，MCPT 統計量改用「相對 B1 的超額報酬」，並把市場代表標的（台股 0050／幣圈 BTC）列入合格標準｜EXP-001 的 Sharpe 統計量在機制上偏袒低波動；打不贏買進持有就沒有實用價值｜不會推翻
- 2026-10-28｜圖表統一 ECharts 6＋自寫 hook，不用 lightweight-charts/plotly｜一套函式庫涵蓋所有圖型、免署名義務｜需要專業 K 線互動時
