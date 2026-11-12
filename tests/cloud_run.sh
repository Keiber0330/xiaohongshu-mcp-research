#!/usr/bin/env bash
# Run xpzouying/xiaohongshu-mcp inside a Claude Code cloud session and test it.
#
# Needs a cloud environment whose network can reach *.xiaohongshu.com,
# *.xhscdn.com and cdn.one-world.ai (e.g. an "unrestricted" environment).
#
#   tests/cloud_run.sh setup            # clone pinned upstream tag + build
#   tests/cloud_run.sh start [visible]  # start server on 127.0.0.1:18060 (visible = Xvfb + -headless=false)
#   tests/cloud_run.sh qr OUT.png       # fetch login QR code (valid 4 min) -> send to the user to scan
#   tests/cloud_run.sh status           # login status
#   tests/cloud_run.sh check KEYWORD [run_live_check args...]
#   tests/cloud_run.sh stop
#   tests/cloud_run.sh cleanup          # stop + delete cookies and token (do this at the end)
#
# Server binds 127.0.0.1 only and requires a random Bearer token kept in $WORK/token.
# Cookies live in $WORK/cookies.json, outside the repo. Nothing is committed.
set -euo pipefail

TAG="${XHS_MCP_TAG:-v2.7.4}"
WORK="${XHS_WORK:-$HOME/xhs-cloud}"
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ADDR="127.0.0.1:18060"
BASE="http://$ADDR"
mkdir -p "$WORK"
chmod 700 "$WORK"

token() { cat "$WORK/token"; }
api() { curl -sS --max-time "${2:-90}" -H "Authorization: Bearer $(token)" "$BASE$1"; }

case "${1:-}" in
setup)
  if [ ! -d "$WORK/src" ]; then
    git clone -q --depth 1 --branch "$TAG" https://github.com/xpzouying/xiaohongshu-mcp.git "$WORK/src"
  fi
  (cd "$WORK/src" && git log -1 --format='upstream %h %cs %s' && go build -o "$WORK/xiaohongshu-mcp" .)
  echo "built $WORK/xiaohongshu-mcp ($TAG)"
  ;;
start)
  [ -s "$WORK/token" ] || { python3 -c 'import secrets;print(secrets.token_urlsafe(24))' > "$WORK/token"; chmod 600 "$WORK/token"; }
  headless=true; wrap=()
  if [ "${2:-}" = "visible" ]; then headless=false; wrap=(xvfb-run -a -s "-screen 0 1440x900x24"); fi
  cd "$WORK"
  AUTH_TOKEN="$(token)" COOKIES_PATH="$WORK/cookies.json" \
    nohup "${wrap[@]}" "$WORK/xiaohongshu-mcp" -port "$ADDR" -headless="$headless" > "$WORK/server.log" 2>&1 &
  echo $! > "$WORK/server.pid"
  echo "starting (headless=$headless); first start downloads the bundled browser (~150MB)..."
  for _ in $(seq 1 180); do
    if curl -s -o /dev/null --max-time 2 "$BASE/health"; then echo "server up: $BASE/mcp"; exit 0; fi
    if ! kill -0 "$(cat "$WORK/server.pid")" 2>/dev/null; then echo "server exited:"; tail -20 "$WORK/server.log"; exit 1; fi
    sleep 2
  done
  echo "server did not come up in 6 min"; tail -20 "$WORK/server.log"; exit 1
  ;;
qr)
  out="${2:?usage: qr OUT.png}"
  api /api/v1/login/qrcode 120 | python3 -c '
import base64, json, sys
r = json.load(sys.stdin)
d = r.get("data") or {}
if not r.get("success"):
    sys.exit("qrcode failed: %s" % r)
if d.get("is_logged_in"):
    print("already logged in"); sys.exit(0)
img = d.get("img", "")
b64 = img.split(",", 1)[1] if img.startswith("data:") else img
open(sys.argv[1], "wb").write(base64.b64decode(b64))
print("QR saved to %s; scan within %s" % (sys.argv[1], d.get("timeout")))
' "$out"
  ;;
status)
  api /api/v1/login/status; echo
  ;;
check)
  kw="${2:?usage: check KEYWORD}"; shift 2
  cd "$REPO_DIR"
  XHS_MCP_TOKEN="$(token)" uv run tests/run_live_check.py --url "$BASE/mcp" --keyword "$kw" --out results/live_cloud "$@"
  ;;
stop)
  if [ -f "$WORK/server.pid" ]; then kill "$(cat "$WORK/server.pid")" 2>/dev/null || true; rm -f "$WORK/server.pid"; fi
  pkill -f "$WORK/xiaohongshu-mcp" 2>/dev/null || true
  echo stopped
  ;;
cleanup)
  "$0" stop
  rm -f "$WORK/cookies.json" "$WORK/token"
  echo "deleted cookies and token in $WORK"
  ;;
*)
  sed -n '2,16p' "$0"; exit 2 ;;
esac
