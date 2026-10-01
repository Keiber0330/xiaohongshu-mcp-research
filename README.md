# xiaohongshu-mcp-research

Research and feasibility check of open-source MCP servers and tools for reading
Xiaohongshu (小红书 / RED / RedNote) data. **Read [REPORT.md](REPORT.md).**

| Path | What |
|---|---|
| `REPORT.md` | Full report (Chinese): candidates, comparison, install log, security review, test results, risks |
| `results/` | Real outputs from this environment: MCP `tools/list` dumps, probe results, export samples |
| `tools/xhs_export.py` | Normalize MCP JSON output → `notes.json` / `notes.csv` / `comments.csv` (stdlib only) |
| `tools/xhs_downloader_stdio.py` | Run XHS-Downloader's MCP server over stdio (fixes upstream stdio bug) |
| `tests/run_live_check.py` | Run on your own machine to get the 20-item PASS/FAIL matrix against a live, logged-in server |
| `tests/mcp_probe.py` | Generic Streamable-HTTP MCP probe (list tools, call one) |
| `tests/xpzouying/zz_mcp_discovery_test.go` | In-process MCP discovery test for xpzouying/xiaohongshu-mcp (copy into its repo root) |
| `tests/fixtures/` | **Synthetic** fixtures (not real data) for exporter tests |
| `configs/` | Claude Code / Claude Desktop MCP config examples |

No Xiaohongshu data was collected: the platform's domains are blocked from the
environment this research ran in.

```bash
python3 -m pytest tests -q        # exporter tests (5)
```
