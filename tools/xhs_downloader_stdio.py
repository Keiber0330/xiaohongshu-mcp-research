#!/usr/bin/env python3
"""Run JoeanAmier/XHS-Downloader's own MCP server over stdio (for Claude Desktop).

The upstream `python main.py mcp` serves Streamable HTTP on 0.0.0.0:5556 with
no authentication. This launcher reuses the same XHS.run_mcp_server() and only
switches the transport to stdio, so nothing listens on the network.

usage: XHS_DOWNLOADER_DIR=/path/to/XHS-Downloader python xhs_downloader_stdio.py
"""
import asyncio
import os
import sys

repo = os.environ.get("XHS_DOWNLOADER_DIR") or os.getcwd()
os.chdir(repo)  # settings.json / Volume/ are resolved relative to the repo
sys.path.insert(0, repo)

# MCP stdio owns stdout; route the app's console output (rich) to stderr.
_real_stdout = sys.stdout
sys.stdout = sys.stderr

from fastmcp import FastMCP  # noqa: E402
from source import Settings, XHS  # noqa: E402

# Upstream run_mcp_server() always passes host/port/log_level, which fastmcp's
# stdio runner rejects (TypeError). Drop them for the stdio transport only.
_orig_run_async = FastMCP.run_async


async def _run_async(self, transport=None, **kwargs):
    if transport == "stdio":
        for k in ("host", "port", "log_level"):
            kwargs.pop(k, None)
    return await _orig_run_async(self, transport=transport, **kwargs)


FastMCP.run_async = _run_async


async def main():
    async with XHS(**Settings().run()) as xhs:
        sys.stdout = _real_stdout
        await xhs.run_mcp_server(transport="stdio")


if __name__ == "__main__":
    asyncio.run(main())
