"""Tests for tools/xhs_export.py against synthetic fixtures (see fixtures/README.md)."""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import xhs_export  # noqa: E402

FX = ROOT / "tests" / "fixtures"


def run(tmp_path, *names, **kw):
    s = xhs_export.export([str(FX / n) for n in names], str(tmp_path), crawl_time="2026-10-01T00:00:00+00:00", **kw)
    rows = list(csv.DictReader(open(tmp_path / "notes.csv", encoding="utf-8-sig")))
    return s, {r["note_id"]: r for r in rows}


def test_search_cards_filter_non_notes(tmp_path):
    s, rows = run(tmp_path, "xpz_search_feeds.json", keyword="FIXTURE关键词")
    assert s["notes"] == 2 and "fixture_hot_query" not in rows
    a = rows["fixture00000000000000000a"]
    assert a["title"] == "FIXTURE 标题 A" and a["likes"] == "1.2万" and a["keyword"] == "FIXTURE关键词"
    assert a["description"] == "" and a["publish_time"] == ""  # search cards carry neither
    assert rows["fixture00000000000000000b"]["author_name"] == "FIXTURE作者2"  # nickName fallback


def test_detail_merges_over_search_card(tmp_path):
    s, rows = run(tmp_path, "xpz_search_feeds.json", "xpz_feed_detail_a.json", "xpz_feed_detail_b_video.json")
    a = rows["fixture00000000000000000a"]
    assert a["description"].startswith("FIXTURE 正文") and "\n" in a["description"]
    assert a["publish_time"] == "2025-09-16T05:20:00+00:00"
    assert (a["likes"], a["favorites"], a["comments"], a["shares"]) == ("12000", "789", "56", "34")
    assert a["image_urls"] == "https://example.invalid/a1.webp|https://example.invalid/a2.webp"
    assert a["source"] == "xpzouying:feed_card+xpzouying:get_feed_detail"
    assert rows["fixture00000000000000000b"]["video_url"] == "https://example.invalid/b_h264.mp4"
    comments = list(csv.DictReader(open(tmp_path / "comments.csv", encoding="utf-8-sig")))
    assert [(c["comment_id"], c["parent_comment_id"]) for c in comments] == [
        ("fixturecomment01", ""), ("fixturecomment02", "fixturecomment01")]


def test_xhs_downloader_shape(tmp_path):
    s, rows = run(tmp_path, "xhsdl_get_detail_data.json")
    c = rows["fixture00000000000000000c"]
    assert c["author_id"] == "fixtureuser0000000000003" and c["favorites"] == "10"
    assert c["image_urls"].count("|") == 1 and c["video_url"] == ""
    assert json.load(open(tmp_path / "notes.json"))[0]["tags"] == "FIXTURE标签1 FIXTURE标签2"


def test_header_has_requested_columns(tmp_path):
    run(tmp_path, "xhsdl_get_detail_data.json")
    header = next(csv.reader(open(tmp_path / "notes.csv", encoding="utf-8-sig")))
    required = ("note_id title description author_name author_id publish_time likes favorites "
                "comments shares image_urls video_url note_url keyword crawl_time").split()
    assert header[:len(required)] == required


def test_failed_fetch_yields_no_rows(tmp_path):
    p = tmp_path / "failed.json"
    p.write_text(json.dumps({"message": "获取小红书作品数据失败", "data": {}}, ensure_ascii=False))
    s = xhs_export.export([str(p)], str(tmp_path / "out"))
    assert s["notes"] == 0
