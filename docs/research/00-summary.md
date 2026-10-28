# 量化 Alpha 因子研究平台：Step 1～5 研究總報告

> 日期：2026-10-28｜狀態：**等待使用者確認後才開始 Step 6（MVP 開發）**
> 本報告是索引與結論；細節與所有可點擊來源在各分報告中。

| 步驟 | 分報告 | 一句話結論 |
|---|---|---|
| Step 1 GitHub 調查 | [01-github-repos.md](01-github-repos.md) | 22 個 repo 全部以 GitHub API 實查 Stars/License/更新日 |
| Step 2 論文調查 | [02a](02a-papers-momentum-reversal-value-risk.md)、[02b](02b-papers-quality-liquidity-ml-meta.md) | 39 篇，DOI 全部經 Crossref 驗證；其中台灣市場證據 3 篇 |
| Step 3 因子資料庫 | [03-factor-database.md](03-factor-database.md)、[../../factors/factors.yaml](../../factors/factors.yaml) | 真實收錄 36 個（文獻實證 23、尚未驗證 13、自行回測 0），77 項測試全過 |
| Step 4 驗證方法 | [04-validation-methodology.md](04-validation-methodology.md) | 證據標籤＋L0–L4 驗證等級＋DSR/多重檢定＋台股成本模型 |
| Step 5 網站規劃 | [05-website-plan.md](05-website-plan.md)、[05b-tech-stack-verification.md](05b-tech-stack-verification.md) | 離線預算＋靜態網站為 MVP；套件版本與 Python 3.13 相容性已實測 |
| 獨立抽查 | [06-verification-report.md](06-verification-report.md) | 見第 6 節 |

---

## 1. GitHub 調查（Step 1）

收錄 22 個，archived 皆為否。**推薦深入研究的 5 個**：

| 專案 | License | 推薦理由 |
|---|---|---|
| [microsoft/qlib](https://github.com/microsoft/qlib) | MIT | 最完整的因子研究平台；Alpha158/360 以表達式字串定義，運算子設計值得參考 |
| [wukan1986/ta_cn](https://github.com/wukan1986/ta_cn) | MIT | Alpha101 與 Alpha191 完整函式＋WorldQuant 運算子；授權乾淨，可直接參考實作（約 3 年未更新） |
| [stefan-jansen/alphalens-reloaded](https://github.com/stefan-jansen/alphalens-reloaded) | Apache-2.0 | 業界標準因子評估（IC/分組/換手），當本平台引擎的「驗算器」 |
| [OpenSourceAP/CrossSection](https://github.com/OpenSourceAP/CrossSection) | GPL-2.0 | 212 個學術異象的複製，每個訊號都有文件；**只能參考概念與資料，不能複製程式碼** |
| [trevorstephens/gplearn](https://github.com/trevorstephens/gplearn) | BSD-3 | 遺傳規劃/符號迴歸，是之後「自動因子挖掘」的基礎 |

**授權紅線**（只能參考概念，不能複製程式碼）：
- 沒有 License：yli188 Alpha101、popbo/alphas、alphagen、QuantsPlaybook、ReplicationCrisis。
- GPL 或 AGPL，會傳染授權：CrossSection、backtrader、backtesting.py。
- Commons Clause，收費服務受限：vectorbt，已決定不引入。

## 2. 論文調查（Step 2）

共 39 篇。02a 有 18 篇：動能 7、反轉 3、價值 4、波動/風險 4。02b 有 21 篇：品質 6、流動性/成交量 5、ML/挖掘 3、方法論 6、台灣 1。

**台灣市場證據**：
- Chiao, Hung & Yao（2009/2010）：發現台股**不存在** B/M 效果。這說明美股文獻不能直接套用到台股。
- Wang, Huang & Huang（2012）：研究台股的動能與反轉。
- Barber, Lee, Liu & Odean（2009, RFS）：用 TWSE 全體交易紀錄，發現散戶每年落後 3.8 個百分點。

**必須誠實說明的限制**：
- **Elsevier、OUP、SSRN 的全文對自動擷取回 403。** 所以除了 Alpha101 的 8 個公式（從 arXiv 原文逐字抄錄）以外，所有公式都標「標準化定義（依原文文字描述整理）」，沒有一個能宣稱是原文公式。
- 多數論文的樣本期間與 Table 數字只取自摘要或二手轉述，報告中逐項標為「依記憶，待核對」或「摘要」。
- 上線前，必須有人讀全文逐一核對。你若有學校或圖書館的全文權限，這一步會快很多。
- 抽查時發現並修正了 2 個錯誤 DOI（Lehmann 1990；Gervais 等人 2001），所以「所有 DOI 都實查」這條規則確實必要。

## 3. 因子資料庫（Step 3）

**真實收錄 36 個**，沒有拆參數湊數。

| 類別 | 數量 | 代表因子 |
|---|---|---|
| 動能 | 5（含台股月營收 2 個） | MOM_12_1、HIGH_52W、TSMOM_12、REV_YOY、REV_MOM_3_12 |
| 反轉 | 3 | REV_1M、REV_1W、LTREV_60_13 |
| 價值 | 4 | BM、EP、CFP、SALES_GROWTH |
| 品質/獲利 | 8 | GPOA、ROE、ROA、CFOA、OP_PROFIT、ACCRUALS、FSCORE、ASSET_GROWTH |
| 風險 | 5 | VOL_252、IVOL_CAPM、BETA_BAB、DOWNSIDE_BETA、SIZE |
| 流動性/成交量 | 3 | ILLIQ（Amihud）、TURNOVER、ABN_VOLUME |
| Alpha101 | 8 | #2、#3、#4、#6、#9、#12、#41、#101（原文公式） |

- **證據狀態**：`文獻實證` 23 個、`尚未驗證` 13 個、`自行回測` 0 個（還沒回測，不得出現這個標籤）。
- 標 `尚未驗證` 的原因：
  - Alpha101：論文沒有逐個 alpha 的績效。
  - TSMOM：原文是期貨，個股版是改編的。
  - ROA、CFOA：只是複合分數的成分。
  - 台股月營收 2 個：沒有找到學術文獻。
- **與原論文定義不同的變體**已寫在各因子的 `limitations`，網站不得把原論文的數字掛在這些變體上：
  - VOL_252 用日頻，原文是 60 個月月報酬。
  - IVOL 用 CAPM 殘差，原文是 FF3。
  - BETA_BAB 的市場代理用等權平均。
  - ACCRUALS 用現金流量表法，原文是資產負債表法。
  - FSCORE 對全體股票計算，原文只用於高 B/M 股票。
- **不收錄 15 項並附原因**，例如：QMJ 合成分數、Pástor-Stambaugh 流動性 beta、需要產業分類的其餘 Alpha101、台股籌碼因子。
- **自動測試**（`tests/test_factors_smoke.py`，77 passed）檢查以下四項：
  - YAML schema 與 ID 唯一。
  - 每個 paper_id 都存在於論文文件。
  - 程式碼沒有 eval、exec、負 shift。
  - **每個因子都有防前視測試**：竄改最後 20 天的輸入，之前的因子值必須逐位元不變。

## 4. 驗證方法（Step 4）重點

- 四種標籤 `文獻實證`、`自行回測`、`尚未驗證`、`示範資料` 永遠分開顯示。
- `自行回測` 分 L0～L4 五級，只能逐級往上升：
  - L2 需要樣本外確認，且全期 t ≥ 3（Harvey-Liu-Zhu 門檻）。
  - L3 需要扣成本後仍有效，且 Deflated Sharpe ≥ 0.95。試驗次數 N 由平台自動記錄。
- 台股成本：來回約 0.585% 再加滑價（手續費 0.1425% × 2，加證交稅 0.3%）。高換手的反轉與成交量因子要並排顯示扣成本前後的結果。
- 台股多空報酬難以實際交易（放空受限），所以台股預設以「做多頂組 vs 基準」為可交易版本。
- 每個數字都要附出生證明：資料源、股票池、期間、成本、N、程式版本。缺任何一項的數字不能進比較頁。

## 5. 網站規劃（Step 5）重點

- 共 6 頁：儀表板、因子資料庫、因子詳細、比較、回測、論文與 GitHub。各頁元件見 05 第 4 節。
- **架構**：Python 離線算好 IC、分組、衰減，輸出 JSON，Next.js 靜態網站直接讀檔。**沒有任何 API key 也能啟動**，全部顯示示範資料並加浮水印。第二階段才加 FastAPI 做自訂回測。
- **技術**：
  - 前端：Next.js 16、TypeScript、Tailwind 4、shadcn/ui、ECharts 6、TanStack Table 9、KaTeX。
  - 後端：Python 3.13，pandas、statsmodels。
  - 資料：Parquet＋DuckDB，放在 `C:\trading-data\quant-factors\`。
- **公式安全**：用 AST 白名單 DSL 解析，絕不使用 eval。MVP 不開放使用者自訂公式。
- **資料現實**：免費資料源**沒有一個**同時具備「含下市股、真實公告日、可公開展示」三項。
  - 台股真實資料可用 FinMind REST，但條款限非商業使用，而且財報沒有公告日。
  - 美股 MVP 只做 Ken French 與 Open Source Asset Pricing 的組合報酬對照。
  - 學術級資料（TEJ、CRSP）需要付費。

## 6. 獨立抽查結果

一個與作者無關的驗收 agent 用 `shuf` 隨機抽樣，再自行實查。**判定：有條件通過，沒有發現任何虛構內容。**

| 抽查項 | 結果 |
|---|---|
| GitHub Stars、License、更新日（隨機 5 個，重打 API） | 5/5 一致 |
| 論文書目（隨機 8 篇，重打 Crossref） | 8/8 一致 |
| 論文績效數字對原文（Jegadeesh 2.49%/月、McLean-Pontiff 26%/58%、AlphaGen Table 2） | 3/3 一致 |
| Alpha101 公式對 arXiv 原文逐字比對 | 8/8 相同 |
| 經典因子（動能、Amihud、GP、短期反轉、IVOL）：公式與程式是否一致、是否符合學術定義、方向是否正確 | 全部正確 |
| pytest | 77 passed |

抽查提出 2 條必須修正，**都已修好並重跑測試，仍是 77 passed**：
- Alpha101 運算子的出處原本指向不存在的「02b 附錄 A.2」，已改為 arXiv 原文附錄 A.1。
- LTREV 的跳過期原本是 273 日，實際算的是第 14～60 個月。已改為 252 日，對應第 13～60 個月，與 Ken French 定義一致。

另外修了 3 個小錯：REV_1M 公式補上參數 h；AlphaGen 第 7 位作者已核對；P-A07 期號已確認。完整證據見 [06-verification-report.md](06-verification-report.md)。

---

## 7. 需要你確認的事項（確認後開始 Step 6）

1. **MVP 範圍**：照 05 第 9 節的 M1～M3（引擎與測試、6 頁前端、示範資料圖表）。M4 台股真實資料要現在做，還是等 MVP 看過之後再做？
2. **資料預算**：先只用免費資料，接受存活者偏誤與估計的公告日（結果會加警示）？還是之後評估 TEJ 這類付費資料（價格未查到，需要你決定是否詢價）？
3. **部署**：MVP 先只在本機跑？還是要上線（例如 GitHub Pages 或 Vercel 靜態站，免費額度內）？
4. **全文核對**：你有沒有學術資料庫的全文權限？有的話，可以把「標準化定義」升級成「原文公式」，並補上 Table 數字。
5. **36 個因子與 5 個推薦 repo**：要增刪的請告訴我。
