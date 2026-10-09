"""8.2 ルールフィルタ。"""
from otoku.pipeline.rules import RuleFilter


def test_include_matches_title_or_body(cfg):
    f = RuleFilter(cfg.keywords.include, cfg.keywords.exclude)
    assert f.check("新商品のお知らせ", "先着1万名に全額キャッシュバック")[0]
    assert f.check("【抽選販売】拡張パック", "")[0]
    assert not f.check("新店舗オープンのお知らせ", "営業時間は10時から")[0]


def test_exclude_looks_at_title_only(cfg):
    f = RuleFilter(cfg.keywords.include, cfg.keywords.exclude)
    ok, why = f.check("抽選販売の当選発表について", "")
    assert not ok and "当選発表" in why
    assert not f.check("全額返金保証キャンペーン", "")[0]          # 返金保証（2章）
    assert not f.check("初回無料 定期コースのご案内", "プレゼント")[0]  # 定期契約（2章）
    assert not f.check("【抽選販売】◯◯ ※応募は終了しました", "")[0]   # 受付終了
    # 本文の「受付終了」は受付中の告知にもよく出るので落とさない
    assert f.check("【抽選販売】◯◯", "受付期間：10/1〜 受付終了：10/15 16:59")[0]


def test_width_and_case_are_ignored(cfg):
    f = RuleFilter(cfg.keywords.include, cfg.keywords.exclude)
    assert f.check("Pony Island (Steam) GIVEAWAY", "")[0]
    assert f.check("ｻﾝﾌﾟﾙ配布", "")[0]  # 半角カナ
    assert f.check("【３,３５０円→０円】無料配布", "")[0]  # 全角数字
    assert not f.check("１０円引きセール", "")[0]  # 「0円」だけでは拾わない
