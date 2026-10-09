"""RSS・公開JSONの読み取りと、取得のマナー（条件付きGET・再試行・同じホストの間隔）。"""
import httpx
import pytest

from otoku.collectors import FetchError, Fetcher, ParseError, json_api, rss, user_agent

from .conftest import FIX, NOW, Router, make_fetcher, make_source


def read(path):
    return (FIX / path).read_bytes()


def test_rss_prtimes_rdf():
    items = rss.parse(read("feeds/prtimes_index.rdf"), make_source("prtimes_all"))
    assert len(items) == 4
    first = items[0]
    assert first.url.startswith("https://prtimes.jp/main/html/rd/p/")
    assert first.title and first.body
    assert first.published_at is not None and first.published_at.tzinfo is not None


def test_rss_wordpress_and_gamerpower():
    hb = rss.parse(read("feeds/hobbystation_news.xml"), make_source("hobbystation_news"))
    assert len(hb) == 3 and all("<" not in i.body for i in hb)  # HTML を外したテキスト
    gp = rss.parse(read("feeds/gamerpower_giveaways.xml"), make_source("gamerpower_rss"))
    assert len(gp) == 3 and all("Giveaway" in i.title for i in gp)


def test_rss_rejects_non_feed():
    with pytest.raises(ParseError):
        rss.parse(b"<html><body>not a feed</body></html>", make_source())


def test_json_kirin_jsonp_skips_ended_campaigns():
    src = make_source("kirin_campaign", type="json_api", url="https://www.kirin.co.jp/campaign/json/campaign.js")
    items = json_api.parse(read("json/kirin_campaign.js"), src, NOW)
    assert len(items) == 2  # 3件のうち 2025-12-31 終了の1件は外れる
    zettai = items[0]
    assert "印：" in zettai.body and "絶対もらえる" in zettai.body
    assert "応募期間：" in zettai.body
    assert all("\x0b" not in i.title for i in items)  # 制御文字を除く


def test_json_matsuzakaya_dedupes_across_categories():
    src = make_source("matsuzakaya_ueno_topics", type="json_api",
                      url="https://www.matsuzakaya.co.jp/ueno/topics/topics.json")
    items = json_api.parse(read("json/matsuzakaya_topics.json"), src, NOW)
    urls = [i.url for i in items]
    assert len(urls) == 4 and len(set(urls)) == 4  # 5件のうち重複1件
    assert all(u.startswith("https://") for u in urls)  # 相対URLは絶対URLに
    assert all(i.body.startswith("カテゴリ：") for i in items)


def test_json_unknown_source_is_error():
    with pytest.raises(ParseError):
        json_api.parse(b"[]", make_source("unknown_json", type="json_api"), NOW)


def test_conditional_get_and_304():
    url = "https://feeds.example.com/feed.xml"
    router = Router({url: httpx.Response(304)})
    res = make_fetcher(router).get(url, etag='"abc"', last_modified="Fri, 09 Oct 2026 00:00:00 GMT")
    assert res.status == 304
    req = router.requests[0]
    assert req.headers["If-None-Match"] == '"abc"'
    assert req.headers["If-Modified-Since"] == "Fri, 09 Oct 2026 00:00:00 GMT"
    assert req.headers["User-Agent"] == user_agent("test@example.invalid")
    assert "test@example.invalid" in req.headers["User-Agent"]


def test_retry_once_then_fail():
    url = "https://feeds.example.com/feed.xml"
    router = Router({url: [httpx.Response(503), httpx.Response(200, content=b"ok", headers={"ETag": '"e1"'})]})
    res = make_fetcher(router).get(url)
    assert res.status == 200 and res.etag == '"e1"' and len(router.requests) == 2

    router = Router({url: httpx.Response(500)})
    with pytest.raises(FetchError, match="HTTP 500"):
        make_fetcher(router).get(url)
    assert len(router.requests) == 2  # 最初の1回＋再試行1回だけ


def test_same_host_requests_are_spaced():
    clock = {"t": 100.0}
    waits = []

    def sleep(s):
        waits.append(s)
        clock["t"] += s

    router = Router({"https://a.example.com/1": httpx.Response(200, content=b""),
                     "https://a.example.com/2": httpx.Response(200, content=b""),
                     "https://b.example.com/1": httpx.Response(200, content=b"")})
    f = Fetcher(contact="", timeout=5, host_spacing=2, retry=0, client=httpx.Client(transport=httpx.MockTransport(router)),
                sleep=sleep, clock=lambda: clock["t"])
    f.get("https://a.example.com/1")
    f.get("https://b.example.com/1")  # 別ホストは待たない
    f.get("https://a.example.com/2")  # 同じホストは2秒あける
    assert waits == [2.0]


def test_user_agent_without_contact():
    assert "contact" not in user_agent("")
