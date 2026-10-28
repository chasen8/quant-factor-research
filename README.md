# 量化 Alpha 因子研究平台（MVP）

從學術論文與 GitHub 開源程式整理出 **36 個公式明確、可程式化的量化因子**，提供搜尋、公式、程式碼、來源追溯、因子評估圖表、因子比較與回測展示。

> ⚠️ **目前所有績效數字都是「示範資料」（決定性合成資料），不是真實研究結果，也不是投資建議。**
> 每個因子的「文獻實證」欄位才是論文原始報告的結論；本平台尚未對真實市場做獨立回測（所有因子驗證等級為 L0）。

- 線上版：https://chasen8.github.io/quant-factor-research/
- 研究報告：[`docs/research/00-summary.md`](docs/research/00-summary.md)（GitHub 調查、39 篇論文、因子資料庫、驗證方法、網站規劃）

## 證據標籤

| 標籤 | 意義 |
|---|---|
| 文獻實證 | 論文原始報告的結果（附出處與樣本期間） |
| 自行回測 | 本平台用自己的資料重算（目前尚無） |
| 尚未驗證 | 只有公式，沒有可引用的績效證據 |
| 示範資料 | 合成資料，只用來展示介面 |

## 目錄

```
factors/        因子、論文、repo 的 YAML（單一真實來源）
engine/         Python 引擎：示範資料、前處理、IC/分組/衰減評估、回測、安全公式 DSL、JSON 匯出
tests/          pytest
web/            Next.js 靜態網站（讀 web/public/data 的 JSON）
docs/           研究報告、資料合約、章程
scripts/web.sh  在 OneDrive 外的鏡像目錄執行 npm（避免 node_modules 進雲端同步）
```

## 本機執行

需求：Python 3.13、Node 22。

### 1. Python 引擎（可選；示範 JSON 已提交在 repo 內）

```bash
py -3.13 -m venv C:\trading-data\quant-factors\venv          # venv 放在 OneDrive 外
C:\trading-data\quant-factors\venv\Scripts\python.exe -m pip install -r requirements.txt
C:\trading-data\quant-factors\venv\Scripts\python.exe -m pytest tests -q
C:\trading-data\quant-factors\venv\Scripts\python.exe -m engine.cli build --demo --out web/public/data
```

### 2. 網站

```bash
bash scripts/web.sh install   # 第一次
bash scripts/web.sh dev       # 開發伺服器 http://localhost:3000
bash scripts/web.sh test      # 前端測試
bash scripts/web.sh build     # 靜態輸出到鏡像目錄的 out/
```

不在 OneDrive 內開發的話，也可以直接 `cd web && npm install && npm run dev`。

**不需要任何 API key 就能啟動。**

## 部署

推送到 `main` 時，GitHub Actions（`.github/workflows/deploy.yml`）會依序：跑 pytest → 建置 Next.js 靜態站 → 部署到 GitHub Pages。

## 安全

- 金鑰只放 `.env`（已 gitignore），前端不持有任何金鑰。
- 使用者自訂公式（第二階段）只走 `engine/dsl` 的 AST 白名單解析器，絕不 `eval`。
- 論文 PDF 與行情原始資料不進 git。

## 資料與授權

- 因子程式碼為本專案撰寫；參考的開源專案與授權見 `factors/repos.yaml`（GPL／無授權專案只作概念參考，未複製程式碼）。
- 示範資料為合成資料。日後接真實資料時，免費來源會有存活者偏誤與估計的財報公告日，結果頁會自動標示。
