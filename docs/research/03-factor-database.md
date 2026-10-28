# 03 因子資料庫（Factor Database）說明

建立日期：2026-10-28。機器可讀來源：`factors/factors.yaml`（`schema_version: 1`，**單一真實來源**；本文件是它的人讀版）。
所有來源都取自本專案已完成的研究：`01-github-repos.md`、`02a-papers-...md`、`02b-papers-...md`、`04-validation-methodology.md`。沒有另起爐灶，也沒有引入未經本專案核對的論文。

## 0. 真實數量統計（先看這裡）

- **收錄因子總數：36 個**（目標 30，已達成；沒有拆分同一因子湊數 —— 例如 12-1/6-1 動能是同一因子的 `formation_days` 參數，不重複計）。
- 各類別（category）：momentum 5；reversal 3；value 4；quality 8；risk 5；liquidity 3；composite_ml 8。
- 證據狀態：`文獻實證` 23 個；`尚未驗證` 13 個；`自行回測` **0 個**（尚未做任何回測）。
- 所有因子 `validation_level` 皆為 `{TW: L0, US: L0}`。
- 頻率（`frequency` 指因子值實質更新頻率）：daily 25、monthly 2、quarterly 9。所有因子輸入皆為日頻寬表（會計/營收欄位已 forward-fill），輸出也是日頻同形狀；quarterly 表示值只在新財報可得日改變（純財報因子），含市值的價值因子（BM、EP、CFP）隨價格每日變動故為 daily。
- Alpha101：收錄 **8 個**，公式逐字抄自 arXiv:1601.00991 Appendix A.1（見第 7 節）。
- 標 `尚未驗證` 的 13 個：TSMOM_12、ROA、CFOA、ALPHA101_002、ALPHA101_003、ALPHA101_004、ALPHA101_006、ALPHA101_009、ALPHA101_012、ALPHA101_041、ALPHA101_101、REV_YOY、REV_MOM_3_12。原因：(a) TSMOM_12：原文為期貨，個股版為改編；(b) ROA、CFOA：僅為 QMJ/F-Score 成分，單獨績效未見於已核對文獻；(c) Alpha101 系列：論文未提供逐 alpha 績效；(d) REV_YOY、REV_MOM_3_12：台股月營收，本專案文獻中無學術出處（`paper_ids` 為空，已寫明原因）。
- **公式來源類型**：`原文公式` 8 個（皆 Alpha101）；其餘 28 個為 `標準化定義`（02a/02b 自述絕大多數論文僅讀到摘要，沒有取得原文公式；詳見各因子 `limitations`）。
- 重要：`known_results` 只收 02a/02b 已記錄的摘要層級結論，**未引入任何新數字**；無數值者明寫「尚未查證」。

## 1. 總覽表

`paper_ids` 格式為 `<文件>:<論文編號>`。**02a 與 02b 的論文編號有重疊**（兩份都有 P-B01、P-B02、P-B03），例如 `02a:P-B01` 是 Jegadeesh (1990)，`02b:P-B01` 是 Novy-Marx (2013)，所以一定要帶前綴。

| ID | 名稱 | 類別 | 所需資料 | 頻率 | 方向 | 論文 | 證據狀態 |
|---|---|---|---|---|---|---|---|
| MOM_12_1 | 中期價格動能（12-1 個月） | momentum | close_adj | daily | +1 | 02a:P-A01, 02a:P-A04, 02a:P-A05, 02a:P-A06, 02a:P-A07 | 文獻實證 |
| HIGH_52W | 接近 52 週高點程度 | momentum | close_adj | daily | +1 | 02a:P-A03 | 文獻實證 |
| TSMOM_12 | 時間序列動能（波動率縮放訊號） | momentum | close_adj | daily | +1 | 02a:P-A02 | 尚未驗證 |
| REV_1M | 短期反轉（上月報酬） | reversal | close_adj | daily | -1 | 02a:P-B01, 02a:P-B02 | 文獻實證 |
| REV_1W | 週反轉（Lehmann 逆向權重） | reversal | close_adj | daily | -1 | 02a:P-B02 | 文獻實證 |
| LTREV_60_13 | 長期反轉（過去 13-60 個月報酬） | reversal | close_adj | daily | -1 | 02a:P-B03 | 文獻實證 |
| BM | 帳面市值比 | value | book_equity, market_cap | daily | +1 | 02a:P-C01, 02a:P-C02, 02a:P-C03, 02a:P-C04 | 文獻實證 |
| EP | 盈餘市值比 | value | net_income, market_cap | daily | +1 | 02a:P-C01, 02a:P-C03 | 文獻實證 |
| CFP | 現金流量市值比 | value | operating_cash_flow, market_cap | daily | +1 | 02a:P-C03 | 文獻實證 |
| SALES_GROWTH | 營收成長（過去 N 年） | value | revenue | quarterly | -1 | 02a:P-C03 | 文獻實證 |
| GPOA | 毛利資產比 | quality | gross_profit, total_assets | quarterly | +1 | 02b:P-B01, 02b:P-B03 | 文獻實證 |
| ROE | 股東權益報酬率 | quality | net_income, book_equity | quarterly | +1 | 02b:P-B06, 02b:P-B03 | 文獻實證 |
| ROA | 資產報酬率 | quality | net_income, total_assets | quarterly | +1 | 02b:P-B03, 02b:P-B05 | 尚未驗證 |
| CFOA | 營業現金流資產比 | quality | operating_cash_flow, total_assets | quarterly | +1 | 02b:P-B03, 02b:P-B05 | 尚未驗證 |
| OP_PROFIT | 營運獲利／帳面權益（RMW 排序變數） | quality | revenue, cogs, sga_expense, interest_expense, book_equity | quarterly | +1 | 02b:P-B02 | 文獻實證 |
| ACCRUALS | 應計項目（現金流量表法） | quality | net_income, operating_cash_flow, total_assets | quarterly | -1 | 02b:P-B04 | 文獻實證 |
| FSCORE | Piotroski F-Score | quality | net_income, operating_cash_flow, total_assets, long_term_debt, current_assets, current_liabilities, shares_outstanding, gross_profit, revenue | quarterly | +1 | 02b:P-B05 | 文獻實證 |
| ASSET_GROWTH | 總資產成長率（投資因子） | quality | total_assets | quarterly | -1 | 02b:P-B02, 02b:P-B06 | 文獻實證 |
| VOL_252 | 低波動（歷史波動度） | risk | close_adj | daily | -1 | 02a:P-E04, 02a:P-E02 | 文獻實證 |
| IVOL_CAPM | 特質波動（市場模型殘差） | risk | close_adj | daily | -1 | 02a:P-E01 | 文獻實證 |
| BETA_BAB | 市場 Beta（BAB 收縮估計） | risk | close_adj | daily | -1 | 02a:P-E02, 02a:P-C01 | 文獻實證 |
| DOWNSIDE_BETA | 下方 Beta | risk | close_adj | daily | +1 | 02a:P-E03 | 文獻實證 |
| SIZE | 規模（對數市值） | risk | market_cap | daily | -1 | 02a:P-C01, 02a:P-C02 | 文獻實證 |
| ILLIQ | Amihud 不流動性 | liquidity | close_adj, turnover_value | daily | +1 | 02b:P-B07 | 文獻實證 |
| TURNOVER | 平均週轉率 | liquidity | volume, shares_outstanding | daily | -1 | 02b:P-B08, 02b:P-B09 | 文獻實證 |
| ABN_VOLUME | 異常成交量 | liquidity | volume | daily | +1 | 02b:P-B10 | 文獻實證 |
| ALPHA101_002 | Alpha#2 量價相關反轉 | composite_ml | close_adj, open, volume | daily | +1 | 02b:P-B12 | 尚未驗證 |
| ALPHA101_003 | Alpha#3 開盤價與成交量排名相關 | composite_ml | open, volume | daily | +1 | 02b:P-B12 | 尚未驗證 |
| ALPHA101_004 | Alpha#4 最低價排名的時序排名 | composite_ml | low | daily | +1 | 02b:P-B12 | 尚未驗證 |
| ALPHA101_006 | Alpha#6 開盤價與成交量相關 | composite_ml | open, volume | daily | +1 | 02b:P-B12 | 尚未驗證 |
| ALPHA101_009 | Alpha#9 5 日價差趨勢條件反轉 | composite_ml | close_adj | daily | +1 | 02b:P-B12 | 尚未驗證 |
| ALPHA101_012 | Alpha#12 量增價跌訊號 | composite_ml | close_adj, volume | daily | +1 | 02b:P-B12 | 尚未驗證 |
| ALPHA101_041 | Alpha#41 高低價幾何平均減 VWAP | composite_ml | high, low, vwap | daily | +1 | 02b:P-B12 | 尚未驗證 |
| ALPHA101_101 | Alpha#101 日內實體相對區間 | composite_ml | close_adj, open, high, low | daily | +1 | 02b:P-B12 | 尚未驗證 |
| REV_YOY | 月營收年增率 | momentum | monthly_revenue | monthly | +1 | （無） | 尚未驗證 |
| REV_MOM_3_12 | 月營收動能（近 3 月均 / 近 12 月均） | momentum | monthly_revenue | monthly | +1 | （無） | 尚未驗證 |

## 2. 資料欄位詞彙表（`required_fields` 固定詞彙）

所有欄位都是寬表（index=交易日 `DatetimeIndex`、columns=股票代號）。會計欄位已由資料層依 PIT 規則對齊到「可得日」並 forward-fill；**流量項一律用近四季滾動（TTM）、存量項用期末值**。標「新增詞彙」者是為了公式需要而加入。

| 欄位 | 原始更新頻率 | 定義 | 單位 | PIT 類型 | 使用的因子 |
|---|---|---|---|---|---|
| `close_adj` | 日 | 含息還原收盤價（total return 口徑） | 價格 | 價量，t 日收盤後可得 | MOM_12_1, HIGH_52W, TSMOM_12, REV_1M, REV_1W, LTREV_60_13, VOL_252, IVOL_CAPM, BETA_BAB, DOWNSIDE_BETA, ILLIQ, ALPHA101_002, ALPHA101_009, ALPHA101_012, ALPHA101_101 |
| `close_raw` | 日 | 未還原收盤價（價格門檻過濾、算市值用） | 價格 | 價量 | （目前無因子使用） |
| `open` | 日 | 開盤價，須與 close_adj 同一還原因子 | 價格 | 價量 | ALPHA101_002, ALPHA101_003, ALPHA101_006, ALPHA101_101 |
| `high` | 日 | 最高價，須與 close_adj 同一還原因子 | 價格 | 價量 | ALPHA101_041, ALPHA101_101 |
| `low` | 日 | 最低價，須與 close_adj 同一還原因子 | 價格 | 價量 | ALPHA101_004, ALPHA101_041, ALPHA101_101 |
| `vwap` | 日 | 當日成交量加權平均價（Alpha#41 需要；新增詞彙），須與 close_adj 同一還原因子 | 價格 | 價量 | ALPHA101_041 |
| `volume` | 日 | 成交股數（依分割/減資還原口徑） | 股 | 價量 | TURNOVER, ABN_VOLUME, ALPHA101_002, ALPHA101_003, ALPHA101_006, ALPHA101_012 |
| `turnover_value` | 日 | 成交金額 | 貨幣 | 價量 | ILLIQ |
| `shares_outstanding` | 日（事件更新） | 流通在外股數，與 volume 同口徑；以公告/生效日起算 | 股 | 股本事件，不得回填 | FSCORE, TURNOVER |
| `market_cap` | 日 | 當日 close_raw x 當時最新可得股數 | 貨幣 | 價量+股本 | BM, EP, CFP, SIZE |
| `book_equity` | 季 | 股東權益帳面價值（期末，存量） | 貨幣 | 財報 PIT（台股法定截止日/美股 filing date） | BM, ROE, OP_PROFIT |
| `net_income` | 季 | 稅後淨利，近四季滾動（TTM，流量） | 貨幣 | 財報 PIT | EP, ROE, ROA, ACCRUALS, FSCORE |
| `operating_cash_flow` | 季 | 營業活動現金流量，TTM | 貨幣 | 財報 PIT | CFP, CFOA, ACCRUALS, FSCORE |
| `total_assets` | 季 | 總資產（期末） | 貨幣 | 財報 PIT | GPOA, ROA, CFOA, ACCRUALS, FSCORE, ASSET_GROWTH |
| `revenue` | 季 | 營業收入，TTM | 貨幣 | 財報 PIT | SALES_GROWTH, OP_PROFIT, FSCORE |
| `cogs` | 季 | 銷貨成本，TTM | 貨幣 | 財報 PIT | OP_PROFIT |
| `gross_profit` | 季 | 毛利 = revenue - cogs，TTM | 貨幣 | 財報 PIT | GPOA, FSCORE |
| `sga_expense` | 季 | 銷管費用，TTM（新增詞彙） | 貨幣 | 財報 PIT | OP_PROFIT |
| `interest_expense` | 季 | 利息費用，TTM（新增詞彙） | 貨幣 | 財報 PIT | OP_PROFIT |
| `long_term_debt` | 季 | 長期負債（期末）（新增詞彙） | 貨幣 | 財報 PIT | FSCORE |
| `current_assets` | 季 | 流動資產（期末）（新增詞彙） | 貨幣 | 財報 PIT | FSCORE |
| `current_liabilities` | 季 | 流動負債（期末）（新增詞彙） | 貨幣 | 財報 PIT | FSCORE |
| `monthly_revenue` | 月 | 單月營業收入（台股月營收，新增詞彙）；每月 10 日前公告，10 日後次一交易日生效 | 貨幣 | 月營收 PIT | REV_YOY, REV_MOM_3_12 |

## 3. 相同因子不同名稱／相同名稱不同公式

### 3.1 相同因子不同名稱（aliases）

| 因子 ID | 別名 |
|---|---|
| MOM_12_1 | Momentum、WML、UMD、2-12 momentum、12-2 momentum |
| HIGH_52W | 52-week high、George-Hwang 52WH |
| TSMOM_12 | TSMOM、Trend following signal |
| REV_1M | STR、ST_Rev、1-month reversal |
| REV_1W | Weekly contrarian、1-week reversal |
| LTREV_60_13 | LT_Rev、De Bondt-Thaler overreaction |
| BM | B/M、BE/ME、P/B 倒數、PBR 倒數、HML 的排序變數 |
| EP | E/P、Earnings Yield、本益比倒數、PER 倒數 |
| CFP | C/P、CF/P、Cash Flow Yield |
| SALES_GROWTH | GS、Glamour / growth proxy |
| GPOA | Gross Profits-to-Assets、GP/A、Novy-Marx profitability |
| ROE | ROE、q-factor profitability proxy |
| ROA | ROA |
| CFOA | CFO/A、CFOA |
| OP_PROFIT | OP、RMW sorting variable、Robust minus Weak |
| ACCRUALS | ACC、Sloan accruals、Total accruals / assets |
| FSCORE | F-Score、Piotroski score、PS |
| ASSET_GROWTH | Inv、I/A、CMA sorting variable、Investment-to-assets |
| VOL_252 | Low Volatility、Total volatility、Realized volatility |
| IVOL_CAPM | IVOL、Idiosyncratic Vol |
| BETA_BAB | Beta、Betting-against-beta beta、Low-beta |
| DOWNSIDE_BETA | Beta minus、Downside risk beta |
| SIZE | ME、SMB sorting variable、Market Equity |
| ILLIQ | Amihud ILLIQ、Illiquidity ratio |
| TURNOVER | Turnover、Share turnover、Volume/Shares |
| ABN_VOLUME | High-volume return premium、Volume surge、Relative volume |
| REV_YOY | 月營收 YoY、Revenue YoY |
| REV_MOM_3_12 | 營收動能、Revenue momentum |

補充：BM 與 PBR（股價淨值比）互為倒數，EP 與 PER 互為倒數 —— **方向相反**，轉換時務必取倒數並翻轉 direction。

### 3.2 相同名稱不同公式（各因子 `same_name_different_formula`）

| 因子 ID | 差異說明 |
|---|---|
| MOM_12_1 | 『動能』常見變體：12-1（本因子，跳過最近 1 個月）、12-0（不跳過，含短期反轉成分）、6-1、6-6（J=K=6）；Ken French 的 Mom 為 2-12 的簡化版而非完全複製 Jegadeesh-Titman。比較文獻數字時必須對齊定義。 |
| HIGH_52W | 52 週高點分母可用日內最高價 high 或收盤價最高；本庫用收盤價（close_adj）。 |
| TSMOM_12 | 與 MOM_12_1（截面動能）不同：TSMOM 比較自身過去報酬正負，截面動能比較股票之間排名。 |
| REV_1M | 『反轉』可指 1 週（REV_1W）、1 個月（本因子）、或 3-5 年長期反轉（LTREV_60_13）；三者機制與持有期不同。 |
| REV_1W | 與 REV_1M 的差別在回看 5 日 vs 21 日，且本因子扣除截面平均（Lehmann 權重 w=-(r-rbar)/N）。 |
| LTREV_60_13 | De Bondt-Thaler 原文用 3-5 年累計超額報酬；Ken French 用 13-60 個月報酬；本庫採後者。 |
| BM | BM 與 PBR（股價淨值比）互為倒數，方向相反：PBR 越低越便宜。Fama-French 的 HML 是 B/M 排序的多空組合報酬，不是因子值本身。 |
| EP | EP 為 PER 的倒數；PER 越低越便宜，方向相反。分子為淨利（本庫）或營業利益/稅前盈餘（其他定義）。 |
| CFP | 現金流可為營業現金流、盈餘+折舊、或自由現金流，不同文獻不同；本庫用 operating_cash_flow。 |
| SALES_GROWTH | 『成長』因子在文獻中指過去成長（本因子，預期負報酬）與預期成長/投資（q-factor I/A）兩類。 |
| GPOA | GP 毛利有『營收-銷貨成本』與廠商自報毛利兩種來源；本庫定義 gross_profit = revenue - cogs（TTM）。 |
| ROE | ROE 分子可為稅後淨利、非常項目前盈餘；分母可為期初/平均/期末權益。比較時須對齊。 |
| ROA | Piotroski 的 ROA 用稅前非常項目前盈餘/期初總資產；本庫用 TTM 淨利/期末總資產。 |
| CFOA | Piotroski 的 CFO 以期初總資產標準化；本庫用期末。 |
| OP_PROFIT | OP（FF5）= 營收-銷貨成本-銷管-利息，除以權益；GPOA = 毛利/總資產。兩者分子分母皆不同。 |
| ACCRUALS | Sloan (1996) 資產負債表法 vs 現金流量表法 (NI-CFO)；兩者在併購、非現金項目下可能差異很大。本庫用後者。 |
| FSCORE | 『F-Score』另有 Altman Z、Ohlson O 等同名不同物的財務困境分數；本庫指 Piotroski (2000) 九項。 |
| ASSET_GROWTH | FF5 的 Inv（CMA 排序變數）與 HXZ 的 I/A 概念相近但分組/時間對齊不同。 |
| VOL_252 | 『低波動』可指總波動（本因子）、特質波動（IVOL）、beta（BETA_BAB）；三者相關但不相同。 |
| IVOL_CAPM | IVOL 殘差可來自 CAPM、FF3、Carhart 等不同模型；結果不可直接比較。 |
| BETA_BAB | Beta 可為 OLS 斜率（Cov/Var）、Scholes-Williams 修正、或本庫的 rho*sigma_i/sigma_m 收縮估計。 |
| DOWNSIDE_BETA | 『下方 beta』另有 Estrada 的半變異數 (semivariance) 版本等；本庫採 Ang-Chen-Xing 條件於市場低於平均的定義。 |
| SIZE | Size 可用市值、對數市值、或總資產；SMB 為組合報酬而非因子值。 |
| ILLIQ | Amihud 原文以美元成交金額；台股以新台幣，單位不可直接與美股比較，建議截面排序使用。 |
| TURNOVER | Turnover 可為成交股數/流通股數（本因子）或成交值/市值；Datar 用月，Lee-Swaminathan 用 3-12 個月平均。 |
| ABN_VOLUME | 異常量可用比值（本因子）、z-score、或分位數判定極端；原文以極端事件為主。 |
| REV_YOY | 『營收年增率』可用單月、累計(YTD)或近三月合計；本因子為單月 YoY。 |
| REV_MOM_3_12 | 『營收動能』在券商研究中可指 YoY 加速度、近月均值比、或創高；本因子為近 3 月均/近 12 月均。 |

補充：「動能」至少有 12-1（本庫 MOM_12_1 預設）、12-0、6-1、6-6 等；Ken French 的 Mom 為 2-12 簡化版，非 Jegadeesh-Titman 完全複製。網站比較文獻數字時必須對齊定義。

## 4. 方向與單位慣例

- `direction`：+1 表「值越大，預期報酬越高」，-1 表「值越大，預期報酬越低」。**因子值本身不翻號**（例如 REV_1M 的值是上月報酬，direction=-1），翻號由引擎乘 direction 處理。方向依文獻在看資料前固定，不可事後翻轉（04 文件第 1 節）。
- Alpha101：值依原文公式的符號，direction 固定 +1。
- 因子值為**原始值，不做 winsorize / z-score**（那是引擎的事，預設 1%/99% 或 MAD 截尾後截面 z-score，見 04 文件）。
- 單位：報酬為小數（0.05=5%）；比率為無單位小數；波動為日報酬標準差（未年化，TSMOM 內部年化僅作縮放）。
- 價格類單位與市場幣別無關；跨市場比較只用截面排序，不比絕對值。

## 5. PIT 與公司行動處理總則

PIT（point-in-time）規則的權威來源是 04 文件第 1 節，本庫逐因子在 `pit_rules` 欄位具體化：

1. **價量**：t 日因子值只用 <= t 日資料；交易最早 t+1。程式碼禁止負 shift（smoke test 以『改寫最後 20 天』驗證）。
2. **台股財報**：以法定公告截止日的**次一交易日**生效：年報 3/31、Q1 5/15、Q2 8/14、Q3 11/14；有實際公告日（MOPS/TEJ）且更早，可用實際公告日次一交易日。絕不用會計期末日。
3. **台股月營收**：每月 10 日前公告，10 日之後次一交易日生效。
4. **美股財報**：SEC EDGAR filing（acceptance）date 次一交易日；無則年報 90 天、季報 45 天保守落後。
5. **重編財報**：只能用當時版本；無版本資料時須在結果頁註明偏誤。
6. **年度比較（YoY / 年前值）**：因子程式碼以 `_lag(df, days)` 用**日曆日 as-of 查找**（只往過去 reindex + ffill），不依賴交易日數 shift，避免假日差異與前視。
7. **公司行動**：價格報酬一律用含息還原 `close_adj`；開高低 vwap 與 close_adj 同一還原因子；價格門檻（如股價 < 10 元）用 `close_raw`；`market_cap` = 當日 `close_raw` x 當時最新可得股數；股本變動從公告/生效日起算，不回填。
8. **台股特有**：漲跌停（10%）鎖死日成交量極小且報酬被截斷，使 ILLIQ、ABN_VOLUME、波動類因子失真；證交稅（賣出 0.3%）與手續費影響高換手因子（見各因子 `transaction_cost_note`）。
9. **金融業**：無『毛利』概念，毛利類因子（GPOA、OP_PROFIT、FSCORE 的 margin）須排除金融保險業。

## 6. 缺漏值與異常值規則（引用 04 文件第 1 節）

- 因子值缺漏 → 該期不納入排序（不補 0、不補均值）；一個截面有效樣本 < 30 檔則該期 IC 記為缺漏；報告每期覆蓋率。
- 因子程式碼的缺漏約定：分母 <= 0（權益、資產、市值、成交值、營收）→ 輸出 NaN；窗內資料不足 → NaN（不前補）；除以 0 或 inf → NaN。
- 異常值：由引擎在截面做 winsorize（預設 1%/99%）或 MAD 截尾（中位數 ± 5xMAD），再 z-score；因子程式碼不做。
- 存活者偏誤、股票池（排除 ETF/DR/全額交割、上市未滿 60 交易日；美股 microcap 剔除）同 04 文件，屬引擎層。

## 7. Alpha101 收錄說明

來源：Kakushadze, "101 Formulaic Alphas", arXiv:1601.00991（02b:P-B12）。公式與運算子定義**逐字抄自 arXiv PDF 實際文字**（本次以 pdftotext 從 arXiv PDF 抽出，Appendix A.1 為 Alpha 公式、運算子定義節為『A.1. Functions and Operators』、輸入資料節為『A.2. Input Data』—— 原文節標題在 PDF 中編號有重複，以文字為準）。

收錄的 8 個（只用價量、無產業分類）：

| ID | 原文公式（逐字，換行處已接成一行） |
|---|---|
| ALPHA101_002 | `(-1 * correlation(rank(delta(log(volume), 2)), rank(((close - open) / open)), 6))` |
| ALPHA101_003 | `(-1 * correlation(rank(open), rank(volume), 10))` |
| ALPHA101_004 | `(-1 * Ts_Rank(rank(low), 9))` |
| ALPHA101_006 | `(-1 * correlation(open, volume, 10))` |
| ALPHA101_009 | `((0 < ts_min(delta(close, 1), 5)) ? delta(close, 1) : ((ts_max(delta(close, 1), 5) < 0) ? delta(close, 1) : (-1 * delta(close, 1))))` |
| ALPHA101_012 | `(sign(delta(volume, 1)) * (-1 * delta(close, 1)))` |
| ALPHA101_041 | `(((high * low)^0.5) - vwap)` |
| ALPHA101_101 | `((close - open) / ((high - low) + .001))` |

原文運算子定義（逐字，節錄本庫使用者）：

- `rank(x)` = cross-sectional rank
- `delay(x, d)` = value of x d days ago
- `correlation(x, y, d)` = time-serial correlation of x and y for the past d days
- `covariance(x, y, d)` = time-serial covariance of x and y for the past d days
- `delta(x, d)` = today's value of x minus the value of x d days ago
- `decay_linear(x, d)` = weighted moving average over the past d days with linearly decaying weights d, d - 1, ..., 1 (rescaled to sum up to 1)
- `ts_min(x, d)` / `ts_max(x, d)` = time-series min / max over the past d days
- `ts_rank(x, d)` = time-series rank in the past d days
- `sum(x, d)` = time-series sum over the past d days; `stddev(x, d)` = moving time-series standard deviation over the past d days
- `sign(x)`, `log(x)`, `abs(x)` = standard definitions
- 輸入資料：`vwap` = daily volume-weighted average price；`returns` = daily close-to-close returns；`adv{d}` = average daily dollar volume for the past d days

實作約定（原文未規定處，本庫自行決定且已寫入各因子 `limitations`）：`rank` 用截面百分位 `rank(axis=1, pct=True)`；`ts_rank` 用窗內百分位；`correlation` 遇常數序列得 NaN；三元運算子以 `where` 實作。`decay_linear`、`scale` 等本版未使用的運算子不在此重述。

Alpha101 的證據標 `尚未驗證`：論文是公式清單，02b 記錄其摘要僅稱平均持有期約 0.6~6.4 天、alpha 兩兩平均相關 15.9%，**沒有逐 alpha 績效**。網站不得顯示任何績效數字。

## 8. 不收錄清單（考慮過但公式不明確或來源不足而排除）

| 項目 | 排除原因 |
|---|---|
| QMJ 合成品質因子（02b:P-B03） | 子指標清單與權重為『記憶，未核對』，標準化/合成細節未驗證；任何實作都會變成自創公式。已收其成分（GPOA、ROA、CFOA、ACCRUALS）但不收合成分數。 |
| Pastor-Stambaugh 流動性 beta（02b:P-B11） | 個股流動性 gamma 的迴歸式為記憶，且需要市場流動性創新序列與 FF 因子、足夠長的日資料；非單一個股價量欄位可算，優先級低。 |
| 聚合波動風險 beta_VIX（02a:P-E01） | 需要 VIX 序列與 FF3 因子；台股無對應 VIX 資料源（本專案未確認）。 |
| B/M 分解（無形報酬，02a:P-C04） | 分解定義為『依記憶，待核對』，細節未取得；公式不明確。 |
| 動能崩盤動態權重（02a:P-A05） | 是依預測均值/變異數調整曝險的策略層設計，預測式未核對；不是個股因子值。 |
| 景氣同時指標條件動能（02a:P-A07） | 文獻自述『非單一閉式公式』，細節未核對。其結論（台股動能/反轉無顯著利潤）已放入 MOM_12_1 known_results。 |
| 跨國個人主義迴歸（02a:P-A06） | 是國家層次迴歸，不是個股因子。結論已放入 MOM_12_1 known_results。 |
| SMB / HML / RMW / CMA / UMD / BAB 因子報酬序列 | 這些是『多空組合報酬』，屬引擎層組合建構結果，不是個股因子值。其個股排序變數（SIZE、BM、OP_PROFIT、ASSET_GROWTH、MOM_12_1、BETA_BAB）已收錄。 |
| Gu-Kelly-Xiu 機器學習（02b:P-B13）、AlphaGen（02b:P-B14） | 方法論而非公式明確的因子；屬 composite_ml 未來擴充，目前無可實作的固定公式。 |
| Harvey-Liu-Zhu、Deflated Sharpe、McLean-Pontiff、Hou-Xue-Zhang 重現、OSAP、JKP（02b:P-B15~P-B19、P-B20） | 驗證方法論，用於 04 文件的驗證流程，不是因子。 |
| Barber et al. 台灣個人投資人（02b:P-B21） | 文件自述『不是流動性因子論文』，無選股公式；只作為成本背景。 |
| Alpha101 其餘 93 個 | 本版刻意只收 8 個價量、無需產業分類、易驗證者。其餘未收入並非公式不明確：多數需要 IndNeutralize（產業分類）、cap、adv{d} 等額外欄位，或結構複雜難以逐字驗證。可於後續擴充。Alpha#1 未收：Ts_ArgMax 的起算索引慣例（0 或 1）原文未規定，結果須再驗證。 |
| 三大法人買賣超、融資融券、當沖比等台股籌碼因子 | 本專案已完成研究（01/02a/02b）沒有可引用的公式出處（FinMind 僅為資料來源）。為避免湊數，不收。 |
| 營收創新高、營收 YoY 加速度等月營收變體 | 無來源且與 REV_YOY/REV_MOM_3_12 高度重疊，不湊數。 |
| Time-series momentum 原始期貨版本 | 原文標的為期貨與資產類別；個股改編版 TSMOM_12 已收錄並標尚未驗證。 |

## 9. 重要限制與使用提醒（給網站實作者）

1. 本庫公式大多為 `標準化定義`，02a/02b 都說明未取得多數付費全文，標『依記憶，待核對』的設定（形成期、持有期、收縮權重 0.6、基準窗 50 日等）在網站顯示時須同樣保留該註記，直到對照全文。
2. 本庫部分因子是**變體**（已在 `limitations` 與 `same_name_different_formula` 明寫）：VOL_252（日報酬代替 60 個月月報酬）、IVOL_CAPM（單因子殘差代替 FF3）、BETA_BAB（日報酬相關係數、等權市場代理）、ACCRUALS（現金流量表法）、DOWNSIDE_BETA（滾動均值因果近似）、BM/EP/CFP（每日以當日市值更新）。不要把這些數字當成原論文數字。
3. `known_results` 是文獻結果，**不是本專案回測**。
4. repo_refs 中 GPL（OpenSourceAP/CrossSection）與無授權者僅『概念參考』，不得複製其程式碼；本庫所有 Python 皆依論文公式自寫。
5. 本庫所有因子 `required_fields` 都在第 2 節詞彙表內；新增欄位須同步更新本節與 smoke test 的合成資料。

## 10. 驗證

`tests/test_factors_smoke.py`：載入 YAML，檢查 id 唯一、欄位齊全、paper_ids 存在於 02a/02b、無 `自行回測`；並對每個因子以 300 日 x 50 檔隨機合成資料執行 compute，檢查不拋例外、形狀相同、暖身後非全 NaN、**防前視**（最後 20 天輸入改亂數後，t <= 倒數第 21 天的輸出必須完全不變）。合成資料僅為程式碼健全性檢查，**不是研究結果**。
