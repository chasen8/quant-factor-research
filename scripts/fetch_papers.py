"""論文下載助手：逐篇在瀏覽器開啟 DOI 頁面，你手動按下載，腳本自動把新 PDF 改名搬到論文資料夾。

用法（先連上學校 VPN，在 PowerShell 執行）：
    C:\\trading-data\\quant-factors\\venv\\Scripts\\python.exe scripts\\fetch_papers.py
選項：
    --priority 高        只處理某優先序（高／中／低；預設全部）
    --downloads PATH     瀏覽器下載資料夾（預設 %USERPROFILE%\\Downloads）

每篇開啟後：在瀏覽器點「Download PDF」即可，腳本偵測到新 PDF 會自動歸檔並開下一篇。
等待時按 s = 跳過這篇、q = 結束。已存在的檔案會自動略過，可隨時中斷再續跑。
這是你本人在瀏覽器操作的半自動流程，不會自動抓取或繞過任何登入。
"""
from __future__ import annotations

import argparse
import msvcrt
import re
import shutil
import sys
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIST_MD = ROOT / "docs" / "papers-to-fetch.md"
PAPERS_DIR = Path(r"C:\trading-data\quant-factors\papers")
PARTIAL_SUFFIXES = (".crdownload", ".part", ".tmp", ".download")

ROW = re.compile(
    r"^\|\s*(?P<prio>[^|]+?)\s*\|\s*(?P<id>\d{2}[ab]:P-[A-Z]\d{2})\s*\|\s*(?P<title>[^|]+?)\s*\|"
    r".*?\]\((?P<doi_url>https://doi\.org/[^)]+)\).*?`(?P<fname>[^`]+\.pdf)`\s*\|\s*$"
)


def load_list(priority: str | None) -> list[dict]:
    rows = []
    for line in LIST_MD.read_text(encoding="utf-8").splitlines():
        m = ROW.match(line)
        if not m or m["prio"].startswith("不需下載"):
            continue
        if priority and m["prio"] != priority:
            continue
        rows.append(m.groupdict())
    return rows


def pdfs(folder: Path) -> dict[Path, float]:
    return {p: p.stat().st_mtime for p in folder.glob("*.pdf")}


def wait_for_new_pdf(folder: Path, before: dict[Path, float]) -> Path | str:
    """回傳新下載完成的 PDF 路徑，或使用者按的 's'/'q'。"""
    while True:
        if msvcrt.kbhit():
            key = msvcrt.getwch().lower()
            if key in ("s", "q"):
                return key
        if any(p.suffix.lower() in PARTIAL_SUFFIXES for p in folder.iterdir()):
            time.sleep(1)
            continue
        new = [p for p, t in pdfs(folder).items() if p not in before or t > before[p]]
        if new:
            p = max(new, key=lambda x: x.stat().st_mtime)
            size = -1
            while size != p.stat().st_size:  # 等檔案大小穩定
                size = p.stat().st_size
                time.sleep(1.5)
            return p
        time.sleep(1)


def is_pdf(p: Path) -> bool:
    with p.open("rb") as fh:
        return fh.read(5) == b"%PDF-"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--priority", choices=["高", "中", "低"])
    ap.add_argument("--downloads", type=Path, default=Path.home() / "Downloads")
    args = ap.parse_args()

    PAPERS_DIR.mkdir(parents=True, exist_ok=True)
    rows = load_list(args.priority)
    todo = [r for r in rows if not (PAPERS_DIR / r["fname"]).exists()]
    print(f"清單 {len(rows)} 篇，已有 {len(rows) - len(todo)} 篇，待下載 {len(todo)} 篇。")
    print(f"下載資料夾：{args.downloads}\n歸檔到：{PAPERS_DIR}\n")

    skipped = []
    for i, r in enumerate(todo, 1):
        print(f"[{i}/{len(todo)}] {r['prio']}｜{r['id']}｜{r['title']}")
        before = pdfs(args.downloads)
        webbrowser.open(r["doi_url"])
        print("   已開啟頁面，請在瀏覽器下載 PDF（s=跳過，q=結束）…", flush=True)
        got = wait_for_new_pdf(args.downloads, before)
        if got == "q":
            break
        if got == "s":
            skipped.append(r["id"])
            print("   已跳過。\n")
            continue
        if not is_pdf(got):
            skipped.append(r["id"])
            print(f"   ⚠ {got.name} 不是有效 PDF（可能是登入頁），已略過，原檔保留。\n")
            continue
        dest = PAPERS_DIR / r["fname"]
        shutil.move(str(got), dest)
        print(f"   ✓ {got.name} → {dest.name}\n")

    missing = [r["id"] for r in rows if not (PAPERS_DIR / r["fname"]).exists()]
    print(f"完成。仍缺 {len(missing)} 篇：{', '.join(missing) if missing else '無'}")
    if skipped:
        print(f"本次跳過：{', '.join(skipped)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
