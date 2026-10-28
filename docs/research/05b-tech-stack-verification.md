# 05b：技術選型與資料來源查證

查證日期：2026-10-28。環境：Windows 11、Node v22.19.0、npm 11.17.0、Python 3.13（`py -3.13`）。
方法：npm registry（`npm view`）、PyPI JSON API、GitHub API（`pushed_at`）、官方網頁（WebFetch）、實際呼叫 API。
「尚未查證」= 本次沒有取得可靠來源。未註冊任何帳號、未申請 key、未付費。

---

## A1. 前端套件（npm registry，查詢日 2026-10-28）

| 套件 | 最新穩定版（釋出日） | License | registry 最近更新 | 維護 | React 19 | 備註 |
|---|---|---|---|---|---|---|
| next | 16.4.3（2026-10-23） | MIT | 2026-10-26 | 活躍 | peer 含 `^19.0.0` | 已是 16.x；App Router；規劃文件寫 Next.js 即可，不要鎖舊版 |
| react | 19.3.1（2026-10-14） | MIT | 2026-10-27 | 活躍 | — | |
| tailwindcss | 4.3.3（2026-07-16） | MIT | 2026-10-19 | 活躍 | 不相依 | v4 設定走 CSS-first，與 v3 教學不同 |
| shadcn（CLI） | 4.23.0（2026-10-27） | MIT | 2026-10-27 | 活躍 | 支援 | 是 CLI，元件原始碼複製進專案 |
| echarts | 6.1.0（2026-05-19） | Apache-2.0 | 2026-05-19 | 活躍 | 不相依 | 已是 6.x（主題/預設樣式與 5.x 不同） |
| echarts-for-react | 3.0.6（2026-01-21） | MIT | 2026-05-19 | 低頻維護 | peer `>=16` | 薄包裝；也可直接用 echarts 自寫 hook，避免第三方包裝落後 |
| lightweight-charts | 5.2.1（2026-08-12） | Apache-2.0 + NOTICE | 2026-08-12 | 活躍（repo pushed 2026-10-23） | 不相依（需自寫 React 包裝） | **有署名義務**，見下 |
| plotly.js | 4.1.2（2026-10-05） | MIT | 2026-10-05 | 活躍 | 不相依 | 體積大；ECharts 已足夠，不建議 MVP 用 |
| @tanstack/react-table | 9.3.1（2026-10-12） | MIT | 2026-10-12 | 活躍 | peer `>=18` | 已 v9（API 與 v8 教學不同，先看新版文件） |
| katex | 0.19.1（2026-10-23） | MIT | 2026-10-23 | 活躍 | 不相依 | |
| fuse.js | 7.5.0（2026-07-13） | Apache-2.0 | 2026-08-09 | 活躍 | 不相依 | 規劃寫「MIT」類假設不成立，實為 Apache-2.0（無衝突） |
| next-themes | 0.4.6（2025-03-11） | MIT | 2025-03-11 | **約 19 個月無新版** | peer 含 `^19` | 小而穩，仍可用；風險：Next 16 / React 19.3 相容性需實測 |
| shiki | 4.5.0（2026-10-01） | MIT | 2026-10-01 | 活躍 | 不相依 | 可在 build time / server component 上色，不增加前端 bundle |
| vitest | 5.0.5（2026-10-15） | MIT | 2026-10-19 | 活躍 | 不相依 | 已 5.x |
| playwright | 1.64.1（2026-10-14） | Apache-2.0 | 2026-10-27 | 活躍 | 不相依 | |

來源：`https://registry.npmjs.org/<pkg>`（例：https://www.npmjs.com/package/next ）；lightweight-charts repo：https://github.com/tradingview/lightweight-charts （Apache-2.0，pushed_at 2026-10-23）。

**lightweight-charts 署名要求**（來源：repo README／NOTICE，https://github.com/tradingview/lightweight-charts/blob/master/NOTICE ）：
- 授權是 Apache-2.0，但要求「標明 TradingView 為產品創作者」，網站/App 須含 NOTICE 檔的署名文字（NOTICE 內容：`TradingView Lightweight Charts™ Copyright (с) 2025 TradingView, Inc. https://www.tradingview.com/`），並在使用者可見頁面放連到 https://www.tradingview.com/ 的連結。
- 圖上 `attributionLogo` 選項顯示的 logo 連結，官方說明可滿足連結要求；若關掉它，必須在別處（如頁尾「圖表：TradingView Lightweight Charts™」）自行放署名與連結。
- 結論：可用，僅 1 處頁尾署名即可；若 ECharts 已能畫淨值曲線，MVP 可完全不引入此套件以減少義務。

## A2. 後端／計算套件（PyPI JSON，查詢日 2026-10-28）

| 套件 | 最新穩定版（釋出日） | License | requires-python／3.13 classifier | 維護 | 備註 |
|---|---|---|---|---|---|
| fastapi | 0.162.0（2026-10-23） | MIT | >=3.10／有 | 活躍 | 仍 0.x，升級要看 changelog |
| pydantic | 2.14.1（2026-10-11） | MIT | >=3.10／有 | 活躍 | |
| pandas | 3.1.0（2026-10-22） | BSD-3 | >=3.11／有 | 活躍 | **3.x 與 FinMind 衝突**，見下 |
| numpy | 2.5.4（2026-10-10） | BSD-3（含 0BSD/MIT/Zlib/CC0 的 wheel 元件） | >=3.12／有 | 活躍 | |
| scipy | 1.18.1（2026-08-21） | BSD-3 | >=3.12／有 | 活躍 | |
| statsmodels | 0.15.0（2026-08-30） | BSD-3 | >=3.10／有 | 活躍 | Newey-West 可用 |
| polars | 2.1.0（2026-10-25） | MIT | >=3.11／有 | 活躍 | 已 2.x |
| duckdb | 2.0.0（2026-10-21） | MIT | >=3.11／有 | 活躍 | 已 2.0；舊教學語法/檔案格式可能不同 |
| pyarrow | 26.0.0（2026-10-09） | Apache-2.0 | >=3.11／有 | 活躍 | |
| alphalens-reloaded | 0.5.1（2026-10-26） | Apache-2.0 | >=3.11,<3.16／有 | 活躍（repo pushed 2026-10-26） | stefan-jansen 維護的 fork；pandas <4 |
| quantstats | 0.0.86（2026-09-27） | Apache-2.0 | >=3.10／有 | 活躍（pushed 2026-09-27） | 依賴 yfinance |
| empyrical-reloaded | 0.7.1（2026-10-26） | Apache-2.0 | >=3.11／有 | 活躍 | |
| pyfolio-reloaded | 0.10.1（2026-10-25） | Apache-2.0 | >=3.11,<3.16／有 | 活躍 | 本次未實測安裝（僅查 metadata） |
| bt | 1.4.1（2026-10-10） | MIT | >=3.9／有 | 活躍（pushed 2026-10-25） | 本次未實測安裝 |
| vectorbt | 1.2.0（2026-10-19） | **Apache-2.0 + Commons Clause** | >=3.11,<3.15／有 | 活躍（pushed 2026-10-23） | 見下；PyPI metadata license 欄位是空的，GitHub 判為 NOASSERTION |
| FinMind（PyPI） | 2.1.0（2026-10-24） | Apache-2.0 | >=3.8／有 | 活躍 | 依賴 `pandas<3.0.0`；GitHub 路徑 FinMind/FinMind（FinMind-Github/FinMind 已 404） |
| yfinance | 1.7.0（2026-08-26） | Apache-2.0 | 無 requires 欄位／有 | 活躍（pushed 2026-10-26） | 條款見 B 節 |

來源：`https://pypi.org/pypi/<pkg>/json`；GitHub：polakowo/vectorbt、stefan-jansen/{alphalens,empyrical,pyfolio}-reloaded、ranaroussi/{quantstats,yfinance}、pmorissette/bt。

**vectorbt Commons Clause**（https://raw.githubusercontent.com/polakowo/vectorbt/master/LICENSE.md ）：授權為 Apache 2.0 加 Commons Clause。條件禁止「Sell」，定義包含「以收費（含託管或諮詢/支援服務費用）向第三方提供，其價值全部或實質上來自本軟體功能的產品或服務」。個人研究、免費網站不受影響；一旦網站收費或以訂閱提供回測功能，就有違約風險。規劃已定自寫回測，維持「不引入」即可。注意：vectorbt 也不是 OSI 認可的開源授權。

## A3. Python 3.13 實測

指令（venv 位於 `C:\trading-data\quant-factors\tmp-venv`，非 OneDrive，已保留）：

```
py -3.13 -m venv tmp-venv
tmp-venv/Scripts/python.exe -m pip install pandas numpy scipy statsmodels duckdb pyarrow fastapi alphalens-reloaded quantstats FinMind yfinance
```

結果：全部成功安裝，皆為 cp313 win_amd64 wheel（無需編譯），`pip check` 輸出 `No broken requirements found.`。逐一 import：

```
OK pandas 2.3.3
OK numpy 2.5.4
OK scipy 1.18.1
OK statsmodels 0.15.0
OK duckdb 2.0.0
OK pyarrow 26.0.0
OK fastapi 0.162.0
OK alphalens 0.5.1
OK quantstats 0.0.86
OK FinMind 2.1.0
OK yfinance 1.7.0
```

無安裝失敗、無 import 失敗。**但有一個隱性衝突**：同時安裝 FinMind 時，pip 解析出 pandas 2.3.3 而不是最新的 3.1.0，因為 FinMind 2.1.0 宣告 `pandas<3.0.0`。若要用 pandas 3.x，FinMind 必須放在獨立 venv（或自己用 `requests` 打 FinMind REST API，不裝套件）。alphalens-reloaded 與 empyrical-reloaded 與 pandas 3 相容（宣告 `<4`）。這次只測安裝與 import，沒有跑 alphalens 功能測試（尚未查證其在 pandas 2.3/3.x 的實際行為）。pyfolio-reloaded、bt、vectorbt、polars 沒有實際安裝。

凍結版本清單：`C:\trading-data\quant-factors\scratch\freeze.txt`。

---

## B1. 台股資料來源

| 來源 | 提供內容 | 歷史深度 | 下市股 | 財報公告日（PIT） | 免費額度／速率 | 註冊／key | 使用條款（個人研究網站展示衍生統計） | 官方網址 |
|---|---|---|---|---|---|---|---|---|
| TWSE OpenAPI | 143 個端點（實測 swagger）：上市個股日成交 `STOCK_DAY_ALL`、本益比/殖利率/淨值比 `BWIBBU_ALL`、月營收 `t187ap05_L`、損益表/資產負債表 `t187ap06/07_L_*`、除權息預告、終止上市公司名單 `suspendListingCsvAndHtml` | **實測 `STOCK_DAY_ALL` 只回「最新一個交易日」**（回傳 Date 1151022），無日期參數 → 不能回補歷史；財報端點為最新一期 | 有「終止上市公司」名單，無下市股歷史價 | 無（財報端點無公告日欄位，需自行存快照累積） | 無公布限額；社群客戶端習慣間隔 0.5 秒（非官方數字） | 不需 | swagger 首頁標示適用「政府資料開放授權條款」(https://data.gov.tw/license) 與 TWSE 使用條款；使用條款主文要求「引用須載明出處、資料完整、不得任意更改」，並禁止未經同意的自動化擷取（OpenAPI 本身屬開放資料例外，但網站 STOCK_DAY 等頁面爬蟲不在此例） | https://openapi.twse.com.tw/ ；條款 https://www.twse.com.tw/zh/page/terms/use.html |
| TPEx OpenAPI | 225 個端點：上櫃行情 `tpex_mainboard_daily_close_quotes`、本益比/淨值比、除權息、三大法人、融資融券、停止交易 | 同為最新快照為主（尚未逐一驗證每個端點是否有歷史參數 → 尚未查證） | 有「暫停/恢復交易」歷史名單；下市股價無 | 尚未查證 | 無公布限額（尚未查證） | 不需 | 有使用條款連結 (https://www.tpex.org.tw/web/inc/gtsm_disclaimer.php?l=zh-tw)，細節尚未查證 | https://www.tpex.org.tw/openapi/ |
| TWSE 網站歷史下載 | 個股日成交、除權息等（如 `STOCK_DAY` 月檔） | 深（歷史多年）；本次未實測 | 不確定（尚未查證） | 無 | 網站會封鎖高頻存取 | 不需 | 使用條款**明文禁止未經同意的自動化擷取**，且未經書面同意不得使用/重製網站內容（僅開放平臺授權資料例外）→ **爬蟲有條款風險** | https://www.twse.com.tw/zh/page/terms/use.html |
| FinMind | 50+（官方宣稱 75+）資料集：日價 `TaiwanStockPrice`、PER/PBR、財報、現金流、資產負債表、月營收、股利、除權息、三大法人、融資融券；下市名單 `TaiwanStockDelisting`；另含美股日線 | 價格與財報多年（逐 ticker 深度尚未查證） | `TaiwanStockDelisting` **實測不需 token 即回傳**（名單：日期、代號、名稱） | **財報資料的 `date` 為期末日（如 2024-03-31），無公告日**（實測 `TaiwanStockFinancialStatements`）→ 非 PIT，需用法定申報期限（如 Q1 5/15）保守估計落後；月營收需同法 | README：未註冊 300 次/小時，註冊並驗證信箱帶 token 600 次/小時；超限回 HTTP 402。**還原價 `TaiwanStockPriceAdj` 實測在 free level 回 400「Your level is free. Please update your user level」→ 需付費/贊助** | 免註冊可用但額度低；token 需註冊（不得由我代註冊，使用者自行申請，放 .env） | README 稱「僅供教育與非商業用途、資料僅供參考」。展示衍生統計（IC 等）屬非商業可行；不建議重新散佈原始資料 | https://finmindtrade.com/ ；https://finmind.github.io/ ；https://github.com/FinMind/FinMind |
| TEJ | 台灣上市櫃學術級財金資料庫，官網稱有 PIT 資料庫 | 宣稱 30+ 年 | 官網首頁未提及（尚未查證） | 官網稱 PIT 資料庫還原財報實際發布時點 | 價格、學術方案內容首頁皆未揭露（尚未查證）；一般認知為付費 | 需簽約（未註冊） | 尚未查證 | https://www.tejwin.com/ |
| MOPS 公開資訊觀測站 | 財報、月營收、重大訊息、公告 | 深；財報可依季查 | 部分（可查已終止上市公司的歷史申報，尚未實測） | 有（申報/公告日期在查詢結果中，尚未實測欄位） | 無公布；網站有存取頻率管制 | 不需 | WebFetch 未取得頁面內容（動態頁）→ **自動化擷取條款尚未查證**；上市公司月營收與財報也可由 TWSE OpenAPI `t187ap05_L`、`t187ap06/07_L_*` 取得最新一期 | https://mops.twse.com.tw/ |

## B2. 美股／國際資料來源

| 來源 | 提供內容 | 歷史深度 | 下市股 | PIT | 免費額度／速率 | 註冊／key | 使用條款 | 官方網址 |
|---|---|---|---|---|---|---|---|---|
| SEC EDGAR XBRL API | companyfacts（單一公司全部 XBRL 事實）、frames（單一概念、單一期間跨公司）；`companyfacts.zip` 每日約 03:00 ET 重建的整包 | XBRL 自 2009 年起 | 含已下市公司的歷史申報（僅限 SEC 申報者） | **有**：每筆事實有申報日 `filed` 與表格 `form`，天然 PIT | 官方：10 req/s 上限；須在 header 宣告 User-Agent（格式：公司名稱＋聯絡 email）；不支援 CORS（前端不可直連） | 不需 key、不需註冊 | 公開資料；SEC 不提供技術支援。因 User-Agent 要寫聯絡方式，請用專案專用信箱（勿寫入 repo） | https://www.sec.gov/search-filings/edgar-application-programming-interfaces ；https://www.sec.gov/os/webmaster-faq#developers |
| Ken French Data Library | 美國 FF3/FF5 因子、動能、各式排序投組報酬、產業投組；國際 Developed／Emerging／Asia Pacific ex Japan 等區域因子 | 美國自 1926；國際自約 1990 | 不適用（組合報酬） | 不適用 | 無限制，下載 zip/CSV | 不需 | 頁面僅有版權標示 Copyright Eugene F. Fama and Kenneth R. French，無明確再散佈條款；引用出處即可。**無台灣單一國家因子**（只有區域/新興市場合計） | https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html |
| Open Source Asset Pricing | 212 個 predictor 的月/日組合報酬（免費，Google Drive）；個股層級訊號 CSV（209 項，約 1.6 GB zip） | 多數至 2024-12（2025-10-22 版）；選擇權隱含波動率類到 2022-12 | 個股訊號依 CRSP permno | 以 CRSP 為底的美股，月頻 | 免費下載 | 不需 | 頁面未明載授權條款（尚未查證；使用時引用 Chen & Zimmermann 論文） | https://www.openassetpricing.com/data/ |
| | 個股訊號是否需 CRSP | **個股訊號檔本身可免費下載**，但缺 Price、Size、STreversal 三項，需自行用 CRSP 補；以 permno 為鍵，要對應你自己的價格資料就得有 CRSP 或另備映射 | | | | | | |
| jkpfactors.com | 153 個特徵/因子、13 主題、**93 個國家** | 尚未查證 | 尚未查證 | 尚未查證 | 有 Data Download 區（格式尚未查證） | 尚未查證 | **CC BY-NC 4.0**（非商業、需署名並引用 Jensen-Kelly-Pedersen 2023 JF）；分析程式碼 MIT。**是否涵蓋台灣：頁面未列國家，尚未查證**（若網站收費則 NC 條款禁用） | https://jkpfactors.com/ |
| yfinance／Yahoo | 日價與基本資料（爬 Yahoo 非公開端點） | 數十年（個股差異大） | **無**（下市股通常取不到）→ 存活者偏誤 | 無 | 無明確額度，易被限流 | 不需 | yfinance README：「intended for research and educational purposes」「Yahoo finance API is intended for personal use only」，並要求使用者自行遵守 Yahoo 條款 → **公開網站展示可能違反 Yahoo 條款**；展示衍生統計風險較低但仍屬灰色 | https://github.com/ranaroussi/yfinance |
| Stooq | 日價 CSV（`stooq.com/q/d/l/`） | 尚未查證 | 尚未查證 | 無 | **實測（curl）兩次皆回 JavaScript 驗證頁（proof-of-work），無法腳本化下載** | 尚未查證 | 尚未查證 | https://stooq.com/ |
| Tiingo 免費層 | 日價 30+ 年、基本面 5 年 | 價格 30+ 年 | 頁面未提下市（尚未查證） | 尚未查證 | Starter $0：500 unique symbols/月、50 requests/小時、1,000 requests/日、1 GB/月 | 需註冊（未註冊） | 授權為「Internal Use Only」：僅限自己個人使用，**不可與他人分享或展示**；內部商業用途 $50/月；轉散佈須洽業務 → 不能直接用於公開網站展示原始資料 | https://www.tiingo.com/about/pricing |
| Alpha Vantage 免費層 | 日價、基本面等 | 尚未查證 | 尚未查證 | 無 | 免費 25 requests/日；付費 $49.99–$249.99/月（75–1200 req/min） | 需 key（免費申請，未申請） | 尚未查證 | https://www.alphavantage.co/premium/ |
| Nasdaq Data Link Sharadar（SF1/SEP） | 美股價格＋基本面（含 PIT 欄位） | 尚未查證 | 第三方資料（QuantRocket）稱含 active 與 delisted | 稱有 as-reported／PIT 維度（尚未查證官方頁） | 付費；官方頁需登入才顯示價格，**本次未取得價格**（尚未查證） | 需註冊（未註冊） | 專業用途需另購授權（QuantRocket 說明）；一般條款尚未查證 | https://data.nasdaq.com/databases/SFA ；https://www.quantrocket.com/sharadar/ |

---

## 對規劃的修正建議（針對 05-website-plan.md，未改動原檔）

1. **第 7 節台股資料源：不要把 TWSE/TPEx OpenAPI 當歷史來源。** 實測 `STOCK_DAY_ALL` 只回最新一個交易日，無日期參數。它適合做「每日增量快照」（每日跑排程累積）而非回補歷史。M4 若要歷史價，需要 FinMind（低額度）、TWSE 網站月檔（條款禁自動化，需先評估或取得同意）、或付費 TEJ。建議在 M4 前先決定歷史價怎麼來，並把這一點寫進 charter 決策記錄。
2. **PIT 欄位改寫法：FinMind 財報只有期末日，沒有公告日。** 05 的 PIT 規則（「財報落後至公告日」）需改為「用法定申報期限保守估計落後」（例如 Q1 → 5/15），並在證據標籤標明「PIT 為估計」；MOPS／TEJ 才有真正公告日。FinMind 的 `TaiwanStockPriceAdj` 還原價需付費層，免費版要自己用除權息資料還原（TWSE `TWT48U_ALL`、TPEx `tpex_exright_daily` 只提供預告/當日，歷史除權息需另找或 FinMind `TaiwanStockDividend` 類資料集，尚未驗證）。
3. **FinMind 的非商業限制：** README 稱僅供教育與非商業，且免費額度只有 300/600 次每小時。展示「衍生統計」可以，但網站不要重新散布原始價量；若網站日後商業化或收費，要重審。
4. **FinMind 套件與 pandas 3 衝突：** FinMind 2.1.0 釘 `pandas<3.0.0`。建議 engine 不依賴 FinMind PyPI 套件，改用 `requests` 直接打 REST API（簡單、少依賴、可自己控制重試與額度），或把 ingest 放獨立 venv。
5. **圖表：** 維持 ECharts 為主（Apache-2.0、已 6.x）。lightweight-charts（Apache-2.0＋署名 NOTICE）MVP 不需要；若引入，頁尾加署名與 tradingview.com 連結並保留 `attributionLogo`。plotly.js 不建議（體積大、功能重疊）。echarts-for-react 更新慢，建議自寫 30 行 hook。
6. **版本表更新：** 規劃中隱含的舊版認知需更新：Next.js 16、Tailwind 4（CSS-first 設定）、TanStack Table v9、DuckDB 2.0、Polars 2.x、Vitest 5、ECharts 6。這些主版本都比一般教學新，實作前先讀新版文件，不要照舊教學複製。
7. **回測：維持自寫，並把 vectorbt 列為「不得引入」。** 理由：Apache-2.0＋Commons Clause 禁止販售以其功能為價值主體的服務，且不是標準開源授權；bt（MIT）可作參考。**alphalens-reloaded（Apache-2.0）可作驗算器**，Python 3.13 可裝，但它拉進 IPython、matplotlib、seaborn 等重依賴，放在 dev/驗算用的獨立 extras，不要進線上後端。
8. **美股資料：** 因子報酬驗算基準用 Ken French（免費、無限制）。若要個股層級美股研究，最可行免費路徑是 SEC EDGAR（天然 PIT 財報）＋ 價格另尋（yfinance 有條款疑慮與存活者偏誤；Tiingo 免費層禁止展示；Stooq 無法腳本化）。建議 MVP 美股只做「Open Source Asset Pricing 組合報酬＋Ken French」驗證層，不放個股價格資料，避免條款問題。個股訊號需 CRSP 補三項，且 permno 鍵無法直接對應免費價格 → 不作 MVP 範圍。
9. **jkpfactors 為 CC BY-NC：** 只能作非商業參考（且台灣是否涵蓋尚未查證），不能納入若網站會收費；若使用須在頁面標示 CC BY-NC 4.0 與引用。
10. **示範資料維持為 MVP 主軸**（05 已如此規劃）：免費源沒有一個同時滿足「含下市股＋真 PIT＋可公開展示」，所以 `自行回測` 的台股結果應固定標示「免費資料，含存活者偏誤、PIT 為估計」。真正合格資料需 TEJ（付費，使用前先問使用者）。

## 尚未查證清單
TPEx OpenAPI 各端點的歷史參數與條款細節；TWSE 網站歷史檔的下市股涵蓋；MOPS 自動化擷取條款與欄位；TEJ 價格與學術方案（官網首頁無資訊）；jkpfactors 是否含台灣及下載格式；Open Source Asset Pricing 授權條款；Stooq 條款與替代下載方式；Alpha Vantage 條款與歷史深度；Sharadar 價格與條款；FinMind 逐資料集的歷史深度與付費層分界（僅實測 3 個資料集）；alphalens-reloaded 在 pandas 2.3/3.x 下的實際功能行為；next-themes 在 Next 16 的實測相容性；npm 套件皆未實際安裝建置（只查 registry）。
