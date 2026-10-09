"""一覧ページの差分（html_diff）とサイトマップ。"""
import httpx
import pytest

from otoku.cli import run_collect
from otoku.collectors import ParseError, html_diff, sitemap

from .conftest import NOW, Router, make_fetcher, make_source

LIST_URL = "https://www.example.co.jp/campaign/"

PAGE_V1 = """<html><head><meta charset="utf-8"></head><body>
<nav><a href="/campaign/old-nav/">キャンペーン</a><a href="/">トップ</a></nav>
<div class="list">
  <div class="card">
    <p>買って応募</p><h3>先着1万名に全額キャッシュバック！新商品キャンペーン</h3>
    <p>応募締切：2026年10月31日</p>
    <a class="btn" href="/campaign/cp-001/?utm_source=list">詳細を見る</a>
  </div>
  <div class="card">
    <a href="https://cp.example.jp/cp-002/"><img src="b.jpg" alt="無料サンプルプレゼント（全員）"></a>
    <a href="https://cp.example.jp/cp-002/">詳しく</a>
  </div>
  <!-- 終了したキャンペーン
  <div class="card"><a href="/campaign/ended-999/">終了分</a></div>
  -->
  <a href="javascript:void(0)">もっと見る</a>
</div>
</body></html>"""

PAGE_V2 = PAGE_V1.replace('<!-- 終了したキャンペーン', '''<div class="card"><h3>抽選で100名様にプレゼント</h3>
  <a class="btn" href="/campaign/cp-003/">詳細を見る</a></div>
  <!-- 終了したキャンペーン''')


def src(**kw):
    return make_source("example_list", type="html_diff", url=LIST_URL, min_interval_minutes=360, **kw)


def test_short_link_text_gets_the_card_text_and_comments_are_ignored():
    links = html_diff.extract_links(PAGE_V1.encode(), LIST_URL, selector="div.list")
    urls = [u for u, _, _ in links]
    assert urls == ["https://www.example.co.jp/campaign/cp-001/?utm_source=list", "https://cp.example.jp/cp-002/"]
    text = links[0][1]
    assert "先着1万名に全額キャッシュバック" in text and "応募締切：2026年10月31日" in text  # 「詳細を見る」だけにしない
    assert links[1][1].startswith("無料サンプルプレゼント（全員）")                         # 画像の alt


def test_pattern_and_selector_exclude_navigation():
    everything = html_diff.extract_links(PAGE_V1.encode(), LIST_URL)
    assert any("old-nav" in u for u, _, _ in everything)
    by_pattern = html_diff.extract_links(PAGE_V1.encode(), LIST_URL, pattern=r"/campaign/cp-|cp\.example\.jp")
    assert len(by_pattern) == 2 and not any("old-nav" in u for u, _, _ in by_pattern)


def test_only_new_links_are_processed(cfg, store, dry_log):
    router = Router({LIST_URL: [httpx.Response(200, content=PAGE_V1.encode()),
                                httpx.Response(200, content=PAGE_V2.encode())]})
    fetcher = make_fetcher(router)
    source = src(link_selector="div.list")
    s1 = run_collect(cfg=cfg, sources=[source], store=store, fetcher=fetcher, extractor=None, log_channel=dry_log,
                     now=NOW)
    assert s1.sources["example_list"].new == 2
    s2 = run_collect(cfg=cfg, sources=[source], store=store, fetcher=fetcher, extractor=None, log_channel=dry_log,
                     now=NOW + __import__("datetime").timedelta(hours=6))
    assert s2.sources["example_list"].fetched == 3 and s2.sources["example_list"].new == 1  # 増えた cp-003 だけ
    titles = [r[0] for r in store.conn.execute("SELECT title FROM raw_items ORDER BY id")]
    assert "抽選で100名様にプレゼント" in titles[-1]


def test_zero_links_is_not_an_error(cfg, store, dry_log):
    router = Router({LIST_URL: httpx.Response(200, content=b"<html><body><p>Coming soon</p></body></html>")})
    s = run_collect(cfg=cfg, sources=[src(link_selector="div.list")], store=store, fetcher=make_fetcher(router),
                    extractor=None, log_channel=dry_log, now=NOW)
    assert s.sources["example_list"].note == "監視対象のリンク0件" and not s.errors
    assert store.source_state("example_list").fail_streak == 0


SITEMAP = b"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://www.example.co.jp/campaign/cp-001/</loc><lastmod>2026-10-08</lastmod></url>
  <url><loc>https://www.example.co.jp/products/abc/</loc></url>
</urlset>"""


def test_sitemap_urlset_with_pattern():
    s = make_source("example_sitemap", type="sitemap", url="https://www.example.co.jp/sitemap.xml",
                    link_pattern="/campaign/")
    items = sitemap.parse(SITEMAP, s)
    assert [(i.url, i.body) for i in items] == [("https://www.example.co.jp/campaign/cp-001/", "更新日：2026-10-08")]


def test_sitemap_index_and_garbage_are_errors():
    s = make_source("example_sitemap", type="sitemap", url="https://www.example.co.jp/sitemap.xml")
    with pytest.raises(ParseError, match="インデックス"):
        sitemap.parse(b'<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></sitemapindex>', s)
    with pytest.raises(ParseError):
        sitemap.parse(b"<html>not xml", s)
