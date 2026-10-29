# AGENTS.md — 給 Codex 與其他 AI 工具的專案守則

量化 Alpha 因子研究平台：整理論文與開源專案中可程式化的因子，用台股、加密貨幣資料做**預先登記、扣成本、樣本外、蒙地卡羅檢定**的實證，並以靜態網站展示。使用者 chris，**一律用繁體中文溝通**。

## 開工前先讀
1. `docs/project-charter.md` 的「目前狀態」和「決策記錄」。決策記錄的格式是：日期｜決定｜原因｜何時可推翻。
2. `docs/lessons.md`：本專案踩過的坑。
3. 要做實驗時，讀 `docs/experiments/` 裡最新的 EXP-xxx 預先登記檔和結果檔。

## 鐵律（違反即停）
- **金鑰**：API key、secret 只放 `.env` 或環境變數。不可寫進程式碼、文件、commit 或回覆。不建立、也不使用有交易權限的 key，本專案只做研究。
- **大檔不進專案資料夾**：專案在 OneDrive 同步範圍內。行情資料、Parquet、DuckDB、venv、node_modules、論文 PDF 一律放 `C:\trading-data\quant-factors\`。論文 PDF 有版權，絕不進 git。
- **花錢、註冊帳號、付費資料**：一律先問使用者。目前的決定是只用免費資料。
- **不可虛構**論文、DOI、GitHub 網址、Stars、License。DOI 用 `https://api.crossref.org/works/<DOI>` 核對，查不到就寫「尚未查證」。
- **使用者輸入的公式不可用 eval**：只能走 `engine/dsl` 的 AST 白名單。

## 研究紀律
- 一次只測一個策略。程式動手前先寫 `docs/experiments/EXP-xxx-*.md` 預先登記並 commit。
- **預先登記檔 commit 後，正文一個字都不能改**。只能在文末「偏離記錄」追加內容，`git diff` 必須只有新增行。
- 不可依 IS 或 OOS 結果調參數。OOS 只跑一次；除錯時只用 IS 或合成資料。
- 合格標準要同時打贏：等權基準 B1、MCPT（統計量用相對 B1 的超額報酬）、市場代表標的（台股 0050／幣圈 BTC）。同一批測多個策略時，p 值要做 Holm 校正。
- 證據標籤有四種：`文獻實證`、`自行回測`、`尚未驗證`、`示範資料`，絕不混用。示範資料必須在 UI 和資料檔上標明。
- 數字要抽查：從原始資料獨立重算 2–3 筆再提交。

## 環境（Windows 11）
- PowerShell 是 5.1，沒有 `&&`；POSIX 指令改用 Git Bash。路徑含中文與空白，一律加雙引號。
- Python 一律用 `C:\trading-data\quant-factors\venv\Scripts\python.exe`（3.13）。不要用裸的 `python`，它會跑到 3.12。讀寫檔一律 `encoding="utf-8"`。
- 測試指令：`C:\trading-data\quant-factors\venv\Scripts\python.exe -m pytest tests -q`
- **npm 只能透過 `bash scripts/web.sh install|add|build|test|lint|dev` 執行**，它會在 OneDrive 外的鏡像目錄跑。禁止在 `web/` 內直接 `npm install`。
- 因子定義的唯一來源是 `factors/factors.yaml`，直接手改。`C:\trading-data\quant-factors\scratch\` 裡的生成腳本不要重跑，會覆蓋手改的內容。
- 資料快取：台股在 `C:\trading-data\quant-factors\blave-cdn\`（Blave CDN）；幣圈在 `C:\trading-data\quant-factors\binance-spot\`（data.binance.vision）。

## Git 與部署
- 推到 `main` 會觸發 GitHub Actions，依序跑 pytest、next build，**然後部署到公開網站** https://chasen8.github.io/quant-factor-research/ 。push 前測試必須全過。
- 只在使用者要求時 commit 或 push。

## 與 CLAUDE.md 的關係
`CLAUDE.md` 是 Claude Code 用的版本，本檔是它加上使用者全域守則的濃縮版。兩者衝突時，以 `docs/project-charter.md` 的最新決策為準。修改任一份規則時，要同步另一份。
