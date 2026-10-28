# 02a 動能／反轉／價值／波動風險因子：學術論文清單與核對

查證日期：2026-10-28。範圍：動能(A)、反轉(B)、價值(C)、波動/風險(E)；品質、流動性、ML、多重檢定由另一位研究員負責。

## 0. 讀這份報告前必讀（查證等級與限制）

- **書目資料**（標題、作者、年份、期刊、卷頁）：全部以 Crossref API 逐筆比對，標「已驗證 DOI」。
- **摘要層級事實**：來自 Crossref 內嵌摘要（Wiley/JF 系列）或網路搜尋對摘要的轉述。標「摘要」。
- **未能開啟付費全文**（Elsevier/OUP/Wiley 全文皆 403 或需訂閱）。因此：
  - 第 7 欄公式一律標「標準化定義（依原文文字描述整理）」，**沒有任何一條可宣稱為原文逐字公式**，網站引用時請同樣標示，或之後取得全文再升級為「原文公式」。
  - 各 Table 內的績效數字（t 值、月報酬）多數**尚未查證**；只收錄在摘要中看到的數字。
  - 研究樣本期間若非取自摘要/搜尋結果，標「依記憶，待核對全文」。
- 本報告**無任何自行計算**。「（後續文獻）」標記的是他人研究，非原論文。
- 「第 13 欄 適合台股/美股」是依制度特徵（漲跌幅 10%、散戶比重高、放空限制、證交稅 0.3%）所做的**推論判斷**，不是論文結論。
- 台灣市場證據：見 P-A06（Chui et al.，東亞弱動能，台灣是否在樣本**未能確認**）、P-C05（Chiao et al. 2010，台灣本地，已驗證）、P-A07（Wang et al. 2012，台灣本地，已驗證）。

## 1. 總覽表

| 編號 | 標題 | 作者 | 年 | 期刊 | 類別 | 驗證狀態 |
|---|---|---|---|---|---|---|
| P-A01 | Returns to Buying Winners and Selling Losers | Jegadeesh, Titman | 1993 | JF 48(1):65-91 | A 價格動能 | 已驗證 DOI + 摘要 |
| P-A02 | Time series momentum | Moskowitz, Ooi, Pedersen | 2012 | JFE 104(2):228-250 | A 時間序列動能 | 已驗證 DOI；摘要取自搜尋轉述 |
| P-A03 | The 52-Week High and Momentum Investing | George, Hwang | 2004 | JF 59(5):2145-2176 | A 52 週高點 | 已驗證 DOI + 摘要 |
| P-A04 | Value and Momentum Everywhere | Asness, Moskowitz, Pedersen | 2013 | JF 68(3):929-985 | A/C 跨市場價值+動能 | 已驗證 DOI + 摘要 |
| P-A05 | Momentum crashes | Daniel, Moskowitz | 2016 | JFE 122(2):221-247 | A 動能風險 | 已驗證 DOI；摘要取自搜尋轉述 |
| P-A06 | Individualism and Momentum around the World | Chui, Titman, Wei | 2010 | JF 65(1):361-392 | A 國際動能（含東亞/台灣待確認） | 已驗證 DOI + 摘要 |
| P-A07 | Momentum and Contrarian Profits Corresponding to the Coincident Economic Indicator on the Taiwan Stock Market | Wang, Huang, Huang | 2012 | Emerging Markets Finance and Trade 48(sup1):29-40 | A/B 台灣動能/反轉 | 已驗證 DOI（Crossref）+ 已開啟 IDEAS 頁 |
| P-B01 | Evidence of Predictable Behavior of Security Returns | Jegadeesh | 1990 | JF 45(3):881-898 | B 短期反轉 | 已驗證 DOI + 摘要 |
| P-B02 | Fads, Martingales, and Market Efficiency | Lehmann | 1990 | QJE 105(1):1-28（起始頁 1 經 Crossref 驗證；迄頁 28 未驗證） | B 週反轉 | 已驗證 DOI（Crossref，DOI 見節內）+ NBER 摘要 |
| P-B03 | Does the Stock Market Overreact? | De Bondt, Thaler | 1985 | JF 40(3):793-805 | B 長期反轉 | 已驗證 DOI + 摘要 |
| P-C01 | The Cross-Section of Expected Stock Returns | Fama, French | 1992 | JF 47(2):427-465 | C 規模+B/M | 已驗證 DOI + 摘要 |
| P-C02 | Common risk factors in the returns on stocks and bonds | Fama, French | 1993 | JFE 33(1):3-56 | C SMB/HML | 已驗證 DOI（無摘要） |
| P-C03 | Contrarian Investment, Extrapolation, and Risk | Lakonishok, Shleifer, Vishny | 1994 | JF 49(5):1541-1578 | C 價值（B/M, E/P, C/P, 成長） | 已驗證 DOI + 摘要 |
| P-C04 | The Absence of the Book-to-Market Effect in the Taiwan Stock Market: A Decomposition Approach | Chiao, Hung, Yao | 2009 線上/2010 紙本 | Japanese Economic Review 61(2):289-299 | C 台灣 B/M | 已驗證 DOI + 已開啟 IDEAS 頁 |
| P-E01 | The Cross-Section of Volatility and Expected Returns | Ang, Hodrick, Xing, Zhang | 2006 | JF 61(1):259-299 | E 特質波動 | 已驗證 DOI + 摘要 |
| P-E02 | Betting against beta | Frazzini, Pedersen | 2014 | JFE 111(1):1-25 | E BAB | 已驗證 DOI；摘要取自 Semantic Scholar |
| P-E03 | Downside Risk | Ang, Chen, Xing | 2006 | RFS 19(4):1191-1239 | E 下方風險 | 已驗證 DOI；摘要取自搜尋轉述 |
| P-E04 | Benchmarks as Limits to Arbitrage: Understanding the Low-Volatility Anomaly | Baker, Bradley, Wurgler | 2011 | FAJ 67(1):40-54 | E 低波動異象 | 已驗證 DOI；摘要未取得 |

共 18 篇：A 類 7、B 類 3、C 類 4、E 類 4（P-A04 兼跨 A/C，只計一次）。台灣本地 2 篇 (P-A07、P-C04)，跨國含東亞 1 篇 (P-A06)。

通用資料源（已用 curl 確認網址回 200）：
- Ken French Data Library：https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html（頁面已見 Momentum Factor、Long-Term Reversal 系列；Short-Term Reversal 因輸出截斷未逐項確認，該庫一般有提供）。
- Open Source Asset Pricing：https://www.openassetpricing.com/ ，GitHub：https://github.com/OpenSourceAP/CrossSection （該庫是複製 200+ 個信號的程式碼；**各篇論文是否有對應信號未逐篇核對**）。
- AQR Data Sets：https://www.aqr.com/Insights/Datasets （已見 Betting Against Beta: Equity Factors Monthly/Daily、Value and Momentum Everywhere: Factors/Portfolios Monthly；**頁面文字中未找到 Time Series Momentum 因子資料集**）。
- 以上均為美國或國際「已建好的因子報酬」。**台股沒有現成公開因子庫被我確認**，需用 TEJ 等資料自行建構。

---

## P-A01 Returns to Buying Winners and Selling Losers（Jegadeesh & Titman 1993）

1. 標題：Returns to Buying Winners and Selling Losers: Implications for Stock Market Efficiency
2. 作者：Narasimhan Jegadeesh, Sheridan Titman
3. 年份：1993（Crossref issued 1993-03）
4. 期刊：The Journal of Finance 48(1), 65-91
5. DOI：https://doi.org/10.1111/j.1540-6261.1993.tb04702.x （已驗證 DOI）。免費版：未查證。
6. 市場/期間：美國股票（依記憶：NYSE/AMEX，1965-1989，待核對全文）。
7. 公式（標準化定義，依原文文字描述整理）：J 月形成期、K 月持有期的 $J\times K$ 策略。
   $R^{J}_{i,t}=\prod_{s=t-J}^{t-1}(1+r_{i,s})-1$；依 $R^{J}$ 排序分組，買最高組(winners)、賣最低組(losers)，持有 $K$ 個月；$WML_{t}=\bar r^{W}_{t}-\bar r^{L}_{t}$。常見版本 12-1：形成期為 t-12 至 t-2，跳過 t-1 月（跳過期是否為論文主設定：論文有「跳過一週」的變體，主設定細節待核對全文）。論文使用重疊持有的組合（每月 1/K 資金再平衡），權重為等權（依記憶，待核對）。
8. 變數：$r_{i,s}$ 股票 i 月報酬；$J$ 形成期月數（論文 3/6/9/12）；$K$ 持有期月數（3/6/9/12）；W/L 最高/最低十分位或組。
9. 直覺：投資人對資訊反應不足(underreaction)，中期趨勢延續；摘要另述 12 個月後部分報酬在之後兩年消退。
10. 驗證方法：排序分組、多空組合、風險調整（CAPM / 控制系統性風險）、事件研究（盈餘公告期報酬）。
11. 論文報告績效：摘要僅稱 3-12 個月持有期有顯著正報酬、非系統風險或對共同因子延遲反應所致；之後兩年部分消退（摘要）。具體月報酬與 t 值：尚未查證（需 Table 1）。
12. 程式碼/資料：Ken French 庫的 Momentum Factor (Mom) 為 2-12 的相近簡化版（非完全複製）；Open Source Asset Pricing 有動能信號（逐篇對應未核對）。
13. 台股/美股：美股適合（但需剔除微型股、考慮交易成本）。台股：散戶比重高、漲跌幅 10%、證交稅 0.3% 使換手成本高；台灣證據見 P-A06/P-A07，結論不一致，不建議照搬美股參數，需自行回測。
14. 限制：後續文獻發現 1990s 以後動能在美股減弱且有崩盤風險 (P-A05)；東亞動能弱 (P-A06)；轉換成交易策略須扣交易成本。

## P-A02 Time series momentum（Moskowitz, Ooi, Pedersen 2012）

1. Time series momentum
2. Tobias J. Moskowitz, Yao Hua Ooi, Lasse Heje Pedersen
3. 2012（Crossref issued 2012-05）
4. Journal of Financial Economics 104(2), 228-250
5. DOI：https://doi.org/10.1016/j.jfineco.2011.11.003 （已驗證 DOI）；SSRN：https://papers.ssrn.com/abstract=2089463 （由搜尋結果得到，curl 403 未能開啟，標「搜尋結果提供，未開啟」）
6. 市場/期間：58 種流動性工具，含股價指數、貨幣、商品、債券期貨（摘要）；期間依記憶約 1985-2009，待核對。
7. 公式（標準化定義，依原文文字描述整理）：以自身過去報酬預測未來報酬，並以事前波動度縮放：
   $\dfrac{r^{s}_{t}}{\sigma^{s}_{t-1}}=\alpha+\beta_h\dfrac{r^{s}_{t-h}}{\sigma^{s}_{t-h-1}}+\varepsilon_t$；
   策略：$r^{TSMOM,s}_{t,t+1}=\mathrm{sign}(r^{s}_{t-12,t})\dfrac{40\%}{\sigma^{s}_{t}}r^{s}_{t,t+1}$（40% 年化目標波動、12 個月回顧、1 個月持有為依記憶的主設定，待核對全文）。
8. 變數：$r^s_t$ 工具 s 的超額報酬；$\sigma$ 事前年化波動估計；$h$ 滯後月數；sign 為過去報酬方向。
9. 直覺：自身趨勢延續（初期反應不足、延遲過度反應），投機者獲利、避險者付出（摘要）。
10. 方法：預測迴歸（pooled / 各資產）、時間序列組合、對標準因子做迴歸。
11. 績效：摘要稱 58 工具皆有顯著時間序列動能；1-12 個月持續、之後部分反轉；分散化組合有異常報酬、極端市場表現最好（摘要，經搜尋轉述）。Sharpe 與 t 值：尚未查證。
12. 程式碼：AQR Data Sets 頁面文字**未找到** TSMOM 因子資料集（僅確認 BAB、Value and Momentum Everywhere）；GitHub 複製碼未查證。
13. 台股/美股：主體是期貨，非個股截面因子。可用於「個股自身趨勢」篩選或台灣加權指數擇時，但台股放空限制使 sign=-1 的空頭腿難執行；需以期貨/反向 ETF 變通。標「判斷」。
14. 限制：後續文獻（Kim, Tse, Wald）認為波動縮放貢獻大，去縮放後 alpha 由 1.27% 降至 0.41%（經 Quantpedia 二手轉述，未核對原文）；2010 年後 CTA 趨勢策略績效衰退（本欄為常識性說法，未逐篇查證）。

## P-A03 The 52-Week High and Momentum Investing（George & Hwang 2004）

1. The 52-Week High and Momentum Investing
2. Thomas J. George, Chuan-Yang Hwang
3. 2004（Crossref issued 2004-10）
4. The Journal of Finance 59(5), 2145-2176
5. DOI：https://doi.org/10.1111/j.1540-6261.2004.00695.x （已驗證 DOI）；免費版未查證
6. 市場：美國（依記憶 1963-2001，待核對）。
7. 公式（標準化定義，依原文文字描述整理）：$\mathrm{Near52}_{i,t}=\dfrac{P_{i,t-1}}{\max_{s\in[t-12,t-1]}P_{i,s}}$（價格接近 52 週高點的程度）；依此排序，買最高組、賣最低組，持有 6 個月（依記憶，待核對）。
8. 變數：$P$ 股價（收盤價）；分母為過去 52 週最高價。
9. 直覺：投資人以 52 週高點作錨定參考點，股價接近高點時不願意追價，造成反應不足。
10. 方法：排序分組、Fama-MacBeth 式迴歸（與過去報酬比較，依記憶）。
11. 績效：摘要稱 52 週高點解釋大部分動能利潤，且未來報酬不長期反轉，顯示短期動能與長期反轉大致是分離現象；具體數值尚未查證。
12. 程式碼：Open Source Asset Pricing 含 52 週高點相關信號（未逐項核對）；單獨可由價格資料自行計算。
13. 台股/美股：可用日價格輕易計算，台股漲跌幅限制可能使股價「卡」在高點，但屬判斷；建議回測。
14. 限制：後續研究多關注是否仍具超額報酬，本報告未查證衰退證據；仍受動能崩盤同類風險影響 (P-A05)。

## P-A04 Value and Momentum Everywhere（Asness, Moskowitz, Pedersen 2013）

1. Value and Momentum Everywhere
2. Clifford S. Asness, Tobias J. Moskowitz, Lasse Heje Pedersen
3. 2013（Crossref issued 2013-05-20）
4. The Journal of Finance 68(3), 929-985
5. DOI：https://doi.org/10.1111/jofi.12021 （已驗證 DOI）；資料：AQR Data Sets 頁已確認有「Value and Momentum Everywhere: Factors/Portfolios, Monthly」。
6. 市場：八種不同市場與資產類別（摘要）。**台灣：樣本未確認，不得宣稱含台灣。**
7. 公式（標準化定義，依原文文字描述整理）：價值=便宜度指標（個股用 B/M）；動能=過去 12 個月報酬（跳過最近 1 個月，依記憶）；因子=依排序給權重的多空組合，權重 $w_i\propto \mathrm{rank}(s_i)-\overline{\mathrm{rank}}$（依記憶，待核對）。
8. 變數：$s_i$ 排序指標；權重 rank 去中心化以使總和為零。
9. 直覺：價值與動能彼此負相關，混合後分散；共同風險含全球資金流動性風險（摘要）。
10. 方法：多資產排序組合、因子結構、三因子模型。
11. 績效：摘要稱各市場價值與動能溢酬一致，價值與動能彼此負相關；數值尚未查證。
12. 程式碼/資料：AQR Data Sets（已確認）。
13. 台股/美股：價值+動能組合概念適用；但因子資料不含台股，需自建。
14. 限制：之後文獻對價值溢酬衰退有爭議（本報告未逐篇查證）。

## P-A05 Momentum crashes（Daniel & Moskowitz 2016）

1. Momentum crashes
2. Kent Daniel, Tobias J. Moskowitz
3. 2016（Crossref 2016-11）
4. Journal of Financial Economics 122(2), 221-247
5. DOI：https://doi.org/10.1016/j.jfineco.2015.12.002 （已驗證 DOI）；NBER 免費版：https://www.nber.org/papers/w20439 （搜尋結果提供，未開啟全文）
6. 市場：美國（2013 版工作論文為 1927-2013 年，摘要稱跨期間、國際股票與其他資產皆穩健）。
7. 公式（標準化定義，依原文文字描述整理）：動態動能策略：依對動能報酬均值與變異數的預測調整曝險 $w^{*}_{t-1}=\dfrac{1}{2\lambda}\dfrac{\mu_{t-1}}{\sigma^{2}_{t-1}}$（依記憶，均值-變異數最適權重形式；$\mu,\sigma^2$ 的預測式細節未核對）。
8. 變數：$\mu_{t-1}$ 預測動能多空報酬均值；$\sigma^2_{t-1}$ 預測變異數；$\lambda$ 風險趨避。
9. 直覺：過去輸家在市場大跌後像選擇權（高 beta），市場反彈時輸家大漲，動能多空組合崩盤。
10. 方法：條件迴歸、動態策略樣本外檢驗。
11. 績效：摘要稱動能崩盤發生於「恐慌」狀態（大跌後、高波動），與市場反彈同時；動態策略使 alpha 與 Sharpe 約為靜態策略的兩倍（摘要，搜尋轉述）。
12. 程式碼：Daniel 個人網站有資料（未查證）；Ken French 動能報酬可重現主要序列。
13. 台股/美股：概念可轉移，台股市場風險 regime 切換亦會造成動能崩盤，但需自建。
14. 限制：本文即是動能風險文獻；動態策略為樣本內設計版本之樣本外表現未再核對。

## P-A06 Individualism and Momentum around the World（Chui, Titman, Wei 2010）

1. Individualism and Momentum around the World
2. Andy C. W. Chui, Sheridan Titman, K. C. John Wei
3. 2010（Crossref issued 2010-01-13）
4. The Journal of Finance 65(1), 361-392
5. DOI：https://doi.org/10.1111/j.1540-6261.2009.01532.x （已驗證 DOI）；IDEAS 頁無免費版連結。
6. 市場：41 個國家、超過 20,000 檔股票，1980-2003（HKUST 二手摘要）。**台灣是否在 41 國內：未能確認。**
7. 公式（標準化定義，依原文文字描述整理）：各國動能利潤 $MOM_c$（中期過去報酬排序的多空報酬）對 Hofstede 個人主義指數 $IDV_c$ 做橫斷面迴歸：$MOM_c=a+b\,IDV_c+\gamma' X_c+u_c$。
8. 變數：$IDV_c$ 國家 c 個人主義分數；$X_c$ 控制變數（成交量、波動、分析師分歧、交易成本、市值等）。
9. 直覺：個人主義文化→過度自信與自我歸因偏誤→動能較強；東亞動能弱。
10. 方法：各國動能組合+跨國迴歸。
11. 績效：摘要稱個人主義與交易量、波動及動能利潤正相關，控制其他變數後仍成立；HKUST 摘要稱東亞效果弱。各國數值尚未查證。
12. 程式碼：無；Hofstede 分數公開。
13. 台股/美股：重點啟示是「亞洲市場動能弱，不宜直接移植美股動能」。
14. 限制：國家層次樣本僅約 41 個觀察點；台灣明確數值需讀全文。

## P-A07 Momentum and Contrarian Profits ... Taiwan Stock Market（Wang, Huang, Huang 2012）

1. Momentum and Contrarian Profits Corresponding to the Coincident Economic Indicator on the Taiwan Stock Market
2. Ching-Ping Wang, Hung-Hsi Huang, Chi-Chung Huang
3. 2012（Crossref issued 2012-01）
4. Emerging Markets Finance and Trade 48（卷內增刊號 Crossref 顯示 pp. 29-40；期號未確認）
5. DOI：https://doi.org/10.2753/REE1540-496X4801S103 （已驗證 DOI）；IDEAS 頁已開啟。
6. 市場：台灣股市；樣本期間未取得。
7. 公式：依景氣同時指標狀態形成動能/反轉組合（標準化描述，細節未核對），非單一閉式公式。尚未查證。
8. 變數：景氣同時指標、規模組合、CAPM/FF 調整後報酬。
9. 直覺：動能/反轉利潤與景氣循環相關。
10. 方法：排序組合，CAPM 與 Fama-French 調整。
11. 績效：摘要稱平均而言動能與反轉策略皆無統計顯著利潤；贏家/輸家組合調整後皆有正超額報酬；同時指標與長期動能正相關（IDEAS 摘要轉述）。數值尚未查證。
12. 程式碼：尚未查證（台股資料多來自 TEJ，需授權）。
13. 台股/美股：台灣本地證據，直接相關。
14. 限制：樣本期、方法細節不明；單篇結論。

## P-B01 Evidence of Predictable Behavior of Security Returns（Jegadeesh 1990）

1. Evidence of Predictable Behavior of Security Returns
2. Narasimhan Jegadeesh
3. 1990（Crossref issued 1990-07）
4. The Journal of Finance 45(3), 881-898
5. DOI：https://doi.org/10.1111/j.1540-6261.1990.tb05110.x （已驗證 DOI）
6. 市場：美國，1934-1987（摘要）。
7. 公式（標準化定義，依原文文字描述整理）：1 個月報酬的橫斷面預測：$r_{i,t}=a_t+b_t\,r_{i,t-1}+u_{i,t}$（$b_t$ 預期為負）；短期反轉因子：依上月報酬排序，買上月輸家、賣上月贏家，持有 1 個月。論文另用多個落後期的橫斷面迴歸預測，再依預測值分十組（摘要）。
8. 變數：$r_{i,t-1}$ 上月報酬。
9. 直覺：流動性供給/過度反應的短期修正。
10. 方法：序列相關檢定、橫斷面迴歸、預測值排序十分位組合。
11. 績效：摘要：月報酬第一階序列相關顯著為負；12 個月落後呈強正相關；極端十分位組合的異常報酬差為每月 2.49%，期間 1934-1987。
12. 程式碼：Ken French 庫的 Short-Term Reversal Factor；公式簡單可自建。
13. 台股/美股：美股該效應在小型股、含買賣價差反彈的樣本較大。台股：散戶佔比高，短期反轉通常被認為較強（判斷，非查證），但雙邊成本（手續費+證交稅 0.3%）+月度高換手可吃掉大部分利潤。
14. 限制：後續文獻認為大部分利潤集中在小型股與流動性差的股票，且被交易成本侵蝕（一般共識，本報告未逐篇查證）。

## P-B02 Fads, Martingales, and Market Efficiency（Lehmann 1990）

1. Fads, Martingales, and Market Efficiency
2. Bruce N. Lehmann
3. 1990（Crossref issued 1990-02）
4. Quarterly Journal of Economics 105(1)，起始頁 1（Crossref 驗證；迄頁 28 為記憶，未驗證）
5. DOI：https://doi.org/10.2307/2937816 （已驗證 DOI；任務提示中未標 DOI，另外錯誤的 10.2307/2937928 是他篇，**勿用**）。免費版：NBER w2533 https://doi.org/10.3386/w2533 （已開啟 NBER 頁）
6. 市場：美國個股，週資料（NBER 摘要）；期間依記憶 1962-1986，待核對。
7. 公式（標準化定義，依原文文字描述整理）：逆向策略：$w_{i,t}=-\dfrac{1}{N}(r_{i,t-1}-\bar r_{t-1})$，$\;R_t=\sum_i w_{i,t}\,r_{i,t}$（依上週報酬的負相對權重，等同上週輸家買、贏家賣）。
8. 變數：$r_{i,t-1}$ 上週報酬；$\bar r_{t-1}$ 截面平均；N 檔數。
9. 直覺：週內基本面少有變動，週度反轉反映過度反應或流動性價格壓力。
10. 方法：週資料零成本逆向組合，並做薄交易/買賣價差調整與交易成本討論。
11. 績效：NBER 摘要稱週贏家次週反轉、輸家反彈，利潤在調整薄交易、價差、合理交易成本後仍存在；數值尚未查證。
12. 程式碼：無官方；公式簡單可自建。
13. 台股/美股：週度高換手，台股成本結構（證交稅 0.3%）極不利，需先回測再決定。
14. 限制：後續研究指出週反轉有很大部分來自買賣價差反彈與流動性（一般共識，未逐篇查證）。

## P-B03 Does the Stock Market Overreact?（De Bondt & Thaler 1985）

1. Does the Stock Market Overreact?
2. Werner F. M. De Bondt, Richard Thaler
3. 1985（Crossref 1985-07）
4. The Journal of Finance 40(3), 793-805
5. DOI：https://doi.org/10.1111/j.1540-6261.1985.tb05004.x （已驗證 DOI）
6. 市場：美國 CRSP 月資料（摘要）；期間依記憶 1926 起，待核對。
7. 公式（標準化定義，依原文文字描述整理）：形成期（3 至 5 年）累計超額報酬 $CU_{i}=\sum_{t=1}^{T}(r_{i,t}-r_{m,t})$；依 $CU$ 分出贏家組合 W 與輸家組合 L；測試期累計異常報酬差 $ACAR_L-ACAR_W$。
8. 變數：$r_m$ 市場報酬；T 形成期月數。
9. 直覺：投資人對劇烈壞消息過度反應，價格長期後修正。
10. 方法：事件時間累計異常報酬、贏家/輸家組合比較。
11. 績效：摘要稱經驗證據符合過度反應假說，輸家組合在形成後最多五年仍有特別大的一月報酬；數值尚未查證。
12. 程式碼：Ken French 庫的 Long-Term Reversal（已見，但定義為 13-60 個月報酬，與原論文不完全相同）。
13. 台股/美股：長期反轉需 3-5 年形成期，台股上市歷史較短且樣本小，月度表現不穩定（判斷）。
14. 限制：後續文獻指出與規模、價值效果重疊（Fama-French 1996 等，本報告未逐篇查證）。

## P-C01 The Cross-Section of Expected Stock Returns（Fama & French 1992）

1. The Cross-Section of Expected Stock Returns
2. Eugene F. Fama, Kenneth R. French
3. 1992（Crossref 1992-06）
4. The Journal of Finance 47(2), 427-465
5. DOI：https://doi.org/10.1111/j.1540-6261.1992.tb04398.x （已驗證 DOI）
6. 市場：美國 NYSE/AMEX/NASDAQ，依記憶 1963-1990，待核對。
7. 公式（標準化定義，依原文文字描述整理）：每月橫斷面 Fama-MacBeth 迴歸：$r_{i,t}=\gamma_{0,t}+\gamma_{1,t}\beta_{i}+\gamma_{2,t}\ln ME_{i}+\gamma_{3,t}\ln(BE/ME)_{i}+\gamma_{4,t}\,\mathrm{Lev}_i+\gamma_{5,t}(E/P)_i+\varepsilon$；特徵 $\ln(BE/ME)$ 使用上一年底帳面權益與 6 月底市值（時間對齊依記憶，待核對）。
8. 變數：ME 市值；BE 帳面權益；β 市場 beta；Lev 槓桿；E/P 盈餘市值比。
9. 直覺：規模與 B/M 捕捉風險與（或）錯誤定價，beta 本身解釋力為零。
10. 方法：Fama-MacBeth 橫斷面迴歸；β 先做規模分組。
11. 績效：摘要稱規模與 B/M 吸收槓桿、E/P 與 beta 所含的平均報酬資訊；加入規模後 beta 與平均報酬關係平坦（摘要）。係數與 t 值尚未查證（需 Table）。
12. 程式碼/資料：Ken French 庫提供 Size/B-M 分組報酬與因子。
13. 台股/美股：美股適合；台股：見 P-C04，B/M 效果在台灣的本地證據不一致。
14. 限制：後續文獻（含 Fama-French 本人）指出價值溢酬在 2000s 之後衰退；美股小型股效果近乎消失（一般共識，本報告未逐篇查證）。

## P-C02 Common risk factors in the returns on stocks and bonds（Fama & French 1993）

1. Common risk factors in the returns on stocks and bonds
2. Eugene F. Fama, Kenneth R. French
3. 1993（Crossref 1993-02）
4. Journal of Financial Economics 33(1), 3-56
5. DOI：https://doi.org/10.1016/0304-405X(93)90023-5 （已驗證 DOI）；免費版連結（Semantic Scholar 提供，未開啟）：http://www.nes.ru/~agoriaev/Papers/Fama-French%205%20factors%20for%20stocks%20and%20vonds%20JFE93.pdf
6. 市場：美國股票與債券，依記憶 1963-1991，待核對。
7. 公式（標準化定義，依原文文字描述整理）：$R_{i,t}-R_{f,t}=a_i+b_i(R_{m,t}-R_{f,t})+s_i\,SMB_t+h_i\,HML_t+\varepsilon_{i,t}$；SMB=小型股組合減大型股組合；HML=高 B/M 組合減低 B/M 組合（2x3 排序，NYSE 分位點，市值加權，6 月再平衡——依記憶，待核對）。
8. 變數：$SMB$ 規模因子；$HML$ 價值因子。
9. 直覺：規模與 B/M 代表共同風險因子（相對財務困境）。
10. 方法：時間序列迴歸、25 組合。
11. 績效：Crossref 無摘要，績效尚未查證。
12. 程式碼/資料：Ken French 庫 F-F_Research_Data_Factors（SMB、HML）。
13. 台股/美股：美股標準；台股需自建（見 P-C04）。
14. 限制：HML 在 2007 年後表現弱（一般共識）；Fama-French 2015 五因子後 HML 被質疑為冗餘（未查證）。

## P-C03 Contrarian Investment, Extrapolation, and Risk（Lakonishok, Shleifer, Vishny 1994）

1. Contrarian Investment, Extrapolation, and Risk
2. Josef Lakonishok, Andrei Shleifer, Robert W. Vishny
3. 1994（Crossref 1994-12）
4. The Journal of Finance 49(5), 1541-1578
5. DOI：https://doi.org/10.1111/j.1540-6261.1994.tb04772.x （已驗證 DOI）
6. 市場：美國，依記憶 1963-1990，待核對。
7. 公式（標準化定義，依原文文字描述整理）：價值指標：$B/M$、$C/P$（現金流/價格）、$E/P$，以及銷售成長 GS；每年依指標排序成十分位組合，持有 1-5 年，比較價值股與成長股報酬。
8. 變數：C 現金流；P 價格；GS 過去銷售成長。
9. 直覺：價值股被過度悲觀外推，報酬較高是行為偏誤而非風險（摘要）。
10. 方法：十分位排序、持有期報酬、檢驗風險（下跌市況表現、貝塔）。
11. 績效：摘要只稱價值策略績效較佳且非因風險較高；數值尚未查證。
12. 程式碼：無官方；Open Source Asset Pricing 有 BM、CF/P、EP 信號（未逐項核對）。
13. 台股/美股：台股有 PBR、PER 資料，易於實作；但見 P-C04 台灣 B/M 不穩定。
14. 限制：後續對「價值是風險或錯誤定價」仍有爭論；價值陷阱。

## P-C04 The Absence of the Book-to-Market Effect in the Taiwan Stock Market（Chiao, Hung, Yao）

1. The Absence of the Book-to-Market Effect in the Taiwan Stock Market: A Decomposition Approach
2. Chaoshin Chiao, Weifeng Hung, Chun Yao
3. 2009 線上（Crossref issued 2009-04-08）；IDEAS 列 2010 年 6 月紙本
4. Japanese Economic Review 61(2), 289-299
5. DOI：https://doi.org/10.1111/j.1468-5876.2009.00485.x （已驗證 DOI）；IDEAS 頁已開啟：https://ideas.repec.org/a/bla/jecrev/v61y2010i2p289-299.html
6. 市場：台灣股市；樣本期間尚未查證。
7. 公式（標準化定義，依原文文字描述整理）：採 Daniel-Titman (2006) 的 B/M 分解：$\ln(B/M)_t=\ln(B_{t-5}/M_{t-5})+\text{(5 年帳面報酬)}-\text{(5 年市場報酬)}$，即將 B/M 拆為「無形資產報酬 vs 有形資產」部分（具體定義依記憶，待核對）。
8. 變數：intangible return（市場報酬中不被帳面成長解釋的部分）。
9. 直覺：台灣 R&D 密集（電子）公司低 B/M 且過去表現好、未來也好，掩蓋了 B/M 效果。
10. 方法：B/M 分解後做報酬預測（細節未核對）。
11. 績效：IDEAS 摘要：台灣 R&D 密集公司未來報酬與無形報酬無顯著負相關；R&D 公司低估可能解釋 B/M 效果不存在；無數值。
12. 程式碼：無。
13. 台股/美股：直接台灣證據，提醒 B/M 單因子在台股可能無效，價值因子需搭配其他指標（判斷）。
14. 限制：單篇、期間不明；結論僅適用該樣本，後來台股是否出現 B/M 效果尚未查證。

## P-E01 The Cross-Section of Volatility and Expected Returns（Ang, Hodrick, Xing, Zhang 2006）

1. The Cross-Section of Volatility and Expected Returns
2. Andrew Ang, Robert J. Hodrick, Yuhang Xing, Xiaoyan Zhang
3. 2006（Crossref 2006-01-20）
4. The Journal of Finance 61(1), 259-299
5. DOI：https://doi.org/10.1111/j.1540-6261.2006.00836.x （已驗證 DOI）
6. 市場：美國（依記憶 1963-2000，待核對）。
7. 公式（標準化定義，依原文文字描述整理）：特質波動 $IVOL_{i,t}=\sqrt{\mathrm{Var}(\varepsilon_{i,d})}$，其中日報酬對 FF3 迴歸：$r_{i,d}-r_{f,d}=a+b\,MKT_d+s\,SMB_d+h\,HML_d+\varepsilon_{i,d}$，以過去 1 個月日資料估計（依記憶）；聚合波動率風險：對 VIX 變動 $\Delta VIX$ 的敏感度 $\beta_{VIX}$。
8. 變數：$\varepsilon$ 殘差；$\Delta VIX$ 聚合波動創新。
9. 直覺：高特質波動股票平均報酬反而極低（反常）；對聚合波動風險暴露高者報酬低（與理論一致）。
10. 方法：依 IVOL / $\beta_{VIX}$ 排序分組、控制規模/B/M/動能/流動性。
11. 績效：摘要稱高特質波動股票平均報酬「極低(abysmally low)」，不能被聚合波動風險、規模、B/M、動能與流動性解釋；數值尚未查證。
12. 程式碼：Open Source Asset Pricing 有 IdioVol 信號（未逐項核對）；公式簡單可自建。
13. 台股/美股：台股日資料易算；但散戶偏好彩券型股票使效果可能更明顯（判斷）；放空限制使空頭腿（買低 IVOL 賣高 IVOL）難實現；漲跌停會扭曲日波動估計。
14. 限制：後續文獻指出效果主要來自小型/低價股，與前月報酬反轉重疊（一般共識，未逐篇查證）。

## P-E02 Betting against beta（Frazzini & Pedersen 2014）

1. Betting against beta
2. Andrea Frazzini, Lasse Heje Pedersen
3. 2014（Crossref 2014-01）
4. Journal of Financial Economics 111(1), 1-25
5. DOI：https://doi.org/10.1016/j.jfineco.2013.10.005 （已驗證 DOI）；Semantic Scholar 提供開放版：https://www.sciencedirect.com/science/article/pii/S0304405X13002675/pdf （CC BY-NC-ND，未開啟）。AQR 頁：https://www.aqr.com/Insights/Research/Journal-Article/Betting-Against-Beta （curl 200）
6. 市場：美國股票、20 個全球股票市場、國債、公司債、期貨（摘要）。台灣：未確認是否含。
7. 公式（標準化定義，依原文文字描述整理）：$\beta_i^{ts}=\hat\rho\,\dfrac{\hat\sigma_i}{\hat\sigma_m}$，收縮：$\beta_i=w\,\beta_i^{ts}+(1-w)\cdot 1$（$w=0.6$ 為依記憶）。BAB：$r^{BAB}_{t+1}=\dfrac{1}{\beta^{L}_t}(r^{L}_{t+1}-r_f)-\dfrac{1}{\beta^{H}_t}(r^{H}_{t+1}-r_f)$，其中 L/H 為低/高 beta 組合。
8. 變數：$\hat\rho$ 與市場相關係數(5 年)；$\hat\sigma$ 波動（1 年日資料）；$\beta^L,\beta^H$ 組合 beta。
9. 直覺：槓桿限制投資人哄抬高 beta 資產；低 beta 資產需槓桿放大才有同等風險報酬。
10. 方法：beta 排序組合，槓桿到 beta=1，FF/動能四因子 alpha。
11. 績效：摘要稱各資產類別 BAB 皆有顯著風險調整報酬；資金限制收緊時 BAB 報酬低。數值尚未查證。
12. 資料：AQR Data Sets 的 BAB 因子（已確認頁面有 Equity Factors Monthly/Daily）；
13. 台股/美股：BAB 需槓桿放大低 beta 多頭並放空高 beta，台股融資融券成本與放空限制不利；可改做「僅多方低 beta」版本，但那已不是原策略（判斷）。
14. 限制：後續研究質疑 BAB 的穩健度與成本（未逐篇查證）；對利率上升敏感（BAB 隱含債券多頭，判斷）。

## P-E03 Downside Risk（Ang, Chen, Xing 2006）

1. Downside Risk
2. Andrew Ang, Joseph Chen, Yuhang Xing
3. 2006（Crossref 2006）
4. Review of Financial Studies 19(4), 1191-1239
5. DOI：https://doi.org/10.1093/rfs/hhj035 （已驗證 DOI）；工作論文：https://www.nber.org/papers/w11824 （搜尋結果出現，curl 未單獨測試）
6. 市場：美國，依記憶 1963-2001，待核對。
7. 公式（標準化定義，依原文文字描述整理）：下方 beta：$\beta^{-}_i=\dfrac{\mathrm{Cov}(r_i,r_m\mid r_m<\mu_m)}{\mathrm{Var}(r_m\mid r_m<\mu_m)}$；下方-上方差 $\beta^{-}-\beta^{+}$。
8. 變數：$\mu_m$ 市場平均報酬；條件為市場低於平均的期間。
9. 直覺：市場下跌時與市場同跌的股票，需要風險補償。
10. 方法：依 $\beta^-$ 排序，控制 beta、規模、B/M。
11. 績效：搜尋摘要轉述：下方風險溢酬約每年 6%，不被 beta、coskewness、流動性及 FF 因子解釋；早期工作論文為 6.55%（二手轉述，數值待查證原文）。
12. 程式碼：無官方；Open Source Asset Pricing 有 Beta 相關信號（未核對是否為 downside beta）。
13. 台股/美股：日資料可自算；注意台股漲跌停截斷。
14. 限制：Atilgan, Demirtas, Gunaydin (2020) 重現原結果在等權 NYSE 樣本，但價值加權或加入其他控制/延長樣本則消失（搜尋轉述，未核對原文）。

## P-E04 Benchmarks as Limits to Arbitrage（Baker, Bradley, Wurgler 2011）

1. Benchmarks as Limits to Arbitrage: Understanding the Low-Volatility Anomaly
2. Malcolm Baker, Brendan Bradley, Jeffrey Wurgler
3. 2011（Crossref 2011-01）
4. Financial Analysts Journal 67(1), 40-54
5. DOI：https://doi.org/10.2469/faj.v67.n1.4 （已驗證 DOI）；SSRN：https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1585031 （由 Semantic Scholar 提供，curl 403，未開啟）
6. 市場：美國；期間依記憶 1968-2008，待核對。
7. 公式（標準化定義，依原文文字描述整理）：依過去 60 個月月報酬波動度（或 beta）排序五分位，持有一個月，比較報酬：$\sigma_{i,t}=\mathrm{std}(r_{i,t-60:t-1})$。
8. 變數：$\sigma$ 波動度。
9. 直覺：以相對基準(tracking error)為目標的經理人沒有動機持有低波動股票，導致低波動股相對被低估。
10. 方法：波動度/beta 排序組合比較。
11. 績效：摘要未取得，數值尚未查證。
12. 程式碼：無；公式簡單。
13. 台股/美股：台股法人比重較美股低，基準約束論點的適用性需另行檢驗；多方低波動版本易實作，成本低（判斷）。
14. 限制：低波動投資後續擁擠與利率敏感（一般共識，未查證）。

---

## 附錄：公式來源類型統計

18 篇的公式全部為「標準化定義（依原文文字描述整理）」；0 篇為「原文公式」（因無法取得全文）。計算或設定細節標「依記憶，待核對」者，網站上線前須逐項對照全文。
