# 量化 Alpha 因子相關 GitHub 開源專案調查

- 查詢日：2026-10-28（Stars、pushed_at、License 均為當日以 `gh api repos/OWNER/REPO` / GitHub API 取得）
- 收錄：22 個（含 1 個已不維護但仍具參考價值者）。所有網址皆已以 HTTP 請求確認可開啟（200）。
- 因子數量／功能欄位：以 README、原始碼目錄、`grep` 函式數實際確認；無法確認者寫「尚未查證」。
- License 欄位：API 的 `spdx_id`；`None` = 該 repo 沒有 LICENSE 檔（預設保留所有權利，不可重用）。
- 說明：Stars 為查詢日數字，不含任何憑記憶填入者。

## 一、總覽表

| # | 專案 | 類別 | 因子數 | 公式明確 | 語言 | 回測 | pushed_at | Stars | License | 整合可行性 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [microsoft/qlib](https://github.com/microsoft/qlib) | 平台（資料/因子/模型/回測） | Alpha158=158、Alpha360=360（handler.py） | 是 | Python | 有 | 2026-10-22 | 49,754 | MIT | 高 |
| 2 | [microsoft/RD-Agent](https://github.com/microsoft/RD-Agent) | LLM 自動因子/模型研發 | 非固定庫（agent 產生） | 由 agent 產生 | Python | 透過 Qlib | 2026-10-21 | 15,098 | MIT | 中 |
| 3 | [stefan-jansen/alphalens-reloaded](https://github.com/stefan-jansen/alphalens-reloaded) | 因子評估 | 不適用 | 不適用 | Python | 僅因子評估（IC/分組/換手） | 2026-10-26 | 678 | Apache-2.0 | 高 |
| 4 | [quantopian/alphalens](https://github.com/quantopian/alphalens) | 因子評估（原版） | 不適用 | 不適用 | Jupyter/Python | 僅因子評估 | 2024-02-12 | 4,480 | Apache-2.0 | 低（被 #3 取代） |
| 5 | [stefan-jansen/zipline-reloaded](https://github.com/stefan-jansen/zipline-reloaded) | 事件驅動回測 | 無 | 無 | Python | 有 | 2026-10-26 | 1,990 | Apache-2.0 | 中 |
| 6 | [stefan-jansen/machine-learning-for-trading](https://github.com/stefan-jansen/machine-learning-for-trading) | 教科書程式碼（ML4T） | 尚未查證 | 部分 | Jupyter | 有（範例） | 2026-10-23 | 21,594 | MIT | 中（參考） |
| 7 | [OpenSourceAP/CrossSection](https://github.com/OpenSourceAP/CrossSection) | 學術複製（Chen-Zimmermann） | 331 列 SignalDoc：212 Predictor、114 Placebo、5 Drop | 是（各 signal 一個 .py） | Python + R | 僅 portfolio 排序 | 2026-10-26 | 1,071 | GPL-2.0 | 低（程式碼）/中（概念與資料） |
| 8 | [bkelly-lab/ReplicationCrisis](https://github.com/bkelly-lab/ReplicationCrisis) | 學術複製（JKP，舊版） | 尚未查證 | 是 | SAS/R | 無 | 2026-05-29 | 378 | None（無授權） | 低 |
| 9 | [bkelly-lab/jkp-data](https://github.com/bkelly-lab/jkp-data) | 學術複製（JKP，現行 Python 版） | 尚未查證（論文為 153 因子，未於 repo 逐項核對） | 是 | Python | 無 | 2026-10-27 | 82 | MIT（資料另有 DATA_LICENSE） | 中 |
| 10 | [polakowo/vectorbt](https://github.com/polakowo/vectorbt) | 向量化回測 | 無 | 無 | Python | 有 | 2026-10-23 | 9,557 | Apache-2.0 + Commons Clause（API 顯示 NOASSERTION） | 低（商用受限） |
| 11 | [kernc/backtesting.py](https://github.com/kernc/backtesting.py) | 回測 | 無 | 無 | Python | 有 | 2026-08-05 | 9,151 | AGPL-3.0 | 低（網路服務傳染） |
| 12 | [pmorissette/bt](https://github.com/pmorissette/bt) | 組合回測 | 無 | 無 | Python | 有 | 2026-10-25 | 3,010 | MIT | 中高 |
| 13 | [mementum/backtrader](https://github.com/mementum/backtrader) | 事件驅動回測 | 無 | 無 | Python | 有 | 2024-08-19 | 23,594 | GPL-3.0 | 低 |
| 14 | [ranaroussi/quantstats](https://github.com/ranaroussi/quantstats) | 績效報告 | 無 | 無 | Python | 僅績效分析（tear sheet） | 2026-09-27 | 7,757 | Apache-2.0 | 高 |
| 15 | [ICT-FinD-Lab/alphagen](https://github.com/ICT-FinD-Lab/alphagen)（原 RL-MLDM/alphagen，已轉址） | RL / LLM 因子挖掘 | 動態產生 | 是（表達式樹） | Python | 以 IC 評估 | 2026-06-04 | 1,283 | None（無授權） | 低 |
| 16 | [hugo2046/QuantsPlaybook](https://github.com/hugo2046/QuantsPlaybook) | 券商研報因子複現 | 多（B-因子构建类下約 24 個子專案，已列約 24 個資料夾名） | 是（notebook） | Jupyter | 部分 | 2026-10-03 | 6,755 | None（無授權） | 低（只能參考概念） |
| 17 | [FinMind/FinMind](https://github.com/FinMind/FinMind) | 台股資料 API / SDK | 無（資料集） | 無 | Python（GitHub 顯示 HTML） | 無 | 2026-10-24 | 2,858 | Apache-2.0 | 高（外部依賴） |
| 18 | [trevorstephens/gplearn](https://github.com/trevorstephens/gplearn) | 遺傳規劃（符號回歸） | 動態產生 | 是 | Python | 無 | 2026-08-14 | 1,894 | BSD-3-Clause | 高 |
| 19 | [yli188/WorldQuant_alpha101_code](https://github.com/yli188/WorldQuant_alpha101_code) | Alpha101 實作 | `101Alpha_code_1.py` 內 83 個 `def alpha`；`_2.py` 為 0 個（實作不完整） | 是 | Python (pandas) | 無 | 2019-03-07 | 880 | None（無授權） | 低（只能參考） |
| 20 | [popbo/alphas](https://github.com/popbo/alphas) | Alpha101 + Alpha191（A 股） | alphas101.py 83、alphas191.py 191 | 是 | Python/Jupyter | 有（backtrader notebook + alphalens） | 2023-04-14 | 598 | None（無授權） | 低 |
| 21 | [wukan1986/ta_cn](https://github.com/wukan1986/ta_cn) | WorldQuant 算子 + Alpha101/191 | alpha101.py 101、alpha191.py 191（`def alpha_` 計數） | 是 | Python (numpy/numba) | 無（有 performance.py 績效函式） | 2023-12-27 | 196 | MIT | 高 |
| 22 | [Menooker/KunQuant](https://github.com/Menooker/KunQuant) | 因子表達式編譯器 | Alpha101.py 82 個函式 + Alpha158.py | 是 | Python + C++ | 無 | 2026-10-09 | 326 | Apache-2.0 | 中高 |

archived 狀態：以上 22 個 `archived` 全部為 False，但 #8 README 開頭明寫「THIS REPO IS NO LONGER MAINTAINED」，已移轉至 #9。#4 最後 push 為 2024-02，實質停止維護。#19、#20 長期無更新。

## 二、各專案細節

### 1. microsoft/qlib
- 用途：AI 導向量化投資平台，含資料層、因子 handler、模型 zoo、回測與分析。
- 因子：`qlib/contrib/data/handler.py` 定義 `Alpha158`（158 個特徵）與 `Alpha360`（360 個原始價量特徵）及 vwap 變體。公式以表達式字串明確定義。
- 回測：有（qlib.backtest、strategy、executor）。
- 學術依據：Qlib: An AI-oriented Quantitative Investment Platform（arXiv 2009.11189，來自論文引用，未於本次逐頁開啟）。
- 限制：資料需自備或自建 provider（官方 cn_data 為中國 A 股）。台股/美股需自行轉成 Qlib bin 格式（本次未查證是否有現成台股 provider）。框架重，直接嵌入網站成本高，適合當離線因子計算引擎或參考運算子設計。

### 2. microsoft/RD-Agent
- 用途：LLM 驅動的研發自動化；含 R&D-Agent-Quant（因子與模型協同優化），README 有 factor loop demo 與 NeurIPS 2025 論文連結。
- 因子數：非固定庫。回測：透過 Qlib。
- 學術依據：R&D-Agent-Quant（arXiv 2505.15155，README 列出，NeurIPS 2025）。
- 限制：依賴 LLM API（花錢）、依賴 Qlib 與 Docker，運行成本與複雜度高。

### 3. stefan-jansen/alphalens-reloaded
- 用途：預測性（alpha）因子績效分析；README 列出 Returns / Information Coefficient / Turnover / Grouped Analysis。
- 僅因子評估，無回測。維護中（2026-10-26），README 聲明持續修 bug、安全與相容性。
- 限制：圖表為 matplotlib，需自行轉成網頁（可只取統計函式 `performance`/`utils`，圖表自畫）。

### 4. quantopian/alphalens
- 原版，Apache-2.0，最後 push 2024-02-12，與 #3 同源。新專案請用 #3。

### 5. stefan-jansen/zipline-reloaded
- 用途：Quantopian Zipline 的維護分支，事件驅動回測，與 alphalens/pyfolio 搭配。維護活躍。
- 限制：資料需 bundle 化，API 偏舊，對「截面因子分組回測」不如自寫向量化簡單。

### 6. stefan-jansen/machine-learning-for-trading
- 用途：ML for Trading 書籍程式碼。目前 repo 目錄含 `04_fundamental_alternative_data`、`05_synthetic_data`、`24_autonomous_agents` 等；舊版 alpha factor 章節是否仍在本次未逐檔確認，故因子數寫「尚未查證」。
- MIT，適合參考流程（IC、特徵工程、ML 模型）。

### 7. OpenSourceAP/CrossSection
- 用途：Chen & Zimmermann 複製 200+ 學術 cross-sectional predictors，另提供 data page（openassetpricing.com）。
- 因子：`SignalDoc.csv` 實測 331 列：Predictor 212、Placebo 114、Drop 5。`Signals/pyCode/Predictors/` 每個因子一個 .py，公式明確；Portfolios 為 R；整體約 15,000 行。
- 學術依據：Chen & Zimmermann, "Open Source Cross-Sectional Asset Pricing", Critical Finance Review 2022。
- 限制：License GPL-2.0（複製程式碼會傳染）；原始資料靠 WRDS（CRSP/Compustat 付費訂閱），是美股資料，不含台股。可用其預先算好的下載資料與 SignalDoc.csv 文件當因子目錄，但資料的再散布條件需再看 data page（尚未查證）。

### 8. bkelly-lab/ReplicationCrisis
- Jensen-Kelly-Pedersen（2023）程式碼舊版（SAS/R），README 明寫不再維護，請改用 #9。根目錄無 LICENSE（API 回 None）。僅作文獻參照。
- 學術依據：Is There a Replication Crisis in Finance?, Journal of Finance 78(5), 2023。

### 9. bkelly-lab/jkp-data
- 用途：上述 JKP 全球因子資料集的 Python 現行版（含 WRDS 全球股票，涵蓋多國市場）。MIT（程式碼），另有 DATA_LICENSE。
- 限制：需 WRDS 訂閱；沒有 WRDS 時可下載預算好的因子組合（jkpfactors.com）。是否涵蓋台灣：本次未逐國核對，尚未查證。

### 10. polakowo/vectorbt
- 向量化回測與分析，numba 加速。License 檔為 Apache 2.0 + Commons Clause（禁止 Sell：以其功能為主要價值的付費產品/服務含託管）。
- 若網站未來收費，風險高；免費且非 MIT 傳染可作外部依賴。維護活躍。

### 11. kernc/backtesting.py
- AGPL-3.0：若作為網路服務提供使用者互動，須釋出整份對應原始碼。除非整站可 AGPL，否則避免。

### 12. pmorissette/bt
- MIT，組合層級回測（可做 rebalance 權重策略），pandas 友善，維護活躍。可作為分組/多空回測參考或依賴。

### 13. mementum/backtrader
- GPL-3.0，最後 push 2024-08-19，事實上停更。不建議。

### 14. ranaroussi/quantstats
- Apache-2.0，產生 Sharpe、drawdown 等 tear sheet 與 HTML 報告。僅績效分析，不含回測。適合當績效指標計算依賴，或參考指標定義後自寫。

### 15. ICT-FinD-Lab/alphagen（原 RL-MLDM/alphagen）
- 用途：以強化學習產生協同公式化 alpha，附 gplearn / dso baseline 與 `alphagen_llm`（LLM 輔助）。
- 學術依據：Generating Synergistic Formulaic Alpha Collections via Reinforcement Learning（KDD 2023 ADS）。
- 限制：無 LICENSE；資料用 baostock 中國 A 股並依賴 Qlib metadata；內含修改版 gplearn / dso。

### 16. hugo2046/QuantsPlaybook
- 用途：複現券商研報的因子/擇時/組合策略（如 APM、聰明錢、籌碼、振幅因子等），多為 Jupyter notebook。
- 無 LICENSE；使用中國 A 股資料；僅能當概念與研報清單參考。

### 17. FinMind/FinMind
- 用途：台股及國際市場開源資料（股價、基本面、三大法人、月營收等，README 列示），Python SDK。Apache-2.0，維護活躍。
- 限制：資料來自其 API 服務（有 token 與流量限制，具體額度尚未查證），應視為外部資料依賴並做快取。是台股資料的優先候選。

### 18. trevorstephens/gplearn
- sklearn 風格遺傳規劃，常被用於公式化因子挖掘（自訂 function set / fitness）。BSD-3-Clause，最後 push 2026-08-14。
- 學術依據：Koza 的 Genetic Programming（原理）；alphagen 論文亦以其為 baseline。
- 限制：原生 fitness 為單一序列回歸，做截面 IC 需自訂 fitness；對面板資料需額外封裝。

### 19. yli188/WorldQuant_alpha101_code
- Kakushadze 論文 PDF + pandas 實作，被 KunQuant 作為 benchmark 對照。`101Alpha_code_1.py` 計得 83 個 `def alpha`，並非完整 101 個；無 LICENSE，2019 後無更新。
- 學術依據：101 Formulaic Alphas（Kakushadze, 2016, arXiv 1601.00991）。

### 20. popbo/alphas
- 同時含 Alpha101（83）與 Alpha191（191）計算類，並有 alphalens 分析與 backtrader 回測 notebook、下載資料腳本。無 LICENSE，資料為 A 股。191 因子來源：國泰君安《基於短週期價量特徵的多因子選股體系》研報。

### 21. wukan1986/ta_cn
- MIT。`ta_cn/wq/` 實作 WorldQuant 風格算子（time_series、cross_sectional、group、arithmetic…），`ta_cn/alphas/alpha101.py` 計得 101 個 `def alpha_`，`alpha191.py` 計得 191 個。numpy/numba 加速。
- 限制：2023-12 後未更新（作者另建 polars_ta，本次未查證）；中國版技術指標偏 A 股慣例；實際正確性需自行對照論文公式抽測。

### 22. Menooker/KunQuant
- Apache-2.0。將因子表達式編譯為最佳化 C++，`KunQuant/predefined/` 有 Alpha101.py（計得 82 個函式）與 Alpha158.py；README 稱對 pandas 版有最高 170x 加速（廠商自述）。
- 限制：需編譯器與 C++ 執行階段，部署較複雜；僅計算不含評估。

## 三、推薦最值得深入研究的 5 個

1. **microsoft/qlib（MIT）**：Alpha158/360 公式明確、表達式運算子（Ref/Mean/Corr 等）可直接借鏡設計 DSL；內含因子到模型到回測完整鏈，維護極活躍（2026-10-22）。缺點是台股資料要自建 provider，但這只是一次性 ETL 工作。
2. **wukan1986/ta_cn（MIT）**：目前查到唯一同時有 Alpha101（101）與 Alpha191（191）、授權為 MIT 的 Python 實作，且有 WorldQuant 風格算子層，可直接當因子公式庫。需自行抽測驗證正確性，且作者近兩年未更新。
3. **stefan-jansen/alphalens-reloaded（Apache-2.0）**：IC、分組報酬、換手率等因子評估的事實標準，仍在維護。可直接當評估引擎或只移植統計邏輯。
4. **OpenSourceAP/CrossSection（GPL-2.0；搭配 bkelly-lab/jkp-data MIT）**：學術嚴謹度最高，212 個有論文出處的 predictor，SignalDoc.csv 可直接做因子目錄與文獻索引。GPL 與 WRDS 資料限制使其只能當參考與目錄，不能複製程式碼。
5. **trevorstephens/gplearn（BSD-3）**：授權寬鬆、成熟穩定，是遺傳規劃因子挖掘的基底；alphagen 論文即以之為 baseline。搭配 ta_cn 運算子與自訂 IC fitness 可做 MVP 後期的因子挖掘功能。

候補：FinMind（台股資料入口，非因子庫，建議同時採用）、RD-Agent（LLM 因子挖掘前沿，但成本高）、KunQuant（效能需求出現時再看）。

## 四、授權相容性總結（假設網站以 MIT 釋出）

| 類別 | 專案 | 說明 |
|---|---|---|
| 可直接引用程式碼（保留版權聲明） | qlib (MIT)、ta_cn (MIT)、bt (MIT)、ML4T (MIT)、jkp-data (MIT，資料另受 DATA_LICENSE)、gplearn (BSD-3)、alphalens-reloaded / alphalens / zipline-reloaded / quantstats / FinMind / KunQuant (Apache-2.0，需保留 NOTICE 與授權) | Apache-2.0 與 MIT 可相容；BSD-3 需保留聲明且不得用作者名背書 |
| 只能參考概念，不可複製程式碼 | OpenSourceAP/CrossSection (GPL-2.0)、backtrader (GPL-3.0)、yli188 / popbo / alphagen / QuantsPlaybook / ReplicationCrisis（皆無 LICENSE，預設不可重用） | 公式本身（如 Kakushadze 論文、研報）是公開知識，可依論文自行重寫實作 |
| 只能當外部依賴（不併入原始碼，不改寫散布） | vectorbt（Commons Clause，收費服務有風險）、backtesting.py（AGPL，網路服務需開源整站） | 若改為付費產品則 vectorbt 不能用 |

注意：「無 LICENSE」的專案風險最高；若需引用必須先聯絡作者取得授權。公式本身多來自論文，應以論文為依據自行實作。

## 五、對 MVP 的整合建議

- **因子評估引擎**：自行實作薄層（IC、RankIC、分位數分組報酬、換手率），參考並可移植 alphalens-reloaded（Apache-2.0）的邏輯；一句話理由：統計定義簡單、授權乾淨，圖表本就要用前端函式庫重畫，不需綁定 matplotlib。
- **回測引擎**：自行實作向量化的截面分組/多空回測，績效指標可依賴 quantstats（Apache-2.0）或參考 bt（MIT）；一句話理由：因子站只需 rebalance 型回測，自寫最輕，且避開 vectorbt 的 Commons Clause 與 backtesting.py 的 AGPL。
- **因子公式來源**：以 ta_cn（MIT）的 Alpha101/191 與 WorldQuant 算子為底，再借鏡 qlib Alpha158 的表達式設計，並用 CrossSection 的 SignalDoc.csv 做學術因子目錄與文獻對照；一句話理由：三者授權可相容或僅作參考，且涵蓋量價、技術與學術基本面三類因子。
- **台股資料**：FinMind 作外部資料來源並本地快取；美股資料來源本次未調查，須另行決定。
- **因子挖掘（非 MVP）**：後期用 gplearn（可選 RD-Agent）。

## 六、不確定與尚未查證之處

- qlib、alphalens-reloaded 等的論文標題引自 README/記憶中的一般常識，未逐頁開啟 arXiv（arXiv 2009.11189 未確認）。
- ML4T、jkp-data、RD-Agent 的因子數；FinMind 的免費額度；CrossSection 預算資料的再散布授權；jkp-data 是否涵蓋台灣：均尚未查證。
- ta_cn / KunQuant 的公式與論文逐式比對正確性未驗證，僅以函式數計得。
- GitHub API 搜尋期間曾被限流，後改用已登入的 gh CLI，搜尋範圍以 alpha101、alpha191、alpha factor mining、factor investing、alphalens、multi-factor 關鍵字為主；"taiwan stock factor" 與 "alpha158" 的搜尋因限流未取得結果，台股專屬因子專案可能有遺漏。
