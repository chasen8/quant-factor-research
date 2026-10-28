# Step 5：網站系統規劃

> 第 6、7 節已依 `05b-tech-stack-verification.md`（2026-10-28 實測查證）修正。細節與來源網址見該檔。

---

## 1. 設計原則

1. **研究優先，不是行銷頁**：每個數字都有出生證明（見 04 文件第 8 節）與證據標籤。
2. **離線預算、線上展示**：因子統計（IC、分組、衰減）由 Python 批次預先算好存成檔案；網站讀檔即可。只有「自訂回測」才需要即時計算。好處：沒有行情 API 也能啟動，部署簡單，成本低。
3. **單一真實來源**：因子定義只存在 `factors/*.yaml`（研究文件 03 的機器可讀版），前端、後端、文件都從這裡產生，不在三個地方各寫一份。
4. **可持續擴充**：新增一個因子 = 新增一個 YAML ＋（若需要）一個 Python 函式 ＋ 跑一次批次；不用改前端。

---

## 2. 系統架構與資料流

```
                ┌──────────────── 離線（本機 / 之後可上 GitHub Actions）─────────────────┐
 資料源          │  ingest/            pit_store/               engine/                   │
 TWSE/TPEx  ───▶│  下載＋清洗   ──▶   Parquet（PIT、還原、   ──▶  因子計算（factors/*.py）  │
 FinMind        │  （各源 adapter）    含下市股）                 ↓                        │
 SEC EDGAR      │                     C:\trading-data\         評估（IC/分組/衰減）        │
 示範資料產生器 │                     quant-factors\           回測（向量化截面）          │
                │                     ＋ DuckDB 查詢            ↓                         │
                │                                              results/*.parquet＋json    │
                └──────────────────────────────────────────────────┬───────────────────────┘
                                                                   │
                ┌──────────── 後端 FastAPI ──────────────────────────▼──────────┐
                │ GET /factors, /factors/{id}, /factors/{id}/stats             │
                │ GET /papers, /repos, /compare?ids=...                        │
                │ POST /backtest（參數驗證 → 佇列 → 結果快取，記錄試驗次數）   │
                │ 金鑰只在後端環境變數；前端永不持有                           │
                └──────────────────────────────────┬───────────────────────────┘
                                                   │ JSON
                ┌──────────── 前端 Next.js ─────────▼──────────────────────────┐
                │ 儀表板｜因子資料庫｜因子詳細｜比較｜回測｜論文與 GitHub     │
                └──────────────────────────────────────────────────────────────┘
```

**MVP 簡化**：MVP 階段可不跑後端——批次結果輸出成靜態 JSON，Next.js 直接讀，網站完全靜態；回測頁只開放「預先算好的參數組合」。第二階段再接 FastAPI 做自訂回測。

---

## 3. 資料模型（核心實體）

| 實體 | 主要欄位 |
|---|---|
| `Factor` | id（如 `MOM_12_1`）、名稱（中/英）、類別、子類、LaTeX、變數定義、direction、所需欄位、計算週期、參數（含預設與範圍）、建議市場、別名、相同名稱不同公式的對照、PIT 規則、限制、paper_ids、repo_ids、license 備註、evidence（文獻實證列表）、validation_level（L0–L4，分市場） |
| `Paper` | id、標題、作者、年份、期刊、DOI、免費版網址、市場、樣本期間、驗證方法、原始報告數據（含表格位置）、程式碼可得性、限制 |
| `Repo` | id、名稱、網址、用途、因子數、語言、License、stars（附查詢日）、pushed_at（附查詢日）、整合可行性、限制 |
| `FactorRun` | factor_id、市場、股票池、期間、參數、成本假設、資料源、程式版本、結果檔路徑、建立時間、`is_demo` |
| `TrialLog` | factor_id、參數雜湊、時間——用來計算試驗次數 N 與 DSR |

---

## 4. 頁面規劃

全站共用：頂部導覽（6 頁）＋全域市場切換（台股／美股）＋深淺色切換＋語言（繁中為主，術語保留英文）；所有圖表右上角顯示證據標籤，示範資料加浮水印。

### 頁面 1：量化研究儀表板 `/`
- KPI 列：已收錄因子數｜各驗證等級的因子數（L0–L4 堆疊條）｜論文數｜GitHub 專案數
- 因子類別分布（橫條圖，依類別上色）
- 研究進度：每個因子在台股/美股的驗證等級矩陣（小方格熱圖）
- 績效摘要：Rank IC 均值 Top 10（**只列 `自行回測` 且 ≥ L1 的因子**；示範模式下整區加浮水印）
- 最近新增：論文與 repo 時間線

### 頁面 2：Alpha 因子資料庫 `/factors`
- 表格（TanStack Table）：ID｜名稱｜類別｜市場｜證據標籤｜驗證等級｜Rank IC｜ICIR｜換手｜所需資料
- 左側篩選：類別、市場、證據標籤、驗證等級、資料需求（只要價量 / 需財報）、計算週期
- 關鍵字搜尋（名稱、別名、作者、論文標題；用 Fuse.js 本地模糊搜尋）
- 排序：任一數值欄
- 收藏：☆ 存 localStorage（MVP），之後接帳號
- 勾選 2–5 個 → 「比較」按鈕
- 手機版：表格轉為卡片列表

### 頁面 3：因子詳細 `/factors/[id]`
分頁籤以免單頁過長：
1. **概念**：名稱、一句話直覺、類別、方向、別名與「相同名稱不同公式」的警告
2. **公式**：KaTeX 渲染 LaTeX、變數定義表、PIT 規則（例如「財報落後至公告日」）
3. **程式碼**：Python 實作（語法上色、可複製）＋授權說明
4. **來源**：原始論文卡片（含 `文獻實證` 數據與表格位置）、GitHub 來源（含 License）
5. **分析**（`自行回測` 或示範資料）：
   - 參數面板（形成期、跳過期、分組數、調倉頻率、股票池）→ 只能選預先算好的組合（MVP）
   - 因子歷史值分佈（截面分位數帶狀圖）
   - IC / Rank IC 時間序列＋12 個月滾動均值
   - 分組累積報酬（Q1–Q5）＋多空、純做多 vs 基準
   - 因子衰減圖（h = 1, 5, 10, 20, 60, 120）
   - 績效統計卡（扣成本前/後並排）＋偏誤檢查清單＋試驗次數 N / DSR
6. **限制**：已知研究限制、台股/美股差異提醒

### 頁面 4：因子比較 `/compare?ids=A,B,C`
- 選 2–5 個因子（顏色固定對應因子）
- 指標並排表：Rank IC、ICIR、Sharpe、MDD、換手、扣成本後年化
- 累積報酬疊圖（多空或做多）
- 因子值相關係數矩陣（截面相關的時間平均）＋報酬相關矩陣
- 分期間穩定性：事件期 × 因子的 IC 熱圖（2008、2020、2022…）

### 頁面 5：量化策略回測 `/backtest`
- 表單：市場 → 股票池 → 期間 → 因子（多選）→ 參數 → 權重 → 調倉頻率 → 成本（台股預設已含證交稅）→ 執行
- 結果：策略 vs 基準淨值、回撤曲線、年度報酬柱狀、月度報酬熱力圖、風險指標卡、交易次數與換手
- 每次執行寫入 TrialLog；結果頁顯示「你已對此因子組合試了 N 次」與 DSR
- MVP：只開放預先算好的組合；第二階段開放自訂（FastAPI）

### 頁面 6：論文與 GitHub 研究中心 `/sources`
- 兩個分頁：論文 / GitHub
- 論文卡：標題、作者、年份、期刊、DOI 連結、市場與期間、對應因子（可點）、獨立驗證狀態
- Repo 卡：名稱、用途、License 徽章（GPL 類標橘色警告）、stars 與 pushed_at（附查詢日期）、對應因子
- 反向追溯：每個因子 ↔ 論文 ↔ repo 的關聯圖（簡單的二部圖列表即可）

---

## 5. UI / UX 規格

| 項目 | 規格 |
|---|---|
| 風格 | 現代金融研究平台：中性灰底、單一品牌強調色、數字用等寬數字（tabular-nums） |
| 字體 | 介面 Noto Sans TC；數字/程式碼 JetBrains Mono 或系統等寬 |
| 顏色語意 | **不用紅綠表漲跌的地區慣例衝突**：台股慣例紅漲綠跌、美股相反 → 設定可切換，預設跟隨市場；圖表另用色盲友善配色 |
| 深淺色 | CSS 變數 tokens＋`prefers-color-scheme`＋手動切換，圖表主題同步 |
| 響應式 | ≥1280 三欄（篩選/表格/預覽）；768–1279 兩欄；<768 單欄卡片、圖表可左右滑 |
| 圖表互動 | hover 十字線與數值、時間範圍縮放、圖例點擊隱藏系列、匯出 PNG/CSV |
| 資訊密度 | 表格預設 12 列可見；詳細頁用分頁籤分段 |
| 可及性 | 對比度 AA；圖表顏色之外再加線型/標記區分 |

---

## 6. 技術選型（已查證，2026-10-28）

> 主版本都比網路上常見教學新：**Next.js 16、Tailwind 4（CSS-first 設定）、TanStack Table v9、ECharts 6、DuckDB 2.0、Vitest 5**。實作時以官方新版文件為準，不照舊教學。

| 層 | 選擇 | 理由 | 替代／排除 |
|---|---|---|---|
| 前端框架 | Next.js 16（App Router）＋ TypeScript | 靜態輸出與 SSR 皆可；生態大 | Vite＋React（若完全靜態） |
| 樣式 | Tailwind CSS 4 ＋ shadcn/ui | 原始碼複製進專案、MIT、易客製深淺色 | — |
| 圖表 | Apache ECharts 6（Apache-2.0），**自寫約 30 行 React hook 包裝** | 熱力圖、相關矩陣、大量時序、縮放都內建；echarts-for-react 更新慢，不依賴 | lightweight-charts：MVP 不用（Apache-2.0 但須署名並連結 tradingview.com）；plotly.js：不用（體積大、功能重疊） |
| 表格 | TanStack Table v9 | headless、排序篩選分頁完整 | AG Grid Community |
| 公式 | KaTeX | 快、MIT、可 SSR | MathJax |
| 搜尋 | Fuse.js | 因子數百筆以內本地搜尋足夠 | 後端全文檢索 |
| 後端 | FastAPI ＋ Pydantic | 型別驗證、自動 OpenAPI | — |
| 計算 | pandas、NumPy、SciPy、statsmodels（Newey-West）；Python 3.13 實測全部可裝 | 標準 | Polars（效能瓶頸時） |
| 因子評估 | **自行實作**（約數百行）；alphalens-reloaded（Apache-2.0）只當**驗算器**，放 dev extras | 需要 PIT、台股成本、證據標籤、試驗記錄等客製；alphalens 會拉進 IPython/matplotlib/seaborn，不進線上後端 | qlib 評估模組（MIT）作設計參考 |
| 回測 | 自行實作向量化截面回測；bt（MIT）、quantstats 作參考/指標對照 | 截面選股回測邏輯簡單，自寫可控 | **vectorbt 不得引入**（Apache-2.0＋Commons Clause，禁止以其功能為主體的收費服務）；backtrader（GPL-3.0）、backtesting.py（AGPL-3.0）不引入程式碼 |
| 台股資料存取 | `requests` 直接呼叫 FinMind REST API，**不裝 FinMind PyPI 套件** | FinMind 2.1.0 釘 `pandas<3`；直接打 REST 依賴少、可控重試與額度 | — |
| 資料層 | Parquet（原始與因子矩陣）＋ DuckDB（查詢）；YAML（因子/論文/repo 元資料） | 單機、零維運、快 | PostgreSQL（多人帳號、收藏、試驗記錄上雲時） |
| 測試 | pytest（因子公式對手算樣本）、Vitest＋Playwright（前端煙霧測試） | — | — |

### 安全的因子公式執行（使用者自訂公式時）
- **絕不 `eval`/`exec`**。用 Python `ast.parse(mode="eval")` 解析，走白名單訪問器：
  - 允許節點：`Expression, BinOp, UnaryOp, Compare, Call, Name, Constant`
  - 允許運算子：`+ - * / ** 比較`
  - 允許函式：白名單 DSL（`rank, zscore, delay, delta, ts_mean, ts_std, ts_sum, ts_rank, ts_corr, ts_cov, ts_max, ts_min, log, abs, sign, where` 等，仿 Alpha101 運算子）
  - 允許變數：`open, high, low, close, volume, vwap, returns, mktcap` 及財報欄位白名單
  - 拒絕：屬性存取、下標、lambda、comprehension、任何雙底線名稱
- 參數上限（視窗 ≤ 252、巢狀深度 ≤ 10、節點數 ≤ 200）、單次計算逾時、在獨立 worker 行程執行。
- MVP 不開放自訂公式，只先把 DSL 模組與測試寫好。

---

## 7. 資料來源（已查證，2026-10-28）

**核心結論：沒有任何免費來源同時滿足「含下市股＋真 PIT 公告日＋可公開展示」。** 因此 MVP 以示範資料為主軸；之後用免費台股資料跑出的 `自行回測` 一律加註「免費資料：含存活者偏誤、PIT 為法定期限估計」。學術級資料（TEJ）需付費，使用前先問使用者。

| 市場 | 來源 | 內容 | 查證結果與限制 | MVP 角色 |
|---|---|---|---|---|
| 台股 | FinMind REST | 日行情、財報、月營收、法人 | 未註冊 300 次/時、註冊 600 次/時（token 放 .env）；**財報 `date` 是期末日，沒有公告日**；還原價 `TaiwanStockPriceAdj` 免費層不可用 → 需自行用除權息資料還原；README 稱僅限教育/非商業 → 只展示衍生統計，不重新散布原始價量 | M4 主要歷史源 |
| 台股 | TWSE / TPEx OpenAPI | 當日行情、本益比/殖利率/淨值比 | **無法回補歷史**（`STOCK_DAY_ALL` 只回最新一日）；只適合每日增量快照（若要排程，放 GitHub Actions，不在本機排程） | 輔助（可選） |
| 台股 | MOPS 公開資訊觀測站 | 財報、月營收、公告日 | 自動化擷取條款未查證 | 待評估 |
| 台股 | TEJ | 學術級 PIT、含下市 | **付費**；方案與價格未查到 | 需要時先問使用者 |
| 美股 | Ken French Data Library | 因子組合報酬 | 免費；只有組合，無個股 | 驗算基準 |
| 美股 | Open Source Asset Pricing | 200+ 異象的組合報酬 | 組合報酬可免費下載；個股訊號需 CRSP 補欄位、permno 對不上免費價格；授權條款未查證 | 文獻對照層 |
| 美股 | SEC EDGAR XBRL API | 財報＋申報日（天然 PIT） | 免費、需 User-Agent 與速率限制；價格要另找 | 第二階段 |
| 美股 | yfinance / Tiingo 免費層 / Stooq | 日行情 | yfinance 僅限個人使用且無下市股；Tiingo 免費層禁止展示；Stooq 被 JS 驗證擋住 | **不用於網站** |
| 國際 | jkpfactors.com | 全球因子報酬 | CC BY-NC 4.0（網站若收費即不可用）；是否含台灣未查證 | 非商業參考 |

**MVP 美股範圍**：只做「Ken French ＋ Open Source Asset Pricing 組合報酬」的文獻對照層，不放個股價格，避開條款問題。

---

## 8. 目錄結構（Step 6 預定）

```
量化/
├─ CLAUDE.md, README.md
├─ docs/                     研究文件、章程
├─ factors/                  因子定義 YAML（單一真實來源）＋ papers.yaml ＋ repos.yaml
├─ engine/                   Python 套件
│  ├─ data/                  各資料源 adapter、示範資料產生器、PIT 工具
│  ├─ factors/               因子實作（每類一檔）
│  ├─ dsl/                   安全公式解析器
│  ├─ evaluate/              IC、分組、衰減、統計檢定、DSR
│  ├─ backtest/              向量化回測、成本模型
│  └─ cli.py                 批次：計算 → 評估 → 輸出 JSON
├─ api/                      FastAPI（第二階段）
├─ web/                      Next.js 前端
├─ tests/                    pytest
└─ （資料不在此）→ C:\trading-data\quant-factors\
```

---

## 9. MVP 範圍（Step 6，待確認後執行）

| 里程碑 | 內容 | 驗收 |
|---|---|---|
| M1 資料與引擎 | YAML 載入與驗證；示範資料產生器（標示 demo）；≥10 個價量因子實作；IC/分組/衰減/績效指標；pytest | `pytest` 全綠；因子值對手算樣本一致 |
| M2 前端骨架 | 6 頁路由、深淺色、響應式、因子資料庫表格＋搜尋篩選、KaTeX、論文/repo 頁 | `npm run build` 成功；手機寬度無水平捲動 |
| M3 分析圖表 | 詳細頁全部圖表、比較頁、回測頁（預算組合） | 每張圖都有證據標籤與示範浮水印 |
| M4 真實資料（可選） | 台股免費源 adapter（不需付費 key），跑出第一批 `自行回測` | 偏誤檢查清單自動產生 |

MVP 可在沒有任何 API key 的情況下 `npm run dev` 啟動並看到全部頁面（示範資料）。
