# 本專案踩坑記錄

## 2026-10-28｜論文全文抓不到，DOI 驗證改走 Crossref
- 現象：Elsevier（JFE）、OUP（RFS）、SSRN 對 curl/WebFetch 一律回 403，拿不到全文公式與 Table 數字。
- 做法：書目驗證一律用 `curl -s "https://api.crossref.org/works/<DOI>"`；全文找 arXiv、NBER working paper、作者個人頁。
- 教訓：派工給的 DOI「提示」錯了 2 個（Lehmann 1990、Gervais 等人 2001），所以就算是自己給的線索也必須實查，不能直接採用。
- 因子公式拿不到原文時一律標「標準化定義」，並保留「待核對」標示直到有人讀過全文。

- 2026-10-29｜Blave 免費的只有台股價格日線（CDN／電腦版「公開」資料）；**月營收、財報比率、個股三大法人都要付費 API 方案**（blave.org/docs/zh/data_twstock）。Blave 策略庫列表頁只有全期間回測數字，沒有 OOS 期間與 MCPT p 值，不能當驗證過的證據。Threads 貼文圖片 WebFetch 看不到，要用 curl 下載 og 圖片網址後用 Read 看。
