# お得情報収集システム 設計書

個人用。限定品の抽選と100%還元キャンペーンを自動収集し、厳選してDiscordに通知する。

## 1. 目的と方針

- 目的：定価で買えて相場が上にある限定品の抽選と、実質無料になるキャンペーンを、見逃さず・最小限の通知で知る。
- 最優先の方針：**迷ったら通知しない**。取りこぼしよりノイズを出さないことを優先する。過去に同種の仕組みを作り、情報が多すぎて見なくなった経緯がある。
- やらないこと（非目標）
  - 抽選や応募の自動実行（規約違反になるため。システムは「知らせる」まで）
  - ログインが必要なページ、アプリ内限定情報の取得
  - X（旧Twitter）の取得（従量課金のため初期スコープ外）
  - 日次まとめ・「該当なし」通知

## 2. スコープ

### A. 抽選・限定品
| ジャンルID | 内容 |
|---|---|
| `tcg` | トレカ（ポケモンカード、ワンピースカード、遊戯王などの新弾・記念商品の抽選販売） |
| `whisky` | 国産ウイスキー・限定酒の抽選販売 |
| `console` | ゲーム機本体・限定版（限定モデル、同梱版、限定コントローラー）の抽選販売・数量限定販売 |

### B. 100%還元キャンペーン
| 種別ID | 内容 |
|---|---|
| `refund_all` | 全額返金（条件を満たせば全員対象） |
| `refund_first` | 全額返金（先着◯名） |
| `free_item` | 無料引換・サンプル配布 |
| `free_game` | ゲームの無料配布 |

対象ジャンル：`food`（食品）、`drink`（飲料）、`daily`（日用品）、`cvs`（コンビニ）、`game`（ゲーム）

### 必ず除外するもの
- 「抽選で◯名に全額返金」（実質は懸賞）
- 「満足できなければ返金」の返金保証
- 継続購入・定期契約が条件の「初回無料」
- 予告、発売告知のみ、ニュース記事、当選報告、まとめ記事の再掲
- 受付がすでに終了しているもの
- 上記スコープ外のジャンル

## 3. 全体構成

```
情報源（RSS / サイトマップ / HTML差分 / 公開JSON）
  → 収集
  → 重複排除（SQLite）
  → ルールフィルタ（ジャンル・キーワード）
  → AI構造化（Gemini API、JSON出力）
  → 検証（スキーマ・日付・除外条件）
  → グルーピング（同一商品・同一企画を1件に）
  → スコア判定
  → 送信選定（1日の上限）
  → Discord通知（#行動）／全件ログ（#ログ）
  → リアクション取得 → スコア調整・締切リマインド
```

## 4. 実行環境

- 個人用VPS（Ubuntu系）、cronで定期実行。会社の環境・アカウントとは分離する。
- Python 3.11以上。依存は最小限（`httpx`、`feedparser`、`beautifulsoup4`、`pyyaml`、`pydantic`、Gemini公式SDK）。
- DBはSQLite（1ファイル）。
- 秘密情報は `.env`（Gitに含めない）。
- タイムゾーンは `Asia/Tokyo` で統一。DB保存はUTC、表示はJST。

## 5. ディレクトリ構成

```
otoku/
  config/
    config.yaml        # 上限・閾値・重み・静音時間
    sources.yaml       # 情報源の定義
    prompts/extract.md # AI抽出プロンプト
  src/otoku/
    collectors/        # rss.py, sitemap.py, html_diff.py, json_api.py
    pipeline/          # dedupe.py, rules.py, extract.py, validate.py, group.py, score.py, select.py
    notify/            # discord.py（REST）, format.py
    feedback/          # reactions.py, reminder.py
    db.py, models.py, cli.py
  tests/
    fixtures/          # 保存済みRSS/HTML、AI応答のサンプル
  data/otoku.db
  .env.example
  crontab.example
  README.md
```

CLI（`python -m otoku <command>`）：
- `collect` 収集〜候補登録まで
- `send` 送信選定と通知
- `sync` リアクション取得とスコア調整
- `remind` 締切リマインド
- `check-sources` 情報源の疎通・robots確認
- すべてに `--dry-run`（Discord送信とDB書き込みをせず標準出力に出す）

## 6. 情報源

### 6.1 取得方式（優先順）
1. `rss`：RSS/Atom
2. `json_api`：公開されているJSON（認証不要のもののみ）
3. `sitemap`：sitemap.xmlの差分
4. `html_diff`：一覧ページのリンク集合の差分（増えたURLだけを新着とする。本文のレイアウト解析に依存しない）

ヘッドレスブラウザは使わない。JavaScript必須のページは対象外とする。

### 6.2 sources.yaml の形式
```yaml
- id: prtimes_refund
  type: rss
  url: "<検証して確定>"
  scope: B
  genre_hint: [food, drink, daily]
  min_interval_minutes: 30
  enabled: true
  verified: "2026-10-xx robots.txt確認済み、規約上の禁止なし"
```

### 6.3 情報源の候補（フェーズ0で検証して確定する）
URLは推測で書かず、実際にアクセスして存在・RSS有無・robots.txt・利用規約を確認すること。取得が禁止されているものは `enabled: false` にして理由を残す。

**共通（A・B両方）**
- プレスリリース配信サイトのRSS（PR TIMESなど。キーワード・カテゴリ別フィードの有無を確認）
- GoogleアラートのRSS（ユーザーが手動で作成し、URLをsources.yamlに貼る。キーワード案は 6.4）

**A. 抽選・限定品**
- トレカ：ポケモンカード公式のお知らせ、ポケモンセンターオンラインの抽選告知、ワンピースカード公式、家電量販店（ヨドバシ、ビックカメラ、ジョーシン、エディオン、ノジマ）の抽選ページ、ホビー店（あみあみ、ホビーステーション等）の抽選告知
- ウイスキー：サントリー公式の抽選販売、百貨店（高島屋、三越伊勢丹、大丸松坂屋、阪急）のオンラインストア抽選、イオン・ビックカメラ・酒販チェーンの抽選告知、国内蒸溜所の公式お知らせ
- ゲーム機・限定版：任天堂（マイニンテンドーストア）、ソニー（PlayStation公式ストア）、Xbox公式のお知らせ、家電量販店（ヨドバシ、ビックカメラ、ジョーシン、エディオン、ノジマ）の抽選ページ、ゲーム専門店（ゲオ等）の抽選告知。トレカと情報源が重なる店舗は1つの定義で両ジャンルを拾う
  - 対象は「本体」「限定モデル・同梱版」「限定周辺機器」の抽選・数量限定販売のみ。通常のソフト発売、セール、予約開始の告知は除外する
- 抽選まとめサイト：規約で機械取得が禁止されていない場合のみ

**B. 100%還元**
- 食品：日清食品、明治、森永製菓、カルビー、味の素、ニチレイ、山崎製パンの公式キャンペーン一覧
- 飲料：サントリー、キリン、アサヒ、コカ・コーラ、伊藤園の公式キャンペーン一覧
- 日用品：花王、ライオン、P&G、ユニ・チャーム、小林製薬の公式キャンペーン一覧
- コンビニ：セブン‐イレブン、ファミリーマート、ローソンの公式キャンペーン一覧
- ゲーム：Epic Games Storeの無料ゲーム、Steamの期間限定無料配布、GOGの無料配布、Prime Gaming（公開フィードやJSONの有無を確認）
- 懸賞・キャンペーンまとめサイト：規約で機械取得が禁止されていない場合のみ

### 6.4 Googleアラートのキーワード案（ユーザーが手動設定）
`全額返金キャンペーン`、`全額キャッシュバック 先着`、`無料引換券 コンビニ`、`無料サンプル 先着`、`抽選販売 ポケモンカード`、`抽選販売 ウイスキー`、`抽選販売 ゲーム機 本体`、`限定モデル 抽選販売 ゲーム`、`無料配布 ゲーム 期間限定`

### 6.5 取得のマナー
- 各サイトのrobots.txtと利用規約に従う。
- User-Agentに識別名と連絡先を入れる（`.env` の `CONTACT` を使用）。
- 1サイトあたり最短30分間隔、HTML差分は最短6時間間隔。同一ホストへのリクエストは直列で2秒以上あける。
- 条件付きGET（ETag / If-Modified-Since）を使う。
- 3回連続で失敗した情報源は自動で一時停止し、#ログに1回だけ報告する。

## 7. データモデル（SQLite）

```sql
-- 取得した生データ
raw_items(id, source_id, url, url_hash UNIQUE, title, body, fetched_at, content_hash)

-- AI構造化後の候補
items(
  id, raw_item_id, scope,            -- 'A' / 'B'
  kind,                               -- lottery / refund_all / refund_first / free_item / free_game / excluded
  genre, product, organizer,
  start_at, deadline_at,              -- NULL可
  conditions, cost_yen, benefit_yen,  -- NULL可
  apply_url, confidence,              -- 0.0〜1.0
  exclude_reason,                     -- kind=excluded のとき
  group_id, score, status,            -- candidate / sent / dropped / expired
  created_at
)

-- 同一商品・同一企画のまとまり
groups(id, scope, key UNIQUE, title, best_score, discord_message_id, first_sent_at, updated_at)

-- 通知の記録
notifications(id, group_id, channel, discord_message_id, sent_at, kind) -- kind: new / update / remind

-- リアクション
feedback(id, group_id, reaction, recorded_at)  -- applied / later / reject

-- 情報源の成績
source_stats(source_id, sent_count, applied_count, reject_count, fail_streak, paused_until, weight)
```

## 8. 処理の詳細

### 8.1 重複排除
- URLを正規化（クエリの計測パラメータ除去、末尾スラッシュ統一）してハッシュ化。既出は破棄。
- 同一URLでも本文ハッシュが変わった場合は再処理しない（更新通知は出さない）。

### 8.2 ルールフィルタ（AIに渡す前）
- 対象キーワードを1つも含まないものは破棄（例：抽選、抽選販売、全額返金、全額キャッシュバック、無料引換、無料配布、プレゼント、サンプル、先着）。
- 除外キーワードを含むものは破棄（例：当選発表、結果発表、受付終了、満足保証、定期コース）。
- キーワード一覧は `config.yaml` で管理。
- ここでAI呼び出し件数を減らす。

### 8.3 AI構造化
- Gemini API（Flash系の安価なモデル。モデル名は実装時に公式ドキュメントで最新の安定版を確認し、`config.yaml` で指定）。
- 構造化出力（JSONスキーマ指定）を使う。温度は0。
- 入力はタイトル＋本文先頭4,000文字＋取得日時（JST）。
- 出力スキーマ：
```json
{
  "kind": "lottery | refund_all | refund_first | free_item | free_game | excluded",
  "genre": "tcg | whisky | console | food | drink | daily | cvs | game | other",
  "product": "商品名または企画名",
  "organizer": "主催企業・店舗名",
  "start_at": "ISO8601 or null",
  "deadline_at": "ISO8601 or null",
  "conditions": "応募・受取の条件を60字以内",
  "cost_yen": 0,
  "benefit_yen": 0,
  "apply_url": "応募・詳細ページのURL or null",
  "requires_subscription": false,
  "actionable_now": true,
  "confidence": 0.0,
  "exclude_reason": "excludedのときの理由 or null"
}
```
- プロンプトに明記する判断基準：
  - 2章の「必ず除外するもの」に当たれば `excluded`。
  - 確信が持てない場合は `excluded`（`exclude_reason: "不確実"`）。
  - 本文に書かれていない日付・金額は推測せず `null`。
  - `actionable_now` は「取得日時の時点で応募・受取ができる」場合のみ `true`。
  - `console`（スコープAのゲーム機・限定版）と `game`（スコープBのゲーム無料配布）を混同しない。ゲームソフトの通常発売・セール・予約開始は `excluded`。

### 8.4 検証
以下は `dropped` にする（#ログには理由付きで記録）。
- `kind = excluded`
- `genre` がスコープ外
- `confidence < 0.8`
- `actionable_now = false`（ただし `start_at` が未来のものは、開始時刻に再評価する待機状態にする）
- `deadline_at` が過去
- `requires_subscription = true`

### 8.5 グルーピング
- キー：`scope` ＋ 正規化した `product`（全角半角統一、空白・記号除去、小文字化）。
- A（抽選）は商品単位でまとめ、主催店舗をリストとして持つ。
- 既存グループに新しい店舗が加わった場合は、新規通知ではなく既存のDiscordメッセージを編集して店舗を追記する（上限の件数には数えない）。
- 表記ゆれの統合に失敗しても誤って別商品をまとめないよう、一致判定は厳しめにする（完全一致。あいまい一致は使わない）。

### 8.6 スコア（0〜100）
```
score = base[kind] + genre_weight[genre] + urgency + benefit_bonus + source_weight
```
- `base`：refund_first 60 / refund_all 55 / free_item 50 / free_game 45 / lottery 50
- `genre_weight`：tcg +15 / whisky +15 / console +10 / その他 0
- `urgency`：締切まで24時間以内 +15、72時間以内 +5、先着は常に +15
- `benefit_bonus`：`benefit_yen` が1,000円以上 +5、5,000円以上 +10（不明は0）
- `source_weight`：-10〜+10。フィードバックで自動調整（8.9）
- 数値はすべて `config.yaml` で変更可能にする。
- 送信の閾値：`score >= 60`

### 8.7 送信選定（上限管理）
- 1日の新規通知は最大 `daily_cap`（初期値3）。日付はJSTで区切る。
- **緊急**（先着、または締切24時間以内）：閾値以上なら即時送信。
- **通常**：1日2回の選定枠（12:00、19:00）で、未送信候補のうちスコア上位から、残り枠の範囲で送る。
- 上限を超えた候補は翌日に持ち越さず、締切が残っていれば翌日の候補として再評価、なければ `expired`。
- 静音時間（23:00〜7:00）は送信しない。緊急分は7:00にまとめて送る（締切が7:00より前のものは破棄）。
- 候補0件のときは何も送らない。

### 8.8 Discord通知
- DiscordのBotトークンを使い、REST APIのみで実装する（常時接続のゲートウェイは使わない）。
  - 送信：`POST /channels/{id}/messages`
  - 編集：`PATCH /channels/{id}/messages/{message_id}`
  - リアクション付与：`PUT .../reactions/{emoji}/@me`
  - リアクション取得：`GET .../reactions/{emoji}`
- チャンネル
  - `#行動`：厳選通知のみ。通知オン。
  - `#ログ`：全候補と落とした理由、エラー、情報源の停止報告、1日1回の稼働報告。ミュート前提。
- `#行動` の形式（1件3行、装飾なし）
```
【先着・全額返金】◯◯ 新商品（実質0円）
締切：10/15 23:59　条件：レシート応募、1人1回
https://example.com/...
```
```
【抽選】◯◯ BOX（定価7,200円）受付中3店
締切：最短 10/12 16:59　店舗：A、B、C
https://example.com/...
```
- 送信直後にBotが ✅ ⏰ ❌ の3つのリアクションを付ける（ワンタップで回答できるようにする）。
  - ✅ 応募した／もらった
  - ⏰ あとでやる（締切前にリマインド）
  - ❌ いらない
- `#ログ` の形式：1候補1行（`[dropped: 抽選で返金] タイトル / 情報源ID / score`）。

### 8.9 フィードバックと調整
- `sync` でリアクションを取得し、`feedback` に記録する（Bot自身の分は除く）。
- 情報源ごとに直近30件の通知を集計し、❌の割合が50%を超えたら `source_weight` を -5、✅の割合が50%を超えたら +5（範囲 -10〜+10）。
- 週1回、#ログに「通知数、✅率、❌率、情報源別の成績」を1メッセージで報告する。
- 目標指標：`#行動` の通知のうち✅が付く割合が50%以上。

### 8.10 締切リマインド
- ⏰が付いたものだけ、締切の24時間前に `#行動` へ1回だけ送る（元メッセージへの返信として送る）。
- 締切が不明なものはリマインドしない。
- リマインドは `daily_cap` に数えない。

## 9. cron

```
*/30 * * * *  otoku collect && otoku send --urgent-only
0 12,19 * * * otoku send
15 * * * *    otoku sync
0 9 * * *     otoku remind
0 8 * * *     otoku check-sources --report
0 8 * * 1     otoku sync --weekly-report
```
- 多重起動を防ぐためロックファイル（`flock`）を使う。
- 各情報源の `min_interval_minutes` は `collect` 内で判定する。

## 10. 設定（config.yaml の主な項目）

```yaml
daily_cap: 3
score_threshold: 60
min_confidence: 0.8
quiet_hours: {start: "23:00", end: "07:00"}
select_slots: ["12:00", "19:00"]
gemini: {model: "<実装時に確認>", temperature: 0, max_body_chars: 4000}
genres_enabled: [tcg, whisky, console, food, drink, daily, cvs, game]
weights: {...}          # 8.6 の数値
keywords: {include: [...], exclude: [...]}
```

## 11. 環境変数（.env）

```
GEMINI_API_KEY=
DISCORD_BOT_TOKEN=
DISCORD_CHANNEL_ACTION=
DISCORD_CHANNEL_LOG=
CONTACT=            # User-Agentに入れる連絡先
```

## 12. エラー処理と監視

- 情報源の取得失敗：リトライ1回、失敗が3回続いたら24時間停止して#ログに報告。
- AI応答がスキーマに合わない：1回だけ再試行し、だめなら `dropped（AI応答不正）`。
- Discord送信失敗：レート制限（429）は `Retry-After` に従う。それ以外は次回実行で再送。
- 稼働確認：毎朝8:00に#ログへ「前日の取得件数／候補数／送信数／エラー数」を1行で報告。
- ログはファイルにも出力し、14日でローテーションする。

## 13. コストの目安

- AI呼び出しはルールフィルタ通過分のみ。1日数十〜百件程度を想定し、Flash系モデルで月数百円以内に収まる見込み（実測して#ログの週次報告に件数を載せる）。
- VPS費用は別途。

## 14. 開発フェーズと完了条件

| フェーズ | 内容 | 完了条件 |
|---|---|---|
| 0 | 情報源の検証 | 候補すべてについてRSS有無・robots.txt・規約を確認し、`sources.yaml` と検証結果の一覧（採用／不採用と理由）ができている |
| 1 | RSS・JSON収集 → ルール → AI構造化 → 検証 → #ログ出力 | `--dry-run` で実データを流し、除外条件が正しく働くことをテストで確認 |
| 2 | スコア・上限・静音時間・#行動への通知 | 1日の送信が上限を超えないこと、0件時に何も送らないことをテストで確認 |
| 3 | HTML差分・サイトマップ収集、グルーピングとメッセージ編集 | 同一商品の複数店舗が1メッセージにまとまる |
| 4 | リアクション取得、重み調整、締切リマインド、週次報告 | ⏰のものだけリマインドが1回届く |

## 15. テスト方針

- 外部通信はすべてモックし、`tests/fixtures/` の保存データで再現する。
- 必須のテストケース
  - 除外条件（抽選で返金、返金保証、定期購入条件、受付終了、予告のみ）がそれぞれ落ちる
  - `confidence` が閾値未満だと落ちる
  - 上限3件を超えて送らない、日付をまたぐとリセットされる
  - 静音時間に送らない
  - 同一商品のグルーピングと、別商品を誤ってまとめないこと
  - URL正規化と重複排除
  - リアクション集計による重みの増減と上下限

## 16. ユーザーが手動で用意するもの

1. 個人用VPS（Python 3.11以上が動くもの）
2. Discordサーバーと `#行動`・`#ログ` チャンネル、Botの作成とサーバーへの追加（メッセージ送信・履歴閲覧・リアクション追加の権限）
3. Gemini APIキー（個人アカウント）
4. GoogleアラートのRSSフィード（6.4のキーワード）

## 17. 実装時の決定事項（2026-10-09、ユーザー確認済み）

本文（1〜16章）は書き換えず、実装で決めた・変えた点をここにまとめる。根拠の詳細は `docs/sources_review.md` と各ファイルのコメント。

### 2章 スコープ
- 「1個買うと1個もらえる」、「◯◯を買うと△△の無料引換券」は対象（free_item）。値引券・割引券・「◯円引き」は対象外。
- 抽選で当たるプレゼント（懸賞）は対象外。ゲームのDLC・追加コンテンツ・プレイテストは対象外。
- ゲームニュースサイトの記事でも、今受け取れるゲームの無料配布を伝えるものは対象（「ニュース記事は除外」の例外）。

### 4章 実行環境
- 個人用VPSではなく、このマシンで本番まで動かす（4章の例外）。仮想環境とデータはリポジトリ内（`.venv/`・`data/`）だけに置き、鍵は `.env` だけから読む（シェルの環境変数は見ない）。
- AIは `gemini-3.5-flash-lite`（公式の安定版で安価なもの）。公式SDKの interactions を、やり取りをGoogle側に保存しない指定（store=False）で使う。

### 6章 情報源
- `sources.yaml` の `scope` は A・B 共通の情報源では `[A, B]` と書く。
- html_diff 用に、省略できる `link_selector`（CSSセレクタ）と `link_pattern`（URLの正規表現）を追加。一覧ページの文字（リンクの文字・画像の alt・項目の文言）だけを使い、個別ページは取得しない。リンクが0件でもエラーにしない。
- 取得の最短間隔の判定には60秒の余裕を持たせる（cron の起動のずれで丸ごと飛ばさないため）。
- 本番の実行には `.env` の CONTACT（User-Agent の連絡先）が必須。

### 7章 データモデル
- `items.status` に `waiting`（開始前の待機状態）を追加。`items` に `first_come`（先着かどうか）を追加。
- `source_stats` に `last_fetched_at`・`etag`・`last_modified` を追加。
- `items.exclude_reason` には、AIの除外理由だけでなく検証や送信選定で落とした理由も入れる。

### 8章 処理
- 8.2：対象キーワードはタイトルと本文、除外キーワードはタイトルだけを見る（本文の「受付終了：10/15」で受付中の告知が落ちるため）。
- 8.3：AIの出力に `first_come` を追加。タイトルだけで種類が分かれば判定してよい。年のない日付は取得日時の年とする。
- 8.4：検証で、種類とジャンルの組み合わせも見る（抽選は tcg・whisky・console、還元・無料は food〜game、free_game は game）。AIを呼べないときは、その回の残りを次回に回す。
- 8.5：B（還元・無料）は、同じ情報源のURL違いは別の企画としてまとめない。送信済みのグループに同じ店舗や同じ企画が来たら「重複（通知済み）」で落とす。
- 8.6：緊急度は、締切の点数と先着の点数のうち大きいほう（足さない）。
- 8.7：上限で送れなかった締切不明の候補は expired。通常の選定は select_slots の時刻から30分のあいだだけ（それ以外は緊急のみ）。`daily_cap` は 5、`score_threshold` は 50 に変更。
- 8.8：#行動 のリンクは、AIが返した応募URLが本文に書かれているときだけそれを使い、それ以外は元の記事のURL。リンクのプレビューは出さない。
- 8.9：情報源の重みの調整は週1回（週次報告のとき）、±5ずつ。通知が5件未満の情報源は調整しない。
- 8.10：⏰ と ✅ の両方が付いているものはリマインドしない。リマインドは毎朝9:00のまま（締切の24時間前を過ぎた最初の9:00に届く）。

### 9章・12章 運用
- ロックが取れないときは、先の実行が終わるのを最大600秒待つ（12:00・19:00 に collect と send が同時に起動するため）。
- `check-sources` と毎朝の稼働報告はフェーズ4で実装。robots.txt で禁止、または robots.txt に応答がない情報源は、次の朝の確認まで止めて #ログ に報告する。
- 稼働報告の「取得件数」は新規の件数、「エラー数」はログファイルの警告・エラーの行数。
