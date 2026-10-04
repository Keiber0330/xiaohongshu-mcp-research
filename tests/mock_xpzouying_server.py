"""MOCK of xpzouying/xiaohongshu-mcp's read-only tools, serving the synthetic
fixtures in tests/fixtures/. Used only to test tests/run_live_check.py plumbing.
Returns JSON as text content, like the real server does."""
import json
import os
import sys
from pathlib import Path

from fastmcp import FastMCP

FX = Path(__file__).parent / "fixtures"
mcp = FastMCP("mock-xiaohongshu-mcp")


def _t(name):
    return (FX / name).read_text(encoding="utf-8")


@mcp.tool
def check_login_status() -> str:
    return "MOCK: 已登录"


@mcp.tool
def search_feeds(keyword: str) -> str:
    if os.environ.get("MOCK_EMPTY_SEARCH"):  # reproduce "logged in but 0 notes"
        return json.dumps({"feeds": [], "count": 0})
    return _t("xpz_search_feeds.json")


@mcp.tool
def get_feed_detail(feed_id: str, xsec_token: str, load_all_comments: bool = False, limit: int = 20) -> str:
    f = {"fixture00000000000000000a": "xpz_feed_detail_a.json", "fixture00000000000000000b": "xpz_feed_detail_b_video.json"}
    return _t(f[feed_id])


@mcp.tool
def user_profile(user_id: str, xsec_token: str) -> str:
    feeds = json.loads(_t("xpz_search_feeds.json"))["feeds"][:1]
    return json.dumps({"userBasicInfo": {"nickname": "FIXTURE作者1"}, "interactions": [], "feeds": feeds}, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=int(sys.argv[1]) if len(sys.argv) > 1 else 18999, show_banner=False)
