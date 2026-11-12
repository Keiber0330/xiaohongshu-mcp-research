# Handoff: run the live test in a cloud session

For a new Claude Code session on an environment with unrestricted network
(e.g. "Claude-Full-Access"), on branch `claude/xiaohongshu-mcp-research-wpsoxf`.

1. `tests/cloud_run.sh setup` — builds upstream xpzouying/xiaohongshu-mcp **v2.7.4**
   (contains search fixes for the 0-results symptom seen in October, see REPORT.md F.1b).
2. `tests/cloud_run.sh start` — server on 127.0.0.1:18060 with a random token.
3. `tests/cloud_run.sh qr <scratchpad>/qr.png`, send the PNG to the user (SendUserFile),
   ask them to scan it in the Xiaohongshu app within 4 minutes; then `tests/cloud_run.sh status`.
4. `tests/cloud_run.sh check 咖啡` — read-only 20-item check -> `results/live_cloud/matrix.md`.
   If search reports a security verification (ErrVerificationRequired) or login loss: STOP,
   do not retry, do not try to get around it; record it.
   If headless search keeps returning 0 notes, try once with `stop` + `start visible`.
5. Export: `python3 tools/xhs_export.py results/live_cloud/export results/live_cloud/raw_*_search.json results/live_cloud/raw_*_detail_*.json --keyword 咖啡`
6. Update REPORT.md (F.1, F.1b, final answer) with the measured results; commit only
   `matrix.md` + export (raw_*.json contain other users' public data and xsec tokens — keep out of git).
7. `tests/cloud_run.sh cleanup` — deletes cookies and token. Tell the user they can also
   remove the web login device in the Xiaohongshu app.

Do not ask the user for passwords or cookies. Do not use write tools (publish/comment/like).
