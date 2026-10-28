# 06 驗收報告：GitHub / 論文 / 因子資料庫抽查

- 驗收日：2026-10-28；驗收者獨立於產出作者，未修改任何被審檔案。
- 被審：`01-github-repos.md`、`02a-papers-momentum-reversal-value-risk.md`、`02b-papers-quality-liquidity-ml-meta.md`、`factors/factors.yaml`、`03-factor-database.md`。
- 抽樣方式：Git Bash `shuf`（系統亂數，種子 `date +%s%N` = 1793124408333127700 時段）從編號序列隨機抽，不依熟悉度挑選；抽樣指令與結果見各節。

## 總判定：有條件通過

7 個抽查項目全部 PASS，沒有發現虛構的 repo、DOI、Stars、License 或公式。另有 2 處「必須修正」（一處來源指標錯誤、一處參數與宣稱定義不一致），以及數條「建議修正」，詳見文末。

---

## 1. GitHub repo 抽查：PASS（5/5）

抽樣：`seq 1 22 | shuf -n 5` 的結果為 #2、#4、#18、#20、#22。查詢方式：`curl -s https://api.github.com/repos/OWNER/REPO`。

| # | repo | 報告 Stars / License / pushed_at（01:行） | API 回傳 | 判定 |
|---|---|---|---|---|
| 2 | microsoft/RD-Agent | 15,098 / MIT / 2026-10-21（01:14） | 15099 / MIT / 2026-10-21T16:01:22Z / archived False | PASS（+0.007%） |
| 4 | quantopian/alphalens | 4,480 / Apache-2.0 / 2024-02-12（01:16） | 4480 / Apache-2.0 / 2024-02-12T06:44:22Z | PASS |
| 18 | trevorstephens/gplearn | 1,894 / BSD-3-Clause / 2026-08-14（01:30） | 1894 / BSD-3-Clause / 2026-08-14T23:44:19Z | PASS |
| 20 | popbo/alphas | 598 / None / 2023-04-14（01:32） | 598 / license=null / 2023-04-14T13:26:33Z | PASS |
| 22 | Menooker/KunQuant | 326 / Apache-2.0 / 2026-10-09（01:34） | 326 / Apache-2.0 / 2026-10-09T14:24:22Z | PASS |

5 個 repo 都存在，archived 都是 False，與 01:36 的敘述一致。

## 2. 論文書目抽查（Crossref）：PASS（8/8）

抽樣：02a 依總覽表列序 `seq 1 18 | shuf -n 4` 得 7、14、15、16，對應 P-A07、P-C04、P-E01、P-E02。02b 依總覽表列序 `seq 1 21 | shuf -n 4` 得 8、10、13、16，對應 P-B08、P-B10、P-B13、P-B16。查詢方式：`curl -s "https://api.crossref.org/works/<DOI>"`。

| 檔:編號 | DOI | Crossref 標題 / 第一作者 / 年 / 期刊 卷(期) 頁 | 判定 |
|---|---|---|---|
| 02a:P-A07 | 10.2753/REE1540-496X4801S103 | Momentum and Contrarian Profits Corresponding to the Coincident Economic Indicator on the Taiwan Stock Market / Ching-Ping Wang / 2012-01 / Emerging Markets Finance and Trade 48(sup1) 29-40 | PASS（報告寫「sup1?」並表示期號未確認，但 Crossref 的 issue 欄位就是 sup1，可以去掉問號） |
| 02a:P-C04 | 10.1111/j.1468-5876.2009.00485.x | THE ABSENCE OF THE BOOK-TO-MARKET EFFECT IN THE TAIWAN STOCK MARKET… / Chaoshin Chiao / 2009-04-08 / Japanese Economic Review 61(2) 289-299 | PASS |
| 02a:P-E01 | 10.1111/j.1540-6261.2006.00836.x | The Cross-Section of Volatility and Expected Returns / Andrew Ang / 2006-01-20 / JF 61(1) 259-299 | PASS |
| 02a:P-E02 | 10.1016/j.jfineco.2013.10.005 | Betting against beta / Andrea Frazzini / 2014-01 / JFE 111(1) 1-25 | PASS |
| 02b:P-B08 | 10.1016/S1386-4181(97)00004-9 | Liquidity and stock returns: An alternative test / Vinay T. Datar / 1998-08 / JFM 1(2) 203-219 | PASS |
| 02b:P-B10 | 10.1111/0022-1082.00349 | The High-Volume Return Premium / Simon Gervais / 2001-06 / JF 56(3) 877-919 | PASS |
| 02b:P-B13 | 10.1093/rfs/hhaa009 | Empirical Asset Pricing via Machine Learning / Shihao Gu / 2020-02-26 / RFS 33(5) 2223-2273 | PASS |
| 02b:P-B16 | 10.1111/jofi.12365 | Does Academic Research Destroy Stock Return Predictability? / R. David McLean / 2016-01-14 / JF 71(1) 5-32 | PASS |

額外核對了 02b:P-B14 AlphaGen（DOI 10.1145/3580305.3599831）。Crossref 有完整的 7 位作者，第 7 位是 Qing He；PDF 首頁的作者也是 Qing He。02b:303 寫「Crossref 前六位…第 7 位按記憶」，與事實不符。內容本身沒錯，只是說明錯了，列為建議修正。

## 3. 論文報告的績效數字：PASS（3/3 可核對且一致）

挑選原則：避開本身標「尚未查證」的欄位，挑報告宣稱為原文或摘要數字的項目，並涵蓋 02a 與 02b。

| 出處 | 報告數字 | 核對來源與原文片段 | 判定 |
|---|---|---|---|
| 02a:184（P-B01 Jegadeesh 1990） | 極端十分位異常報酬差每月 2.49%，期間 1934-1987 | Crossref 摘要：「The difference between the abnormal returns on the extreme decile portfolios over the period 1934–1987 is 2.49 percent per month.」 | PASS，來源層級標為「摘要」，正確 |
| 02b:353（P-B16 McLean & Pontiff 2016） | 樣本外低 26%、發表後低 58%、發表帶來 32% | Crossref 摘要：「Portfolio returns are 26% lower out-of-sample and 58% lower post-publication… We estimate a 32% (58%–26%) lower return from publication-informed trading.」 | PASS，標為「Crossref 摘要」，正確 |
| 02b:314（P-B14 AlphaGen Table 2） | CSI300 Ours IC 0.0725 / Rank IC 0.0806；XGBoost 0.0404/0.0576；LightGBM 0.0259/0.0324；CSI500 Ours 0.0438/0.0727；XGBoost 0.0353/0.0639 | arXiv 2306.12964 PDF 抽文字的 Table 2：「XGBoost 0.0404 0.0576 0.0353 0.0639」「LightGBM 0.0259 0.0324 0.0332 0.0609」「Ours* 0.0725 0.0806 0.0438 0.0727」 | PASS，標為「Table 2，逐字抄自 PDF」，正確。資料切分 2009/01/01–2018/12/31、2019、2020/01/01–2021/12/31（02b:307）也與 PDF §4.1.1 一致 |

來源層級標註評估：兩份報告都把「摘要」「搜尋轉述」「記憶，待核對」「尚未查證」分開標示，抽查到的數字都在宣稱的層級上成立。02a:85 Kim-Tse-Wald 的 1.27%→0.41%、02a:337 的 6%/6.55% 已自行標成二手轉述，網站上線時不得去掉這些標註。

## 4. Alpha101 公式逐字比對：PASS（3/3，另外 5 個也一致）

抽樣：`shuf -n 3` 從 {002,003,004,006,009,012,041,101} 中抽出 002、003、006。原文取自 `curl https://arxiv.org/pdf/1601.00991`，用 pypdf 抽文字。

| 因子 | factors.yaml `formula_original` | arXiv 原文（A.1 Formulaic Expressions） | python 實作 | 判定 |
|---|---|---|---|---|
| ALPHA101_002（yaml:1804） | `(-1 * correlation(rank(delta(log(volume), 2)), rank(((close - open) / open)), 6))` | `Alpha#2: (-1 * correlation(rank(delta(log(volume), 2)), rank(((close - open) / open)), 6))` | yaml:1883 `-1 * _corr(_rank(_delta(lv, 2)), _rank((close - open_) / open_), 6)` | PASS，參數 2、6 一致 |
| ALPHA101_003（yaml:1893） | `(-1 * correlation(rank(open), rank(volume), 10))` | `Alpha#3: (-1 * correlation(rank(open), rank(volume), 10))` | yaml:1947 | PASS |
| ALPHA101_006（yaml:2017） | `(-1 * correlation(open, volume, 10))` | `Alpha#6: (-1 * correlation(open, volume, 10))` | yaml:2071 | PASS |

另外也比對了 004、009、012、041、101 的 `formula_original`（yaml:1957/2081/2145/2209/2277），全部與原文逐字一致。02b:270 引的 Alpha#101 與 Alpha#6 也一致。運算子語意與原文 A.1 Functions and Operators 相符：rank 為截面排名，correlation 為過去 d 日時序相關，delta 為今天減 d 日前。

## 5. 經典因子實作正確性：PASS（5/5）

數值驗證用合成資料（5 檔、400 個交易日，seed=0），把 yaml 的 python 直接 exec 後，與手算或 numpy OLS 比較，腳本在 scratchpad 的 numcheck.py。

| 因子（yaml 行） | (a) 公式與 python 一致 | (b) 與學術定義一致 | (c) direction |
|---|---|---|---|
| MOM_12_1（17, 30, 94-96） | `P_{t-21}/P_{t-252}-1` ↔ `close.shift(21)/close.shift(252)-1`；數值相同（-0.36304…） | 有跳過最近 1 個月，形成期 12 個月，等同 Ken French 2-12 | +1，正確 |
| ILLIQ（1603, 1615, 1658-1662） | `10^6/D·Σ|R|/VOLD` ↔ `(|pct_change|/turnover_value*1e6).rolling(D).mean()`；數值相同（0.0042515…） | 是 Amihud 的平均 |r|/成交金額 | +1，正確 |
| GPOA（698, 707, 750-752） | `(REVT-COGS)/AT` ↔ `gross_profit/total_assets`，743 行定義 gross_profit = revenue − cogs（TTM） | 與 Novy-Marx GP/A 一致；用 TTM 而非年報、期末資產，已在 742 行自行揭露 | +1，正確 |
| REV_1M（240, 249, 291-293） | `P_t/P_{t-21}-1` ↔ `close/close.shift(21)-1`；數值相同 | 值為上月報酬 | −1，正確 |
| IVOL_CAPM（1323, 1335, 1376-1383） | 殘差變異 = var_i − cov²/var_m；與 numpy OLS 殘差 std(ddof=1) 相同（0.0159413） | 原文是 FF3 殘差，本庫用單因子（等權市場），已在 1368 行標為變體 | −1，正確 |

小瑕疵（不影響判定）：REV_1M 的 variables 列了符號 h（yaml:245），但公式寫死 21，沒有用到 h。IVOL 的殘差變異用 n−1 自由度，OLS 慣例是 n−2，21 日窗下差約 2.6%，對截面排序沒有影響。

## 6. 36 個因子 direction / category 快速掃描：PASS（方向無錯，1 處定義偏差）

逐一檢查 36 個因子的 formula、python 與 direction。分類計數：quality 8、composite_ml 8、momentum 5、risk 5、value 4、reversal 3、liquidity 3。

- 方向全部合理：BM/EP/CFP +1、SALES_GROWTH −1（LSV 成長股）、ROE/ROA/CFOA/OP/FSCORE +1、ACCRUALS −1、ASSET_GROWTH −1、VOL/IVOL/BETA_BAB −1、DOWNSIDE_BETA +1（Ang-Chen-Xing 正溢酬）、SIZE −1、ILLIQ +1、TURNOVER −1（Datar et al. 負相關）、ABN_VOLUME +1（Gervais et al.）、REV_1W/REV_1M/LTREV −1、MOM/HIGH_52W/TSMOM/REV_YOY/REV_MOM_3_12 +1、Alpha101 +1（依原文符號，03:166 有規則說明）。**沒有發現方向錯誤。**
- **LTREV_60_13 定義偏差（必須修正）**：yaml:361、380 用 skip=273（13×21）、form=1260，但 410 行的 limitations 宣稱採用 Ken French「13-60 個月」。依同一份 yaml 中 MOM_12_1 的慣例（skip 21 + form 252 = 第 2-12 個月），第 13-60 個月應為 skip=252、form=1260。現行 273 實際算的是第 14-60 個月（47 個月）。方向不受影響。
- category 疑慮（建議修正）：SIZE 歸在 `risk`（yaml:1545），文獻與 03 文件慣例多半另立 size 或歸 value；ASSET_GROWTH 歸 `quality`，subcategory 是 investment。這兩項不算錯，但前端篩選時可能讓人困惑。
- HIGH_52W（yaml:105）用 P_t / 含當日的 252 日最高價，02a:95 寫的是 P_{t-1} / 過去 12 個月最高價。屬變體，yaml 沒有註明，建議補一句。
- DOWNSIDE_BETA 用滾動均值逐日判斷下跌日，與原文的全期 μ_m 不同；yaml limitations 已揭露。

## 7. pytest：PASS

指令：`C:\trading-data\quant-factors\venv\Scripts\python.exe -m pytest tests -q`，在 `C:\Users\chris\OneDrive\桌面\量化` 目錄下執行，輸出末 3 行：

```
........................................................................ [ 93%]
.....                                                                    [100%]
77 passed in 10.68s
```

## 附加一致性檢查

- factors.yaml 的 `paper_ids` 與 `known_results.source` 全部能對應到 02a（18 篇）、02b（21 篇）的實際章節，沒有懸空引用。
- 36 個 factor id 全部出現在 03-factor-database.md。
- 證據標籤只有「文獻實證」23 個、「尚未驗證」13 個兩種，符合 yaml 檔頭規則。

---

## 必須修正

1. **Alpha101 的來源指標錯誤**：yaml:1855、1921、1981、2045、2105、2173、2241、2313 的 `same_name_different_formula` 寫「本庫以 02b 附錄 A.2 的定義為準」，但 02b 沒有附錄 A.2（02b 只有 §0-§3）。運算子定義實際在 arXiv:1601.00991 的 A.1 Functions and Operators（03:194 寫得正確）。在不可虛構出處的鐵律下，這是錯誤的引用位置，應改為「arXiv:1601.00991 A.1 Functions and Operators（見 03 文件）」。
2. **LTREV_60_13 的 skip_days 與宣稱定義不一致**：yaml:361、380、420 的 273 應改為 252，才是 Ken French 的第 13-60 個月，與 MOM_12_1 的時間慣例一致。另一種做法是保留 273，但把 limitations 與名稱改成「第 14-60 個月」。

## 建議修正

1. 02b:303 AlphaGen 作者註記改為「Crossref 有 7 位作者，第 7 位 Qing He 已驗證」。
2. 02a:27、160 的 P-A07「sup1?／期號未確認」改為 Crossref 回傳的 48(sup1)。
3. HIGH_52W 在 limitations 補上「用 P_t 含當日，與 George-Hwang 的 P_{t-1} 不同」。REV_1M 刪掉沒用到的變數 h，或把公式改寫成用 h。
4. SIZE 與 ASSET_GROWTH 的 category 可重新考慮（例如獨立 size / investment），或在 03 文件說明分類理由。
5. 所有「依記憶，待核對」的樣本期間與設定細節，網站上線前要保留標示，或補全文核對後再升級；目前只有 AlphaGen 一篇有讀過全文。
