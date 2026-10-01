# Claude Code MCP setup

Both servers were verified in this research to complete the MCP handshake and
`tools/list` (see `../results/`). Live data access was **not** verified.

## xpzouying/xiaohongshu-mcp (Streamable HTTP, port 18060)

Start the server yourself first (it keeps a browser + login session):

```bash
./xiaohongshu-login-<platform>          # one-time QR-code login, writes cookies.json
./xiaohongshu-mcp-<platform>            # serves http://localhost:18060/mcp
# optional: require a bearer token
AUTH_TOKEN=change-me ./xiaohongshu-mcp-<platform>
```

```bash
claude mcp add --transport http xiaohongshu-mcp http://localhost:18060/mcp
# with AUTH_TOKEN set:
claude mcp add --transport http xiaohongshu-mcp http://localhost:18060/mcp \
  --header "Authorization: Bearer change-me"
```

## JoeanAmier/XHS-Downloader

Option A — stdio (recommended: nothing listens on the network):

```bash
claude mcp add xhs-downloader \
  --env XHS_DOWNLOADER_DIR=/abs/path/XHS-Downloader \
  -- /abs/path/XHS-Downloader/.venv/bin/python /abs/path/xiaohongshu-mcp-research/tools/xhs_downloader_stdio.py
```

Option B — upstream HTTP mode. Note it binds **0.0.0.0:5556 with no auth**;
use a firewall or run it only on a trusted network.

```bash
python main.py mcp
claude mcp add --transport http xhs-downloader http://127.0.0.1:5556/mcp
```

Verify inside Claude Code with `/mcp`.
