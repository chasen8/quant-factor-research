#!/usr/bin/env bash
# Run npm for web/ in a mirror outside OneDrive, so node_modules/.next/out never land in the synced folder.
# Source of truth stays in <repo>/web; the mirror is disposable.
#   bash scripts/web.sh install        # npm install (copies package-lock.json back to web/)
#   bash scripts/web.sh add <pkg...>   # npm install <pkg...> (copies package.json + lock back)
#   bash scripts/web.sh build|test|lint|dev
set -euo pipefail
# Git Bash 會把 NEXT_PUBLIC_BASE_PATH=/xxx 當成路徑轉成 C:/Program Files/Git/xxx，傳給 node 前必須關掉轉換。
export MSYS_NO_PATHCONV=1

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC_WIN="$(cygpath -w "$ROOT/web")"
MIRROR="/c/trading-data/quant-factors/web-build"
MIRROR_WIN="$(cygpath -w "$MIRROR")"

sync_to_mirror() {
  mkdir -p "$MIRROR"
  # /MIR mirrors source; excluded dirs are neither copied nor purged in the mirror. Exit codes < 8 are success.
  MSYS_NO_PATHCONV=1 robocopy "$SRC_WIN" "$MIRROR_WIN" /MIR /XD node_modules .next out /NFL /NDL /NJH /NJS /NP >/dev/null || [ $? -lt 8 ]
}

copy_back() {
  for f in "$@"; do
    [ -f "$MIRROR/$f" ] && cp "$MIRROR/$f" "$ROOT/web/$f"
  done
}

cmd="${1:-}"; shift || true
sync_to_mirror
cd "$MIRROR"
case "$cmd" in
  install) npm install; copy_back package-lock.json ;;
  add)     npm install "$@"; copy_back package.json package-lock.json ;;
  build)   npm run build ;;
  test)    npm test ;;
  lint)    npm run lint ;;
  dev)     npm run dev ;;
  *) echo "usage: bash scripts/web.sh install|add <pkg...>|build|test|lint|dev" >&2; exit 2 ;;
esac
