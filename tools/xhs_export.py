#!/usr/bin/env python3
"""Normalize Xiaohongshu MCP tool output into flat JSON + CSV.

Accepts the JSON returned by these MCP tools (one JSON document per file):

  xpzouying/xiaohongshu-mcp
    search_feeds / list_feeds   -> {"feeds": [...], "count": N}
    get_feed_detail             -> {"feed_id": "...", "data": {"note": {...}, "comments": {...}}}
    user_profile / get_my_profile -> {"userBasicInfo": {...}, "interactions": [...], "feeds": [...]}
  JoeanAmier/XHS-Downloader
    get_detail_data             -> {"message": "...", "data": {"作品ID": ...}}

Records for the same note_id are merged; non-empty fields from a detail call
override the sparser search-card fields.

Usage:
  python tools/xhs_export.py OUT_DIR INPUT.json [INPUT.json ...] [--keyword K]
Writes OUT_DIR/notes.json, OUT_DIR/notes.csv, OUT_DIR/comments.csv.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

NOTE_FIELDS = [
    "note_id", "title", "description", "author_name", "author_id",
    "publish_time", "likes", "favorites", "comments", "shares",
    "image_urls", "video_url", "note_url", "keyword", "crawl_time",
    # extra columns that are useful for follow-up calls / provenance
    "note_type", "ip_location", "tags", "xsec_token", "source",
]
COMMENT_FIELDS = [
    "note_id", "comment_id", "parent_comment_id", "content", "user_name",
    "user_id", "like_count", "create_time", "ip_location", "source",
]
VIDEO_CODEC_PREFERENCE = ("h264", "h265", "av1", "h266")


def _ms_to_iso(ms) -> str:
    if not ms:
        return ""
    try:
        return datetime.fromtimestamp(int(ms) / 1000, tz=timezone.utc).isoformat()
    except (TypeError, ValueError, OSError):
        return ""


def _note_url(note_id: str, xsec_token: str = "") -> str:
    if not note_id:
        return ""
    url = f"https://www.xiaohongshu.com/explore/{note_id}"
    return f"{url}?xsec_token={xsec_token}&xsec_source=pc_search" if xsec_token else url


def _interact(info: dict) -> dict:
    info = info or {}
    return {
        "likes": info.get("likedCount", ""),
        "favorites": info.get("collectedCount", ""),
        "comments": info.get("commentCount", ""),
        # xpzouying's struct calls it sharedCount; the raw page state uses shareCount
        "shares": info.get("sharedCount", info.get("shareCount", "")),
    }


def _pick_video_url(video: dict | None) -> str:
    if not video:
        return ""
    streams = ((video.get("media") or {}).get("stream")) or {}
    for codec in VIDEO_CODEC_PREFERENCE + tuple(k for k in streams if k not in VIDEO_CODEC_PREFERENCE):
        for s in streams.get(codec) or []:
            if s.get("masterUrl"):
                return s["masterUrl"]
            if s.get("backupUrls"):
                return s["backupUrls"][0]
    return ""


# ---------------------------------------------------------------- xpzouying

def _from_feed_card(feed: dict) -> dict:
    card = feed.get("noteCard") or {}
    user = card.get("user") or {}
    cover = card.get("cover") or {}
    note_id = feed.get("id", "")
    token = feed.get("xsecToken", "")
    return {
        "note_id": note_id,
        "title": card.get("displayTitle", ""),
        "author_name": user.get("nickname") or user.get("nickName", ""),
        "author_id": user.get("userId", ""),
        **_interact(card.get("interactInfo")),
        "image_urls": [u for u in [cover.get("urlDefault") or cover.get("url")] if u],
        "note_url": _note_url(note_id, token),
        "note_type": card.get("type", ""),
        "xsec_token": token,
        "source": "xpzouying:feed_card",
    }


def _from_feed_detail(doc: dict) -> tuple[dict, list[dict]]:
    data = doc.get("data") or {}
    note = data.get("note") or {}
    user = note.get("user") or {}
    note_id = note.get("noteId") or doc.get("feed_id", "")
    token = note.get("xsecToken", "")
    rec = {
        "note_id": note_id,
        "title": note.get("title", ""),
        "description": note.get("desc", ""),
        "author_name": user.get("nickname") or user.get("nickName", ""),
        "author_id": user.get("userId", ""),
        "publish_time": _ms_to_iso(note.get("time")),
        **_interact(note.get("interactInfo")),
        "image_urls": [i.get("urlDefault") or i.get("urlPre") for i in note.get("imageList") or []
                       if i.get("urlDefault") or i.get("urlPre")],
        "video_url": _pick_video_url(note.get("video")),
        "note_url": _note_url(note_id, token),
        "note_type": note.get("type", ""),
        "ip_location": note.get("ipLocation", ""),
        "xsec_token": token,
        "source": "xpzouying:get_feed_detail",
    }
    comments = []

    def walk(items, parent=""):
        for c in items or []:
            u = c.get("userInfo") or {}
            comments.append({
                "note_id": c.get("noteId") or note_id,
                "comment_id": c.get("id", ""),
                "parent_comment_id": parent,
                "content": c.get("content", ""),
                "user_name": u.get("nickname") or u.get("nickName", ""),
                "user_id": u.get("userId", ""),
                "like_count": c.get("likeCount", ""),
                "create_time": _ms_to_iso(c.get("createTime")),
                "ip_location": c.get("ipLocation", ""),
                "source": "xpzouying:get_feed_detail",
            })
            walk(c.get("subComments"), c.get("id", ""))

    walk((data.get("comments") or {}).get("list"))
    return rec, comments


# --------------------------------------------------------- XHS-Downloader

def _from_xhs_downloader(d: dict) -> dict:
    urls = d.get("下载地址") or []
    if isinstance(urls, str):
        urls = urls.split()
    is_video = d.get("作品类型") == "视频"
    ts = d.get("时间戳")
    return {
        "note_id": d.get("作品ID", ""),
        "title": d.get("作品标题", ""),
        "description": d.get("作品描述", ""),
        "author_name": d.get("作者昵称", ""),
        "author_id": d.get("作者ID", ""),
        "publish_time": _ms_to_iso(ts * 1000) if ts else d.get("发布时间", ""),
        "likes": d.get("点赞数量", ""),
        "favorites": d.get("收藏数量", ""),
        "comments": d.get("评论数量", ""),
        "shares": d.get("分享数量", ""),
        "image_urls": [] if is_video else list(urls),
        "video_url": urls[0] if is_video and urls else "",
        "note_url": d.get("作品链接", "") or _note_url(d.get("作品ID", "")),
        "note_type": d.get("作品类型", ""),
        "tags": d.get("作品标签", ""),
        "source": "xhs-downloader:get_detail_data",
    }


# ------------------------------------------------------------------ driver

def parse_document(doc) -> tuple[list[dict], list[dict]]:
    """Return (note_records, comment_records) for one tool result."""
    # MCP CallToolResult dumped as-is: unwrap the text content.
    if isinstance(doc, dict) and "content" in doc and isinstance(doc["content"], list):
        texts = [c.get("text") for c in doc["content"] if c.get("type") == "text"]
        doc = json.loads(texts[0]) if texts else {}
    # raw_*.json written by tests/run_live_check.py / tests/mcp_probe.py
    if isinstance(doc, dict) and "structured" in doc:
        if doc.get("is_error"):
            return [], []
        if doc["structured"] and set(doc["structured"]) != {"result"}:
            doc = doc["structured"]
        elif doc.get("text"):
            doc = json.loads(doc["text"])

    if isinstance(doc, dict) and "feeds" in doc:  # search_feeds / list_feeds / user_profile
        return [_from_feed_card(f) for f in doc["feeds"] or []
                if f.get("modelType", "note") == "note"], []
    if isinstance(doc, dict) and "feed_id" in doc and "data" in doc:
        rec, comments = _from_feed_detail(doc)
        return [rec], comments
    if isinstance(doc, dict) and "data" in doc and "message" in doc:
        d = doc["data"] or {}
        return ([_from_xhs_downloader(d)] if d.get("作品ID") else []), []
    if isinstance(doc, dict) and "作品ID" in doc:
        return [_from_xhs_downloader(doc)], []
    raise ValueError("unrecognized document shape")


def merge(records: list[dict]) -> list[dict]:
    merged: dict[str, dict] = {}
    for r in records:
        cur = merged.setdefault(r["note_id"], {})
        for k, v in r.items():
            if v not in ("", None, []) or k not in cur:
                if k == "source" and cur.get("source") and v not in cur["source"]:
                    v = f"{cur['source']}+{v}"
                cur[k] = v
    return list(merged.values())


def export(paths: list[str], out_dir: str, keyword: str = "", crawl_time: str = "") -> dict:
    notes, comments, errors = [], [], []
    for p in paths:
        try:
            with open(p, encoding="utf-8") as f:
                n, c = parse_document(json.load(f))
        except (OSError, ValueError, json.JSONDecodeError) as e:
            errors.append(f"{p}: {e}")
            continue
        ct = crawl_time or datetime.fromtimestamp(os.path.getmtime(p), tz=timezone.utc).isoformat()
        for r in n:
            r.setdefault("crawl_time", ct)
        notes += n
        comments += c

    notes = merge([r for r in notes if r.get("note_id")])
    for r in notes:
        r["keyword"] = keyword or r.get("keyword", "")
        for k in NOTE_FIELDS:
            r.setdefault(k, "")

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "notes.json").write_text(json.dumps(notes, ensure_ascii=False, indent=2), encoding="utf-8")
    # utf-8-sig so Excel on Windows opens Chinese text correctly
    with open(out / "notes.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=NOTE_FIELDS, extrasaction="ignore")
        w.writeheader()
        for r in notes:
            w.writerow({**r, "image_urls": "|".join(r["image_urls"]) if isinstance(r["image_urls"], list) else r["image_urls"]})
    with open(out / "comments.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=COMMENT_FIELDS)
        w.writeheader()
        w.writerows(comments)
    return {"notes": len(notes), "comments": len(comments), "errors": errors}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out_dir")
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--keyword", default="")
    ap.add_argument("--crawl-time", default="", help="ISO time; default = input file mtime")
    a = ap.parse_args(argv)
    summary = export(a.inputs, a.out_dir, a.keyword, a.crawl_time)
    print(json.dumps(summary, ensure_ascii=False))
    return 1 if summary["errors"] and not summary["notes"] else 0


if __name__ == "__main__":
    sys.exit(main())
