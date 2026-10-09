"""15章：URL正規化と重複排除。"""
from otoku.models import RawItem
from otoku.pipeline.dedupe import content_hash, normalize_url, url_hash

from .conftest import NOW


def test_tracking_params_removed_and_others_kept():
    u = "https://www.wakatsuru.co.jp/saburomaru/information/news-1/?utm_source=rss&utm_medium=rss&utm_campaign=x"
    assert normalize_url(u) == "https://www.wakatsuru.co.jp/saburomaru/information/news-1"
    # 記事IDの p は計測用ではないので残す（ホビーステーション）
    assert normalize_url("https://www.hbst.net/?p=411288&fbclid=abc") == "https://www.hbst.net/?p=411288"


def test_trailing_slash_case_fragment_and_query_order():
    assert normalize_url("HTTPS://Example.COM/campaign/") == "https://example.com/campaign"
    assert normalize_url("https://example.com/") == "https://example.com/"
    assert normalize_url("https://example.com") == "https://example.com/"
    assert normalize_url("https://example.com/a?b=2&a=1#top") == "https://example.com/a?a=1&b=2"
    assert normalize_url("https://example.com:443/a") == "https://example.com/a"


def test_same_page_same_hash():
    assert url_hash("https://example.com/a/?utm_source=x") == url_hash("https://example.com/a")
    assert url_hash("https://example.com/a") != url_hash("https://example.com/b")


def test_store_skips_seen_url_even_if_content_changed(store):
    raw = RawItem(source_id="s", url="https://example.com/a?utm_source=x", title="t", body="b1")
    h = url_hash(raw.url)
    assert not store.seen(h)
    store.add_raw(raw, h, content_hash(raw.title, raw.body), NOW)
    store.commit()
    changed = RawItem(source_id="s", url="https://example.com/a/", title="t", body="b2（本文が変わった）")
    assert store.seen(url_hash(changed.url))
