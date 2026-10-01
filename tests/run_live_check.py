# /// script
# requires-python = ">=3.10"
# dependencies = ["fastmcp>=2.10"]
# ///
"""Live capability test for xpzouying/xiaohongshu-mcp (+ optional XHS-Downloader).

Run this on YOUR machine, after you have logged in with xiaohongshu-login and
started xiaohongshu-mcp. It makes a small number of read-only calls with
pauses in between, then writes a PASS/FAIL/PARTIAL/NOT SUPPORTED matrix.

    uv run tests/run_live_check.py --keyword 咖啡
    XHS_MCP_TOKEN=<AUTH_TOKEN> uv run tests/run_live_check.py --keyword 咖啡
    uv run tests/run_live_check.py --keyword 咖啡 --xhsdl-url http://127.0.0.1:5556/mcp

Only read-only tools are called (search_feeds, get_feed_detail, user_profile,
check_login_status; XHS-Downloader get_detail_data). Nothing is posted,
liked, or commented.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import random
import sys
import time
from pathlib import Path

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


def make_client(url: str, token: str = "") -> Client:
    """Client for a Streamable-HTTP MCP server, with optional Bearer token
    (matches xiaohongshu-mcp's AUTH_TOKEN)."""
    headers = {"Authorization": f"Bearer {token}"} if token else None
    return Client(StreamableHttpTransport(url, headers=headers))

ITEMS = [
    "搜索关键词", "获取搜索结果", "获取笔记 ID", "获取笔记标题", "获取正文", "获取发布时间",
    "获取作者昵称", "获取作者 ID", "获取点赞数", "获取收藏数", "获取评论数", "获取分享数",
    "获取图片 URL", "获取视频 URL", "获取评论内容", "获取评论用户", "获取作者主页",
    "获取作者历史笔记", "分页", "批量请求",
]
READ_ONLY_TOOLS = {"search_feeds", "get_feed_detail", "user_profile", "check_login_status", "get_detail_data"}


class Run:
    def __init__(self, out: Path, pause: float):
        self.out, self.pause = out, pause
        self.results: dict[str, tuple[str, str]] = {}
        self.calls = 0

    def mark(self, item: str, status: str, evidence: str = ""):
        self.results[item] = (status, evidence[:160])

    async def call(self, c: Client, tool: str, args: dict, tag: str):
        assert tool in READ_ONLY_TOOLS, tool
        if self.calls:
            await asyncio.sleep(self.pause + random.uniform(0, self.pause / 2))
        self.calls += 1
        t0 = time.time()
        res = await c.call_tool(tool, args, raise_on_error=False)
        text = next((x.text for x in res.content if getattr(x, "type", "") == "text"), "")
        raw = {"tool": tool, "args": args, "is_error": res.is_error, "seconds": round(time.time() - t0, 1),
               "structured": res.structured_content, "text": text}
        (self.out / f"raw_{self.calls:02d}_{tag}.json").write_text(json.dumps(raw, ensure_ascii=False, indent=2))
        print(f"  [{self.calls}] {tool} {tag}: is_error={res.is_error} {raw['seconds']}s")
        if res.is_error:
            return None, text
        if res.structured_content and not (set(res.structured_content) == {"result"}):
            return res.structured_content, text
        try:
            return json.loads(text), text
        except json.JSONDecodeError:
            return None, text


def nonempty(v) -> bool:
    # "0" is a legitimate count; only missing/blank values fail
    return v not in (None, "", [], {})


async def test_xpzouying(url: str, keyword: str, n_detail: int, r: Run, token: str = ""):
    async with make_client(url, token) as c:
        tools = {t.name: t for t in await c.list_tools()}
        print(f"tools/list: {len(tools)} tools")
        login, txt = await r.call(c, "check_login_status", {}, "login")
        print("  login:", (txt or "")[:120].replace("\n", " "))

        search, txt = await r.call(c, "search_feeds", {"keyword": keyword}, "search")
        feeds = [f for f in (search or {}).get("feeds", []) if f.get("modelType", "note") == "note"]
        r.mark(ITEMS[0], "PASS" if search is not None else "FAIL", txt if search is None else f"keyword={keyword}")
        r.mark(ITEMS[1], "PASS" if feeds else "FAIL", f"{len(feeds)} notes")
        if not feeds:
            return
        f0 = feeds[0]
        card = f0.get("noteCard", {})
        r.mark(ITEMS[2], "PASS" if f0.get("id") else "FAIL", f0.get("id", ""))
        r.mark(ITEMS[3], "PASS" if any(f.get("noteCard", {}).get("displayTitle") for f in feeds) else "FAIL",
               card.get("displayTitle", ""))

        # detail for a few notes, preferring to include one video note
        videos = [f for f in feeds if f.get("noteCard", {}).get("type") == "video"]
        picks = ([videos[0]] if videos else []) + [f for f in feeds if f not in videos[:1]]
        picks = picks[:n_detail]
        details = []
        for i, f in enumerate(picks):
            args = {"feed_id": f["id"], "xsec_token": f.get("xsecToken", "")}
            if i == 0:
                args |= {"load_all_comments": True, "limit": 30}
            d, txt = await r.call(c, "get_feed_detail", args, f"detail_{f['id']}")
            if d:
                details.append(d)
        notes = [d.get("data", {}).get("note", {}) for d in details]
        comments = [cm for d in details for cm in d.get("data", {}).get("comments", {}).get("list", [])]

        def check(item, getter, label):
            vals = [getter(n) for n in notes]
            ok = [v for v in vals if nonempty(v)]
            status = "PASS" if notes and len(ok) == len(vals) else ("PARTIAL" if ok else "FAIL")
            r.mark(item, status, f"{len(ok)}/{len(vals)} {label}; e.g. {str(ok[0])[:60] if ok else ''}")

        check(ITEMS[4], lambda n: n.get("desc"), "notes have desc")
        check(ITEMS[5], lambda n: n.get("time"), "notes have time")
        check(ITEMS[6], lambda n: (n.get("user") or {}).get("nickname"), "nickname")
        check(ITEMS[7], lambda n: (n.get("user") or {}).get("userId"), "userId")
        check(ITEMS[8], lambda n: (n.get("interactInfo") or {}).get("likedCount"), "likedCount")
        check(ITEMS[9], lambda n: (n.get("interactInfo") or {}).get("collectedCount"), "collectedCount")
        check(ITEMS[10], lambda n: (n.get("interactInfo") or {}).get("commentCount"), "commentCount")
        check(ITEMS[11], lambda n: (n.get("interactInfo") or {}).get("sharedCount"), "sharedCount")
        imgs = [n for n in notes if n.get("type") != "video"]
        r.mark(ITEMS[12], "PASS" if imgs and all(n.get("imageList") for n in imgs) else
               ("NOT TESTED" if not imgs else "FAIL"), f"{len(imgs)} image notes")
        vids = [n for n in notes if n.get("type") == "video"]
        vurl = [s.get("masterUrl") for n in vids for st in ((n.get("video") or {}).get("media") or {}).get("stream", {}).values() for s in st]
        r.mark(ITEMS[13], "PASS" if any(vurl) else ("NOT TESTED" if not vids else "FAIL"),
               f"{len(vids)} video notes in sample")
        r.mark(ITEMS[14], "PASS" if any(cm.get("content") for cm in comments) else "FAIL", f"{len(comments)} top-level comments")
        r.mark(ITEMS[15], "PASS" if any((cm.get("userInfo") or {}).get("nickname") for cm in comments) else "FAIL", "")

        # author profile + history notes
        u = card.get("user", {})
        prof, txt = await r.call(c, "user_profile", {"user_id": u.get("userId", ""), "xsec_token": f0.get("xsecToken", "")}, "profile")
        r.mark(ITEMS[16], "PASS" if prof and (prof.get("userBasicInfo") or {}).get("nickname") else "FAIL",
               (prof or {}).get("userBasicInfo", {}).get("nickname", txt[:80]))
        r.mark(ITEMS[17], "PASS" if prof and prof.get("feeds") else "FAIL", f"{len((prof or {}).get('feeds') or [])} notes (first page only)")

        # pagination: search tool exposes no page/cursor arg; comments can scroll-load
        schema = getattr(tools["search_feeds"], "input_schema", None) or tools["search_feeds"].inputSchema
        props = set((schema or {}).get("properties", {}))
        has_page = bool(props & {"page", "cursor", "page_size", "offset"})
        first = details[0].get("data", {}).get("comments", {}).get("list", []) if details else []
        r.mark(ITEMS[18], "PASS" if has_page else ("PARTIAL" if len(first) > 10 else "NOT SUPPORTED"),
               f"search params={sorted(props)}; comments loaded with limit=30: {len(first)}")
        r.mark(ITEMS[19], "PARTIAL" if len(details) > 1 else "FAIL",
               f"no batch tool; {len(details)}/{len(picks)} sequential detail calls succeeded")


async def test_xhsdl(url: str, note_urls: list[str], r: Run):
    async with make_client(url) as c:
        for i, u in enumerate(note_urls):
            d, txt = await r.call(c, "get_detail_data", {"url": u}, f"xhsdl_{i}")
            data = (d or {}).get("data") or {}
            print(f"    XHS-Downloader {u[:70]} -> {'OK' if data.get('作品ID') else 'EMPTY'} {d and d.get('message')}")


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:18060/mcp")
    ap.add_argument("--token", default=os.environ.get("XHS_MCP_TOKEN", ""),
                    help="Bearer token = the AUTH_TOKEN the server was started with (or env XHS_MCP_TOKEN)")
    ap.add_argument("--keyword", required=True)
    ap.add_argument("--details", type=int, default=3, help="how many notes to open (keep small)")
    ap.add_argument("--pause", type=float, default=6.0, help="seconds between calls")
    ap.add_argument("--xhsdl-url", default="", help="XHS-Downloader MCP url, e.g. http://127.0.0.1:5556/mcp")
    ap.add_argument("--out", default="results/live")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    r = Run(out, a.pause)
    try:
        await test_xpzouying(a.url, a.keyword, a.details, r, a.token)
    except Exception as e:  # report, don't hide
        print("xpzouying test aborted:", repr(e))
    for item in ITEMS:
        r.results.setdefault(item, ("FAIL", "not reached"))
    if a.xhsdl_url:
        urls = []
        for p in sorted(out.glob("raw_*_search.json")):
            s = json.loads(p.read_text())
            body = s["structured"] or json.loads(s["text"] or "{}")
            urls += [f"https://www.xiaohongshu.com/explore/{f['id']}?xsec_token={f.get('xsecToken','')}&xsec_source=pc_search"
                     for f in body.get("feeds", [])[:2] if f.get("modelType", "note") == "note"]
        await test_xhsdl(a.xhsdl_url, urls, r)

    md = ["| # | 能力 | 结果 | 证据 |", "|---|---|---|---|"]
    md += [f"| {i+1} | {k} | {r.results[k][0]} | {r.results[k][1].replace('|', '/')} |" for i, k in enumerate(ITEMS)]
    (out / "matrix.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))
    print(f"\nraw responses + matrix.md in {out}/ ; export with:\n"
          f"  python tools/xhs_export.py {out}/export {out}/raw_*_search.json {out}/raw_*_detail_*.json --keyword {a.keyword}")


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
