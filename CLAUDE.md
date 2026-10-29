# 量化 Alpha 因子研究平台

從 GitHub 開源碼與學術論文整理「公式明確、可程式化、可回測」的量化因子，建成可搜尋、可比較、可視覺化、可驗證的研究網站（初期：台股、美股；加密貨幣為未來擴充）。
目前狀態：Step 1～5 已完成（2026-10-28），總報告 `docs/research/00-summary.md`。Step 6 MVP 開發**須等使用者回覆總報告第 7 節後**才開始。

## 本專案特有約定
- 研究產出放 `docs/research/`；總報告 `docs/research/00-summary.md`。
- 證據標籤三分：`文獻實證`（論文原始報告）／`自行回測`（本專案重算）／`尚未驗證`。絕不混用。
- 不可虛構論文、DOI、GitHub 網址、Stars、License；查不到寫「尚未查證」。
- 示範資料一律在 UI 與資料檔標「示範資料」，不得當研究結果。
- 行情資料、Parquet、DuckDB 檔放 `C:\trading-data\quant-factors\`（不進 OneDrive）。
- 不碰任何有交易權限的 API key；本專案只做研究與回測。
- 使用者公式輸入不得用 eval；只走白名單 AST／運算子 DSL。

## 路由
- 全域準則（環境坑、派工、判斷、維護）：`C:\Users\chris\.claude\CLAUDE.md` 會自動載入，衝突時本檔優先。
- 決策與進度：`docs/project-charter.md`。
- 本專案踩坑：`docs/lessons.md`。
- 給 Codex／其他 AI 的濃縮守則：`AGENTS.md`（改本檔或全域規則時同步它）。
- 因子定義唯一來源：`factors/factors.yaml`（直接手改，不要重跑 trading-data 裡的生成腳本）；測試：`C:\trading-data\quant-factors\venv\Scripts\python.exe -m pytest tests -q`。
