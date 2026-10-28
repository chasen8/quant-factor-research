"""命令列：python -m engine.cli build --demo --out web/public/data"""
from __future__ import annotations

import argparse
import sys

from .export import build


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="engine.cli")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="計算並輸出網站讀的 JSON")
    b.add_argument("--demo", action="store_true", help="使用合成示範資料（M1 唯一支援）")
    b.add_argument("--out", required=True, help="輸出目錄，如 web/public/data")
    b.add_argument("--n-stocks", type=int, default=None, help="覆寫每市場股票數（測試用）")
    args = ap.parse_args(argv)
    if args.cmd == "build":
        if not args.demo:
            print("目前只支援 --demo", file=sys.stderr)
            return 2
        build(args.out, demo=True, n_stocks=args.n_stocks)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
