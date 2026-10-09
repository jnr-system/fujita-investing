"""8.5 グルーピングとメッセージの編集（15章：同一商品のグルーピングと、別商品を誤ってまとめないこと）。"""
import httpx

from otoku.cli import run_collect
from otoku.pipeline.extract import Extractor
from otoku.pipeline.group import group_key, normalize_product

from .conftest import NOW, FakeAI, Router, make_fetcher, make_source
from .test_send import FakeDiscord, add_candidate, at, run, statuses

PRODUCT = "ポケモンカードゲーム 拡張パック「ストームエメラルダ」"


def test_normalize_unifies_width_case_space_and_symbols():
    assert normalize_product("ポケモンカードゲーム　拡張パック「ストームエメラルダ」") == \
        normalize_product("ﾎﾟｹﾓﾝｶｰﾄﾞｹﾞｰﾑ 拡張パック ストームエメラルダ")
    assert normalize_product("ONE PIECE Card Game BOX!!") == normalize_product("one piece card game box")
    assert normalize_product("山崎 ２５年") == normalize_product("山崎25年")


def test_different_products_are_not_merged():
    # あいまい一致は使わない。少しでも違えば別グループ
    assert group_key("A", "山崎12年") != group_key("A", "山崎18年")
    assert group_key("A", "拡張パック ストームエメラルダ") != group_key("A", "拡張パック ストームエメラルダ（再販）")
    assert group_key("A", "ゲーム機 本体") != group_key("B", "ゲーム機 本体")  # スコープが違えば別
    assert group_key("A", "「」") is None  # 商品名が空ならまとめない


def test_same_product_from_several_stores_becomes_one_message(cfg, store):
    """フェーズ3の完了条件：同一商品の複数店舗が1メッセージにまとまる。"""
    add_candidate(store, 1, kind="lottery", genre="tcg", product=PRODUCT, organizer="ヨドバシ",
                  deadline=at(16, 59, day=12), cost=5400, group=True, source="a")
    add_candidate(store, 2, kind="lottery", genre="tcg", product="ポケモンカードゲーム 拡張パック ストームエメラルダ",
                  organizer="ゲオ", deadline=at(23, 59, day=11), group=True, source="b")
    add_candidate(store, 3, kind="lottery", genre="tcg", product=PRODUCT, organizer="ホビーステーション",
                  group=True, source="c")
    add_candidate(store, 4, kind="lottery", genre="tcg", product="ワンピースカード ブースターパック",
                  organizer="ゲオ", deadline=at(12, day=13), group=True, source="b")
    fake = FakeDiscord()
    s, log = run(cfg, store, at(12), fake)
    assert len(fake.posts) == 2  # ポケモン（3店）とワンピース（1店）
    poke = fake.posts[0]["content"].splitlines()
    # 見出しの商品名はスコアがいちばん高い候補（締切が最短のゲオ）のもの、定価は分かる店舗のもの
    assert poke[0] == "【抽選】ポケモンカードゲーム 拡張パック ストームエメラルダ（定価5,400円）受付中3店"
    assert poke[1] == "締切：最短 10/11 23:59　店舗：ゲオ、ヨドバシ、ホビーステーション"
    assert poke[2] == "https://example.com/2"  # 締切がいちばん早い店舗のリンク
    assert fake.posts[1]["content"].splitlines()[:2] == ["【抽選】ワンピースカード ブースターパック",
                                                          "締切：10/13 12:00　店舗：ゲオ"]
    assert statuses(store) == {"sent": 4}
    n = store.conn.execute("SELECT COUNT(*) FROM notifications WHERE kind = 'new'").fetchone()[0]
    assert n == 2 and s.sent_before == 0


def test_new_store_edits_the_sent_message_without_using_the_cap(cfg, store):
    add_candidate(store, 1, kind="lottery", genre="tcg", product=PRODUCT, organizer="ヨドバシ",
                  deadline=at(16, 59, day=12), group=True)
    fake = FakeDiscord()
    run(cfg, store, at(12), fake)
    assert len(fake.posts) == 1
    message_id = "1001"
    # あとから別の店舗の抽選が見つかる
    add_candidate(store, 2, kind="lottery", genre="tcg", product=PRODUCT, organizer="ゲオ",
                  deadline=at(10, day=11), group=True, source="geo")
    s, log = run(cfg, store, at(12, 30), fake)
    assert len(fake.posts) == 1                      # 新しい通知は送らない
    assert fake.edits[0][0] == message_id            # 元のメッセージを編集
    edited = fake.edits[0][1]["content"].splitlines()
    assert edited[0].endswith("受付中2店")
    assert edited[1] == "締切：最短 10/11 10:00　店舗：ゲオ、ヨドバシ"
    assert "[update: 店舗を追記（2店）]" in log
    counts = dict(store.conn.execute("SELECT kind, COUNT(*) FROM notifications GROUP BY kind").fetchall())
    assert counts == {"new": 1, "update": 1}         # 上限は new だけ数える
    assert s.sent_before == 1 and statuses(store) == {"sent": 2}


def test_same_store_or_same_campaign_again_is_a_duplicate(cfg, store):
    add_candidate(store, 1, kind="lottery", genre="tcg", product=PRODUCT, organizer="ヨドバシ",
                  deadline=at(16, 59, day=12), group=True)
    add_candidate(store, 2, kind="free_game", genre="game", product="Pony Island", organizer="Steam",
                  first_come=False, deadline=at(10, day=10), group=True, source="gamerpower_rss")  # 45+15=60
    fake = FakeDiscord()
    run(cfg, store, at(12), fake)
    assert len(fake.posts) == 2
    add_candidate(store, 3, kind="lottery", genre="tcg", product=PRODUCT, organizer="ヨドバシ",
                  deadline=at(16, 59, day=12), group=True, source="prtimes_all")      # 同じ店舗
    add_candidate(store, 4, kind="free_game", genre="game", product="Pony Island", organizer="Steam",
                  group=True, source="automaton_news")                                 # Bの同じ企画
    s, log = run(cfg, store, at(12, 30), fake)
    assert len(fake.posts) == 2 and fake.edits == []
    assert s.duplicates == 2
    assert log.count("[dropped: 重複（通知済み）]") == 2


def test_collect_assigns_groups(cfg, store, dry_log):
    feed_url = "https://feeds.example.com/feed.xml"
    entries = ["【抽選販売】ストームエメラルダ 店A", "【抽選販売】ストームエメラルダ 店B", "【抽選販売】山崎12年"]
    items = "".join(f"<item><title>{t}</title><link>https://example.com/{i}</link></item>" for i, t in enumerate(entries))
    feed = f'<rss version="2.0"><channel><title>t</title>{items}</channel></rss>'.encode()
    ai = FakeAI({"店A": "lottery_tcg_ok", "店B": "lottery_tcg_ok", "山崎": "preview_future"})
    run_collect(cfg=cfg, sources=[make_source(scope="A", genre_hint=["tcg"])], store=store,
                fetcher=make_fetcher(Router({feed_url: httpx.Response(200, content=feed)})),
                extractor=Extractor(cfg.gemini, "system", call=ai), log_channel=dry_log, now=NOW)
    rows = store.conn.execute("SELECT i.product, i.status, g.key FROM items i LEFT JOIN groups g "
                              "ON g.id = i.group_id ORDER BY i.id").fetchall()
    assert rows[0][2] == rows[1][2] == "A:ポケモンカードゲーム拡張パック"   # 同じ商品名 → 同じグループ
    assert rows[2][1] == "waiting" and rows[2][2] == "A:限定ウイスキー"     # 待機中もグループに入る


def test_b_same_name_from_same_source_is_not_merged(cfg, store):
    """ローソンの「飲料1本もらえるキャンペーン」のように、同じ情報源の同じ名前の別企画はまとめない。"""
    name = "飲料1本もらえるキャンペーン"
    a = add_candidate(store, 1, product=name, group=True, source="lawson_sale", first_come=True)
    b = add_candidate(store, 2, product=name, group=True, source="lawson_sale", first_come=True)
    c = add_candidate(store, 3, product=name, group=True, source="prtimes_all", first_come=True)
    groups = dict(store.conn.execute("SELECT id, group_id FROM items").fetchall())
    assert groups[a] != groups[b]          # 同じ情報源 → 別々
    assert groups[c] == groups[a]          # 別の情報源から同じ名前 → まとめる
    fake = FakeDiscord()
    run(cfg, store, at(12), fake)
    assert len(fake.posts) == 2            # (1と3) と 2


import pytest  # noqa: E402


@pytest.fixture(autouse=True)
def _pin_send_numbers(cfg):
    """このファイルのテストは、上限3件・閾値60点を前提に書いている（config.yaml の調整に左右されないように固定）。"""
    cfg.daily_cap = 3
    cfg.score_threshold = 60

