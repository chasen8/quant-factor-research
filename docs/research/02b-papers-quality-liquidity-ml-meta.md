# 02b 文獻清單：品質/獲利、流動性/成交量、複合/ML/挖掘、方法論（含台灣證據）

撰寫日期：2026-10-28。範圍：D 品質/獲利、F 流動性/成交量、G 複合/ML/挖掘、M 方法論、T 台灣證據。動能/反轉/價值/波動由另一份報告負責。

## 0. 讀這份報告前必讀的查證規則

- 「已驗證 DOI」＝我用 Crossref API 查過，標題／作者／年份／期刊／卷期頁與本表一致。
- 「已開啟網址」＝我實際開啟（HTTP 200 或抓到內容）。SSRN 對機器人回 403，所以 SSRN 連結只標「Crossref 有登錄該 SSRN DOI 或搜尋結果曾出現，未能直接開啟」。
- 「摘要已核對」＝我讀到該論文的摘要原文或其出版社／NBER 摘要。**沒有開啟全文的論文，樣本期間、表號、細部變數定義一律標明來源等級**，不假裝是逐字核對。
- 公式來源類型只有兩種：**原文公式**（我實際讀到原文該式）；**標準化定義（依原文文字描述整理）**（業界／後續文獻通用定義，非逐字引用）。本報告絕大多數屬後者，因為多數論文我只讀到摘要。唯一實際開過全文 PDF 的是 AlphaGen（B14）。
- 本任務未做任何自己的計算；所有績效數字都來自摘要或我開啟的頁面，並標位置。
- 以「（記憶，未核對）」標記的內容是我憑訓練記憶寫的，**網站入庫前必須先開全文確認**，不可直接當事實顯示。

## 1. 總覽表

| 編號 | 標題 | 作者 | 年 | 期刊 | 類別 | 驗證狀態 |
|---|---|---|---|---|---|---|
| P-B01 | The Other Side of Value: The Gross Profitability Premium | Novy-Marx | 2013 | JFE 108(1) | D 品質 | 已驗證 DOI；NBER 已開啟；摘要已核對 |
| P-B02 | A Five-Factor Asset Pricing Model | Fama, French | 2015 | JFE 116(1) | D 品質 | 已驗證 DOI；摘要僅二手 |
| P-B03 | Quality Minus Junk | Asness, Frazzini, Pedersen | 2019（線上 2018） | Rev. Accounting Studies 24(1) | D 品質 | 已驗證 DOI；摘要已核對（搜尋） |
| P-B04 | Do Stock Prices Fully Reflect Information in Accruals and Cash Flows About Future Earnings? | Sloan | 1996 | The Accounting Review 71(3) | D 品質 | 已驗證 DOI；Crossref 摘要極簡 |
| P-B05 | Value Investing: The Use of Historical Financial Statement Information to Separate Winners from Losers | Piotroski | 2000 | J. Accounting Research 38 (Supp.) | D 品質 | 已驗證 DOI；摘要已核對（搜尋） |
| P-B06 | Digesting Anomalies: An Investment Approach（q-factor 模型） | Hou, Xue, Zhang | 2015（線上 2014） | RFS 28(3) | D 品質 | 已驗證 DOI；NBER 已開啟 |
| P-B07 | Illiquidity and Stock Returns: Cross-Section and Time-Series Effects | Amihud | 2002 | J. Financial Markets 5(1) | F 流動性 | 已驗證 DOI；摘要已核對 |
| P-B08 | Liquidity and Stock Returns: An Alternative Test | Datar, Naik, Radcliffe | 1998 | J. Financial Markets 1(2) | F 流動性 | 已驗證 DOI；摘要已核對（搜尋） |
| P-B09 | Price Momentum and Trading Volume | Lee, Swaminathan | 2000 | J. Finance 55(5) | F 成交量 | 已驗證 DOI；Crossref 摘要全文 |
| P-B10 | The High-Volume Return Premium | Gervais, Kaniel, Mingelgrin | 2001 | J. Finance 56(3) | F 成交量 | 已驗證 DOI（見 §3 更正）；Crossref 摘要全文 |
| P-B11 | Liquidity Risk and Expected Stock Returns | Pástor, Stambaugh | 2003 | J. Political Economy 111(3) | F 流動性 | 已驗證 DOI；摘要已核對（搜尋） |
| P-B12 | 101 Formulaic Alphas | Kakushadze | 2016 | Wilmott 2016(84)；arXiv:1601.00991 | G 挖掘/公式庫 | 已驗證 DOI；arXiv 已開啟 |
| P-B13 | Empirical Asset Pricing via Machine Learning | Gu, Kelly, Xiu | 2020 | RFS 33(5) | G ML | 已驗證 DOI；Crossref 摘要全文 |
| P-B14 | Generating Synergistic Formulaic Alpha Collections via Reinforcement Learning（AlphaGen） | Yu, Xue, Ao, Pan, He, Tu | 2023 | KDD '23；arXiv:2306.12964 | G RL 挖掘 | 已驗證 DOI；arXiv 全文 PDF 已讀 |
| P-B15 | … and the Cross-Section of Expected Returns | Harvey, Liu, Zhu | 2016（線上 2015） | RFS 29(1) | M 方法論 | 已驗證 DOI；NBER 已開啟 |
| P-B16 | Does Academic Research Destroy Stock Return Predictability? | McLean, Pontiff | 2016 | J. Finance 71(1) | M 方法論 | 已驗證 DOI；Crossref 摘要全文 |
| P-B17 | Replicating Anomalies | Hou, Xue, Zhang | 2020（線上 2018） | RFS 33(5) | M 方法論 | 已驗證 DOI；Crossref 摘要全文 |
| P-B18 | Open Source Cross-Sectional Asset Pricing | Chen, Zimmermann | 2022 | Critical Finance Review 11(2) | M 方法論 | 已驗證 DOI；GitHub 已開啟 |
| P-B19 | Is There a Replication Crisis in Finance? | Jensen, Kelly, Pedersen | 2023 | J. Finance 78(5) | M 方法論 | 已驗證 DOI；Crossref 摘要全文 |
| P-B20 | The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality | Bailey, López de Prado | 2014 | J. Portfolio Management 40(5) | M 方法論 | 已驗證 DOI；公式僅二手 |
| P-B21 | Just How Much Do Individual Investors Lose by Trading? | Barber, Lee, Liu, Odean | 2009（線上 2008） | RFS 22(2) | T 台灣證據 | 已驗證 DOI；摘要已核對（搜尋） |

篇數：D 6、F 5、G 3、M 6、T 1，共 21 篇（超過目標 15 篇上限，因為 D/F/M 線索全數查證通過，網站需要；若要精簡，B08、B09 可降為「備選」）。

## 2. 全站共通注意事項（台股／美股實作）

- **財報落後期**（台股）：年報 3/31、Q1 5/15、Q2 8/14、Q3 11/14（依任務給定）。任何會計因子，在公布截止日之前不得使用該期數字。建議：以「截止日次一交易日」為最早可用日，而非財報期末日；美股則用 SEC 申報日（filing date）或 Compustat 常見的期末後 3–6 個月落後。
- **FF 的美股時序**：t 年 6 月底重組，市值取 t-1 年 12 月底，會計數據取 t-1 會計年度。台股若照搬，t-1 年報 3/31 才公布，6 月重組是安全的；但季資料因子要依上列日期另設落後。
- **台股成本**：證交稅賣出 0.3%、手續費（買賣各約 0.1425% 乘折讓）、漲跌幅 10%。流動性類與高週轉因子在台股換手極高，扣成本後多半被吃掉，是「學術異象 vs 扣成本後仍有效」區分的關鍵檢驗對象。
- **漲跌停**：漲停鎖死會讓日報酬、Amihud 這類以絕對報酬／成交值為分子的指標失真（鎖停時成交量極小、報酬被截斷）。
- 以下各篇「13 適合台股／美股」欄為我的評估（非論文結論），標「評估」。

---

## P-B01 Novy-Marx (2013) Gross Profitability

1. **完整標題**：The Other Side of Value: The Gross Profitability Premium（NBER 工作論文版名為 "…Good Growth and the Gross Profitability Premium", w15940）
2. **作者**：Robert Novy-Marx
3. **年份**：2013（JFE 2013 年 4 月；NBER 2010）
4. **期刊**：Journal of Financial Economics 108(1), 1–28
5. **連結**：DOI 10.1016/j.jfineco.2013.01.003（**已驗證 DOI**）；免費版 https://www.nber.org/papers/w15940（**已開啟網址**）；作者頁 PDF 搜尋結果有 https://www.johnhcochrane.com/s/Novy_marx_OSoV.pdf（未開啟）
6. **市場與期間**：美國（CRSP/Compustat）。具體期間：尚未查證（我記憶為 1963–2010，需開全文確認）。
7. **公式**（標準化定義，依原文文字「gross profits-to-assets」整理）：
   $$GP/A_{i,t}=\frac{REVT_{i,t}-COGS_{i,t}}{AT_{i,t}}$$
   組合：依 GP/A 排序做多高 GP/A、做空低 GP/A（十分位或大小交叉雙重排序）。
8. **變數**：REVT 營業收入（Compustat REVT）；COGS 銷貨成本；AT 總資產（期末）。原文用「毛利／總資產」；以哪個年度資產（期初或期末）與重組月份，**尚未查證，需對照全文**。
9. **直覺**：毛利是損益表最上面、最少被會計操縱的獲利，比盈餘或 ROE 乾淨；獲利高的公司通常 B/M 低，單看價值會漏掉，二者搭配效果更好（「價值的另一面」）。
10. **驗證方法**：Fama-MacBeth 迴歸、獲利／價值雙排序投資組合，與 FF/Carhart 三四因子 alpha 檢定。（細節：全文尚未開啟）
11. **報告結果**（NBER/二手摘要，非表號）：毛利／資產對橫斷面平均報酬的預測力與 B/M 大致相當；獲利公司報酬顯著較高，儘管其 B/M 較低、市值較大；控制獲利後價值策略表現大幅提升，尤其在最大型、最具流動性的股票；GP 可解釋多數盈餘類異象。**確切 alpha／t 值：尚未查證。**
12. **程式碼／資料**：Open Source Asset Pricing 有重現版（變數 GP，https://github.com/OpenSourceAP/CrossSection，已開啟）；JKP 因子 `gp_at`（jkpfactors.com，已開啟網站首頁，變數名未核對）。
13. **台股／美股（評估）**：美股適合。台股：用營收、營業成本；可用性取決於年報／季報公布日落後。台灣財報 IFRS 分類「營業毛利」直接可得，實作簡單。金融業無毛利概念，需排除。
14. **限制**：不適用金融業；小型股流動性成本；後續研究（B16–B19）顯示發表後衰退；跨國穩健性要看 B19。

## P-B02 Fama & French (2015) 五因子模型

1. **標題**：A Five-Factor Asset Pricing Model
2. **作者**：Eugene F. Fama, Kenneth R. French
3. **年份**：2015
4. **期刊**：Journal of Financial Economics 116(1), 1–22
5. **連結**：DOI 10.1016/j.jfineco.2014.10.010（**已驗證 DOI**）；因子資料 Ken French Data Library https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html（**已開啟網址**）；SSRN 版 ID：尚未查證
6. **市場與期間**：美國（NYSE/AMEX/NASDAQ），1963 年 7 月起（我記憶為 1963–2013，**尚未核對**）。
7. **公式**：
   $$R_{it}-R_{Ft}=a_i+b_i\,(R_{Mt}-R_{Ft})+s_i\,SMB_t+h_i\,HML_t+r_i\,RMW_t+c_i\,CMA_t+e_{it}$$
   RMW = 穩健（Robust）營運獲利減疲弱（Weak）；CMA = 保守（Conservative）投資減積極（Aggressive）投資。（標準化定義；迴歸式為原文模型。）
8. **變數**：RMW 的獲利指標 OP = 營收 − 銷貨成本 − 銷管費用 − 利息費用，除以帳面權益（均取 t-1 會計年度）；投資指標 Inv = 總資產成長率 $(AT_{t-1}/AT_{t-2})-1$；SMB/HML 為規模與 B/M 因子；重組在每年 6 月底，市值取 t-1 年 12 月底。**（上述 OP 與 Inv 的定義為我記憶，Ken French 資料庫頁面有同樣描述；未逐字核對全文。）**
9. **直覺**：由股利折現模型推得——在其他條件相同下，B/M 越高、預期獲利越高、預期投資（資產成長）越低，預期報酬越高。
10. **驗證**：以 2×3 與 2×2×2×2 雙排序／多排序組合，用 GRS 檢定比較三因子、四因子、五因子模型能否解釋規模／B/M／OP／Inv 排序組合。
11. **結果**：二手摘要稱五因子模型下 HML 的平均報酬被其他因子完全解釋而變得多餘（etf.com Swedroe 轉述，**非原文摘要**）。GRS 數值、解釋力比例：尚未查證。
12. **程式碼／資料**：因子日／月資料公開於 Ken French Data Library（美國及國際 5 因子）；建構程式碼無官方版，需自行依 library 說明重建。
13. **台股／美股（評估）**：美股直接可用。台股可自行建構，但資料庫需自建，OP 需 SG&A 與利息費用科目；注意 CMA 對台灣企業資產成長（含併購、增資）定義。
14. **限制**：HML 冗餘的結論有爭議（見 B06 對比）；5 因子對動能無解；樣本以美國為主；後續 B16–B19 指出部分異象衰退。

## P-B03 Asness, Frazzini & Pedersen (2019) QMJ

1. **標題**：Quality Minus Junk
2. **作者**：Clifford S. Asness, Andrea Frazzini, Lasse Heje Pedersen
3. **年份**：2019（線上 2018-11；SSRN 工作論文 2013）
4. **期刊**：Review of Accounting Studies 24(1), 34–112
5. **連結**：DOI 10.1007/s11142-018-9470-2（**已驗證 DOI**）；SSRN https://papers.ssrn.com/abstract=2312432（搜尋結果出現，機器人 403，未直接開啟）；AQR 資料頁含 QMJ 因子（見第 12 項）。
6. **市場與期間**：美國及全球 24 國（摘要已核對）；期間：美國我記憶為 1957 起，**尚未核對**。
7. **公式**（標準化定義，依原文描述整理；細節以全文為準）：
   $$Quality_{i,t}=z\big(Profitability_{i,t}+Growth_{i,t}+Safety_{i,t}\big),\quad z(x)=\frac{r(x)-\bar r}{\sigma_r}$$
   $$QMJ_t=\tfrac12\,(SmallQuality+BigQuality)-\tfrac12\,(SmallJunk+BigJunk)$$
   其中 $r(\cdot)$ 為橫斷面排名。**注意**：2013 工作論文版另含 Payout 子分數，2019 發表版以獲利、成長、安全為三大構面（搜尋摘要）；子指標清單（GPOA、ROE、ROA、CFOA、GMAR、ACC…）是我記憶，**尚未核對**。
8. **變數**：Profitability（毛利／資產、ROE、ROA、現金流／資產、毛利率、低應計）；Growth（上述獲利指標的 5 年變化）；Safety（低 beta、低槓桿、低 ROE 波動、低 Altman Z 風險）。Z 為橫斷面標準化。
9. **直覺**：高品質股（安全、獲利、成長、管理佳）理應價格更高，但實際只貴一點；這個「品質價格偏低」解釋其風險調整後超額報酬。
10. **驗證**：美國及 24 國，Fama-French 風格雙排序組合，因子 alpha 與跨時間「品質價格」預測力。
11. **結果**（摘要）：QMJ 在美國及全球 24 國都有顯著風險調整報酬；品質的價格偏低時，未來 QMJ 報酬較高。數值：尚未查證。
12. **程式碼／資料**：AQR 官方資料集（QMJ Factors，AQR 網站「Data Sets」頁，**我未開啟，URL 尚未驗證**）；JKP 的 `qmj`／quality 主題（jkpfactors.com）。
13. **台股／美股（評估）**：美股適合；台股需要多個會計科目（現金流量表、資產負債表）且多期，財報落後期要逐科目處理；也可用 JKP 的全球因子。
14. **限制**：因子由多指標合成，權重與標準化選擇多；發表前樣本；合成導致歸因困難；與 B01、B05 內容重疊。

## P-B04 Sloan (1996) Accruals

1. **標題**：Do Stock Prices Fully Reflect Information in Accruals and Cash Flows About Future Earnings?
2. **作者**：Richard G. Sloan
3. **年份**：1996
4. **期刊**：The Accounting Review 71(3), 289–315
5. **連結**：DOI 10.2308/tar-9608042309（**已驗證 DOI**，Crossref 查證卷期頁一致）；免費版：尚未查證
6. **市場與期間**：美國；期間我記憶為 1962–1991，**尚未核對**。
7. **公式**（標準化定義，依原文資產負債表法）：
   $$ACC=\frac{(\Delta CA-\Delta Cash)-(\Delta CL-\Delta STD-\Delta TP)-Dep}{\text{Average Total Assets}}$$
8. **變數**：ΔCA 流動資產變動；ΔCash 現金及約當現金變動；ΔCL 流動負債變動；ΔSTD 一年內到期長期負債變動；ΔTP 應付所得稅變動；Dep 折舊與攤銷；分母為期初期末平均總資產。（此式為業界通用的原文定義，**未對照全文逐字**。）現代做法常改用現金流量表法 $ACC=(NI-CFO)/\text{avg AT}$。
9. **直覺**：盈餘中的應計部分持續性低於現金流部分，但投資人固定於盈餘（functional fixation），高應計股被高估，後續報酬較低。
10. **驗證**：以應計十分位建立對沖組合，檢驗盈餘持續性迴歸與後續報酬。
11. **結果**：Crossref 摘要只有主題描述，無數字。對沖報酬與 t 值：尚未查證。
12. **程式碼／資料**：Open Source Asset Pricing 含 Accruals 系列訊號（OSAP，已開啟 GitHub）；JKP 有 `acc`類（變數名未核對）。
13. **台股／美股（評估）**：美股適合但發表後衰退；台股可用現金流量表法，需 Q 報落後處理；台股應計與合併報表、季報樣態不同，需實證。
14. **限制**：資產負債表法在併購、非現金項目下產生測量誤差（後續文獻批評，本報告未逐篇核對）；效應集中於小型股、空頭端（記憶，未核對）。

## P-B05 Piotroski (2000) F-Score

1. **標題**：Value Investing: The Use of Historical Financial Statement Information to Separate Winners from Losers
2. **作者**：Joseph D. Piotroski
3. **年份**：2000
4. **期刊**：Journal of Accounting Research 38 (Supplement), 1–41（Crossref 頁碼欄僅顯示 1）
5. **連結**：DOI 10.2307/2672906（**已驗證 DOI**）；免費版：https://test2.ivey.uwo.ca/media/3775523/value_investing_the_use_of_historical_financial_statement_information.pdf（搜尋結果出現，未開啟）
6. **市場與期間**：美國，高 B/M 股票，1976–1996（搜尋核對的摘要）。
7. **公式**（標準化定義；9 項二元訊號加總，來自原文文字描述，我記憶的清單）：
   $$F=\sum_{k=1}^{9} F_k,\quad F_k\in\{0,1\}$$
   獲利 4 項：ROA>0、CFO>0、ΔROA>0、ACCRUAL（CFO/Assets > ROA）；槓桿／流動性 3 項：ΔLEVER<0、ΔLIQUID>0、無增資（EQ_OFFER=0）；營運效率 2 項：ΔMARGIN>0、ΔTURN>0。
8. **變數**：ROA=稅前非常項目前盈餘／期初總資產；CFO=營業現金流／期初總資產；LEVER=長期負債／平均總資產；LIQUID=流動比率；MARGIN=毛利率；TURN=營收／期初總資產。（細部定義：尚未核對全文。）
9. **直覺**：價值股大多是困境股，單一 B/M 分不出贏家輸家；用財報基本面訊號分離出體質改善者。
10. **驗證**：先篩高 B/M 股票，依 F-Score 建立買高分、賣低分的對沖組合，與市場、規模、動能等控制比較。
11. **結果**（摘要）：買入預期贏家、放空預期輸家的策略 1976–1996 年平均年報酬 23%；高 B/M 全體平均報酬提升至少 7.5% 每年（JAR 摘要措辭；Alpha Architect 版寫 7%，以 JAR 為準）。
12. **程式碼／資料**：OSAP 含 PS（Piotroski Score）訊號（已開啟 GitHub，變數名未核對）。無作者官方程式碼。
13. **台股／美股（評估）**：美股適合，但對沖報酬多靠放空低分股，台股可放空性（借券、融券）受限；僅做多版本要另行評估。需要的科目多，落後期要注意。
14. **限制**：只限高 B/M 股票；原文樣本小型股比例高、報酬含空頭端；發表後衰退（B16–B17）；二元門檻武斷。

## P-B06 Hou, Xue & Zhang (2015) q-factor

1. **標題**：Digesting Anomalies: An Investment Approach
2. **作者**：Kewei Hou, Chen Xue, Lu Zhang
3. **年份**：2015（RFS 線上 2014-09）
4. **期刊**：Review of Financial Studies 28(3), 650–705
5. **連結**：DOI 10.1093/rfs/hhu068（**已驗證 DOI**）；免費版 https://www.nber.org/papers/w18435（**已開啟網址**）；SSRN https://doi.org/10.2139/ssrn.2152674（Crossref 登錄，未直接開啟）
6. **市場與期間**：美國；搜尋轉述為 1972–2012，**以 NBER 摘要為準**，期間為二手資訊。
7. **公式**（原文模型；因子建構為標準化定義）：
   $$R_{it}-R_{ft}=\alpha_i+\beta^{MKT}_i\,MKT_t+\beta^{ME}_i\,R_{ME,t}+\beta^{I/A}_i\,R_{I/A,t}+\beta^{ROE}_i\,R_{ROE,t}+\varepsilon_{it}$$
8. **變數**：$R_{I/A}$=低投資減高投資；$R_{ROE}$=高 ROE 減低 ROE。I/A=總資產年度變動／落後一期總資產；ROE=季度非常項目前盈餘／落後一期帳面權益（記憶，未逐字核對）。原文以每月（I/A 用年度，ROE 用每月更新的最近季報）2×3×3 排序建構，細節尚未核對。
9. **直覺**：新古典投資 q 理論——預期報酬（資本成本）高時，公司會更多投資；獲利高但投資低，必然是折現率高。
10. **驗證**：對近 80 個異象做十分位多空組合，與 FF3、Carhart 比較；以 alpha 與 GRS 檢定。
11. **結果**（摘要）：近 80 個異象中約一半在全體股票中不顯著；q 模型解釋剩餘顯著異象的能力至少與 FF3/Carhart 相當，多數情形更好。q 模型在盈餘驚喜、特質波動、財務困境、發行量上勝過 Carhart；動能與規模相當；在總應計十分位較差（NBER 摘要轉述）。
12. **程式碼／資料**：q-factor 資料由作者網站發布（global-q.org，**URL 尚未開啟驗證**）；OSAP 與 JKP 亦有相關因子。
13. **台股／美股（評估）**：美股適合；台股需要季度 ROE 與資產成長，落後期要用公告日而非期末；q 模型每月更新獲利使資料時效更敏感。
14. **限制**：因子為作者建構而非可交易資產之外證；HXZ 自己的後續文章 B17 顯示大量異象不可重現；與 FF5 在因子定義上有爭議。

## P-B07 Amihud (2002) ILLIQ

1. **標題**：Illiquidity and Stock Returns: Cross-Section and Time-Series Effects
2. **作者**：Yakov Amihud
3. **年份**：2002
4. **期刊**：Journal of Financial Markets 5(1), 31–56
5. **連結**：DOI 10.1016/S1386-4181(01)00024-6（**已驗證 DOI**）；免費版 https://www.cis.upenn.edu/~mkearns/finread/amihud.pdf（搜尋結果出現，未開啟）
6. **市場與期間**：美國 NYSE；期間我記憶為 1963–1997，**尚未核對**。
7. **公式**（原文以文字描述，「日報酬絕對值／日成交金額的平均」；數學式為標準化定義）：
   $$ILLIQ_{i,y}=\frac{1}{D_{i,y}}\sum_{d=1}^{D_{i,y}}\frac{|R_{i,y,d}|}{VOLD_{i,y,d}}$$
   市場流動性 $AILLIQ_y$ 為跨股票平均。
8. **變數**：$D_{i,y}$ 股票 i 在年 y 有資料的交易日數；$R$ 日報酬；$VOLD$ 日成交金額（股價×成交股數，美元）。單位常乘上 $10^6$。
9. **直覺**：單位成交金額造成的價格變動 ＝ 價格衝擊（Kyle lambda 的粗略代理）；越不流動，投資人要求越高報酬。
10. **驗證**：橫斷面 Fama-MacBeth（個股報酬對 ILLIQ、規模、beta、B/M 等）與市場層級時間序列預期／未預期流動性迴歸。
11. **結果**（摘要）：預期市場不流動性增加預期超額報酬（流動性溢酬）；未預期不流動性與當期報酬負相關；效應在小型股較強。數字：尚未查證。後續 Harris & Amato 重現發現原結果可重現但近期資料中關係大幅減弱（搜尋轉述）。
12. **程式碼／資料**：不需特殊資料，用日報酬與成交金額即可；OSAP 與 JKP 皆有 Amihud 指標（變數名未核對）。
13. **台股／美股（評估）**：台股資料（TWSE 日成交值）易取得、實作簡單。但需處理漲跌停鎖死日（成交量近零、報酬被截斷）；台股週轉率高，ILLIQ 之溢酬扣 0.3% 稅後是否存活要實證。
14. **限制**：只有日資料近似價格衝擊；零成交日；與規模高度共線（Amihud 自己指出小型股效應較強）；近年溢酬減弱。

## P-B08 Datar, Naik & Radcliffe (1998) Turnover

1. **標題**：Liquidity and Stock Returns: An Alternative Test
2. **作者**：Vinay T. Datar, Narayan Y. Naik, Robert Radcliffe
3. **年份**：1998（倫敦商學院工作論文版為 1997）
4. **期刊**：Journal of Financial Markets 1(2), 203–219
5. **連結**：DOI 10.1016/S1386-4181(97)00004-9（**已驗證 DOI**）；LBS 條目 https://www.london.edu/faculty-and-research/academic-research/l/liquidity-and-stock-returns-an-alternative-test（搜尋結果，未開啟）
6. **市場與期間**：美國 NYSE；期間我記憶為 1962–1991，**尚未核對**。
7. **公式**（標準化定義，摘要只說 turnover＝成交股數／流通股數）：
   $$TO_{i,t}=\frac{\text{Shares traded}_{i,t}}{\text{Shares outstanding}_{i,t}}$$
8. **變數**：以月（或過去若干月平均）週轉率為流動性代理（週轉率越高＝越流動）。
9. **直覺**：Amihud-Mendelson (1986) 預測流動性差股票要求較高報酬；週轉率比買賣價差更容易取得，故用為替代。
10. **驗證**：Fama-MacBeth 橫斷面迴歸，控制規模、B/M、beta。
11. **結果**（摘要，二手）：週轉率與報酬顯著負相關，控制規模／B/M／beta 後仍成立，且不限於一月（不同於 Eleswarapu & Reinganum 1993）。數字：尚未查證。
12. **程式碼**：無官方；OSAP 有週轉率類訊號（名稱未核對）。
13. **台股／美股（評估）**：台股週轉率極高、由散戶主導，且高週轉常被解讀為「彩券／投機」而非流動性（與原文符號可能相反）；美股結果需要考慮後來「高週轉預測低報酬」是流動性還是錯價之爭。須實證，**不要預設同號**。
14. **限制**：週轉率並非單純流動性（也反映意見分歧、投機）；NASDAQ 的成交量重複計算問題需調整（記憶，未核對）。

## P-B09 Lee & Swaminathan (2000) Volume and Momentum

1. **標題**：Price Momentum and Trading Volume
2. **作者**：Charles M. C. Lee, Bhaskaran Swaminathan
3. **年份**：2000
4. **期刊**：Journal of Finance 55(5), 2017–2069
5. **連結**：DOI 10.1111/0022-1082.00280（**已驗證 DOI**）；免費版：尚未查證
6. **市場與期間**：美國；期間尚未查證（記憶 1965–1995）。
7. **公式**（標準化定義）：過去 $J$ 月（原文以 3–12 月形成期）平均週轉率
   $$\overline{TO}_{i,t}=\frac{1}{J}\sum_{k=1}^{J}\frac{Vol_{i,t-k}}{Shares_{i,t-k}}$$
   與過去報酬做 $3\times3$ 雙排序（動能 × 週轉率）。
8. **變數**：Vol 月成交股數；Shares 流通股數。
9. **直覺**：高成交量代表「魅力股」（glamour）被追捧、會反轉；低成交量為價值股。成交量預測動能的大小與持續期。
10. **驗證**：價格動能與過去週轉率雙排序、盈餘驚喜、長期（至 5 年）事件時間分析。
11. **結果**（Crossref 摘要全文）：高（低）過去週轉率股票呈現魅力（價值）特徵、未來報酬較低（高）、之後八季盈餘驚喜更負（正）；過去成交量預測動能的幅度與持續性；動能效應在未來五年反轉，高（低）成交量贏家（輸家）反轉更快。
12. **程式碼**：無官方；需 CRSP 成交量。
13. **台股／美股（評估）**：台股週轉率高、散戶主導，雙排序可能很有結構，但台股動能本身證據弱（另一份報告負責動能），應實證。美股 NASDAQ 成交量需調整。
14. **限制**：樣本舊；NASDAQ 成交量定義問題；與動能因子相關，不是獨立因子。

## P-B10 Gervais, Kaniel & Mingelgrin (2001) High-Volume Return Premium

1. **標題**：The High-Volume Return Premium
2. **作者**：Simon Gervais, Ron Kaniel, Dan H. Mingelgrin
3. **年份**：2001
4. **期刊**：Journal of Finance 56(3), 877–919
5. **連結**：DOI **10.1111/0022-1082.00349**（**已驗證 DOI**）；免費版：尚未查證
6. **市場與期間**：美國；期間尚未查證（記憶 1963–1996）。
7. **公式**（標準化定義，原文僅描述「異常高／低成交量的日或週」；形成期與基準窗為我記憶，**尚未核對**）：
   $$AV_{i,t}=\frac{Vol_{i,t}}{\overline{Vol}_{i,t-50:t-1}}\quad(\text{或以分位數判定極端})$$
   極端高量日／週為形成期，持有期約 1 個月。
8. **變數**：Vol 日（週）成交量；基準為過去平均成交量。
9. **直覺**：成交量暴增提升股票的能見度（visibility），吸引更多買盤與投資人認知，推高價格（investor recognition）。
10. **驗證**：事件式分組，檢驗是否可被報酬自相關、公司公告、市場風險、流動性解釋。
11. **結果**（Crossref 摘要全文）：日或週內成交量異常高（低）的股票，其後一個月傾向上漲（下跌）；報酬自相關、公司公告、市場風險與流動性不足以解釋。數字：尚未查證。
12. **程式碼**：無官方。
13. **台股／美股（評估）**：台股漲停鎖死日的成交量異常需排除；散戶注意力假說適用於台股，值得優先實證。其他國家證據：搜尋曾出現 Kaniel, Li & Starks (2003) 國際證據（SSRN 474100），未核對內容。
14. **限制**：效應期短（1 個月）、換手成本敏感；0.3% 稅後可能消失。

## P-B11 Pástor & Stambaugh (2003) 流動性風險

1. **標題**：Liquidity Risk and Expected Stock Returns
2. **作者**：L'uboš Pástor, Robert F. Stambaugh
3. **年份**：2003
4. **期刊**：Journal of Political Economy 111(3), 642–685
5. **連結**：DOI 10.1086/374184（**已驗證 DOI**）；SSRN https://doi.org/10.2139/ssrn.279804；NBER w8462（Crossref 登錄）；免費 PDF 搜尋結果出現（https://www.cis.upenn.edu/~mkearns/finread/pastor.pdf，未開啟）
6. **市場與期間**：美國，1966–1999（摘要）。
7. **公式**（標準化定義，與原文方法一致；個股流動性估計式為我記憶，**尚未逐字核對**）：
   $$r^e_{i,d+1,t}=\theta_{i,t}+\phi_{i,t}\,r_{i,d,t}+\gamma_{i,t}\,\mathrm{sign}(r^e_{i,d,t})\,v_{i,d,t}+\epsilon_{i,d+1,t}$$
   $\gamma_{i,t}$ 通常為負，越負越不流動；彙總為市場流動性，取創新 $L_t$；再估流動性 beta：
   $$r^e_{i,t}=\beta^0_i+\beta^L_i L_t+\beta^M_i MKT_t+\beta^S_i SMB_t+\beta^H_i HML_t+\epsilon_{i,t}$$
8. **變數**：$v$ 日成交金額；$r^e$ 超額報酬；sign 項捕捉「帶方向的成交量造成的反轉」；$\beta^L$ 為對市場流動性創新的敏感度。
9. **直覺**：訂單流越多、流動性越低時，報酬反轉越大；對整體流動性衝擊敏感的股票要求流動性風險溢酬。
10. **驗證**：流動性 beta 十分位組合，控制市場、規模、價值、動能因子的 alpha；因子化為可交易 traded factor。
11. **結果**（摘要）：1966–1999，高流動性 beta 組合平均報酬比低者高 7.5% 每年（調整 market、size、value、momentum）；流動性風險因子可解釋同期動能策略約一半的獲利。後續批評（Li, Novy-Marx & Velikov，搜尋結果轉述）：動能那一半的結論受預測流動性時使用動能變數影響，結果較弱。
12. **程式碼／資料**：作者網站提供流動性因子序列（Pástor 個人網頁，**URL 尚未開啟驗證**）；WRDS 亦有。
13. **台股／美股（評估）**：美股適合；台股需以日資料估個股 $\gamma$，且需足夠長樣本；整體市場流動性衝擊在台股如何度量需自行設計，工作量大、優先級較低。
14. **限制**：流動性 beta 估計噪音大；樣本止於 1999；動能那一半結論有爭議；使用 NYSE/AMEX。

## P-B12 Kakushadze (2016) 101 Formulaic Alphas

1. **標題**：101 Formulaic Alphas
2. **作者**：Zura Kakushadze
3. **年份**：2016
4. **期刊**：Wilmott Magazine 2016(84), 72–81；arXiv:1601.00991
5. **連結**：DOI 10.1002/wilm.10525（**已驗證 DOI**）；arXiv https://arxiv.org/abs/1601.00991（**已開啟網址**）；SSRN https://doi.org/10.2139/ssrn.2701346（未直接開啟）
6. **市場與期間**：未指定市場；本文為公式清單，並以實際交易（Quantigic）的 alpha 為基礎。實證樣本期間：尚未查證。
7. **公式**（**原文公式**，我記憶的例子，網站入庫前須對照原文逐字確認）：
   Alpha#101：$\dfrac{close-open}{(high-low)+0.001}$；
   Alpha#6：$-1\times \mathrm{correlation}(open,\ volume,\ 10)$。
   其餘 99 個以同一運算子語法（rank、ts_rank、delta、delay、correlation、scale、decay_linear 等）給出。
8. **變數**：open/close/high/low/volume/vwap/returns 等日資料欄位；rank 為橫斷面排名；ts_* 為時序運算。
9. **直覺**：多為短期量價反轉／動能微結構訊號，持有期很短。
10. **驗證**：摘要稱：平均持有期約 0.6–6.4 天；alpha 兩兩平均相關 15.9%；報酬與波動度強相關，與換手率無顯著相依。（**摘要已核對**）
11. **結果**：見上；論文未提供單一 alpha 樣本外績效表（我印象是如此，**尚未核對**）。
12. **程式碼**：論文本身即公式；社群有許多非官方 Python 實作（未核對，不建議直接信任）。
13. **台股／美股（評估）**：持有期僅 1–6 天，換手極高，台股 0.3% 證交稅會吃掉大部分；僅適合作為「候選特徵庫」，不是可直接上架的因子；用 vwap 要有 vwap 資料。
14. **限制**：未提供嚴格樣本外與成本後績效；部分公式在作者資料／市場慣例下才可執行；純量價；有資料窺探風險。

## P-B13 Gu, Kelly & Xiu (2020) ML 資產定價

1. **標題**：Empirical Asset Pricing via Machine Learning
2. **作者**：Shihao Gu, Bryan Kelly, Dacheng Xiu
3. **年份**：2020（線上 2020-02）
4. **期刊**：Review of Financial Studies 33(5), 2223–2273
5. **連結**：DOI 10.1093/rfs/hhaa009（**已驗證 DOI**）；NBER w25398（記憶，**尚未開啟**）
6. **市場與期間**：美國個股；樣本規模與期間：我記憶約 30,000 檔、1957–2016、94 個特徵，**尚未核對**。
7. **公式**（標準化定義；樣本外 R² 為原文使用的指標，式為記憶）：
   $$r_{i,t+1}=E_t(r_{i,t+1})+\varepsilon_{i,t+1},\quad E_t(r_{i,t+1})=g^*(z_{i,t})$$
   $$R^2_{oos}=1-\frac{\sum (r_{i,t+1}-\hat r_{i,t+1})^2}{\sum r_{i,t+1}^2}$$
   （分母不去平均，即相對於預測值為零的基準。）
8. **變數**：$z_{i,t}$ 為公司特徵與宏觀變數（含交互作用）；$g^*$ 為待估函數，用線性、懲罰迴歸、PCR/PLS、隨機森林／GBRT、神經網路。
9. **直覺**：報酬預測存在非線性與特徵交互，機器學習能捕捉。
10. **驗證**：訓練／驗證／測試的時間切分（遞增窗），以樣本外 R² 與預測為基礎的多空投資組合績效評估。
11. **結果**（摘要）：機器學習預測帶來大額經濟收益，部分情況使領先迴歸策略績效加倍；樹與神經網路最佳，其優勢來自非線性預測變數交互；各方法一致認為主要預測訊號是動能、流動性與波動度的變形。具體 R² 與 Sharpe：尚未查證。
12. **程式碼／資料**：Dacheng Xiu 網站提供特徵資料與程式（**URL 尚未開啟驗證**）；資料本身為專有（CRSP/Compustat）。
13. **台股／美股（評估）**：美股適合；台股樣本小（約 1,700 檔）、特徵少時 ML 易過擬合；且預測集中在微型股與高換手，需考慮成本。
14. **限制**：預測大量來自小型／難套利股票；交易成本未充分處理；特徵可得性採保守落後但仍可能有細微洩漏；後續研究指出市值加權下績效顯著下降（記憶，未核對）。

## P-B14 Yu et al. (2023) AlphaGen

1. **標題**：Generating Synergistic Formulaic Alpha Collections via Reinforcement Learning
2. **作者**：Shuo Yu, Hongyan Xue, Xiang Ao, Feiyang Pan, Jia He, Dandan Tu, Qing He（Crossref 列 7 位作者，已由獨立抽查核對，見 06 報告）
3. **年份**：2023
4. **期刊**：Proceedings of the 29th ACM SIGKDD Conference on Knowledge Discovery and Data Mining (KDD '23), pp. 5476–5486；arXiv:2306.12964
5. **連結**：DOI 10.1145/3580305.3599831（**已驗證 DOI**）；arXiv https://arxiv.org/abs/2306.12964（**已開啟網址，全文 PDF 已讀**）；程式碼 https://github.com/RL-MLDM/alphagen（**已開啟，HTTP 200**）
6. **市場與期間**：中國 A 股，CSI300 與 CSI500 成分股；訓練 2009/01/01–2018/12/31，驗證 2019 全年，測試 2020/01/01–2021/12/31（論文 §4.1.1）。特徵僅開高低收量 vwap；目標為 20 日報酬 $Ref(close,-20)/close-1$。
7. **公式**：原文以 IC（Pearson 相關）為目標；組合模型為線性：
   $$f(x)=\sum_k w_k\,\tilde\alpha_k(x),\quad \tilde\alpha=\text{標準化後的 alpha 值}$$
   RL 報酬 ＝ 加入新 alpha 後組合模型的 IC 提升（**原文敘述**，具體式號未逐字核對）。IC：$IC_t=\mathrm{corr}(\alpha_t,\ r_{t+20})$，Rank IC 為排序版。（標準化定義＋原文敘述）
8. **變數**：alpha 表示為運算子 token 序列（逆波蘭表示法），PPO 作為策略梯度演算法生成；組合權重由線性模型最佳化。
9. **直覺**：逐個挖掘 alpha（GP、單因子 RL）忽略它們日後要被合併；直接用下游組合的表現當獎勵，使挖出的 alpha 彼此互補。
10. **驗證**：與 MLP、XGBoost、LightGBM、PPO/GP（top 與 filter 兩種選取）比較，10 個隨機種子；以 top-k/drop-n 策略做回測（僅 CSI300，測試期 2020–2021）。
11. **結果**（Table 2，均值）：CSI300：Ours IC 0.0725、Rank IC 0.0806；XGBoost 0.0404/0.0576；LightGBM 0.0259/0.0324。CSI500：Ours 0.0438/0.0727；XGBoost 0.0353/0.0639。（Table 2，逐字抄自 PDF 抽出文字。）Table 3 為 10 個 alpha 的組合範例；Figure 5 為回測淨值曲線（我未讀其細節，是否扣成本：尚未查證）。
12. **程式碼**：官方 GitHub 見上（授權條款未核對）。
13. **台股／美股（評估）**：方法可移植到台股／美股，但原文只在 A 股；需要自備特徵資料並考慮漲跌幅、交易稅。測試期僅 2 年，結果不可視為穩健樣本外。
14. **限制**：A 股市場特性（T+1、漲跌幅 10%）；測試期短；IC 提升不等於扣成本後可獲利；搜尋空間大，**自身就是多重檢定問題**（需套用 B15、B20）；未見大量樣本外驗證。

## P-B15 Harvey, Liu & Zhu (2016) 多重檢定

1. **標題**：… and the Cross-Section of Expected Returns
2. **作者**：Campbell R. Harvey, Yan Liu, Heqing Zhu
3. **年份**：2016（RFS 線上 2015-10）
4. **期刊**：Review of Financial Studies 29(1), 5–68
5. **連結**：DOI 10.1093/rfs/hhv059（**已驗證 DOI**）；NBER https://www.nber.org/papers/w20592（**已開啟網址**）；SSRN https://papers.ssrn.com/abstract=2249314（搜尋結果出現，未直接開啟）
6. **市場與期間**：美國為主的文獻整理，歷史截止值自 1967 年第一批實證檢驗起算（NBER 頁）。搜尋轉述審查了 316 個因子（二手來源，非摘要原文；NBER 頁只寫 "hundreds"）。
7. **公式**（標準化定義，依多重檢定理論整理）：
   Bonferroni：$p_{adj}=\min(1,\ M\cdot p)$；Holm、BHY（Benjamini-Hochberg-Yekutieli）控制 FDR：
   $$p_{(k)}\le \frac{k}{M\,c(M)}\,\alpha,\quad c(M)=\sum_{j=1}^{M}\frac1j$$
   原文並以歷史上已檢驗因子數 $M$ 的增長推算各年門檻 t 值。
8. **變數**：M 為累計已檢驗因子數；$c(M)$ 調和級數修正；α 顯著水準；t 統計量門檻隨年遞增。
9. **直覺**：當檢驗上百個因子，某些「顯著」純屬運氣；新因子門檻應提高。
10. **驗證**：蒐集文獻因子，建立控制 FWER／FDR 的框架並處理檢定間相關與缺失資料。
11. **結果**（NBER 摘要）：新因子需達 t > 3.0；多數文獻主張很可能是假的。各年份門檻表、通過因子名單：尚未查證。
12. **程式碼／資料**：Campbell Harvey 網站提供因子清單與資料（URL 尚未開啟驗證）；Chen & Zimmermann 的 OSAP 可另行用於重做。
13. **台股／美股（評估）**：直接作為網站驗證規則：因子顯著性門檻用 t>3（至少 2.78，見 B17），且需記錄「嘗試了多少因子」。台股樣本較短，t>3 更難達成。
14. **限制**：t>3 是美國文獻的校準；HLZ 假設的「檢驗總數」難以確實計算；批評者（B19）認為過度悲觀。

## P-B16 McLean & Pontiff (2016) 發表後衰退

1. **標題**：Does Academic Research Destroy Stock Return Predictability?
2. **作者**：R. David McLean, Jeffrey Pontiff
3. **年份**：2016（線上 2016-01）
4. **期刊**：Journal of Finance 71(1), 5–32
5. **連結**：DOI 10.1111/jofi.12365（**已驗證 DOI**）；免費版：尚未查證
6. **市場與期間**：美國；97 個預測變數（Crossref 摘要）；期間尚未查證。
7. **公式**（標準化定義，依摘要描述；三期間迴歸為記憶，**未逐字核對**）：
   $$R_{i,t}=\alpha_i+\beta_1\,Post\text{-}Sample_t+\beta_2\,Post\text{-}Publication_t+\varepsilon_{i,t}$$
   樣本外下降 $=\beta_1/\alpha$；發表後下降 $=\beta_2/\alpha$（含 $\beta_1$ 之累計）。
8. **變數**：Post-Sample 指標＝原文樣本結束後、發表前；Post-Publication 指標＝發表後。
9. **直覺**：樣本外衰退＝資料挖掘上界；發表後額外衰退＝套利者學習。
10. **驗證**：97 個預測變數的組合報酬，比較樣本內、樣本外、發表後三期間。
11. **結果**（Crossref 摘要）：投資組合報酬樣本外低 26%，發表後低 58%；發表資訊交易帶來 32%（58%−26%）的下降；發表後衰退對樣本內報酬高者更大；高特質風險、低流動性股票集中的組合報酬較高；預測變數組合發表後與其他已發表預測變數的相關上升。
12. **程式碼／資料**：作者提供 97 個變數清單（Jeffrey Pontiff 網頁，未開啟）；OSAP（B18）可涵蓋大部分。
13. **台股／美股（評估）**：網站應顯示每個因子的「發表年」與「發表前／後績效」。台股異象發表時間不同，本研究只能提供框架。
14. **限制**：「發表」日期的認定；衰退也可能來自市場演化；樣本偏重 NYSE/AMEX/NASDAQ。

## P-B17 Hou, Xue & Zhang (2020) Replicating Anomalies

1. **標題**：Replicating Anomalies
2. **作者**：Kewei Hou, Chen Xue, Lu Zhang
3. **年份**：2020（線上 2018-12）
4. **期刊**：Review of Financial Studies 33(5), 2019–2133
5. **連結**：DOI 10.1093/rfs/hhy131（**已驗證 DOI**）；NBER w23394（記憶，未開啟）；SSRN 版：尚未查證
6. **市場與期間**：美國；452 個異象（Crossref 摘要）；期間尚未查證（記憶 1967–2014）。
7. **公式**（標準化定義，檢定統計量）：
   $$t=\frac{\bar r}{s/\sqrt T},\quad \text{單檢定門檻 }|t|\ge1.96;\ \text{多重門檻 }|t|\ge2.78$$
8. **變數**：$\bar r$ 多空組合月平均報酬；s 標準差；T 月數。微型股以 NYSE 分位點與市值加權緩解。
9. **直覺**：許多異象依賴微型股與等權重，在更嚴格組合建構下消失。
10. **驗證**：以 NYSE 分位點、市值加權重建 452 個異象，並套用多重檢定門檻。
11. **結果**（摘要）：65% 的 452 個異象（包括 96% 的交易摩擦類）無法通過 |t|≥1.96；套用 2.78 後失敗率升至 82%；即使可重現，經濟規模也比原文小得多。
12. **程式碼／資料**：作者資料庫（q-factor 網站 global-q.org，URL 尚未開啟驗證）；程式碼公開狀態：尚未查證。
13. **台股／美股（評估）**：直接支持網站採用「NYSE 分位點／市值加權／排除微型股」的嚴格版本；台股相當於以上市（TWSE）市值分位點建 breakpoints，排除微型股後再看。
14. **限制**：只在美國；其結論較 B18、B19 悲觀，三者差異來自重現標準與檢定設計。

## P-B18 Chen & Zimmermann (2022) Open Source Asset Pricing

1. **標題**：Open Source Cross-Sectional Asset Pricing
2. **作者**：Andrew Y. Chen, Tom Zimmermann
3. **年份**：2022
4. **期刊**：Critical Finance Review 11(2), 207–264
5. **連結**：DOI 10.1561/104.00000112（**已驗證 DOI**）；SSRN https://papers.ssrn.com/abstract=3604626（搜尋結果出現，未直接開啟）；資料站 https://www.openassetpricing.com（**已開啟，HTTP 200**）；GitHub https://github.com/OpenSourceAP/CrossSection（**已開啟，HTTP 200**）
6. **市場與期間**：美國；319 個特徵（搜尋轉述）；期間尚未查證。
7. **公式**（標準化定義）：重現檢定——對原文與重現的 t 統計量做迴歸
   $$t^{rep}_j=a+b\,t^{orig}_j+u_j$$
   搜尋轉述發表版斜率 0.88、R² 82%（工作論文版為 0.90 與 83%）。
8. **變數**：$t^{rep}$ 重現的長短組合 t 值；$t^{orig}$ 原文報告 t 值。
9. **直覺**：先確認「能不能重現」，再討論「是不是多重檢定」。
10. **驗證**：開源重寫 319 個特徵，與原文 t 統計量比較。
11. **結果**（搜尋轉述，非原文）：161 個原文明確顯著的特徵中，98% 的重現 t>1.96；44 個證據混合者平均 t 約 2；其餘 114 個為原文不顯著或 HXZ 的修改版。（請入庫前對照原文確認。）
12. **程式碼／資料**：openassetpricing.com 提供特徵與組合下載；GitHub 有完整程式；R 套件 `OpenSourceAP.DownloadR`（搜尋結果出現）。
13. **台股／美股（評估）**：美股資料免費，可直接作為美股因子資料庫的驗證來源；台股無對應資料，需自建。
14. **限制**：僅美國；頻率為月；重現的是「文獻上的定義」而非穩健性；與 B17 的結論分歧在於是否剔除微型股。

## P-B19 Jensen, Kelly & Pedersen (2023) Replication Crisis

1. **標題**：Is There a Replication Crisis in Finance?
2. **作者**：Theis Ingerslev Jensen, Bryan Kelly, Lasse Heje Pedersen
3. **年份**：2023（線上 2022-06）
4. **期刊**：Journal of Finance 78(5), 2465–2518
5. **連結**：DOI 10.1111/jofi.13249（**已驗證 DOI**）；資料站 https://jkpfactors.com（**已開啟，HTTP 200**）；程式碼 https://github.com/bkelly-lab/ReplicationCrisis（GitHub 組織清單中出現，**repo 存在，頁面未開啟**）
6. **市場與期間**：93 國（Crossref 摘要）；期間尚未查證。
7. **公式**（標準化定義：階層貝氏——我記憶的結構，**尚未核對全文**）：
   $$\alpha_i\sim N(\alpha_c,\ \sigma_c^2)\ \text{（主題 c 內）},\quad \alpha_c\sim N(\alpha,\ \sigma^2)$$
   以此做縮減，使多因子證據相互加強。
8. **變數**：$\alpha_i$ 因子 i 的 alpha；c 為 13 個主題；σ 為主題內外的離散度。
9. **直覺**：因子數目多不一定削弱證據，如果因子同屬少數主題，則多個獨立資料點彼此支持。
10. **驗證**：貝氏模型估計 α 縮減；因子在 93 國新資料的樣本外檢驗。
11. **結果**（Crossref 摘要）：多數因子可重現；可歸為 13 個主題，其中多數對切線投資組合顯著；在 93 國新資料中樣本外有效；大量因子觀測反而強化證據。
12. **程式碼／資料**：jkpfactors.com 提供各國因子與 13 主題報酬；GitHub bkelly-lab/ReplicationCrisis。
13. **台股／美股（評估）**：**對台股特別有用**，因為內含台灣的因子報酬（我印象是涵蓋 Taiwan，**需自行在 jkpfactors.com 確認**）。可作為網站台股因子「樣本外」比對。
14. **限制**：模型假設可能偏向支持因子存在；因子建構為統一規則而非各論文原版；主題層級的稀釋效果；與 B17 結論衝突需並列呈現。

## P-B20 Bailey & López de Prado (2014) Deflated Sharpe Ratio

1. **標題**：The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality
2. **作者**：David H. Bailey, Marcos López de Prado
3. **年份**：2014
4. **期刊**：Journal of Portfolio Management 40(5), 94–107
5. **連結**：DOI 10.3905/jpm.2014.40.5.094（**已驗證 DOI**）；SSRN https://papers.ssrn.com/abstract=2460551（搜尋結果出現，機器人 403，未直接開啟）
6. **市場與期間**：方法論文，非特定市場。
7. **公式**（標準化定義；我沒有開啟原文，**以下為通用寫法，須對照原文確認**）：
   $$PSR(SR^*)=\Phi\!\left(\frac{(\widehat{SR}-SR^*)\sqrt{T-1}}{\sqrt{1-\hat\gamma_3\widehat{SR}+\frac{\hat\gamma_4-1}{4}\widehat{SR}^2}}\right)$$
   $$DSR=PSR(SR_0),\quad SR_0=\sqrt{V[\{\widehat{SR}_n\}]}\Big((1-\gamma)\Phi^{-1}\!\big(1-\tfrac1N\big)+\gamma\,\Phi^{-1}\!\big(1-\tfrac1{Ne}\big)\Big)$$
   （γ 為 Euler–Mascheroni 常數 ≈0.5772；搜尋結果描述一致。）
8. **變數**：$\widehat{SR}$ 樣本 Sharpe（非年化）；T 樣本長度；$\hat\gamma_3$ 偏態；$\hat\gamma_4$ 峰度；N 獨立試驗數；$V[\{\widehat{SR}_n\}]$ 各試驗 Sharpe 的變異；Φ 標準常態 CDF。
9. **直覺**：試了 N 個策略後挑最好的，其 Sharpe 必然被高估；要與「N 個零技能試驗中最大者的期望」比較，同時修正非常態報酬與短樣本。
10. **驗證**：理論推導與蒙地卡羅模擬（細節：尚未查證）。
11. **結果**：摘要稱此指標修正選擇偏誤（多重檢定）與非常態報酬造成的績效膨脹。數值案例：尚未查證。
12. **程式碼**：R 套件 quantstrat 有 `deflatedSharpe` 函數（rdocumentation 搜尋結果出現）；作者書與 GitHub 另有實作（未核對）。
13. **台股／美股（評估）**：網站驗證系統必備：每個因子要記錄所嘗試的參數組合數 N，才能算 DSR。對 AlphaGen 這類自動挖掘因子尤其必要。
14. **限制**：N（獨立試驗數）難以決定；對高度相關的試驗需估計有效 N；常態近似在極端偏態下失準。

## P-B21 Barber, Lee, Liu & Odean (2009) 台灣個人投資人

1. **標題**：Just How Much Do Individual Investors Lose by Trading?
2. **作者**：Brad M. Barber, Yi-Tsung Lee, Yu-Jane Liu, Terrance Odean
3. **年份**：2009（Crossref 顯示線上 2008-04-19，卷期為 RFS 22(2)）
4. **期刊**：Review of Financial Studies 22(2), 609–632
5. **連結**：DOI 10.1093/rfs/hhn046（**已驗證 DOI**）；免費版 https://faculty.haas.berkeley.edu/odean/papers%20current%20versions/justhowmuchdoindividualinvestorslose_rfs_2009.pdf（搜尋結果出現，未開啟）
6. **市場與期間**：台灣證交所（TWSE）全體投資人逐筆交易紀錄。期間：摘要未載，我記憶為 1995–1999，**尚未核對**。
7. **公式**：本文不提供選股因子；績效以交易後報酬（投資組合超額報酬與交易成本）計算（標準化描述，細節尚未核對）。
8. **變數**：個人與機構投資人的總投資組合報酬、交易成本（手續費、證交稅）、委託單類型（主動／被動）。
9. **直覺**：個人投資人主動下單吃價差，系統性虧損；機構與外資獲利。
10. **驗證**：使用台灣全體投資人完整交易紀錄，比較個人與機構的績效。
11. **結果**（摘要，搜尋核對）：個人投資人整體投資組合每年落後 3.8 個百分點（約台灣 GDP 的 2.2%、個人總所得的 2.8%）；幾乎所有虧損可追溯至其主動委託單；機構每年多賺約 1.5 個百分點，外資獲得近半的機構利潤。較早版本（2005 工作論文 "Who Loses from Trade? Evidence from Taiwan"）曾拆解損失來源，但已發表摘要沒有該拆解，**不可引用**。
12. **程式碼／資料**：交易紀錄資料專有，無法取得。
13. **台股／美股（評估）**：直接相關於台股結構（散戶為主，證交稅 0.3%）。可作為「高週轉、散戶偏好的因子（如高成交量、彩券型）在台股扣成本後可能失效」的背景證據；**這不是流動性因子論文**。
14. **限制**：期間較舊（1990 年代，之後台股制度、外資比重、當沖降稅都改變）；非因子研究。
    **補充**：搜尋也出現 Gau & Liao (2010) "Market Returns and the Trading of Individual and Institutional Investors: Evidence from the Taiwan Futures Market"（SSRN 1662376）與 Lin & Chen (2013) "Does Foreign Institutional Trading Facilitate Stock Liquidity? Evidence from Taiwan"（SSRN 2243040），標題與作者經 Crossref 搜尋結果確認，內容與發表狀態**尚未查證**，未列入正式清單。

---

## 3. 校正紀錄與不確定點

- **Gervais–Kaniel–Mingelgrin DOI**：任務線索給的 `10.1111/0022-1082.00347` 實際是 Lettau & Ludvigson 的論文；正確 DOI 為 `10.1111/0022-1082.00349`（Crossref 驗證）。
- **HXZ 2015 標題**：正式標題是 "Digesting Anomalies: An Investment Approach"，不是 "q-factor"；q-factor 是其中提出的模型。
- **RFS 年份**：HLZ 與 Barber 等人的 Crossref 線上日期較出刊年早一年，表格採出刊年並註記線上年。
- 全文未開啟的論文（B01–B13、B15–B21），其樣本期間與大部分公式細節為記憶或二手，已逐項標註；**入庫前須以全文校對**。
- 普遍查不到／尚未核對的欄位：各論文確切樣本期間、具體 alpha／t 值與 Table 編號、免費 PDF 連結（SSRN 對機器人 403）、官方程式碼（除 AlphaGen、OSAP、JKP 外幾乎沒有）。
- 台灣證據：有 1 篇（B21），但屬散戶交易成本／績效，不是流動性因子論文；未找到以 TWSE 資料檢驗 Amihud／週轉率溢酬的已驗證期刊論文。
