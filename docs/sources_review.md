# 情報源の検証結果（フェーズ0）

確認日：2026-10-09　対象：DESIGN.md「6.3 情報源の候補」の全候補と、ゲームの代わりの案（計69件）＋Googleアラート（手動設定のため空欄のみ）

## 確認の方法

- 対象サイトへのアクセスは、識別名入りの User-Agent（`otoku-source-check/0.1 (personal non-commercial use; phase-0 manual source verification)`）で行い、全リクエストを記録した。
- 1ホストあたり最大5回、同じホストへの間隔は2秒以上。合計274リクエスト・90ホスト、5回を超えたホストはない（任天堂の旧ホストからの転送で1回分だけ別ホストを経由）。1つの企業で複数のホストを使った場合、企業単位では最大10回（イオン）になった。
- URLの手がかりは検索で探し、実際に取得して 200 と中身を確かめたものだけを「確認済み」とした。検索で見ただけのURLは「未確認」。
- robots.txt は RFC 9309 の方法で判定した（最も長く一致する規則を採用、同じ長さなら Allow を優先、404 は制限なし）。
- 規約は、スクレイピング・クローラー・ロボット・自動取得を名指しで禁じる条文があれば「禁止あり」とした。「無断複製・転載の禁止」「過度な負荷の禁止」「私的使用の範囲」だけの場合は、機械的な取得の禁止には当たらないものとして「禁止なし」とした。
- こちらの User-Agent に 403・429・ボット判定画面が返ったものは、ブロックとして不採用にした（別のUAで試すなどの回避はしていない）。
- JavaScript を実行せずに、生のHTMLに個別の項目へのリンクがあるかを数えた。

## 集計

判定の内訳：採用 29件／未確認 8件／不採用 32件

採用した情報源の数（ジャンル別。共通の PR TIMES は含めない。1つの情報源が複数ジャンルにまたがる場合はそれぞれに数える）

| スコープ | ジャンル | 採用数 | 情報源 |
|---|---|---|---|
| A | tcg | 3 | pokemon_card_news, hobbystation_news, geo_news_lottery |
| A | whisky | 6 | mistore_whisky_collection, matsuzakaya_ueno_topics, kakuyasu_featured, hombo_mars_news, gaiaflow_news, saburomaru_news |
| A | console | 3 | geo_news_lottery, playstation_blog_jp, xbox_wire_jp |
| B | food | 5 | nissin_campaigns, meiji_campaign, morinaga_campaign, calbee_campaign, yamazaki_campaign |
| B | drink | 4 | kirin_campaign, asahibeer_campaign, asahiinryo_campaign, itoen_campaign |
| B | daily | 2 | lion_lidea_campaign, unicharm_campaign |
| B | cvs | 3 | sej_campaign, familymart_campaign, lawson_sale |
| B | game | 3 | gamerpower_rss, gamespark_news, automaton_news |
| 共通 | 全ジャンル | 1 | prtimes_all（ほかに Googleアラート9本が手動設定待ち） |

## 一覧表

判定：採用＝enabled: true／未確認＝確認しきれなかった／不採用

### 共通（A・B）

| 候補 | 判定 | 取得方式 | 確認したURL | robots.txt | 規約 | JSなし | 理由 |
|---|---|---|---|---|---|---|---|
| PR TIMES 新着プレスリリースRSS | 採用 | rss | https://prtimes.jp/index.rdf | 許可 | 禁止なし | 可（200件） | RSSあり・robots全許可・規約に機械取得の禁止なし |

### A トレカ

| 候補 | 判定 | 取得方式 | 確認したURL | robots.txt | 規約 | JSなし | 理由 |
|---|---|---|---|---|---|---|---|
| ポケモンカード公式 ニュース一覧 | 採用 | html_diff | https://www.pokemon-card.com/info/ | 許可（404） | 禁止なし | 可（135件） | JSなしで記事リンクが取れる・robots制限なし・規約に機械取得の禁止なし。ポケセンオンラインの抽選告知も外部リンクとして載る |
| ポケモンセンターオンライン お知らせ（抽選告知） | 不採用 | — | https://www.pokemoncenter-online.com/ | 許可 | 禁止あり | 可（22件） | 利用規約 第6条⑰⑱でクローリング・スクレイピング・自動手段による情報取得を明示的に禁止 |
| ワンピースカードゲーム公式 ニュース（お知らせ一覧） | 未確認 | json_api | https://www.onepiece-cardgame.com/common/templates/api/article_list.php?start=0&limit=10&data=%7B%22category%22%3A%22INFORMATION%22%2C%22subcategory%22%3A%5B%22%22%5D%2C%22is_history%22%3Atrue%7D | 許可（404） | 規約ページなし | 不可 | 取得の手段は確認できた（公開JSON・robots制限なし・規約なし）。ただし、ニュースに抽選の告知が載るかを確かめられなかった（直近10件に抽選なし。アクセス上限とWeb検索の上限に達した） |
| あみあみ 抽選販売告知 | 不採用 | — | https://www.amiami.jp/（403） | 許可（404） | 未確認 | — | トップページ https://www.amiami.jp/ が Cloudflare の 403「Sorry, you have been blocked」で、こちらの UA をブロック |
| ホビーステーション 最新ニュース（抽選販売告知） | 採用 | rss | https://www.hbst.net/category/news/feed | 許可 | 規約ページなし | 可（10件） | ニュースのカテゴリRSSに抽選販売の告知がそのまま流れる・robots許可・規約ページなし |

### A 家電量販店・ゲーム専門店（トレカ・ゲーム機共通）

| 候補 | 判定 | 取得方式 | 確認したURL | robots.txt | 規約 | JSなし | 理由 |
|---|---|---|---|---|---|---|---|
| ヨドバシ・ドット・コム 人気商品抽選（limited.yodobashi.com） | 不採用 | html_diff | https://limited.yodobashi.com/ | 許可（404） | 禁止なし | 本文のみ（項目リンク0件） | 取得・robots.txt・規約は問題ないが、ページ内に抽選ごとのリンクがなく、抽選のたびに本文が差し替わる形式で、仕様（6.1：増えたURLだけを新着とする）の html_diff では新着を検出できない。ユーザー判断で不採用（2026-10-09） |
| ビックカメラ.com 抽選販売ページ（トレカ・ゲーム機） | 不採用 | — | https://www.biccamera.com/（403） | 許可 | 未確認 | — | トップが今回のUAに403（アクセス遮断）を返すうえ、抽選の一覧ページがない |
| Joshin webショップ 抽選販売 | 未確認 | — | 未確認 | 許可 | 未確認 | 不可 | 抽選販売の一覧ページが見つからず、利用規約（PDF）も未読 |
| エディオン 抽選販売 | 不採用 | — | 未確認 | 許可 | 禁止なし | 不可 | 抽選は別ドメイン edion-cp.com の企画ごとのページで、一覧がなく（ルートは404）、本体サイトのトップやお知らせにも載らない |
| ノジマオンライン 抽選販売 | 不採用 | — | https://online.nojima.co.jp/（200） | 許可（404） | 未確認 | 不可 | トップが今回のUAに Akamai のボット判定チャレンジ（JS必須の検証画面）を返す＝ブロック |
| ゲオオンライン お知らせ（抽選販売受付のお知らせ） | 採用 | html_diff | https://geo-online.co.jp/news/ | 許可 | 禁止なし | 可（7件） | お知らせ一覧に抽選販売の告知が素のHTMLで載り、robots許可・規約に機械取得の禁止なし |

### A ウイスキー（メーカー・百貨店・量販店・酒販チェーン）

| 候補 | 判定 | 取得方式 | 確認したURL | robots.txt | 規約 | JSなし | 理由 |
|---|---|---|---|---|---|---|---|
| サントリー 公式の抽選販売（山崎・白州・響などの抽選販売の告知） | 未確認 | — | https://www.suntory.co.jp/whisky/hakushu/kurashi/ | 許可 | 禁止なし | 不可 | 抽選の告知はブランドごとのページに分かれ、確認した白州の一覧はJSで描画される。JSONなどのデータ源と、山崎・響の一覧は上限に達して未確認 |
| 高島屋 ウイスキー・酒類の抽選販売（タカシマヤアプリ抽選／オンラインストア） | 未確認 | — | 未確認 | 許可（404） | 禁止なし | — | 抽選は単発の特設ページ（/store/special/<slug>/）とアプリ内告知で、それらが並ぶ一覧ページを予算内で見つけられなかった |
| 三越伊勢丹オンラインストア 三越伊勢丹ウイスキーコレクション（毎月20日の抽選販売） | 採用 | html_diff | https://www.mistore.jp/shopping/feature/foods_f3/whisky_festival_f | 許可 | 禁止なし | 可（4件） | 毎月20日に中身が入れ替わる特集ページ。生HTMLに商品リンクと申込期間があり、robotsは許可、規約に禁止なし |
| 大丸松坂屋 抽選販売（オンラインストアに一覧なし → 松坂屋上野店トピックスJSON） | 採用 | json_api | https://www.matsuzakaya.co.jp/ueno/topics/topics.json | 許可 | 禁止なし | 可（146件） | 上野店トップのトピックス枠の元データJSONが公開GETで取れる。店舗のウイスキー抽選告知はここに載る（2026年6〜7月に竹鶴の抽選告知。いまは該当なし） |
| 阪急百貨店 公式通販（HANKYU FOOD／HANKYU HANSHIN E-STORES）の抽選販売 | 不採用 | — | https://web.hh-online.jp/hankyu-food/ | 許可 | 禁止なし | 不可 | 公式通販のトップに抽選の一覧もリンクもない。阪急の抽選は店舗・アプリ・LINEで告知されており、公開の一覧ページは見つからなかった |
| イオン ウイスキー抽選販売の告知（イオンリテール／イオンリカー／AEON de WINE） | 未確認 | — | https://www.aeonretail.jp/information/ | 許可（404） | 禁止なし | 本文のみ（項目リンク0件） | ウイスキー抽選（南関東のイオン・イオンスタイル、イオンお買物アプリ会員向け）の公式告知ページを特定できなかった（検索予算切れ）。確認した一覧3か所にはウイスキー抽選がない |
| ビックカメラ（ビック酒販）ウイスキー・お酒の抽選販売 | 不採用 | — | 未確認 | 許可 | 未確認 | — | 酒類の抽選は店頭受付で、告知は公式X（@bic_shuhan）と店頭だけ。巡回できるWebページがなく、ホストも403 |
| カクヤス 特集一覧（希少ウイスキー販売会・抽選） | 採用 | html_diff | https://www.kakuyasu.co.jp/featured_products | 許可 | 禁止なし | 可（51件） | 特集一覧が生HTMLで日付つき。希少ウイスキーの販売会（抽選）がここに載る。robotsは許可、規約に禁止なし |
| やまや 特集・キャンペーン（やまやカード会員限定 ウイスキーWEB抽選） | 不採用 | html_diff | https://www.yamaya.jp/ynhp/contents/campaign/index.php | 許可 | 禁止なし | 可（4件） | 取得・robots.txt・規約は問題ないが、抽選バナーのリンク先が毎回同じ https://rfl.yamaya.jp/ で、商品名と期間は画像の中にしかなく、仕様の html_diff（増えたURL）では検出できない。ユーザー判断で不採用（2026-10-09） |

### A ウイスキー（国内蒸溜所）

| 候補 | 判定 | 取得方式 | 確認したURL | robots.txt | 規約 | JSなし | 理由 |
|---|---|---|---|---|---|---|---|
| ニッカウヰスキー公式 お知らせ（nikka.com・公式オンラインストア） | 不採用 | — | https://www.nikka.com/ | 許可（404） | 未確認 | 可（8件） | 自社のお知らせ一覧がない。トップの NEWS 欄（約1年半で8件）は大半が asahibeer.co.jp へのリンクで、抽選の告知はない。公式ストアのお知らせ（5件）もコーヒー商品の先着販売だけ |
| 秩父蒸溜所（ベンチャーウイスキー）公式お知らせ | 未確認 | — | 未確認 | 未確認 | 未確認 | — | お知らせ一覧のある公式サイトを特定できなかった。根拠は検索結果の要約だけで、サイトにはアクセスしていない |
| 厚岸蒸溜所 新着情報 | 不採用 | — | https://akkeshi-distillery.com/company/news/ | 許可（404） | 規約ページなし | 可（10件） | お知らせは新商品・受賞・イベントで、抽選販売の告知がない。REST API で全記事を「抽選」で検索しても1件（ファン向けイベントの告知）だけ |
| 嘉之助蒸溜所 NEWS | 不採用 | — | https://kanosuke.com/news/（429） | 許可 | 未確認 | — | ニュース一覧が 429（本文 local_rate_limited、Retry-After: 60）を返した。2回目のリクエスト（リダイレクト先）で発生したため、規則4により不採用 |
| 本坊酒造（マルス信州・マルス津貫）お知らせ | 採用 | rss | https://www.hombo.co.jp/feed/ | 許可 | 禁止なし | 可（20件） | RSS あり・robots 許可・規約に禁止なし。抽選の告知は蒸溜所祭りの案内の中に出る程度で、件数は少ない |
| ガイアフロー静岡蒸溜所 ニュース | 採用 | rss | https://www.gaiaflow.co.jp/feed | 許可 | 規約ページなし | 可（38件） | RSS あり・robots 許可・規約ページなし。新商品の記事本文に会員向けの抽選販売の案内が入る（直近2.5か月で2件） |
| 三郎丸蒸留所（若鶴酒造）NEWS | 採用 | rss | https://www.wakatsuru.co.jp/saburomaru/information/feed/ | 許可 | 規約ページなし | 可（20件） | RSS あり・robots 許可・規約ページなし。2026年1〜3月にコラボウイスキーの抽選販売の告知が5件あり、題名に「抽選販売」が出る |
| 長濱蒸溜所（長濱浪漫ビール）ニュース | 不採用 | — | https://www.romanbeer.com/news/ | 許可 | 規約ページなし | 可（10件） | 直近のお知らせ（2026-09-02〜10-06 の10件）は数量限定の発売と見学の案内だけで、抽選販売の告知がない |

### A ゲーム機・限定版

| 候補 | 判定 | 取得方式 | 確認したURL | robots.txt | 規約 | JSなし | 理由 |
|---|---|---|---|---|---|---|---|
| 任天堂 トピックス（nintendo.com/jp/topics）RSS | 不採用 | rss | https://www.nintendo.com/jp/topics/c/feed/rss/ | 許可（ただしコメントでTDM禁止を宣言） | 禁止なし | 可（10件） | robots.txt のコメントで、コンテンツの「web scraping, machine learning, or any form of text or data mining by any means」を書面の許可なく禁止すると宣言している（規則自体は Allow: / だが、禁止の意思表示として不採用にした） |
| マイニンテンドーストア お知らせ | 不採用 | — | 未確認 | 許可 | 未確認 | 不可 | トップへのアクセスが Queue-it 型の待合室（JavaScript・Cookie 必須）に飛ばされ、JSなしでは中身に届かない |
| PlayStation.Blog 日本語版 RSS | 採用 | rss | https://blog.ja.playstation.com/feed/ | 許可 | 禁止なし | 可（10件） | 公式RSSあり・robots許可（crawl-delay 5）・規約に機械取得の禁止なし。限定コントローラー・特別モデルの告知が載る |
| ソニー製品情報・ソニーストア 新着情報 RSS（PS5 のソニーストア販売の代わりとして確認） | 不採用 | — | https://www.sony.jp/ | 許可 | 禁止なし | 可（215件） | 取得はできるが、RSS 215件に抽選販売・PlayStation の告知がなく、対象外 |
| Xbox Wire Japan RSS | 採用 | rss | https://news.xbox.com/ja-jp/feed/ | 許可（404） | 禁止なし | 可（10件） | 公式RSSあり・robots.txtなし（制限なし）・規約に機械取得の禁止なし。限定コントローラー・限定本体の告知が載る |

### A 抽選まとめサイト

| 候補 | 判定 | 取得方式 | 確認したURL | robots.txt | 規約 | JSなし | 理由 |
|---|---|---|---|---|---|---|---|
| 抽選まとめサイト: トレゲト（旧カード抽選まとめ, cardchusen.com） | 不採用 | — | https://cardchusen.com/robots.txt（robots.txtのみ取得） | 許可 | 禁止あり | — | robots.txt で、利用規約第5条が機械的な取得・蓄積を禁じていると明記 |
| 抽選まとめサイト: 攻略大百科プレミアム（premium.gamepedia.jp）ポケカ／買い物ウォッチ | 不採用 | — | https://premium.gamepedia.jp/ | 許可 | 禁止なし | 可（10件） | RSSは個人利用OKで技術的にも取れる。ただし新着として抽選の告知が流れない（ポケカのフィード10件中0件、買い物のフィードはセール記事） |

### B 食品

| 候補 | 判定 | 取得方式 | 確認したURL | robots.txt | 規約 | JSなし | 理由 |
|---|---|---|---|---|---|---|---|
| 日清食品グループ キャンペーン一覧 | 採用 | html_diff | https://www.nissin.com/jp/product/campaigns/ | 許可（404） | 禁止なし | 可（3件） | 一覧が素のHTMLにあり（Astro SSR）、robots制限なし・規約に自動取得の禁止なし |
| 明治 キャンペーン一覧 | 採用 | html_diff | https://www.meiji.co.jp/campaign/ | 許可 | 禁止なし | 可（12件） | 実施中キャンペーン12件が素のHTMLにあり、robots許可・規約に自動取得の禁止なし |
| 森永製菓 キャンペーン情報 | 採用 | html_diff | https://www.morinaga.co.jp/campaign/ | 許可 | 禁止なし | 可（7件） | 一覧7件が素のHTMLにあり、robots許可・規約に自動取得の禁止なし（公式RSSもあるが一覧の全件は載らない） |
| カルビー キャンペーン・動画 | 採用 | html_diff | https://www.calbee.co.jp/campaign/ | 許可（404） | 禁止なし | 可（2件） | キャンペーン欄のリンクが素のHTMLにあり、robots制限なし・規約に自動取得の禁止なし |
| 味の素 キャンペーン一覧 | 未確認 | — | 未確認 | 許可（404） | 禁止なし | — | 公式のキャンペーン一覧ページのURLを特定できなかった（トップに一覧リンクなし、/campaign/ は404、Web検索の上限に達した） |
| ニチレイフーズ キャンペーン一覧 | 不採用 | — | https://www.nichireifoods.co.jp/campaign/（403） | 取得不可（403） | 未確認 | — | robots.txt と /campaign/ の両方が当方のUAに403（AWS ELB）を返す＝ブロックされているため |
| 山崎製パン キャンペーン | 採用 | html_diff | https://www.yamazakipan.co.jp/campaign/ | 許可 | 禁止なし | 可（2件） | 開催中キャンペーンのリンクが素のHTMLにあり、robots許可・規約に自動取得の禁止なし |

### B 飲料

| 候補 | 判定 | 取得方式 | 確認したURL | robots.txt | 規約 | JSなし | 理由 |
|---|---|---|---|---|---|---|---|
| サントリー 公式キャンペーン一覧 | 未確認 | — | https://www.suntory.co.jp/softdrink/ | 許可 | 禁止なし | 可（6件） | 本来のキャンペーン一覧 https://www.suntory.co.jp/softdrink/campaign/ は、ページ内のリンクとして見えただけで未取得（ホストのアクセス上限5回に達した）。確認できたのはソフトドリンクトップのキャンペーン枠（6件）だけ |
| キリン 公式キャンペーン一覧 | 採用 | json_api | https://www.kirin.co.jp/campaign/json/campaign.js | 許可（404） | 禁止なし | 可（491件） | 一覧のHTMLはJS描画だが、同じデータの公開JSON(JSONP)が200で取れる。robots.txtは404、規約に機械取得の禁止なし |
| アサヒビール 公式キャンペーン一覧（候補「アサヒ（アサヒビール／アサヒ飲料）」の1/2） | 採用 | html_diff | https://www.asahibeer.co.jp/campaign/ | 許可 | 禁止なし | 可（12件） | 実施中のキャンペーン12件が生HTMLにあり、robots許可・規約に機械取得の禁止なし。先着・絶対もらえる型も載る |
| アサヒ飲料 公式キャンペーン一覧（候補「アサヒ（アサヒビール／アサヒ飲料）」の2/2） | 採用 | html_diff | https://www.asahiinryo.co.jp/campaign/ | 許可 | 禁止なし | 可（8件） | 実施中のキャンペーン8件が生HTMLにあり、robots許可・規約に機械取得の禁止なし |
| コカ・コーラ（日本コカ・コーラ） 公式キャンペーン一覧 | 不採用 | — | https://www.coca-cola.com/jp/ja/brands/coca-cola/campaign | 許可 | 禁止あり | 可（6件） | 利用規約がロボット・スクレイピングによるアクセスや取得を明記して禁止している |
| 伊藤園 公式キャンペーン一覧 | 採用 | html_diff | https://www.itoen.jp/campaign/ | 許可 | 禁止なし | 可（1件） | 実施中・終了のキャンペーン一覧が生HTMLにあり、robots許可・規約に機械取得の禁止なし |

### B 日用品

| 候補 | 判定 | 取得方式 | 確認したURL | robots.txt | 規約 | JSなし | 理由 |
|---|---|---|---|---|---|---|---|
| 花王 キャンペーン・イベント一覧（My Kao） | 不採用 | — | https://member.kao-kirei.com/jp/campaign/ | 許可 | 禁止なし | 不可 | 一覧は5つの空の<ul>をJS（mustacheテンプレート＋Vue）で埋める作りで、生HTMLにキャンペーンへのリンクがない |
| ライオン キャンペーン一覧（Lidea） | 採用 | html_diff | https://lidea.today/all-campaign.php | 許可 | 禁止なし | 可（2件） | ライオン公式の一覧が生HTMLに載っている・robotsは全許可・規約に機械取得の禁止なし |
| P&G マイレピ お得なキャンペーン | 不採用 | — | https://www.myrepi.com/campaigns/ | 許可 | 禁止あり | 可（9件） | P&Gの利用規約が「スクレイピング」や「ロボット、スパイダー、その他の自動化された手段」でのコピーを明示的に禁じている |
| ユニ・チャーム キャンペーン | 採用 | html_diff | https://www.unicharm.co.jp/ja/campaign.html | 許可 | 禁止なし | 可（4件） | 公式の一覧が生HTMLに載っている・robots許可・規約に機械取得の禁止なし・先着で必ずもらえる型もある |
| 小林製薬 キャンペーン情報 | 不採用 | — | https://www.kobayashi.co.jp/seihin/campaign/ | 許可 | 禁止なし | 不可 | 一覧ページはあるが今は1件も載っておらず、項目リンクの形を確かめられない。更新もまれ |

### B コンビニ

| 候補 | 判定 | 取得方式 | 確認したURL | robots.txt | 規約 | JSなし | 理由 |
|---|---|---|---|---|---|---|---|
| セブン‐イレブン セール・キャンペーン一覧 | 採用 | html_diff | https://www.sej.co.jp/cmp/ | 許可（404） | 禁止なし | 可（39件） | 一覧が素のHTMLに39件あり、無料クーポン系のキャンペーンを含む。robots制限なし・規約に機械取得の禁止なし |
| ファミリーマート キャンペーン一覧 | 採用 | html_diff | https://www.family.co.jp/campaign.html | 許可（404） | 禁止なし | 可（33件） | 一覧が素のHTMLにあり、「1個買うと、1個もらえる」「無料引換券がもらえる」を含む。robots制限なし・規約に機械取得の禁止なし |
| ローソン お得なセール情報（もらえるキャンペーン一覧） | 採用 | html_diff | https://www.lawson.co.jp/recommend/sale/index.html | 許可 | 禁止なし | 可（28件） | 「◯◯1本/1個もらえるキャンペーン」「無料券がもらえる」が個別URLつきで素のHTMLに28件。robots許可・規約に機械取得の禁止なし |
| ローソン エンタメ・キャンペーン一覧（補足） | 不採用 | — | https://www.lawson.co.jp/campaign/ | 許可 | 禁止なし | 可（19件） | 取得はできるが、中身はコラボの購入特典グッズとLoppiの予約商品が中心で、無料引換・全額還元はほとんどない |

### B ゲーム（無料配布）

| 候補 | 判定 | 取得方式 | 確認したURL | robots.txt | 規約 | JSなし | 理由 |
|---|---|---|---|---|---|---|---|
| Epic Games Store 無料ゲーム（freeGamesPromotions JSON） | 不採用 | json_api | https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=ja&country=JP&allowCountries=JP | 許可（404） | 未確認（禁止条項の可能性あり） | 可（12件） | 認証なしのJSONは取れて robots.txt もないが、サイト利用規約がこちらのUAに403で読めず、検索結果の抜粋（未確認）に自動の手段で監視・分析などのためにデータを抽出すること（scraping）を禁じる条項がある可能性があるため、ユーザー判断で不採用（2026-10-09） |
| Steam 期間限定無料配布（Free to Keep） | 不採用 | — | https://store.steampowered.com/search/?maxprice=free&specials=1 | 許可 | 禁止あり | 可（4件） | Steam 利用規約 4.C が、スクリプト・ボット等で Steam のコンテンツやサービスとやり取りすることを禁じている（例示に限定されない書き方） |
| GOG 無料配布（Giveaway） | 不採用 | — | https://www.gog.com/en/ | 許可 | 未確認 | 不可 | トップの生HTMLに配布の中身がない（Angular の JS 描画）。JSON は確認できず、規約ページは 403 で読めない |
| Prime Gaming（Amazon）無料ゲーム | 不採用 | — | 未確認 | 許可 | 未確認 | 不可 | gaming.amazon.com は Amazon Luna の受け取りページに移っていて、生HTMLはリンク0件の JS アプリ（受け取りには Prime ログインが必要） |
| GamerPower 公開API（ゲームの無料配布の一覧） | 不採用 | json_api | https://www.gamerpower.com/api-read | 禁止 | 禁止あり | 不可 | robots.txt が全UAに対して /api/* を Disallow しているため（説明ページはボットでの利用を案内しているが、robots.txt に従う） |
| GamerPower 無料配布RSS | 採用 | rss | https://www.gamerpower.com/rss/giveaways | 許可 | 禁止とも読める条文あり（ユーザー判断で採用） | 可（14件） | robots.txtは許可。利用規約の Acceptable Use Policy に「自動のリクエスト・問い合わせの禁止」があるが、サイト自身がRSSを提供しボットでの利用も案内していることから、RSSの定期取得は想定内とみなしてユーザー判断で採用（2026-10-09） |
| Game*Spark 新着記事RSS | 採用 | rss | https://www.gamespark.jp/rss20/index.rdf | 許可 | 禁止なし | 可（50件） | 取得・robots.txt・規約は問題なし。ニュース記事だが、今受け取れる無料配布を伝える記事は対象とする（2026-10-09 ユーザー判断） |
| AUTOMATON 新着記事RSS | 採用 | rss | https://automaton-media.com/feed/ | 許可 | 禁止なし | 可（60件） | 取得・robots.txt・規約は問題なし。ニュース記事だが、今受け取れる無料配布を伝える記事は対象とする（2026-10-09 ユーザー判断） |
| 4Gamer.net 新着記事RSS | 不採用 | rss | https://www.4gamer.net/rss/index.xml | 許可 | 規約ページなし | 可（100件） | 取得・robots.txt・規約は問題ないが、約2日分100件に、受け取って持ち続けられる無料配布の記事がなかった（Core Keeper のフリーウィークエンドなど、期間中に遊べるだけのもの） |

### B 懸賞・キャンペーンまとめサイト

| 候補 | 判定 | 取得方式 | 確認したURL | robots.txt | 規約 | JSなし | 理由 |
|---|---|---|---|---|---|---|---|
| チャンスイット 懸賞情報（全員・先着） | 不採用 | — | https://www.chance.com/（トップ https://www.chan） | 許可 | 禁止あり | 可（30件） | 規約で「提供されているインターフェイス以外の手段」でのアクセスと、承諾のない情報収集を禁止しているため |
| 懸賞にゃんダフル | 不採用 | — | https://www.nyandaful.jp/ | 許可 | 禁止なし | 不可 | 今は広告利用でポイントがたまるポイントサイトで、メーカーの懸賞やキャンペーンをまとめたものではない（対象を載せていない） |

Googleアラート（6.4 のキーワード9本）：ユーザーが手動で作成する。sources.yaml には `google_alert_*` の空欄だけを用意した（enabled: false）。

## 決定事項（2026-10-09 ユーザー確認）

1. **任天堂**：RSSは robots.txt の規則上は許可だが、同じファイルのコメントでスクレイピング・テキスト・データマイニングの禁止を宣言しているため、不採用で確定。
2. **URLが増えない一覧**：ヨドバシ（抽選ごとに本文が差し替わる）とやまや（バナーのリンク先が毎回同じ）は不採用。
3. **「1個買うと1個もらえる」系**：同じ商品をもう1個もらえるもの、別の商品の無料引換券がもらえるもの（例：弁当を買うとお茶の無料引換券）のどちらも通知の対象（free_item）。ただしファミマの常設ページ（/campaign/spot/2023_1buy1-receipt_cp.html）は毎週同じURLのまま回が替わるため、仕様（8.1：同じURLは再処理しない）では2回目以降を拾えない。
4. **共通の情報源の scope**：`scope: [A, B]` と書く。
5. **Epic Games**：不採用。サイト利用規約（https://www.epicgames.com/site/en-US/tos）はこちらのUAに403で読めず、検索結果の抜粋（未確認）には、自動の手段で監視・分析などのためにデータを抽出すること（scraping）を禁じる条項がある可能性があるため。
6. **森永製菓**：公式RSSではなく、一覧ページの html_diff を使う（RSSに載らない実施中キャンペーンがあるため）。
7. **html_diff の中身**：キャンペーンの概要が取れれば十分。一覧ページの文字（リンクの文字・画像のalt・カードの文言）だけを使い、個別ページは取得しない。リンク先が別ドメインや robots.txt の Disallow（アサヒビールの /web-service/ など）でも問題にならない。
8. **ゲームニュースのRSS**：Game*Spark・AUTOMATON を採用。DESIGN.md 2章の「ニュース記事は除外」の例外として、今受け取れる無料配布を伝える記事は対象にする（予告・終了済み・体験版・基本プレイ無料は除外）。4Gamer は対象記事が見当たらず不採用のまま。
9. **GamerPower**：RSSを採用（規約の「自動のリクエストの禁止」はあるが、サイト自身がRSSを提供していることから想定内とみなす）。APIは robots.txt の Disallow のため不採用のまま。

運用開始後の変更：
- 2026-10-09 ゲオ（geo_news_lottery）は HTTP 403、三越伊勢丹（mistore_whisky_collection）はタイムアウトが 15:42 以降続いたため、sources.yaml で停止（enabled: false）。ボット対策と思われるので回避はしない。数日後に1回だけ再確認する。

まだ決めていないこと：
- （フェーズ3で決定）html_diff で見るリンクは、sources.yaml の省略できる項目 `link_selector`（CSSセレクタ）と `link_pattern`（URLの正規表現）で絞る。17情報源ぶんを保存したページで確かめて設定した。HTMLコメント内の終了分は、リンクとして扱われないので自然に除かれる。
- 嘉之助蒸溜所は最初のリクエストで 429 が返ったため不採用のまま。時間をおいて再確認するかは未定。
- 取得間隔は DESIGN.md 6.5 の最短値（rss・json_api 30分、html_diff 360分）をそのまま入れた。

## 代わりの情報源の案（未検証）

採用が少ないのは B の daily（2件）、A の tcg・console（3件ずつ）。B の game は追加検証で3件になった。以下は検証していない案で、URLもまだ確かめていない。採用する場合は同じ手順で検証する。

- **game（無料配布）**
  - GamerPower（API・RSS）と、Game*Spark・AUTOMATON・4Gamer.net のRSSは検証済み（一覧表「B ゲーム」を参照）
  - Googleアラート「無料配布 ゲーム 期間限定」に加え、「Epic Games 無料配布」「Steam 無料配布 期間限定」など
- **daily（日用品）**
  - 花王・P&G は PR TIMES で発表するキャンペーンがあれば `prtimes_all` で拾える
  - 小林製薬のキャンペーン一覧は、取得・robots.txt・規約とも問題なし。掲載0件で不採用にしただけなので、キャンペーンが載った時点で再確認すれば採用できる見込み
  - ほかの日用品メーカー（エステー、アース製薬、サンスター、ユニリーバ・ジャパン、牛乳石鹸など）の公式キャンペーン一覧
  - ドラッグストア（マツキヨココカラ、ウエルシア、スギ薬局など）のキャンペーン一覧
- **tcg（トレカ）**
  - 未確認のワンピースカード公式JSON：過去分に抽選の告知が載るかを確かめれば採用できる（あと1〜2回のアクセス）
  - 遊戯王OCG公式、デュエル・マスターズ公式、バンダイ カードダス公式のニュース
  - 抽選販売を行う量販店・チェーン（トイザらス、セブンネットショッピング、TSUTAYA、イオンなど）の抽選告知ページ
- **console（ゲーム機・限定版）**
  - 上と同じ量販店・チェーン（トイザらス、セブンネットショッピング、ヤマダデンキ、ケーズデンキなど）の抽選告知ページ
  - ジョーシンは利用規約のPDFを読めば判断できる（一覧ページは未特定）
  - ゲオのお知らせ（採用済み）にゲーム機の抽選が載るかは、運用しながら確認する

## 候補ごとの詳細

### 共通（A・B）

#### PR TIMES 新着プレスリリースRSS（`prtimes_all`）— 採用

- 理由：RSSあり・robots全許可・規約に機械取得の禁止なし
- スコープ・ジャンル：A,B / tcg, whisky, console, food, drink, daily, cvs, game
- 一覧ページ：https://prtimes.jp/（200）
- 取得URL（rss）：https://prtimes.jp/index.rdf
- RSS/Atom：https://prtimes.jp/index.rdf（RSS 1.0、200件、2026-10-09 07:10〜09:45 JST の約2.5時間分。トップとカテゴリページの <link rel=alternate> が指すのはこの1本のみ）
- 公開JSON：なし（確認範囲で見当たらず）
- sitemap：https://prtimes.jp/sitemap.xml, https://prtimes.jp/sitemap-news.xml（robots.txtに記載、未取得。RSSで足りるため）
- robots.txt：https://prtimes.jp/robots.txt（200）→ ALLOW（Allow: /）
- 規約：https://prtimes.jp/main/html/kiyaku → 禁止なし。一般ユーザー・ゲストは「情報閲覧等の情報取得や著作権法上の『私的使用のための複製』や『引用』の範囲内」で企業コンテンツを無償で利用できる（第3条）。禁止事項は不正アクセス・大量のパケット送信など。スクレイピング・クローラーを禁じる条文はない
- JSなしのリンク：可（200件、見方：`RSS <item>`） 例：https://prtimes.jp/main/html/rd/p/000000147.000023848.html
- ログイン：不要　アクセス数：5
- メモ：カテゴリ別フィードはなし（/gourmet/ の <link rel=alternate> も index.rdf を指す）。キーワードページ /topics/keywords/<語> はあるがRSSは見当たらず。全件RSSなのでルールフィルタで絞る前提。各itemに title・description（本文冒頭約100字）・dc:corp（企業名）・dc:date がある。200件で約2.5時間分なので30分間隔なら取りこぼさない見込み。sources.yaml の scope は単一値の形式だが、この情報源はA・B共通（要確認）

### A トレカ

#### ポケモンカード公式 ニュース一覧（`pokemon_card_news`）— 採用

- 理由：JSなしで記事リンクが取れる・robots制限なし・規約に機械取得の禁止なし。ポケセンオンラインの抽選告知も外部リンクとして載る
- スコープ・ジャンル：A / tcg
- 一覧ページ：https://www.pokemon-card.com/info/（200）
- 取得URL（html_diff）：https://www.pokemon-card.com/info/
- RSS/Atom：なし（<link rel=alternate>なし、ページ内に rss/feed/xml へのリンクなし）
- 公開JSON：なし（確認範囲で見当たらず）
- sitemap：robots.txt なし（404）のため記載なし
- robots.txt：https://www.pokemon-card.com/robots.txt（404）→ ALLOW（robots.txt 404 = 制限なし（RFC 9309））
- 規約：https://www.pokemon-card.com/policy.html → 禁止なし。「サイトのご利用」。「データは、個人的に楽しむ場合に限って使用を許諾」「データのコピー、複製、改変、出版、掲示、電送、配布することは固くお断り」「無断転載はお断り」のみ。クローラ・スクレイピング・自動取得を禁じる条文はない（terms_grep の [P] ヒット 0 件）
- JSなしのリンク：可（135件、見方：`/info/\d{6}\.html|pokemoncenter-online\.com/news/`） 例：https://www.pokemon-card.com/info/005559.html、https://www.pokemon-card.com/info/005678.html、https://www.pokemoncenter-online.com/news/?id=20260929
- ログイン：不要　アクセス数：3
- メモ：2026年分のニュース一覧（10月〜1月を月見出しで区切り、133件＋外部リンク2件）。普段のニュース（大会・商品・コラム等）の中に、ときどき抽選の告知が入る。例:「ポケモンセンターオンラインでの商品の抽選受け付けについて (外部リンク) 2026.9.29」→ https://www.pokemoncenter-online.com/news/?id=20260929 、「【第二回】ポケモンセンターオンラインでの30周年商品の抽選受け付けについて」→ ?id=20260821。ポケセンオンライン本体は規約で取得を禁じているので不採用（下記）。ただしこの一覧の見出しで告知そのものは拾える。リンク先のポケセンオンラインを collector が開いてはいけない。記事の形: https://www.pokemon-card.com/info/NNNNNN.html（6桁の通し番号）。外部リンクの href の末尾に空白が入ることがあるので trim すること。各項目はカテゴリ（Calendar_Label_Products/Event/Column 等）・タイトル・日付（YYYY.M.D）を持つ。過去の年は /info/2025.html 形式。ETag・Last-Modified は返らないため条件付きGETはできない。毎回まるごと取得（約220KB）になるので、6時間間隔を守ること。CloudFront 経由で x-cache: Hit・age=442258秒（約5日）。キャッシュが古いままだと反映が遅れるおそれがある。

#### ポケモンセンターオンライン お知らせ（抽選告知）（`pokemoncenter_online_news`）— 不採用

- 理由：利用規約 第6条⑰⑱でクローリング・スクレイピング・自動手段による情報取得を明示的に禁止
- スコープ・ジャンル：A / tcg
- 一覧ページ：https://www.pokemoncenter-online.com/（200）
- RSS/Atom：未確認（規約で禁止のため追跡せず）
- 公開JSON：未確認
- sitemap：robots.txtに記載なし
- robots.txt：https://www.pokemoncenter-online.com/robots.txt（200）→ ALLOW（Disallow: （空））
- 規約：https://www.pokemoncenter-online.com/terms.html → 禁止あり。第6条 禁止事項（会員以外も含む全「ユーザー」に適用）「⑰自動化された手段（自動購入ツール、BOTなどこれらに準ずる手段）を用いて本サービスを利用する行為（在庫情報等の取得行為を含む） ⑱クローリング（クローラ、ロボット又はスパイダー等のプログラム）、スクレイピング及びその他の類似の手段によって本サービスにアクセスし、又は本サービスに関する情報を取得する行為」
- JSなしのリンク：可（22件、見方：`/news/\?id=`） 例：https://www.pokemoncenter-online.com/news/?id=20260929、https://www.pokemoncenter-online.com/news/?id=20260904、https://www.pokemoncenter-online.com/news/?id=20260803
- ログイン：不要　アクセス数：3
- メモ：技術的には取得できる。トップページの「お知らせ」欄に、ログインなし・JSなしで抽選の告知が載っている（例: 2026年09月29日「ポケモンカードゲームの追加抽選販売について」/news/?id=20260929）。ただし規約で禁止されているので不採用。代わりに、ポケモンカード公式のニュース一覧（pokemon_card_news）がポケセンの抽選告知を外部リンクとして載せている。そちらで見出しだけ拾える。混む日には仮想待合室あり（お知らせ ?id=20261006 等）。

#### ワンピースカードゲーム公式 ニュース（お知らせ一覧）（`onepiece_cardgame_news`）— 未確認

- 理由：取得の手段は確認できた（公開JSON・robots制限なし・規約なし）。ただし、ニュースに抽選の告知が載るかを確かめられなかった（直近10件に抽選なし。アクセス上限とWeb検索の上限に達した）
- スコープ・ジャンル：A / tcg
- 一覧ページ：https://www.onepiece-cardgame.com/news/（200）
- 取得URL（json_api）：https://www.onepiece-cardgame.com/common/templates/api/article_list.php?start=0&limit=10&data=%7B%22category%22%3A%22INFORMATION%22%2C%22subcategory%22%3A%5B%22%22%5D%2C%22is_history%22%3Atrue%7D
- RSS/Atom：なし（<link rel=alternate> は hreflang の言語版のみ、RSS/Atom なし）
- 公開JSON：https://www.onepiece-cardgame.com/common/templates/api/article_list.php?start=0&limit=10&data={"category":"INFORMATION","subcategory":[""],"is_history":true}（認証なしで200・application/json。total_count=153）
- sitemap：robots.txt なし（404）のため記載なし
- robots.txt：https://www.onepiece-cardgame.com/robots.txt（404）→ ALLOW（robots.txt 404 = 制限なし（RFC 9309））
- 規約：— → 規約ページなし。トップページのフッターにあるのは「プライバシーポリシー」（https://www.bandai.co.jp/site/privacy/）、「プライバシーノーティス」、推奨環境、お問い合わせのみ。利用規約・サイトのご利用に当たるリンクは見当たらない
- JSなしのリンク：不可（2件、見方：`/news/`） 例：https://www.onepiece-cardgame.com/news/restriction-261012.html、https://www.onepiece-cardgame.com/news/01_379.html
- ログイン：不要　アクセス数：5
- メモ：/news/ の一覧は JS（/renewal/js/news_async.js、Vue）で後から読み込む。生のHTMLには固定のお知らせ2件しかない。その JS が呼んでいる JSON API（上記 fetch_url）を一度だけ取得して確認した。data.article_list[] の各項目は title・dspdate（"2026/10/02 15:03"）・categories.subcategory[0].code（products/cards/events/rules 等）・path（例 01_522）・onepiece.related_item.jp[0]（type=article なら url="/products/eb05" で、表示は url+".html"。type=link なら外部や内部の完全URL）を持つ。一意なIDは _id または path。直近10件（10/2〜9/25）は商品発売・プロモカード・イベント・ルールで、抽選販売は0件。イベント会場での先行販売が1件あるだけ。ワンピカードの抽選は主にプレミアムバンダイなどの販売店が行っており、公式ニュースに載るかは未確認。次に確かめること: limit を増やす（例 limit=50）か start でさかのぼり、過去153件に「抽選」があるかを見る。API は公開されている仕様ではなく、ページの内部エンドポイント。仕様が変わる可能性がある。トップページ（/）の取得は規約リンクを探すためで、結果的に不要だった。

#### あみあみ 抽選販売告知（`amiami_lottery`）— 不採用

- 理由：トップページ https://www.amiami.jp/ が Cloudflare の 403「Sorry, you have been blocked」で、こちらの UA をブロック
- スコープ・ジャンル：A / tcg
- 一覧ページ：未確認（403）
- RSS/Atom：未確認
- 公開JSON：未確認
- sitemap：robots.txt なし（404）のため記載なし
- robots.txt：https://www.amiami.jp/robots.txt（404）→ ALLOW（robots.txt 404 = 制限なし（RFC 9309））
- 規約：— → 未確認。トップページが403でブロックされ、規約へのリンクを確認できず（ブロックのため追加の取得はしていない）
- JSなしのリンク：不可（0件、見方：`None`）
- ログイン：不要　アクセス数：2
- メモ：robots.txt の取得は Cloudflare 経由で 404（HTMLが返った）。トップページは 403（Cloudflare のブロック画面「Attention Required! / You are unable to access amiami.jp」、Ray ID a4799817f86a29e0）。指示どおり回避策は試していない。抽選販売ページのURL・ゲーム機を扱っているかは未確認。

#### ホビーステーション 最新ニュース（抽選販売告知）（`hobbystation_news`）— 採用

- 理由：ニュースのカテゴリRSSに抽選販売の告知がそのまま流れる・robots許可・規約ページなし
- スコープ・ジャンル：A / tcg
- 一覧ページ：https://www.hbst.net/（200）
- 取得URL（rss）：https://www.hbst.net/category/news/feed
- RSS/Atom：https://www.hbst.net/category/news/feed（RSS 2.0、200、10件、2026-08-13〜10-06、10件中6件が抽選販売）
- 公開JSON：未確認（WordPress の wp-json は <link> にあるが、RSSで足りるため取得せず）
- sitemap：https://www.hbst.net/sitemap.xml, https://www.hbst.net/sitemap.rss（robots.txtに記載、未取得）
- robots.txt：https://www.hbst.net/robots.txt（200）→ ALLOW（(no matching rule)（Disallow は /wordpress/wp-admin/ のみ））
- 規約：— → 規約ページなし。トップページのフッターにあるのは会社案内・お問い合わせ・プライバシーポリシー（/privacy/）のみ。利用規約・サイトのご利用に当たるリンクはない
- JSなしのリンク：可（10件、見方：`RSS <item>（トップの HTML でも \?p=\d+ に5件）`） 例：https://www.hbst.net/?p=411288、https://www.hbst.net/?p=411284、https://www.hbst.net/?p=411179
- ログイン：不要　アクセス数：4
- メモ：公式サイトは hbst.net（シングル通販は別の hobbystation-single.jp で、今回は未確認）。<link rel=alternate> で案内されているフィードは /category/items/feed（「ニュース」と題するが中身は新作発売スケジュールで、最新が2025-10と古い）と /category/blog/feed だけ。抽選の告知は「最新ニュース」（トップの欄、一覧は /result/?category=news で未取得）に載る。これは WordPress 標準のカテゴリフィード /category/news/feed で取れることを、200で確かめた。10件のうち抽選販売が6件（例「【2026.10.06】抽選販売「ポケモンカードゲームMEGA 拡張パック ストームエメラルダ （再販）」」）。残りは休業のお知らせなど。月に数件の更新。応募が締め切られると、タイトルの頭に「※応募は終了しました」が付いて書き換わる。重複の判定は guid か ?p=ID で行うこと（タイトルでは判定しない）。link には utm_source 等が付くので ?p=ID に正規化する。応募は外部の Livepocket（t.livepocket.jp）で行う。ETag・Last-Modified あり（条件付きGETが使える。ETag は items のフィードと同じ値で、サイト全体で共通らしい）。X-Robots-Tag: noindex, follow（検索インデックス向けで、取得の可否とは関係ない）。トップに reCAPTCHA v3 のスクリプトがあるが、問い合わせフォーム用で、閲覧のブロックではない。

### A 家電量販店・ゲーム専門店（トレカ・ゲーム機共通）

#### ヨドバシ・ドット・コム 人気商品抽選（limited.yodobashi.com）（`yodobashi_limited_lottery`）— 不採用

- 理由：取得・robots.txt・規約は問題ないが、ページ内に抽選ごとのリンクがなく、抽選のたびに本文が差し替わる形式で、仕様（6.1：増えたURLだけを新着とする）の html_diff では新着を検出できない。ユーザー判断で不採用（2026-10-09）
- スコープ・ジャンル：A / tcg, console
- 一覧ページ：https://limited.yodobashi.com/（200）
- 取得URL（html_diff）：https://limited.yodobashi.com/
- RSS/Atom：なし（<link rel=alternate>なし、ページ内リンクなし）
- 公開JSON：なし
- sitemap：robots.txtに記載なし（www.yodobashi.com の robots.txt は空ファイル、limited.yodobashi.com は404）
- robots.txt：https://limited.yodobashi.com/robots.txt（404）→ ALLOW（robots.txt 404 → 制限なし（www.yodobashi.com/robots.txt は200・0バイトで全許可））
- 規約：https://www.yodobashi.com/ec/sitepolicy/agreement/001/index.html → 禁止なし。「ご利用者の個人的使用の為に提供します」「書面による許可を得ずに…非商業的かつ個人的な目的以外で、使用、複製またはダウンロード…をしないで下さい」。スクレイピング・クローラー・自動取得を禁じる条文なし（サイトポリシー /ec/sitepolicy/index.html も該当なし）
- JSなしのリンク：可（0件、見方：`（リンクではなく本文）h2.application_schedule_text と section.sec03 の本文`） 例：https://limited.yodobashi.com/
- ログイン：不要　アクセス数：7
- メモ：一覧ページではなく、抽選1件ごとにトップ（https://limited.yodobashi.com/）の中身が差し替わる形式。取得時点（2026-10-09）は「お申し込み受付は終了いたしました」、受け取りは10月16日から・「おもちゃ・玩具コーナーでお受け取り」とあるのでトレカ系の抽選とみられる（商品名は終了表示では出ない）。nginx配信で ETag "6ac65e41-da7"・Last-Modified Wed, 07 Oct 2026 14:59:13 GMT があり、条件付きGETが使える。html_diff は ETag/Last-Modified の変化、または h2.application_schedule_text と section.sec03 の本文テキストの変化で検知する（ページ内に個別抽選へのリンクはない。リンクは www.yodobashi.com トップ と店舗受取案内の2本だけ）。www.yodobashi.com/ec/support/news/list/index.html（お知らせ一覧）と www トップには「抽選」の語がなく、抽選の告知には使われていない（第三者記事によると告知はトップのバナーと公式X @Yodobashi_X）。Akamai Bot Manager のピクセルと Cookie（ak_bmsc）が付くが、今回のUAでは200で返った。将来ブロックされる可能性はある。お年玉箱の抽選は lottery.yodobashi.com を使うと第三者記事にあるが未取得・未確認

#### ビックカメラ.com 抽選販売ページ（トレカ・ゲーム機）（`biccamera_lottery`）— 不採用

- 理由：トップが今回のUAに403（アクセス遮断）を返すうえ、抽選の一覧ページがない
- スコープ・ジャンル：A / tcg, console
- 一覧ページ：未確認（403（https://www.biccamera.com/ → /bc/main/ が「通信に問題があるためアクセスを遮断しました」）／200（/bc/c/sale/special/lottery/ は受付終了の告知だけ））
- RSS/Atom：なし（<link rel=alternate>なし、ページ内リンクなし）
- 公開JSON：未確認
- sitemap：robots.txtに記載なし
- robots.txt：https://www.biccamera.com/robots.txt（200）→ ALLOW（(no matching rule)（/bc/c/sale/special/lottery/・/bc/main/ とも該当ルールなし））
- 規約：— → 未確認。トップが403のため規約ページへのリンクを取得できず、未取得
- JSなしのリンク：不可（0件、見方：`抽選|lottery|lot`）
- ログイン：不要　アクセス数：3
- メモ：https://www.biccamera.com/bc/c/sale/special/lottery/ は200だが、中身は「Nintendo Switch 抽選販売お申し込み受付終了 掲載を終了いたしました」だけ（Last-Modified 2025-04-05、リンク9本はすべてナビ）。個別抽選は /bc/c/sale/special/lottery/<名前>.html の形式（例：switch2_order.html。第三者記事 automaton-media.com に載っていたURLで、未取得・未確認）で、まとめて見られる一覧ページは見つからない。トップ（/bc/main/）は今回のUAに403「通信に問題があるためアクセスを遮断しました」を返したので、指示どおり別のUA・別のホストでは試していない。第三者記事（torecamap）によると、店頭の抽選は各店舗の公式Xと店内ポスターで告知され、Webやアプリでは受け付けない

#### Joshin webショップ 抽選販売（`joshin_lottery`）— 未確認

- 理由：抽選販売の一覧ページが見つからず、利用規約（PDF）も未読
- スコープ・ジャンル：A / tcg, console
- 一覧ページ：未確認（200（トップ /top.html・お知らせ一覧 /info.html・ゲームトップ /game/top.html。いずれも抽選販売の掲載なし））
- RSS/Atom：なし（<link rel=alternate>なし、ページ内リンクなし）
- 公開JSON：未確認
- sitemap：https://joshinweb.jp/contents/sitemap/sitemap_index.xml（robots.txtに記載、未取得）
- robots.txt：https://joshinweb.jp/robots.txt（200）→ ALLOW（(no matching rule)（User-agent: * は Disallow: /cgi-bin/ のみ））
- 規約：https://joshinweb.jp/contents/agr/agreement.pdf → 未確認。利用規約は https://joshinweb.jp/other.html#rule から PDF（agreement.pdf、約523KB）でのみ提供。アクセス上限（5回）に達したため未取得
- JSなしのリンク：不可（0件、見方：`抽選|lot|switch_nd|特設`）
- ログイン：不要　アクセス数：5
- メモ：足りないもの：(1) 抽選販売の一覧ページのURL。トップ（https://joshinweb.jp/top.html）、お知らせ一覧（https://joshinweb.jp/info.html、10件）、テレビゲームのトップ（https://joshinweb.jp/game/top.html）に抽選販売のリンクはなかった。トップで「抽選」を含むのは「阪神グッズ抽選プレゼント」（/present.html）の2件だけで、対象外。第三者記事によると、抽選は企画ごとの特設ページ（例：https://joshinweb.jp/game/switch_nd.html、未取得・未確認）と Joshin アプリ・店舗で行われる。(2) 利用規約 PDF の中身。ページはJSなしでも本文とリンクが出る（ただし「Javascriptを有効に」の注意書きあり）。再調査するなら、特設ページのURLの形（/game/<名前>.html）と、トップのバナー alt に「抽選販売」が出るかを確認する

#### エディオン 抽選販売（`edion_lottery`）— 不採用

- 理由：抽選は別ドメイン edion-cp.com の企画ごとのページで、一覧がなく（ルートは404）、本体サイトのトップやお知らせにも載らない
- スコープ・ジャンル：A / tcg, console
- 一覧ページ：未確認（200（www.edion.com トップ・/info.html。抽選の掲載なし）／404（https://edion-cp.com/ と過去の企画ページ /sw2pkza0905））
- RSS/Atom：なし（<link rel=alternate>なし、ページ内リンクなし）
- 公開JSON：未確認
- sitemap：https://www.edion.com/sitemap.xml（robots.txtに記載、未取得。抽選は別ドメイン edion-cp.com なので含まれない見込み）
- robots.txt：https://www.edion.com/robots.txt（200）→ ALLOW（(no matching rule)（Disallow は /member* /order* /catalogmall/ のみ。edion-cp.com/robots.txt は「Disallow:」空で全許可））
- 規約：https://www.edion.com/guide/gid_menu_kiyaku.html → 禁止なし。禁止事項「(4)本サイトのサーバーへの大量のデータ転送、不正な連続アクセス、その他本サービスの正常な運営を妨げる行為」（負荷の禁止のみ）と「著作物の全部または一部を無断で使用、転載することを禁じます」。スクレイピング・クローラーを禁じる条文なし
- JSなしのリンク：不可（0件、見方：`info_detail|抽選|edion-cp`）
- ログイン：不要　アクセス数：8
- メモ：www.edion.com のトップと「お知らせ（一覧）」（https://www.edion.com/info.html）には「抽選」の語も edion-cp.com へのリンクもない（お知らせは5件で、関係があるのは「転売のお断りについて」info_no=0000000285 だけ）。第三者記事（automaton-media.com）によると、抽選の特設ページは https://edion-cp.com/<企画名>（例：sw2pkza0905）の形式だが、そのページもルートも今は404で、終わった企画は消える。応募にはSMS認証が必要。巡回できる一覧がないので不採用。Cloudflare 配信だが、今回のUAで200だった

#### ノジマオンライン 抽選販売（`nojima_lottery`）— 不採用

- 理由：トップが今回のUAに Akamai のボット判定チャレンジ（JS必須の検証画面）を返す＝ブロック
- スコープ・ジャンル：A / tcg, console
- 一覧ページ：未確認（200（ただし本文は Akamai のボット判定チャレンジのみ））
- RSS/Atom：未確認
- 公開JSON：未確認
- sitemap：robots.txt 404 のため記載なし
- robots.txt：https://online.nojima.co.jp/robots.txt（404）→ ALLOW（robots.txt 404 → 制限なし）
- 規約：— → 未確認。トップがボット判定チャレンジでリンクが取れず、未取得
- JSなしのリンク：不可（0件、見方：`None`）
- ログイン：不要　アクセス数：2
- メモ：https://online.nojima.co.jp/ はステータス200だが、本文は1,147バイトの「sec-if-cpt-container」（Akamai の behavioral challenge、「Powered and protected by Akamai」）とスクリプトだけで、実際のページは出ない。指示どおり別のUA・別のホストでは試していない。www.nojima.co.jp/nojiswitch02/（会社サイトのSwitch抽選ページ、検索で見つけたもの）は別ホストのため未取得・未確認。第三者記事によると、Switch 2 は招待販売とX告知のシークレット販売が中心

#### ゲオオンライン お知らせ（抽選販売受付のお知らせ）（`geo_news_lottery`）— 採用

- 理由：お知らせ一覧に抽選販売の告知が素のHTMLで載り、robots許可・規約に機械取得の禁止なし
- スコープ・ジャンル：A / console, tcg
- 一覧ページ：https://geo-online.co.jp/news/（200）
- 取得URL（html_diff）：https://geo-online.co.jp/news/
- RSS/Atom：なし（<link rel=alternate>なし、ページ内リンクなし）
- 公開JSON：なし
- sitemap：robots.txtに記載なし
- robots.txt：https://geo-online.co.jp/robots.txt（200）→ ALLOW（(no matching rule)（Disallow は /store/detail/ /signage/ /m/ /coupon/ /account/ のみ））
- 規約：https://geo-online.co.jp/information/online_guideline.html → 禁止なし。第12条 禁止事項「当社のサーバーまたはネットワーク機能に無権限でアクセスし、または過度な負担を与える行為」「営利を目的とした当サービスの利用」、第15条「著作権法で定める個人の私的使用の範囲外の目的でご使用する事はできない」。スクレイピング・クローラーの禁止なし（GEO会員規約 /information/rule.html にも該当なし）
- JSなしのリンク：可（7件、見方：`^https://geo-online\.co\.jp/news/[0-9]+$`） 例：https://geo-online.co.jp/news/783、https://geo-online.co.jp/news/784、https://geo-online.co.jp/news/785
- ログイン：不要　アクセス数：5
- メモ：一覧（ul#newsList）は7件で、うち4件が抽選関係：2026/09/18「ポケモンカードゲーム MEGA『30th CELEBRATION カードセット』抽選販売受付のお知らせ」(/news/783)、「ONE PIECEカードゲーム エクストラブースター…抽選販売受付のお知らせ」(/news/784)、「ポケモンカードゲーム・ONE PIECEカードゲーム再販商品 抽選販売受付のお知らせ」(/news/785)、2025/06/16「『抽選販売』よくあるお問い合わせについて」(/news/732)。個別記事のURLは https://geo-online.co.jp/news/<連番>。各 li に span.date（YYYY/MM/DD）と span.infoTitle があり、左メニューにも同じリンクが rel="YYYYMMDD-<id>" つきで重複して出る。html_diff は ul#newsList の a[href^=/news/] を見て、タイトルに「抽選」を含む新しいIDを拾う。更新は少なく（月に数件）、重要なお知らせだけを固定で載せる形式（日付順でない並びもある）。ETag/Last-Modified はなく、Cache-Control: no-store なので条件付きGETは使えない（6時間間隔で全文取得）。Akamai Bot Manager の Cookie（_abck・bm_sz）が付くが、今回のUAでは200で返った。現時点の掲載はトレカだけ。ゲーム機（Switch 2 など）の抽選がこの一覧に載るかは未確認で、2025年のSwitch 2抽選はゲオアプリと専用Webページで告知された（第三者記事、URL未確認）。トップ（https://geo-online.co.jp/）にも同じお知らせ5件が出る

### A ウイスキー（メーカー・百貨店・量販店・酒販チェーン）

#### サントリー 公式の抽選販売（山崎・白州・響などの抽選販売の告知）（`suntory_whisky_lottery`）— 未確認

- 理由：抽選の告知はブランドごとのページに分かれ、確認した白州の一覧はJSで描画される。JSONなどのデータ源と、山崎・響の一覧は上限に達して未確認
- スコープ・ジャンル：A / whisky
- 一覧ページ：https://www.suntory.co.jp/whisky/hakushu/kurashi/（200）
- RSS/Atom：なし（/whisky/ と /whisky/hakushu/kurashi/ のどちらにも <link rel=alternate> なし）
- 公開JSON：未確認（白州の一覧は /whisky/hakushu/js/kurashi/news.js が描画。データの取得先は未取得）
- sitemap：robots.txtに記載なし
- robots.txt：https://www.suntory.co.jp/robots.txt（200）→ ALLOW（(no matching rule)（/whisky/、/whisky/hakushu/kurashi/、/news/ とも ALLOW））
- 規約：https://www.suntory.co.jp/guide/ → 禁止なし。個人利用目的のダウンロード・保存は可、他サイト・印刷媒体への転載は不可。自動取得を禁じる条文なし（#1と同じページ）
- JSなしのリンク：不可（0件、見方：`kurashi/20|抽選`）
- ログイン：不要　アクセス数：2
- メモ：ウイスキートップ /whisky/ には抽選販売の告知もお知らせ一覧もない（リンク188本の中に抽選・kurashi なし）。抽選の告知はブランド別に出ている。検索結果で見えたURL（いずれも未取得・未確認）：白州は /whisky/hakushu/kurashi/YYYYMMDD/（例: 20250731=「白州 Story of the Distillery 2025 EDITION」抽選販売のご案内、20260310=受付終了）、山崎は /whisky/yamazaki/yamazaki_club/NNN/（例: 035・036=山崎 Story of the Distillery 2026 EDITION）、響は /whisky/hibiki/member/<数字>/ のページが検索で見えた（抽選の告知かどうかは未確認）。響40年・山崎55年のような大型の抽選は、ニュースリリース /news/article/NNNNN.html（14692・13651）でも告知されている。白州の一覧 /whisky/hakushu/kurashi/ は200を返したが、本文はフィルタボタンだけで記事リンクは0件（isotope と news.js による描画）。次回の確認手順は (1) /whisky/hakushu/js/kurashi/news.js から JSON・XML の取得先を探して取得、(2) /whisky/yamazaki/yamazaki_club/ と /whisky/hibiki/ の一覧が生HTMLかを確認、(3) ニュースリリース /news/ に RSS があるか確認。www.suntory.co.jp は本日5回の上限を使い切った（#1と共用）。検索結果（Gourmet Watch の記事）では、山崎・白州の抽選は3月ごろと7〜9月ごろに、それぞれ2回に分けて応募を受け付けていた

#### 高島屋 ウイスキー・酒類の抽選販売（タカシマヤアプリ抽選／オンラインストア）（`takashimaya_lottery`）— 未確認

- 理由：抽選は単発の特設ページ（/store/special/<slug>/）とアプリ内告知で、それらが並ぶ一覧ページを予算内で見つけられなかった
- スコープ・ジャンル：A / whisky
- 一覧ページ：未確認（一覧ページ未特定（個別の特設ページ https://www.takashimaya.co.jp/store/special/ichirosmalt/ は200））
- RSS/Atom：なし（確認した3ページとも<link rel=alternate>なし、ページ内リンクなし）
- 公開JSON：なし
- sitemap：robots.txtなし（404）。フッターにHTMLのサイトマップ https://www.takashimaya.co.jp/sitemap.html のリンクあり（未取得）
- robots.txt：https://www.takashimaya.co.jp/robots.txt（404）→ ALLOW（robots.txt 404 = 制限なし（RFC 9309））
- 規約：https://www.takashimaya.co.jp/aboutinfo/ → 禁止なし。「コンテンツのご利用は著作権法に定める個人の私的使用のみに限ります…転載、使用、複製、配布…を行うことはできません」。機械的取得・クローラーを禁じる条文はなし（/aboutinfo/index.html は /aboutinfo/ へ301）
- JSなしのリンク：不可（0件、見方：`^https://www\.takashimaya\.co\.jp/store/special/[a-z0-9_]+/$（抽選特設ページ）`）
- ログイン：不要　アクセス数：5
- メモ：確認できたこと：個別ページ /store/special/ichirosmalt/（イチローズモルト ショーウインドーラベル、タカシマヤアプリ抽選、応募はアプリ「クーポン・特典」から、13店舗受取）は生HTMLで読める。/store/special/taketsuru/（竹鶴2026のアプリ抽選）も検索結果に出たが未取得。どこから一覧されるかは不明：/store/special/takaapp/ の「キャンペーン」枠はプレゼント企画2件（/store/special/takaapp/campaign/、card_monthly.html）のみで抽選ページへのリンクなし。トップ https://www.takashimaya.co.jp/ は企業ポータルで、ニュースリリースPDF（/base/corp/topics/YYMMDDa.pdf）とオンラインストア /shopping/ へのリンクのみ。足りないもの：オンラインストア https://www.takashimaya.co.jp/shopping/ 内の抽選一覧の有無と、各店の /<店舗>/topics/food.html などの店舗トピックス（検索で /osaka/topics/fashion.html?page=9 の形を確認）に抽選特設ページが並ぶかどうか。このホストは5回を使い切った。html_diffで監視するなら個別ページのURL形は ^https://www.takashimaya.co.jp/store/special/[a-z0-9_]+/$

#### 三越伊勢丹オンラインストア 三越伊勢丹ウイスキーコレクション（毎月20日の抽選販売）（`mistore_whisky_collection`）— 採用

- 理由：毎月20日に中身が入れ替わる特集ページ。生HTMLに商品リンクと申込期間があり、robotsは許可、規約に禁止なし
- スコープ・ジャンル：A / whisky
- 一覧ページ：https://www.mistore.jp/shopping/feature/foods_f3/whisky_festival_f（200）
- 取得URL（html_diff）：https://www.mistore.jp/shopping/feature/foods_f3/whisky_festival_f
- RSS/Atom：なし（<link rel=alternate>なし、ページ内リンクなし）
- 公開JSON：https://www.mistore.jp/store/shinjuku/rss/whisky.json（200・application/json。ページ内「店頭イベント・抽選情報」枠のデータ元。現在は空配列 [] のため項目の構造は未確認）
- sitemap：robots.txtに記載：https://www.mistore.jp/sitemap_shinjuku_pickup.xml, https://www.mistore.jp/moodmark/sitemap_index.xml（未取得。本件とは無関係とみられる）
- robots.txt：https://www.mistore.jp/robots.txt（200）→ ALLOW（(no matching rule)）
- 規約：https://www.mistore.jp/shopping/help/guide/terms_h.html → 禁止なし。利用規約（会員規約が中心）に、スクレイピング・クローラー・機械的取得を禁じる条文はない。転載・複製の禁止はコミュニティ投稿とアプリについての条項のみ
- JSなしのリンク：可（4件、見方：`^https://www\.mistore\.jp/shopping/product/\d+\.html$`） 例：https://www.mistore.jp/shopping/product/900000000000000003679515.html、https://www.mistore.jp/shopping/product/900000000000000003679513.html、https://www.mistore.jp/shopping/product/900000000000000003447483.html
- ログイン：不要　アクセス数：4
- メモ：一覧ではなく1枚の特集ページで、毎月20日に入れ替わる。meta descriptionは「毎月貴重なウイスキーの抽選販売も実施」、メイン画像のaltは「毎月20日に抽選お申し込み開始！」。ただし今回の回（2026/9/20〜9/30）の見出しは「～毎月20日から先着販売～」で、目玉の4本セット（山崎・白州・碧・岩垂原メルロ、36,300円）も先着の扱い。月によって抽選と先着が変わるので、本文に「抽選」があるかで絞ること。監視対象は /shopping/product/<24桁>.html のリンク集合と「お申し込み期間：」の文字列。応募はエムアイカード＋三越伊勢丹WEB会員が必要（閲覧にログインは不要）。Cloudflareのほか、Akamai Bot Manager系のcookie（_abck, bm_sz）が付く。今回は200で通ったが、将来ブロックされるおそれあり。Cache-Control: no-store で ETag/Last-Modified もないため条件付きGETは使えず、6時間間隔で全文を取ることになる。店舗ごとの抽選告知は https://www.mistore.jp/store/<店舗>/shops/foods/.../shopnews_list/shopnewsNNNN.html の形（検索結果で確認、未取得）。上の whisky.json は新宿店の店頭抽選情報らしく、中身が入れば json_api 候補になる

#### 大丸松坂屋 抽選販売（オンラインストアに一覧なし → 松坂屋上野店トピックスJSON）（`matsuzakaya_ueno_topics`）— 採用

- 理由：上野店トップのトピックス枠の元データJSONが公開GETで取れる。店舗のウイスキー抽選告知はここに載る（2026年6〜7月に竹鶴の抽選告知。いまは該当なし）
- スコープ・ジャンル：A / whisky
- 一覧ページ：https://www.matsuzakaya.co.jp/ueno/（200）
- 取得URL（json_api）：https://www.matsuzakaya.co.jp/ueno/topics/topics.json
- RSS/Atom：なし（<link rel=alternate>なし、ページ内リンクなし）
- 公開JSON：https://www.matsuzakaya.co.jp/ueno/topics/topics.json（200・application/json、10カテゴリ・のべ146件。各項目のキーは title/url/date/period/annotation/image/blank）
- sitemap：robots.txtに記載：http://www.matsuzakaya.co.jp/sitemap.xml（未取得）
- robots.txt：https://www.matsuzakaya.co.jp/robots.txt（200）→ ALLOW（(no matching rule)（Disallowは /press-news のみ））
- 規約：https://dmdepart.jp/siteinfo/ → 禁止なし。「『私的使用』または『引用』など著作権法上認められた場合を除き、当社に無断で、転載、複製、改変…などの利用をすることを禁止します」。機械的取得・クローラーを禁じる条文はなし
- JSなしのリンク：可（146件、見方：`JSON: [ {カテゴリ名: [ {title, url, date, period, ...} ] } ]（url は相対・絶対が混在、同じ記事が複数カテゴリに重複）`） 例：https://www.matsuzakaya.co.jp/ueno/topics/2610hpd_panda_banner.html、https://www.matsuzakaya.co.jp/ueno/topics/261007_mottainaisale.html、https://www.matsuzakaya.co.jp/ueno/topics/2026_ueno_noren_renewal.html
- ログイン：不要　アクセス数：8
- メモ：オンラインストア https://www.daimaru-matsuzakaya.jp/（robots ALLOW）のトップには、抽選のリンクも一覧もない（特集一覧 /dm/Cate.html?cate=dm と規約 /guest_rules/ は未取得）。大丸・松坂屋の抽選は、店舗トピックスで告知して大丸・松坂屋アプリで応募する形。上野店トップのHTMLではトピックスがJSで描画され（/ueno/js_new/top_topicsInfo.js が /ueno/topics/topics.json をGET）、このJSONは生のGETで取れる。過去の抽選告知 /ueno/topics/2606_taketsuru_whiskyapp.html（検索タイトル「竹鶴ピュアモルトエッセンシャルズ 2026 700ml 大丸・松坂屋アプリ会員様限定抽選販売のご案内【松坂屋上野店】」）は、今取ると403（S3が削除済みとして返す404ページ）で、終わった告知は消える。いま「抽選」を含む2件は「店内バナー抽選プレゼント」（景品）で対象外。収集方法：title に「抽選販売」「ウイスキー」などを含む項目を抜き出し、url の重複を除く。ETag/Last-Modified ありなので条件付きGETが使える。名古屋店（検索で /nagoya/topics/... を確認）など他店も /<店舗>/topics/topics.json の同じ形と推測するが未確認。大丸各店（www.daimaru.co.jp）は未アクセス。アクセス内訳：matsuzakaya.co.jp 5、dmdepart.jp 1、daimaru-matsuzakaya.jp 2

#### 阪急百貨店 公式通販（HANKYU FOOD／HANKYU HANSHIN E-STORES）の抽選販売（`hankyu_food_lottery`）— 不採用

- 理由：公式通販のトップに抽選の一覧もリンクもない。阪急の抽選は店舗・アプリ・LINEで告知されており、公開の一覧ページは見つからなかった
- スコープ・ジャンル：A / whisky
- 一覧ページ：https://web.hh-online.jp/hankyu-food/（200）
- RSS/Atom：なし（<link rel=alternate>なし、ページ内リンクなし）
- 公開JSON：なし（抽選用のJSONは見当たらず）
- sitemap：robots.txtに記載：https://web.hh-online.jp/ec/shop/sttc/sitemap/sitemap_index.xml（未取得）
- robots.txt：https://web.hh-online.jp/robots.txt（200）→ ALLOW（(no matching rule)（*/hankyu-food/search/* などはDisallow。ClaudeBot向けに Crawl-delay: 10 があるが当方のUAには適用されない））
- 規約：https://web.hh-online.jp/estores/guide/agreement.html → 禁止なし。利用規約に機械的取得・クローラーを禁じる条文はなし（会員登録は別の『H2O ID会員利用規約』に従う。こちらは未確認）
- JSなしのリンク：不可（0件、見方：`抽選|lottery`）
- ログイン：不要　アクセス数：3
- メモ：HANKYU FOOD のトップは、ニュース（news.html?nseq=…、システム告知だけ）と特集（special.html?fkey=…）のリンクが生HTMLにある。noscriptでJS有効化の警告が出る。「抽選」に当たるリンクは0件。検索では、阪急のウイスキー抽選は大井食品館のLINE（リカー倶楽部会員向け）や阪急阪神百貨店アプリ会員向けの抽選会として出てくるだけで、通販サイトに一覧はない。www.hankyu-dept.co.jp（店舗サイト）は未アクセス。WebSearchの予算が尽きたため、店舗側の一覧は探せていない

#### イオン ウイスキー抽選販売の告知（イオンリテール／イオンリカー／AEON de WINE）（`aeon_whisky_lottery`）— 未確認

- 理由：ウイスキー抽選（南関東のイオン・イオンスタイル、イオンお買物アプリ会員向け）の公式告知ページを特定できなかった（検索予算切れ）。確認した一覧3か所にはウイスキー抽選がない
- スコープ・ジャンル：A / whisky
- 一覧ページ：https://www.aeonretail.jp/information/（200）
- RSS/Atom：なし（<link rel=alternate>なし、ページ内リンクなし）
- 公開JSON：なし（イオンリカー https://www.aeonliquor.jp/ のお知らせは /api/fetchNews.php へのPOSTで描画される。公開のGET JSONではない）
- sitemap：aeonretail.jp：robots.txtなし（404）。aeondewine.com：robots.txtに https://www.aeondewine.com/Sitemap_A106_index.xml（未取得）
- robots.txt：https://www.aeonretail.jp/robots.txt（404）→ ALLOW（robots.txt 404 = 制限なし（RFC 9309））
- 規約：https://www.aeonretail.jp/terms/ → 禁止なし。「著作権法で定める利用者個人の私的使用の範囲を超える複製…はできない」「(7) 当サイトを利用した営業活動もしくは営利を目的とする行為」が禁止。機械的取得の禁止はなし
- JSなしのリンク：可（0件、見方：`ウイスキー|抽選販売`）
- ログイン：不要　アクセス数：10
- メモ：確認した3か所：(1) https://www.aeonretail.jp/information/：生HTMLに日付つきの一覧がある。リンク先は iicoto.info や www.aeon.com/aeonapp/campaign/... などの外部。いまは「抽選で賞品が当たる」型や「もれなく30WAON POINT」など（スコープB向けの候補になりうる）で、ウイスキーの言及は0件。(2) https://www.aeonretail.jp/campaign/：商品・サービスの紹介で、ウイスキーは0件。(3) https://www.aeondewine.com/（/shop/c/ca106 へ301、robots ALLOW）：トップに抽選リンクなし。規約 /shop/contents2/A106/terms.aspx は未取得。https://www.aeonliquor.jp/（robots 404）はワイン専門店で、お知らせはJS（POST）で描画されるため不可。足りないもの：南関東のウイスキー抽選の応募ページと告知の場所（グルメWatchの記事 2082602・2138482 などに公式リンクがあるはず。他グループと予算を共有するニュースサイトのため今回はアクセスを控えた）。iAEON（www.aeon.com/aeonapp/campaign/）経由の可能性あり。アクセス内訳：aeonretail.jp 5、aeondewine.com 2、aeonliquor.jp 3

#### ビックカメラ（ビック酒販）ウイスキー・お酒の抽選販売（`biccamera_liquor_lottery`）— 不採用

- 理由：酒類の抽選は店頭受付で、告知は公式X（@bic_shuhan）と店頭だけ。巡回できるWebページがなく、ホストも403
- スコープ・ジャンル：A / whisky
- 一覧ページ：未確認（未取得（告知Webページが見つからない。同じホストのトップは403））
- RSS/Atom：なし（Web上の告知ページ自体が見つからない）
- 公開JSON：なし
- sitemap：robots.txtに記載なし
- robots.txt：https://www.biccamera.com/robots.txt（200）→ ALLOW（(no matching rule)）
- 規約：— → 未確認。トップが403のため未取得
- JSなしのリンク：不可（0件、見方：`None`）
- ログイン：不要　アクセス数：0
- メモ：第三者記事（gourmet.watch.impress.co.jp/docs/news/2131763.html、2026-08-08）によると、ビック酒販の山崎18年・響21年などの抽選は「店舗のお酒コーナーレジ」で受け付け、告知と当選発表は店頭とビック酒販の公式X（https://x.com/bic_shuhan）。biccamera.com には酒類抽選の一覧ページが見つからない。新春福箱（ウイスキー福箱を含む）はビックカメラ.com の抽選だが、上のトレカ・ゲーム機の候補と同じく403。X の取得はこのグループの担当外

#### カクヤス 特集一覧（希少ウイスキー販売会・抽選）（`kakuyasu_featured`）— 採用

- 理由：特集一覧が生HTMLで日付つき。希少ウイスキーの販売会（抽選）がここに載る。robotsは許可、規約に禁止なし
- スコープ・ジャンル：A / whisky
- 一覧ページ：https://www.kakuyasu.co.jp/featured_products（200）
- 取得URL（html_diff）：https://www.kakuyasu.co.jp/featured_products
- RSS/Atom：なし（<link rel=alternate>なし、ページ内リンクなし）
- 公開JSON：なし
- sitemap：robots.txtに記載：https://www.kakuyasu.co.jp/sitemap.xml（未取得）
- robots.txt：https://www.kakuyasu.co.jp/robots.txt（200）→ ALLOW（(no matching rule)（Disallowは /cart と /user のみ））
- 規約：https://www.kakuyasu.co.jp/guide/guide_membership/ → 禁止なし。第5条 禁止行為：本アプリ等の複製・改変、リバースエンジニアリング、「本サービス利用以外の目的（ビジネス利用、転売目的を含む）に使用する行為」、「サービスの運営を妨げる行為」など。機械的取得の明示的な禁止はなし
- JSなしのリンク：可（51件、見方：`^https://www\.kakuyasu\.co\.jp/featured_products/[^/?#]+/?$`） 例：https://www.kakuyasu.co.jp/featured_products/premiumwhiskey、https://www.kakuyasu.co.jp/featured_products/newhop、https://www.kakuyasu.co.jp/featured_products/beer_pricedown
- ログイン：不要　アクセス数：5
- メモ：サイトリニューアル後の構成。2026/08/20掲載の「希少ウイスキー・プレミアムビールセット販売会」が /featured_products/premiumwhiskey にある。本文は未取得（予算切れ）だが、前年の同名企画はメルマガ会員のエントリー制抽選（グルメWatch記事タイトル「カクヤス、ウイスキー『山崎18年/2025』『白州12年/2025』など抽選販売」）。一覧の大半はウイスキー以外の特集なので、アンカー文字列を「ウイスキー|抽選|販売会」で絞る。一覧の日付は更新日らしい（古い特集が 2026/03/10 にまとまって並ぶ）ため、日付ではなく新しいhrefで検知する。キャンペーン一覧 https://www.kakuyasu.co.jp/campaigns（200、生HTMLで5件、/campaigns/<slug>）はプレゼント懸賞が中心。過去（旧URL /store/app/news_campaign/<YYYYMM>_whisky/、2020〜2025年。検索で確認、未取得）にはウイスキーの抽選・プレゼントもあったので、併せて監視する候補。ETag/Last-Modified なし

#### やまや 特集・キャンペーン（やまやカード会員限定 ウイスキーWEB抽選）（`yamaya_campaign`）— 不採用

- 理由：取得・robots.txt・規約は問題ないが、抽選バナーのリンク先が毎回同じ https://rfl.yamaya.jp/ で、商品名と期間は画像の中にしかなく、仕様の html_diff（増えたURL）では検出できない。ユーザー判断で不採用（2026-10-09）
- スコープ・ジャンル：A / whisky
- 一覧ページ：https://www.yamaya.jp/ynhp/contents/campaign/index.php（200）
- 取得URL（html_diff）：https://www.yamaya.jp/ynhp/contents/campaign/index.php
- RSS/Atom：なし（<link rel=alternate>なし、ページ内リンクなし）
- 公開JSON：なし
- sitemap：robots.txtに記載なし
- robots.txt：https://www.yamaya.jp/robots.txt（200）→ ALLOW（Allow: /）
- 規約：https://www.yamaya.jp/ynhp/contents/company/disclaimer.php → 禁止なし。フッターに利用規約はなく、サイトの方針として読めるのは「免責事項」だけ（掲載情報と運用についての免責）。機械的取得を禁じる記載なし
- JSなしのリンク：可（4件、見方：`div.product-item > a[href][title]（バナー）`） 例：https://rfl.yamaya.jp/、https://dpoint.docomo.ne.jp/branch/hkd/yamaya_261005_7830/index.html、https://www.aeon.co.jp/campaign/member/202610-23/
- ログイン：不要　アクセス数：7
- メモ：現在も抽選バナーが掲出中（title「【やまやカード会員様限定企画】ウイスキーWEB抽選」、img /ynhp/data/top/campaign/01_20261006102725.jpg）。リンク先はいつも https://rfl.yamaya.jp/ の固定URLなので、新しいURLでは検知できない。a@title と img@src（ファイル名 01_YYYYMMDDhhmmss のタイムスタンプ）の変化で検知する必要がある。抽選サイト rfl.yamaya.jp（robots は Allow: /）は同意画面だけで、/c/top.php も同じ内容（「同意する」の先はフォーム）。商品名・期間は生HTMLになく、バナー画像の中だけ。同じバナーはトップ https://www.yamaya.jp/index.html（/ からは302）の section-campaign にもある。抽選結果は「やまや公式ホームページからも確認できる」とある。開催はおおむね月1回前後（検索では2026年5月、9/28〜10/5など）。条件付きGET用のヘッダはなし。アクセス内訳：yamaya.jp 4、rfl.yamaya.jp 3

### A ウイスキー（国内蒸溜所）

#### ニッカウヰスキー公式 お知らせ（nikka.com・公式オンラインストア）（`nikka_news`）— 不採用

- 理由：自社のお知らせ一覧がない。トップの NEWS 欄（約1年半で8件）は大半が asahibeer.co.jp へのリンクで、抽選の告知はない。公式ストアのお知らせ（5件）もコーヒー商品の先着販売だけ
- スコープ・ジャンル：A / whisky
- 一覧ページ：https://www.nikka.com/（200）
- RSS/Atom：なし（<link rel=alternate> は hreflang の ja/en のみ、ページ内にフィードへのリンクなし）
- 公開JSON：なし
- sitemap：www.nikka.com は robots.txt なし（404）。shop.nikka.com の robots.txt に https://shop.nikka.com/sitemap_index.xml（未取得）
- robots.txt：https://www.nikka.com/robots.txt（404）→ ALLOW（robots.txtなし（404）＝制限なし。shop.nikka.com/robots.txt は200で User-Agent: * にルールなし（全許可））
- 規約：https://www.asahigroup-holdings.com/privacy_policy/05/ → 未確認。フッターの「ご利用規約」はアサヒグループのページ。収集対象にならないと決まったため取得していない
- JSなしのリンク：可（8件、見方：`トップの NEWS 欄（日付付きリンク）`） 例：https://www.asahibeer.co.jp/news/2026/0701_1.html、https://www.nikka.com/story/awards/wwa/2026/、https://shop.nikka.com/shop/t/t1002/
- ログイン：不要　アクセス数：4
- メモ：nikka.com にお知らせの一覧ページはなく、トップに NEWS 欄（2025-02〜2026-07 の8件）があるだけ。リンク先の半分は asahibeer.co.jp のニュース（別エージェントの担当）。公式オンラインストア https://shop.nikka.com/shop/default.aspx（2026-07-01 開店）のお知らせは5件で、題名は「NIKKA BARREL AGED COFFEE」の販売開始・販売予定数量到達・休業案内。ウイスキーの販売も抽選もない。ストアのお知らせ記事のURL形式は https://shop.nikka.com/shop/t/t<番号>/、一覧は https://shop.nikka.com/shop/topic/topicdetaillist.aspx?category=0（未取得）。ストアで将来ウイスキーの抽選が始まれば再検討の余地あり。ニッカ限定品の抽選（例：ザ・ニッカ ナインディケイズ）はローソン・オーケー等の小売側で行われる（検索結果）

#### 秩父蒸溜所（ベンチャーウイスキー）公式お知らせ（`chichibu_news`）— 未確認

- 理由：お知らせ一覧のある公式サイトを特定できなかった。根拠は検索結果の要約だけで、サイトにはアクセスしていない
- スコープ・ジャンル：A / whisky
- 一覧ページ：未確認（None）
- RSS/Atom：なし（公式サイトが見つからない）
- 公開JSON：なし（公式サイトが見つからない）
- sitemap：なし（公式サイトが見つからない）
- robots.txt：—（None）→ 未確認（—）
- 規約：— → 未確認。公式サイトが見つからないため確認していない
- JSなしのリンク：不可（0件、見方：`None`）
- ログイン：不要　アクセス数：0
- メモ：WebSearch を7回ほど行ったが公式ドメインは見つからなかった。検索結果の要約に「公式サイトはない」とする記述があった（出典は取得していない）。ドメインを推測してアクセスすることはしていない（アクセス0回）。検索の上限（全エージェント共通）に達したため、それ以上は調べていない。イチローズモルトの抽選は百貨店・酒販店側（高島屋など）で行われる。公式サイトの存在を確認したい場合は、上限が戻ってから追加で調べる必要がある

#### 厚岸蒸溜所 新着情報（`akkeshi_news`）— 不採用

- 理由：お知らせは新商品・受賞・イベントで、抽選販売の告知がない。REST API で全記事を「抽選」で検索しても1件（ファン向けイベントの告知）だけ
- スコープ・ジャンル：A / whisky
- 一覧ページ：https://akkeshi-distillery.com/company/news/（200）
- RSS/Atom：なし（<link rel=alternate> は wp-json の JSON と oEmbed のみ。RSS の告知がなく、/company/feed/ は取得していない）
- 公開JSON：https://akkeshi-distillery.com/company/wp-json/wp/v2/posts（WordPress REST API、認証不要、200を確認。<link rel="https://api.w.org/"> で告知されている）
- sitemap：robots.txt なし（404）のため Sitemap 行なし
- robots.txt：https://akkeshi-distillery.com/robots.txt（404）→ ALLOW（robots.txtなし（404）＝制限なし）
- 規約：— → 規約ページなし。フッターはプライバシーポリシー（/company/privacy）と SNS運用ポリシー（/company/sns）だけで、利用規約へのリンクはない（どちらも取得していない）
- JSなしのリンク：可（10件、見方：`akkeshi-distillery\.com/company/news/\d{8}/\d+/`） 例：https://akkeshi-distillery.com/company/news/20260807/527/、https://akkeshi-distillery.com/company/news/20260728/520/、https://akkeshi-distillery.com/company/news/20260529/497/
- ログイン：不要　アクセス数：3
- メモ：一覧1ページに10件（2026-03-25〜08-07）、全7ページ。記事URLの形は https://akkeshi-distillery.com/company/news/YYYYMMDD/<id>/。新商品は「商品情報を更新しました。」という題で出るので、題名からは商品名が分からない。厚岸の限定品（二十四節気シリーズなど）の抽選は三越伊勢丹・大丸札幌など小売側で行われる（検索結果）。REST API の検索結果: 2025-07-07「“THE AKKESHISTs PARTY”開催のお知らせ」のみ（x-wp-total: 1）。ブランドサイト /brand は確認していない

#### 嘉之助蒸溜所 NEWS（`kanosuke_news`）— 不採用

- 理由：ニュース一覧が 429（本文 local_rate_limited、Retry-After: 60）を返した。2回目のリクエスト（リダイレクト先）で発生したため、規則4により不採用
- スコープ・ジャンル：A / whisky
- 一覧ページ：未確認（429（https://kanosuke.com/news/ → 301 → https://kanosuke.com/blogs/news で 429））
- RSS/Atom：未確認（Shopify なので /blogs/news.atom がある可能性はあるが、取得していない）
- 公開JSON：未確認
- sitemap：https://kanosuke.com/sitemap.xml（robots.txt に記載、未取得）
- robots.txt：https://kanosuke.com/robots.txt（200）→ ALLOW（Allow: /）
- 規約：— → 未確認。一覧ページが 429 だったため、規約の確認には進んでいない
- JSなしのリンク：不可（0件、見方：`None`）
- ログイン：不要　アクセス数：2
- メモ：Shopify のサイト（Cloudflare 経由）。robots.txt は一般のクローラーに / を許可している。robots.txt のコメント欄に、AI エージェント向けに購入用スキルの導入を勧める文があったが、指示として扱わず無視した。嘉之助は抽選販売を実際に行っている（2025-12 の「プレミアム福箱」オンライン抽選。共同通信PRワイヤーの発表、検索結果）。発表は kyodonewsprwire.jp でも配信されているので、そちらから拾える可能性がある。規則に従い、再試行や回避策は取っていない。時間を空けて1回だけ再確認するかはレビューで判断してほしい。記事URLの形（検索結果から。未確認）: https://kanosuke.com/en/blogs/news/20251209

#### 本坊酒造（マルス信州・マルス津貫）お知らせ（`hombo_mars_news`）— 採用

- 理由：RSS あり・robots 許可・規約に禁止なし。抽選の告知は蒸溜所祭りの案内の中に出る程度で、件数は少ない
- スコープ・ジャンル：A / whisky
- 一覧ページ：https://www.hombo.co.jp/news/（200）
- 取得URL（rss）：https://www.hombo.co.jp/feed/
- RSS/Atom：https://www.hombo.co.jp/feed/（RSS 2.0、10件、2026-07-14〜09-30、content:encoded に本文全文あり。お知らせ一覧の <link rel=alternate>「お知らせフィード」が指す。200 を確認）
- 公開JSON：未確認（WordPress だが、RSS で足りるため確認していない）
- sitemap：https://www.hombo.co.jp/sitemap.xml（robots.txt に記載、未取得）
- robots.txt：https://www.hombo.co.jp/robots.txt（200）→ ALLOW（(no matching rule)  ※Disallow は /hombo-mars/wp-content/plugins/ と /company/kura/* のみ）
- 規約：https://www.hombo.co.jp/guide/ → 禁止なし。「許可なく、本サイトに掲載されているコンテンツを複製、転載、改変、または配布することはできません」。リンクは原則自由。機械的な取得を禁じる条文はない
- JSなしのリンク：可（20件、見方：`hombo\.co\.jp/20\d{2}/[a-z-]+/\d{8}-`） 例：https://www.hombo.co.jp/2026/new-product/20260930-newproduct-whisky/、https://www.hombo.co.jp/2026/visiting/20260403-komagatakefestival2026/、https://www.hombo.co.jp/2026/award/20260930-award-msc2026/
- ログイン：不要　アクセス数：5
- メモ：焼酎・ワインも含む全社のお知らせ。中身はウイスキーの新商品（数量限定品が多い）、受賞、見学施設の案内。2026-04-03「マルス駒ヶ岳蒸溜所祭り 2026」開催案内の本文に「祭り記念ボトルの抽選販売受付を行います」とあるのを確認した（会場で受け付ける抽選）。直近10件のフィード本文に「抽選」はない。抽選の告知は年に数回（駒ヶ岳・津貫の蒸溜所祭り）と見込まれるので、優先度は低め。題名には「抽選」が出ないので、本文（content:encoded）でキーワード判定が必要。記事URLの形は https://www.hombo.co.jp/YYYY/<category>/YYYYMMDD-<slug>/（category: new-product, award, visiting, topics）。ウイスキー新商品だけの一覧 /news/new-product/whisky/ もある（検索結果、未取得）。英語版は /en/news/。フィードは ETag・Last-Modified あり、X-Robots-Tag: noindex, follow。robots.txt の Crawl-delay: 600 は MJ12bot・AhrefsBot・Amazonbot だけが対象

#### ガイアフロー静岡蒸溜所 ニュース（`gaiaflow_news`）— 採用

- 理由：RSS あり・robots 許可・規約ページなし。新商品の記事本文に会員向けの抽選販売の案内が入る（直近2.5か月で2件）
- スコープ・ジャンル：A / whisky
- 一覧ページ：https://www.gaiaflow.co.jp/blog（200）
- 取得URL（rss）：https://www.gaiaflow.co.jp/feed
- RSS/Atom：https://www.gaiaflow.co.jp/feed（RSS 2.0、10件、2026-07-23〜10-07、本文全文あり。トップとニュース一覧の <link rel=alternate> が指す。200 を確認）
- 公開JSON：未確認（WordPress だが、RSS で足りるため確認していない）
- sitemap：https://www.gaiaflow.co.jp/wp-sitemap.xml（robots.txt に記載、未取得）
- robots.txt：https://www.gaiaflow.co.jp/robots.txt（200）→ ALLOW（(no matching rule)  ※Disallow は /wp-admin/ のみ）
- 規約：— → 規約ページなし。トップとニュース一覧の HTML 全体に「規約」「ポリシー」「プライバシー」「policy」を含むリンクがない
- JSなしのリンク：可（38件、見方：`gaiaflow\.co\.jp/blog/[a-z-]+/[0-9]+`） 例：https://www.gaiaflow.co.jp/blog/shizuoka-distillery/48476、https://www.gaiaflow.co.jp/blog/shizuoka-distillery/48368、https://www.gaiaflow.co.jp/blog/event/48543
- ログイン：不要　アクセス数：4
- メモ：ガイアフローは輸入代理店も兼ねているので、フィードには輸入ブランド（ブラックアダー、アムルットなど）、イベント、メディア掲載の記事も混じる。抽選は新商品記事の本文に「WHISKY PORT会員及びメールマガジン会員様向け抽選販売」として書かれ、題名には「抽選」が出ない。本文（content:encoded）でキーワード判定が必要。直近の例: 2026-09-18「ポットスティルＫ ５年 100%外国産大麦 ゴールデンプロミス2026年版」、2026-07-23「静岡 ポットスティルＷ 5年100%日本大麦 2026年版」。応募できるのは会員・メルマガ登録者だけ（登録が無料かは未確認）。過去には題名に「抽選販売決定！」とある記事もあった（検索結果）。記事URLの形は https://www.gaiaflow.co.jp/blog/<category>/<post_id>（category の例: shizuoka-distillery, event, media, praivate-cask）。静岡蒸溜所の専用サイト shizuoka-distillery.jp（別ホスト）とオンラインショップ whiskyport.jp は確認していない。フィードは ETag・Last-Modified あり。HTML に recaptchaConfig の記述があるが中身は空で、閲覧の妨げにはならない

#### 三郎丸蒸留所（若鶴酒造）NEWS（`saburomaru_news`）— 採用

- 理由：RSS あり・robots 許可・規約ページなし。2026年1〜3月にコラボウイスキーの抽選販売の告知が5件あり、題名に「抽選販売」が出る
- スコープ・ジャンル：A / whisky
- 一覧ページ：https://www.wakatsuru.co.jp/saburomaru/information/（200）
- 取得URL（rss）：https://www.wakatsuru.co.jp/saburomaru/information/feed/
- RSS/Atom：https://www.wakatsuru.co.jp/saburomaru/information/feed/（RSS 2.0、10件、2026-08-07〜10-07、本文あり。NEWS 一覧の <link rel=alternate>「三郎丸蒸留所 » NEWS フィード」が指す。200 を確認）
- 公開JSON：未確認（WordPress だが、RSS で足りるため確認していない）
- sitemap：https://www.wakatsuru.co.jp/sitemap.xml（robots.txt に記載、未取得）
- robots.txt：https://www.wakatsuru.co.jp/robots.txt（200）→ ALLOW（(no matching rule)  ※中身は User-Agent : * と Sitemap 行だけ）
- 規約：— → 規約ページなし。三郎丸サイト（NEWS 一覧）に規約・ポリシーへのリンクがない。若鶴酒造トップ（https://www.wakatsuru.co.jp/）のフッターにも「SNS運営ポリシー」（PDF、SNS アカウント運営の方針）しかない
- JSなしのリンク：可（20件、見方：`wakatsuru\.co\.jp/saburomaru/information/[^/]+/$`） 例：https://www.wakatsuru.co.jp/saburomaru/information/sangokushi8-saburomaru-cyoun-2026/、https://www.wakatsuru.co.jp/saburomaru/information/sangokushi8-saburomaru-sonsyoko-2026/、https://www.wakatsuru.co.jp/saburomaru/information/sab-ocean-blue-2nd-batch/
- ログイン：不要　アクセス数：5
- メモ：一覧2ページ目（2025-12-23〜2026-05-07）で「三國志8 REMAKE × 三郎丸蒸留所 コラボ『劉備』『関羽』『張飛』『孫尚香』『趙雲』…より抽選販売開始！」の5件を確認した。直近20件（2026-05-26〜10-07）には抽選の告知がない。営業カレンダーなどの告知も混じる。抽選の申込先は自社通販「私と、ALC.」（shop.wakatsuru.co.jp、会員制。未確認）。フィードの <link> には ?utm_source=rss&utm_medium=rss&utm_campaign=… が付くので、重複判定には guid（…/saburomaru/?post_type=information&p=<id>）か、クエリを除いた URL を使う。記事URLの形は https://www.wakatsuru.co.jp/saburomaru/information/<slug>/（slug は英字の場合と日本語の場合がある）。noscript に「JavaScriptを有効に」と出るが、記事リンクは素の HTML にある。フィードは ETag・Last-Modified あり、X-Robots-Tag: noindex, follow。更新は週1件程度（20件で約19週）

#### 長濱蒸溜所（長濱浪漫ビール）ニュース（`nagahama_news`）— 不採用

- 理由：直近のお知らせ（2026-09-02〜10-06 の10件）は数量限定の発売と見学の案内だけで、抽選販売の告知がない
- スコープ・ジャンル：A / whisky
- 一覧ページ：https://www.romanbeer.com/news/（200）
- RSS/Atom：https://www.romanbeer.com/news/feed/（RSS 2.0、10件、2026-09-02〜10-06、200 を確認）。ウイスキーだけの https://www.romanbeer.com/junle/whisky/feed/ も <link rel=alternate> で告知されている（未取得）
- 公開JSON：未確認
- sitemap：https://www.romanbeer.com/sitemap.xml, https://www.romanbeer.com/sitemap.rss（robots.txt に記載、未取得）
- robots.txt：https://www.romanbeer.com/robots.txt（200）→ ALLOW（(no matching rule)  ※Disallow は /wp/wp-admin/ のみ）
- 規約：— → 規約ページなし。ニュース一覧の HTML に規約・ポリシーへのリンクがない（フッターは会社概要・採用情報・製造所固有記号など）
- JSなしのリンク：可（10件、見方：`romanbeer\.com/news/[0-9]{8}`） 例：https://www.romanbeer.com/news/20261006_id2982/、https://www.romanbeer.com/news/20261006_id2986/、https://www.romanbeer.com/news/20260910_id2948/
- ログイン：不要　アクセス数：4
- メモ：数量限定のウイスキー発売の告知は多い（干支ボトル、コラボ、チャリティーボトルなど）が、どれも先着販売。過去には「シングルモルト長濱の抽選販売について」（2021-05）などの抽選告知もあった（検索結果、未取得）。現在の抽選は公式オンラインショップ shop.romanbeer.com の商品ページで行われているようで（「【抽選販売】シングルモルト長濱 THE FIRST BATCH」など、検索結果）、拾うならショップ側を別の候補として検証する必要がある。フィード自体は採用条件を満たしている（robots 許可・規約ページなし・ETag・Last-Modified あり）ので、ニュースに抽選の告知が戻れば採用に切り替えられる。記事URLの形は https://www.romanbeer.com/news/YYYYMMDD_id<id>/。ビールの告知も混じる。一覧は全38ページ

### A ゲーム機・限定版

#### 任天堂 トピックス（nintendo.com/jp/topics）RSS（`nintendo_jp_topics`）— 不採用

- 理由：robots.txt のコメントで、コンテンツの「web scraping, machine learning, or any form of text or data mining by any means」を書面の許可なく禁止すると宣言している（規則自体は Allow: / だが、禁止の意思表示として不採用にした）
- スコープ・ジャンル：A / console
- 一覧ページ：https://www.nintendo.com/jp/topics/（200）
- 取得URL（rss）：https://www.nintendo.com/jp/topics/c/feed/rss/
- RSS/Atom：https://www.nintendo.com/jp/topics/c/feed/rss/（RSS 2.0、10件、10/2〜10/9 の約1週間分。/jp/topics/ の <link rel=alternate> で告知されている。description は空、title・link・pubDate のみ）
- 公開JSON：なし（確認範囲で見当たらず）
- sitemap：https://www.nintendo.com/jp/topics/sitemap.xml ほか（robots.txtに記載、未取得。RSSで足りるため）
- robots.txt：https://www.nintendo.com/robots.txt（200）→ ALLOW（Allow: /）
- 規約：https://www.nintendo.com/jp/about_hp.html → 禁止なし。任天堂ウェブサイトポリシー：著作物は『法律により認められた範囲内（私的使用を目的とする場合など）』を除きコピー・配信等を禁止。リンクは原則自由。機械取得を禁じる条文はない。ただし robots.txt のコメント欄に『Any use of such content for ... AI ..., web scraping, machine learning, or any form of text or data mining by any means, is strictly prohibited, unless ... authorized in writing』という権利留保の宣言がある（下の notes 参照）
- JSなしのリンク：可（10件、見方：`RSS <item>`） 例：https://www.nintendo.com/jp/topics/article/a65622f7-c603-4685-bef7-2e98feb50bf4、https://www.nintendo.com/jp/topics/article/965576b6-1e14-409c-8da6-515804839baf
- ログイン：不要　アクセス数：6
- メモ：【要判断】www.nintendo.com/robots.txt のルール自体は User-agent: * に Allow: /（GPTBot・ClaudeBot などAI系は Disallow）。ただし末尾のコメントに、AI学習・web scraping・TDM 目的でのコンテンツ利用を禁じる権利留保がある。RSS は購読用に公開されているので、RSS をタイトルのキーワードで絞るだけなら『スクレイピング』には当たらないという見方もあるが、禁止の意思表示がある以上は不採用とした。HTMLページの差分監視（html_diff）はこの宣言に触れるおそれがあるので使わないこと。【対象の割合】RSS 10件はほぼソフト・アプリ・映像公開の話題。対象に近いのは『ゼルダの伝説40周年コンサート チケット先行申込（抽選）』の1件だけで、本体の抽選販売ではない（10件中0件）。Switch 2 の抽選販売・招待販売（2025年）もトピックスで告知されたが、本体の抽選は年に数回もない。ルールフィルタ（抽選|招待販売|数量限定|予約受付 など）が前提。【その他】(1) topics.nintendo.co.jp は www.nintendo.com/jp/topics/ へ 301 で移転済み。旧ホストの robots.txt を取りに行ったらリダイレクト先の www.nintendo.com に1回余分に届いたので、www.nintendo.com には計6回アクセスした（ログ上は5回）。(2) /jp/topics/ の生HTMLには記事リンクがない（JSで描画）ので、RSS だけが取得手段。(3) 『更新情報』/jp/news/index.html は JS 描画で中身が空。ページ内の RSS リンク https://www.nintendo.com/jp/news/rss.html は予算の都合で未取得（未確認）。(4) RSS には ETag・Last-Modified が付いていない（server: gunicorn）ので条件付きGETは効かない。30分間隔で全件を取る前提。10件で約1週間分なので取りこぼしはない。

#### マイニンテンドーストア お知らせ（`my_nintendo_store_news`）— 不採用

- 理由：トップへのアクセスが Queue-it 型の待合室（JavaScript・Cookie 必須）に飛ばされ、JSなしでは中身に届かない
- スコープ・ジャンル：A / console
- 一覧ページ：未確認（302→200（待合室ページ store-jp-wr.nintendo.com））
- RSS/Atom：未確認（トップページに到達できず）
- 公開JSON：未確認
- sitemap：https://store-jp.nintendo.com/sitemap_index.xml（robots.txtに記載、未取得）
- robots.txt：https://store-jp.nintendo.com/robots.txt（200）→ ALLOW（(no matching rule)（/order/ /payment/ /wishlist/ などのみDisallow））
- 規約：— → 未確認。待合室で止まりフッターに届かないため未取得
- JSなしのリンク：不可（0件、見方：`news|info|お知らせ`）
- ログイン：不要　アクセス数：2
- メモ：https://store-jp.nintendo.com/ は 302 で https://store-jp-wr.nintendo.com/?c=ncl&e=202601prod&...&enqueuetoken=... に飛ぶ。中身は『このサイトではJavaScriptを有効にする必要があります』と Cookie テスト用のJSだけ（x-robots-tag: noindex）。回避策（ブラウザ相当のUA、トークン再利用など）は試していない。お知らせ一覧のURLも確認できなかった。ストアの抽選・招待販売は任天堂トピックス（nintendo_jp_topics）でも告知されるので、そちらで拾う想定。

#### PlayStation.Blog 日本語版 RSS（`playstation_blog_jp`）— 採用

- 理由：公式RSSあり・robots許可（crawl-delay 5）・規約に機械取得の禁止なし。限定コントローラー・特別モデルの告知が載る
- スコープ・ジャンル：A / console
- 一覧ページ：https://blog.ja.playstation.com/（200）
- 取得URL（rss）：https://blog.ja.playstation.com/feed/
- RSS/Atom：https://blog.ja.playstation.com/feed/（WordPress RSS 2.0、10件・本文全文入り・約370KB、10/1〜10/8 の約1週間分。トップの <link rel=alternate> で告知。ETag・Last-Modified あり）
- 公開JSON：なし（未調査。RSSで足りるため）
- sitemap：https://blog.ja.playstation.com/wp-sitemap.xml（robots.txtに記載、未取得）
- robots.txt：https://blog.ja.playstation.com/robots.txt（200）→ ALLOW（(no matching rule)（/category/ /tag/ /page/ /search/ などは Disallow）、crawl-delay 5）
- 規約：https://www.playstation.com/ja-jp/legal/website-terms-of-use/ → 禁止なし。サイトポリシー（SIE）：禁止事項は財産・プライバシーの侵害、営業活動・営利目的、ウイルス等の使用など。『私的使用その他法律によって明示的に認められる範囲を超えて…使用することは…禁止』。自動取得・クローラーを禁じる条文はない。ブログフッターの規約リンク https://www.jp.playstation.com/about/terms-and-conditions/ は301でここに移る
- JSなしのリンク：可（10件、見方：`RSS <item>（トップの生HTMLにも ^https://blog\.ja\.playstation\.com/20\d\d/\d\d/\d\d/ が42件）`） 例：https://blog.ja.playstation.com/2026/10/02/20261002-dualsense-retail-sale-s/、https://blog.ja.playstation.com/2026/09/24/20260924-psxlisa-dualsense/
- ログイン：不要　アクセス数：4
- メモ：【対象の割合】トップの約20記事（9/22〜10/8）のうち、対象は『DualSense “LISA” リミテッドエディション』（9/24）の1件で約5%。RSS 10件の中では0件（コントローラーのセールのみ）。他はソフト紹介・インタビューが大半。過去には PS5 30周年アニバーサリー リミテッドエディション（予約応募・抽選）、PS App・LINE 連携の抽選プレゼントなども載った。『PS Plus フリープレイ』は加入者向けの特典で、無料配布には当たらない。【注意】robots.txt が /category/ と /tag/ を Disallow にしているので、カテゴリ別・タグ別のフィード（/tag/xxx/feed/）は使わず、全体の /feed/ だけを使う。Crawl-delay 5秒（30分間隔なら問題なし）。cache-control: max-age=300。【PS公式ストアについて】日本では PlayStation Direct は確認できなかった（検索のみ）。PS5 の抽選販売はソニーストアで行われ、告知は https://www.playstation.com/ja-jp/local/campaigns/<slug>/ の個別ページ（検索結果で見ただけ、未確認）。これらをまとめた一覧ページは見つからなかった。

#### ソニー製品情報・ソニーストア 新着情報 RSS（PS5 のソニーストア販売の代わりとして確認）（`sony_jp_news`）— 不採用

- 理由：取得はできるが、RSS 215件に抽選販売・PlayStation の告知がなく、対象外
- スコープ・ジャンル：A / console
- 一覧ページ：https://www.sony.jp/（200）
- RSS/Atom：https://www.sony.jp/xml/index.xml（RSS、215件・2018年〜。トップの <link rel=alternate> で告知。ほぼ全件が製品のプレスリリース）
- 公開JSON：なし（未調査）
- sitemap：http://www.sony.jp/contents.html（robots.txtに記載、HTMLのサイトマップ、未取得）
- robots.txt：https://www.sony.jp/robots.txt（200）→ ALLOW（(no matching rule)）
- 規約：https://www.sony.jp/CorporateCruise/terms/ → 禁止なし。ウェブサイトご利用条件（ソニーマーケティング）：『私的使用その他法律によって明示的に認められる範囲を超えて…使用…することは…禁止』、禁止行為は営利目的・ウイルス等。[P] のヒットは製品名（ロボットトイ等）で、自動取得の禁止条文はない
- JSなしのリンク：可（215件、見方：`RSS <item>`） 例：https://www.sony.jp/CorporateCruise/Press/202610/26-1009/?s_tc=jp_app_msa-_261009_1
- ログイン：不要　アクセス数：5
- メモ：依頼の『ソニー（PlayStation公式ストア）』は、日本ではソニーストアが PS5 を売っている（PS5 Pro の購入申し込み・抽選など）ため、念のため確認した。RSS 215件のうち『抽選』は0件、PlayStation への言及は2件だけ（本文中）。197件が /CorporateCruise/Press/（カメラ・テレビ・Xperia などの製品発表）。ソニーストアのお知らせ（/store/info/261005.html など）はトップの生HTMLにリンクがあるが、障害・お詫びなどが中心で、一覧ページのURLは未確認。https://www.sony.jp/store/ は JS で '/#store' に飛ばすだけの空ページ。PS5 の抽選は PS Blog（playstation_blog_jp）と家電量販店担当の情報源で拾う想定。

#### Xbox Wire Japan RSS（`xbox_wire_jp`）— 採用

- 理由：公式RSSあり・robots.txtなし（制限なし）・規約に機械取得の禁止なし。限定コントローラー・限定本体の告知が載る
- スコープ・ジャンル：A / console
- 一覧ページ：https://news.xbox.com/ja-jp/（200）
- 取得URL（rss）：https://news.xbox.com/ja-jp/feed/
- RSS/Atom：https://news.xbox.com/ja-jp/feed/（WordPress RSS 2.0、10件・本文入り・約56KB、9/17〜10/8 の約3週間分。トップの <link rel=alternate> で告知。ETag・Last-Modified あり）
- 公開JSON：WordPress REST（https://news.xbox.com/ja-jp/wp-json/wp/v2/...）が <link rel=alternate> にあるが未取得（RSSで足りるため）
- sitemap：robots.txtなし（404）のため記載なし
- robots.txt：https://news.xbox.com/robots.txt（404（302で /en-us/robots.txt に飛び、そこが404））→ ALLOW（robots.txtなし＝制限なし（RFC 9309））
- 規約：https://www.microsoft.com/ja-jp/legal/terms-of-use → 禁止なし。Microsoft 使用条件：『サーバー…に損害を与え、使用不能にし、過度な負荷を与え…るような方法…で、本サービスを使用することはできません』。[P] のヒット『キャンセルボット』はマルウェアのアップロード禁止の文脈。自動取得を禁じる条文はない。フッターの『使用条件』リンク（/ja-jp/mscorp/legal/intellectualproperty-copyright.aspx）は会社概要ページに飛ぶため、そこから go.microsoft.com/fwlink/?LinkID=206977 経由で取得した
- JSなしのリンク：可（10件、見方：`RSS <item>（トップの生HTMLにも ^https://news\.xbox\.com/ja-jp/20\d\d/\d\d/\d\d/ が32件）`） 例：https://news.xbox.com/ja-jp/2026/10/02/ikea-xbox-gaming-collection-yxstaby/、https://news.xbox.com/ja-jp/2026/10/08/xbox-game-pass-october-2026-wave-1/
- ログイン：不要　アクセス数：5
- メモ：【対象の割合】RSS 10件（約3週間）のうち対象は0件。ほとんどがゲーム紹介と Game Pass の追加情報。検索で見た限り、限定版の告知（『Forza Horizon 6』リミテッドエディション コントローラー〈2026/4〉、Xbox 25周年『XBOX Series X25 Limited Edition』とコントローラー〈11月にMicrosoft Store限定で日本発売〉など）は年に数件。抽選販売はさらに少ない。更新は週2〜3件と少ない。カテゴリ『アクセサリ』のフィード（/ja-jp/category/アクセサリ/feed/）は未確認。cache-control: max-age=600。

### A 抽選まとめサイト

#### 抽選まとめサイト: トレゲト（旧カード抽選まとめ, cardchusen.com）（`cardchusen`）— 不採用

- 理由：robots.txt で、利用規約第5条が機械的な取得・蓄積を禁じていると明記
- スコープ・ジャンル：A / tcg
- 一覧ページ：未確認（未取得（robots.txt のみ取得））
- RSS/Atom：未確認（規約で禁止のため追跡せず）
- 公開JSON：未確認
- sitemap：https://cardchusen.com/sitemap.xml（robots.txtに記載、未取得）
- robots.txt：https://cardchusen.com/robots.txt（200）→ ALLOW（Allow: /（User-agent: * のグループ。curl・Wget・python-requests・Scrapy 等の名前を指定して Disallow: /））
- 規約：https://cardchusen.com/terms（robots.txt に記載、未取得） → 禁止あり。robots.txt 冒頭のコメント「機械的手段による本サイトの取得・蓄積は利用規約第5条で禁止しています。」「Automated collection is prohibited by our Terms of Use, Article 5.」「（汎用スクレイピングツールの Disallow は）機械的収集を許諾していないことの意思表示として明示する」
- JSなしのリンク：不可（0件、見方：`None`）
- ログイン：不要　アクセス数：1
- メモ：Web検索で見つけた候補。ポケカ・ワンピ・遊戯王の BOX の抽選・予約情報を締切順に集める無料サイトで、2026-08-11 に「カード抽選まとめ」から「トレゲト」に改称（同社の PR TIMES リリースの検索結果による）。robots.txt に禁止の意思がはっきり書かれているので、トップページと規約本文は取得していない（アクセスは1回だけ）。規約第5条の本文は未取得だが、サイト自身が robots.txt で禁止と宣言しているので不採用とした。

#### 抽選まとめサイト: 攻略大百科プレミアム（premium.gamepedia.jp）ポケカ／買い物ウォッチ（`gamepedia_premium_pokeca`）— 不採用

- 理由：RSSは個人利用OKで技術的にも取れる。ただし新着として抽選の告知が流れない（ポケカのフィード10件中0件、買い物のフィードはセール記事）
- スコープ・ジャンル：A / tcg
- 一覧ページ：https://premium.gamepedia.jp/（200）
- RSS/Atom：https://premium.gamepedia.jp/pokeca/feed（RSS、200、10件）／https://premium.gamepedia.jp/shopping/feed（RSS、200、10件）／トップの <link rel=alternate> は https://premium.gamepedia.jp/feed（未取得）
- 公開JSON：未確認（wp-json は <link> にあるが取得せず）
- sitemap：https://premium.gamepedia.jp/sitemap.xml（robots.txtに記載、未取得）
- robots.txt：https://premium.gamepedia.jp/robots.txt（200）→ ALLOW（(no matching rule)（Disallow は /wp-admin/ のみ））
- 規約：https://gamepedia.jp/rule → 禁止なし。禁止事項は「サーバやネットワークへの過度の負荷をかける行為」「アクセス制御機能を解除または回避する手段を流通させる行為」など。クローラ・スクレイピングを禁じる条文はない。RSSの案内ページ https://gamepedia.jp/about_feed には「フィードリーダーやニュースアプリなどで利用されたい場合は…ご利用いただけます。ディレクトリの後ろへfeedを付けて」「法人運営サイトや、商用ツール・アプリでご利用の際は、お問い合わせ」とある
- JSなしのリンク：可（10件、見方：`RSS <item>`） 例：https://premium.gamepedia.jp/pokeca/archives/25741、https://premium.gamepedia.jp/pokeca/archives/327、https://premium.gamepedia.jp/shopping/archives/28217
- ログイン：不要　アクセス数：7
- メモ：株式会社Zender が運営する攻略大百科のサブサイト（WordPress マルチサイト: /pokeca/ /toreca/ /shopping/ /hobby/ /kindle/）。/pokeca/feed は約2か月半で10件。中身は高額カード・新弾情報・サプライ等で、タイトルに「抽選」は0件。抽選の情報は、既存の大きなまとめ記事（例 archives/327「新弾発売予定スケジュールまとめ」、本文に「抽選」33回）を更新して追記する形なので、RSS の新着としては流れてこない。/shopping/feed は1日に数件の更新で、Amazonタイムセール・新商品・サブスクの無料体験（例「Kindle Unlimited 3か月無料」）・福袋の先行エントリー。抽選の告知はなし。スコープBの「無料」系として使えるかは別途判断が必要。/toreca/feed は未確認。アクセス数について: premium.gamepedia.jp に5回（robots・トップ・トップへの誤ったHEADリクエスト1回・pokeca のフィード・shopping のフィード）、gamepedia.jp に2回（/rule・/about_feed）。誤ったHEADは手元の操作ミスで、情報としては使っていない。

### B 食品

#### 日清食品グループ キャンペーン一覧（`nissin_campaigns`）— 採用

- 理由：一覧が素のHTMLにあり（Astro SSR）、robots制限なし・規約に自動取得の禁止なし
- スコープ・ジャンル：B / food
- 一覧ページ：https://www.nissin.com/jp/product/campaigns/（200）
- 取得URL（html_diff）：https://www.nissin.com/jp/product/campaigns/
- RSS/Atom：なし（<link rel=alternate>なし、ページ内にRSSリンクなし）
- 公開JSON：なし（確認範囲で見当たらず）
- sitemap：robots.txtなし（404）のため記載なし
- robots.txt：https://www.nissin.com/robots.txt（404）→ ALLOW（robots.txt 404 → RFC9309により制限なし）
- 規約：https://www.nissin.com/jp/docs/terms/ → 禁止なし。「私的使用その他法律によって明示的に認められる範囲を超えて…使用（複製、改ざん、頒布などを含む。）することはできません」「サービス…を商業目的で利用…することを禁止」。禁止事項(1)〜(12)にクローラー・スクレイピング・自動取得の条文なし（(8)営利目的の行為、(10)ウィルス等）
- JSなしのリンク：可（3件、見方：`^https://www\.nissin\.com/jp/product/campaigns/\d+/$`） 例：https://www.nissin.com/jp/product/campaigns/372/、https://www.nissin.com/jp/product/campaigns/371/、https://www.nissin.com/jp/product/campaigns/367/
- ログイン：不要　アクセス数：5
- メモ：最初に試した /jp/campaign/ は404（1回分むだ）。正しい一覧は /jp/product/campaigns/（パンくず「商品情報 > キャンペーン」）。取得時点の掲載は3件のみ（アンパンマン つくって楽しい!食べておいしい!キャンペーン／シスコーン 今どきグッズ／ごろグラ meets DALLOYAU）。各カードは div.CardCampaign > a[href=/jp/product/campaigns/<数字>/] に title・締切・「対象: 買って応募」「方法: PC、スマホ」だけで、抽選か全員もらえるかはカードからは分からない（個別ページは未取得）。注意: 10/1開始の「ロングセラー袋麺 たまごくじキャンペーン」（ニュース https://www.nissin.com/jp/news/13931/ ）はこの一覧に載っておらず、一覧はグループの全キャンペーンを網羅していない可能性が高い。補助候補として日清食品社のニュースリリース一覧 https://www.nissin.com/jp/company/news/campaigns/nissinfoods/ （200・素のHTMLに10件、リンク形式 /jp/news/<数字>/、URLに campaigns とあるがキャンペーン専用ではなく同社ニュース全般）を確認済み。シリアル用の /jp/products/campaigns/cereal/ は検索結果で見ただけで未確認。一覧ページにETag/Last-Modifiedなし → 条件付きGET不可、本文の該当ブロックのハッシュで差分判定。HTMLなので6時間以上の間隔で。

#### 明治 キャンペーン一覧（`meiji_campaign`）— 採用

- 理由：実施中キャンペーン12件が素のHTMLにあり、robots許可・規約に自動取得の禁止なし
- スコープ・ジャンル：B / food
- 一覧ページ：https://www.meiji.co.jp/campaign/（200）
- 取得URL（html_diff）：https://www.meiji.co.jp/campaign/
- RSS/Atom：なし（<link rel=alternate>なし、ページ内にRSSリンクなし）
- 公開JSON：なし（確認範囲で見当たらず）
- sitemap：http://www.meiji.co.jp/sitemap.xml（robots.txtに記載、未取得。一覧HTMLで足りるため）
- robots.txt：https://www.meiji.co.jp/robots.txt（200）→ ALLOW（(no matching rule)（Disallowは /takuhaimeiji/mailmagazine/ のみ））
- 規約：https://www.meiji.co.jp/regulation/ → 禁止なし。「ダウンロード、プリントアウトその他の方法による複製は、個人的または家庭内での限られた範囲における私的使用に限らせていただきます」「他のホームページや印刷物に転用（コピー、アップロード、掲載、引用など）することはお控え下さい」。クローラー・自動取得を禁じる条文なし
- JSなしのリンク：可（12件、見方：`<a class="l-card-visual-link"[^>]*href="([^"]+)"（ul.campaign-list 内のカード）`） 例：https://campaign.meiji.co.jp/campaignDetail/66544998107506/3af93caa-1468-4d1b-b8b4-de581b733899、https://www.meiji.co.jp/sweets/chocolate/chocokoka/cmp/close2610/、https://www.meiji.co.jp/baby/cmp/close2609/?link=hce26071502
- ログイン：不要　アクセス数：3
- メモ：「実施中のキャンペーン」(id=campaign) の ul.campaign-list > li.js-scroll-item > a.l-card-visual-link が1件1カード。カードに 条件タグ（今すぐ／商品購入）・方法タグ（WEB／SNS／郵送）・ブランド名・タイトル(strong)・「応募締切：」・画像altに賞品と人数がある。絞り込みと並び替えはJSだが中身は素のHTMLにある（noscriptの警告は出るが一覧は取れる）。リンク先がばらばら（x.com・instagram.com・campaign.meiji.co.jp/campaignDetail/<数字>/<uuid>・www.meiji.co.jp/<ブランド>/cmp/<名前>/・meijibulgariayogurt.com など）なので、差分はURLではなく「タイトル＋締切」をキーにするのがよい。中身は抽選中心（SNSのフォロー＆リポストが約半数、レシートのWEB応募・郵送応募）。全員型も1件あり：「ポイント集めて必ずもらえる！QUOカードPay200円分」（/baby/cmp/close2609/）。別に「明治会員ID限定キャンペーン」https://campaign.meiji.co.jp/ があるが未確認（ログイン前提・JSの可能性）。一覧ページにETag/Last-Modifiedなし（CloudFront）→ 本文ハッシュで判定、6時間以上の間隔で。

#### 森永製菓 キャンペーン情報（`morinaga_campaign`）— 採用

- 理由：一覧7件が素のHTMLにあり、robots許可・規約に自動取得の禁止なし（公式RSSもあるが一覧の全件は載らない）
- スコープ・ジャンル：B / food
- 一覧ページ：https://www.morinaga.co.jp/campaign/（200）
- 取得URL（html_diff）：https://www.morinaga.co.jp/campaign/
- RSS/Atom：https://www.morinaga.co.jp/rss/index.rdf（RSS 1.0「森永製菓の新着情報」、200・777件・2015年〜。「〇〇キャンペーン実施中！」の項目あり。ただし実施中7件のうち2件が載っておらず、約400KB・ETag/Last-Modifiedなし。別に https://www.morinaga.co.jp/company/rss/index.rdf（ニュースリリース）がRSS案内ページに記載、未取得）
- 公開JSON：なし（確認範囲で見当たらず）
- sitemap：https://www.morinaga.co.jp/sitemap.xml, https://www.morinaga.co.jp/direct-store/sitemap.xml（robots.txtに記載、未取得）
- robots.txt：https://www.morinaga.co.jp/robots.txt（200）→ ALLOW（(no matching rule)（Disallowは /faq/faq.html のみ。/rss/index.rdf もALLOW））
- 規約：https://www.morinaga.co.jp/terms/ → 禁止なし。「使用者個人、又は家庭内等の限られた少人数の間であくまで個人的に使用する目的であれば情報を複製すること（著作権法30条1項の範囲での私的使用）は認められます」。RSS案内(/rss/)に「配信されたRSSは、個人的な範囲でのご利用にとどめていただく」。クローラー・自動取得の禁止条文なし
- JSなしのリンク：可（7件、見方：`<a class="campaign-list__link" href="([^"]+)"`） 例：https://www.morinaga.co.jp/amazake/present-2026autumn、https://www.morinaga.co.jp/ototo/shinakocp2026/、https://www.morinaga.co.jp/jumbo/campaign/
- ログイン：不要　アクセス数：5
- メモ：ul.campaign-list > li.campaign-list__item > a.campaign-list__link が1件。カードに タイトル(h2)・説明文・応募方法（WEB応募／ハガキ応募／LINE応募など）・「応募締め切り：」の日付がある。リンク先はほぼ www.morinaga.co.jp/<ブランド>/<名前> 形式。中身は抽選中心（レシートのWEB応募、はがき・LINE）。例：森永甘酒 選べる＆癒されるプレゼント、おっとっと×しなこ、板チョコアイス QUOカード500名、年末ジャンボ宝くじ1,000名、カレ・ド・ショコラ毎月900名。常設の「チョコボール おもちゃのカンヅメプレゼント」（ハガキ応募）も載っている。type の選び方：優先順位では rss が上だが、公式RSS（新着情報）には一覧の「森永甘酒 present-2026autumn」と「おもちゃのカンヅメ」が載っておらず、壁紙・レシピなど関係ない項目も多い。しかも毎回約400KBで条件付きGET不可（channel の dc:date が取得時刻）。そのため主はキャンペーン一覧ページ（39KB）の html_diff とし、RSSは補助（使うなら6時間間隔）を推奨。ファンサイト Angel PLUS（ap.morinaga.co.jp）の会員限定キャンペーンは未確認（検索結果で見ただけ）。一覧ページにETag/Last-Modifiedなし。

#### カルビー キャンペーン・動画（`calbee_campaign`）— 採用

- 理由：キャンペーン欄のリンクが素のHTMLにあり、robots制限なし・規約に自動取得の禁止なし
- スコープ・ジャンル：B / food
- 一覧ページ：https://www.calbee.co.jp/campaign/（200）
- 取得URL（html_diff）：https://www.calbee.co.jp/campaign/
- RSS/Atom：なし（<link rel=alternate>なし、ページ内にRSSリンクなし）
- 公開JSON：なし（確認範囲で見当たらず）
- sitemap：robots.txtなし（404）のため記載なし
- robots.txt：https://www.calbee.co.jp/robots.txt（404）→ ALLOW（robots.txt 404 → RFC9309により制限なし）
- 規約：https://www.calbee.co.jp/policy/ → 禁止なし。サイトポリシーの禁止事項は「(1)法令・条例等に違反する行為 (2)本サイトの運営を妨げる行為 (3)誹謗・中傷 (4)知的財産権等の侵害 (5)虚偽登録 (6)その他本規約に違反する行為」。無断使用・複製の禁止はあるが、クローラー・自動取得の明文の禁止なし
- JSなしのリンク：可（2件、見方：`href="(/[^"]+\?banner=campaign)"（section#campaign 内）`） 例：https://www.calbee.co.jp/daishukakusai/?banner=campaign、https://www.calbee.co.jp/yametoma2026/?banner=campaign
- ログイン：不要　アクセス数：3
- メモ：section#campaign の ul.flex > li > a がキャンペーンのバナー（取得時点で2件：カルビー大収穫祭2026 北海道じゃがいも10万名様に当たる（最終締切12/7）、やめとま川柳大募集（10/22締切））。文字情報は画像の alt だけ（タイトル・賞品・締切）なので、差分は href＋alt で取る。各リンクは /<名前>/?banner=campaign の形。直後の section#pickup（?banner=pickup）は商品PRや通販で、キャンペーンではないので除外する。終了分は https://www.calbee.co.jp/campaign/end.php （未取得）。中身は抽選・投稿コンテスト中心で、全員型・先着は取得時点ではなし。X（旧Twitter）だけで行うキャンペーンがこの一覧に載るかは未確認。一覧ページにETag/Last-Modifiedなし → 本文ハッシュで判定、6時間以上の間隔で。

#### 味の素 キャンペーン一覧（`ajinomoto_campaign`）— 未確認

- 理由：公式のキャンペーン一覧ページのURLを特定できなかった（トップに一覧リンクなし、/campaign/ は404、Web検索の上限に達した）
- スコープ・ジャンル：B / food
- 一覧ページ：未確認（未確認（https://www.ajinomoto.co.jp/campaign/ は404））
- RSS/Atom：未確認
- 公開JSON：未確認
- sitemap：www.ajinomoto.co.jp: robots.txtなし（404）。park.ajinomoto.co.jp: https://park.ajinomoto.co.jp/sitemap/sitemap.xml（取得y：sitemapindexで recipe/magazine/recipeFeature/menuFeature/usage/others/food/food_food の8本。キャンペーン用のsitemapはなし）
- robots.txt：https://www.ajinomoto.co.jp/robots.txt（404）→ ALLOW（robots.txt 404 → RFC9309により制限なし（park.ajinomoto.co.jp/robots.txt は200、Disallowは /mypage/ /myrecipebook/ /api/auth/ のみ））
- 規約：https://www.ajinomoto.co.jp/terms/ → 禁止なし。ウェブサイト利用規約：「私的使用等法律によって認められる範囲を超えて、無断で使用（複製、改ざん、頒布等を含みます。）することはできません」。禁止行為は営利目的・虚偽申告・ウィルス等で、クローラー・自動取得の明文の禁止なし
- JSなしのリンク：不可（0件、見方：`campaign|キャンペーン|プレゼント`）
- ログイン：不要　アクセス数：8
- メモ：足りないもの：公式キャンペーン一覧のURL。確認したこと：(1) https://www.ajinomoto.co.jp/ トップ（200）の素のHTMLにはキャンペーンへのリンクが0件。ヘッダー（<header id="header"> が空）とフッターはJSで描画される。(2) 推測で試した https://www.ajinomoto.co.jp/campaign/ は404。(3) ナビのリンクを探すため /shared_file/js/common.js をデータとして取得したが、ナビのリンクは含まれていなかった（実行はしていない。この1回はむだになった）。(4) AJINOMOTO PARK https://park.ajinomoto.co.jp/ （200、noscriptの警告あり）の素のHTMLにもキャンペーン一覧へのリンクはない。あるのは通販の https://direct.ajinomoto.co.jp/campaign/ （今月のおすすめ商品、別ホストで未確認）だけ。(5) PARKのsitemapにもキャンペーン用のものはない。www.ajinomoto.co.jp の取得上限5回を使い切ったので、再確認するには別の日に予算を取るか、人が一覧URLを調べて渡す必要がある。検索結果にはAJINOMOTO ID会員の毎月抽選やAGF（agf.ajinomoto.co.jp、未確認）の記載があり、会員向けが中心の可能性がある。

#### ニチレイフーズ キャンペーン一覧（`nichirei_campaign`）— 不採用

- 理由：robots.txt と /campaign/ の両方が当方のUAに403（AWS ELB）を返す＝ブロックされているため
- スコープ・ジャンル：B / food
- 一覧ページ：未確認（403）
- RSS/Atom：未確認
- 公開JSON：未確認
- sitemap：未確認（robots.txtが403）
- robots.txt：https://www.nichireifoods.co.jp/robots.txt（403）→ 未確認（robots.txt自体が403 Forbidden（server: awselb/2.0））
- 規約：— → 未確認。サイトが当方のUAを拒否するため規約ページは未取得
- JSなしのリンク：不可（0件、見方：`None`）
- ログイン：不要　アクセス数：2
- メモ：https://www.nichireifoods.co.jp/robots.txt と https://www.nichireifoods.co.jp/campaign/ がどちらも HTTP 403（本文は118バイトの『403 Forbidden』、server: awselb/2.0）。WAFなどでUAが拒否されているとみられる。方針どおり回避策（ブラウザUA・別ホスト）は試していない。/campaign/ というURL自体は検索結果に出ていただけで、中身は未確認。

#### 山崎製パン キャンペーン（`yamazaki_campaign`）— 採用

- 理由：開催中キャンペーンのリンクが素のHTMLにあり、robots許可・規約に自動取得の禁止なし
- スコープ・ジャンル：B / food
- 一覧ページ：https://www.yamazakipan.co.jp/campaign/index.html（200）
- 取得URL（html_diff）：https://www.yamazakipan.co.jp/campaign/
- RSS/Atom：なし（<link rel=alternate>なし、ページ内にRSSリンクなし）
- 公開JSON：なし（確認範囲で見当たらず）
- sitemap：robots.txtに記載なし
- robots.txt：https://www.yamazakipan.co.jp/robots.txt（200）→ ALLOW（(no matching rule)（Disallowは /recruit/…/special/ /company/yccgallery/ /denpyo/ のみ））
- 規約：https://www.yamazakipan.co.jp/terms/index.html → 禁止なし。ご利用にあたって：「掲載内容を私的利用など法律によって認められる範囲を超えて、使用（複製、改ざん、頒布などを含む。）することはできません」「当社ウェブサイトへのリンクは、原則として自由です」。自動取得の禁止条文なし
- JSなしのリンク：可（2件、見方：`div#campaign .main ul li a[href]（ヘッダーのメガメニューにも同じリンクがあるので本文ブロックに限定）`） 例：https://yamazaki26a.jp/?openExternalBrowser=1&utm_source=site&utm_medium=lp&utm_campaign=a202609、https://www.yamazakipan.co.jp/feature/tdr_xcp/
- ログイン：不要　アクセス数：3
- メモ：本文の div#campaign > div.main > ul > li > a > img が1件で、文字情報は img の alt だけ（取得時点で「2026 秋のわくわくプレゼント」→ 季節ごとの特設ドメイン yamazaki26a.jp、「2026 東京ディズニーリゾート®＆ホテルミラコスタ宿泊ご招待キャンペーン」→ /feature/tdr_xcp/）。差分は href＋alt で取る。季節の大型キャンペーンは yamazaki<年><季節>.jp のような別ドメインにリンクされるので、URLのホストで絞らないこと。HTMLに『現在キャンペーンは実施しておりません。』がコメントで残っており、掲載がないときはこの文が表示される作り。中身は取得時点では抽選型（秋のわくわくプレゼント、TDR宿泊ご招待）。例年春の「春のパンまつり」（点数を集めて全員もらえる型として知られる）は取得時点では掲載なし（ナビに『春のパンまつりヒストリー』/campaign/spring/history/ があるだけ）。一覧ページにETag/Last-Modifiedなし → 本文ハッシュで判定、6時間以上の間隔で。

### B 飲料

#### サントリー 公式キャンペーン一覧（`suntory_softdrink_campaign`）— 未確認

- 理由：本来のキャンペーン一覧 https://www.suntory.co.jp/softdrink/campaign/ は、ページ内のリンクとして見えただけで未取得（ホストのアクセス上限5回に達した）。確認できたのはソフトドリンクトップのキャンペーン枠（6件）だけ
- スコープ・ジャンル：B / drink
- 一覧ページ：https://www.suntory.co.jp/softdrink/（200）
- RSS/Atom：なし（<link rel=alternate>なし、ページ内にRSSリンクなし）
- 公開JSON：なし（確認範囲で見当たらず）
- sitemap：robots.txtに記載なし
- robots.txt：https://www.suntory.co.jp/robots.txt（200）→ ALLOW（(no matching rule)（Disallowは /mail/ /cgi-bin/ /ZZZ/ /notice/ と年齢確認画像のみ））
- 規約：https://www.suntory.co.jp/guide/ → 禁止なし。「お客様個人で利用するため、このウェブサイトをダウンロードしたり…データを保存…することは構いませんが、これを他のウェブサイトや印刷媒体に転載したりすることはできません」。ロボット・クローラー・自動取得を禁じる条文なし
- JSなしのリンク：可（6件、見方：`トップのキャンペーン枠（「一覧 -> /softdrink/campaign/」の直後）の <a>: mobile\.suntory\.co\.jp/cpn/|closedCampaign\.html|333310\.jp/`） 例：https://mobile.suntory.co.jp/cpn/softdrink/uni/202601061/、https://333310.jp/A2741/、https://touch-suntory-line-mini-app.s3.ap-northeast-1.amazonaws.com/closedCampaign.html?id=9d2a6689-d55f-4c65-8384-bb9eab11f0fa
- ログイン：不要　アクセス数：3
- メモ：サントリー全体を束ねたキャンペーン一覧は見つからなかった。ソフトドリンク（サントリー食品）トップ /softdrink/ にキャンペーン枠があり、生HTMLに6件（スライダーの複製で8リンク）。内容は抽選プレゼントが中心（LINE・自販機限定の抽選、ドリくじ）で、「お試しキャンペーン」（333310.jp、アンケート回答でオトクに試せる型）もある。全員もらえる・先着型は今回見えた範囲ではなし。枠には終了したキャンペーン（closedCampaign.html）も残る。本来の一覧ページ https://www.suntory.co.jp/softdrink/campaign/ へのリンクを生HTMLで確認したが、このホストの上限5回に達したため未取得＝未確認。次回この一覧ページを確認し、生HTMLにリンクがあればこちらを fetch_url に差し替えるのがよい。ETag・Last-Modified なし → 本文ハッシュで差分判定。トップページなのでニュースや商品の変化も混じるため、キャンペーン枠のリンクだけを対象にする。個別エントリの URL は外部ドメインが多い（mobile.suntory.co.jp/cpn/softdrink/…、333310.jp/A数字/、touch-suntory-line-mini-app…/closedCampaign.html?id=UUID、ブランド内 /softdrink/<brand>/…/campaign/ など）。お酒（ビール等）のキャンペーンは対象外で、ブランドサイトに分散している（検索では /non-al/campaign/ や /area/<地域>/campaign/ など。未取得）。キャンペーン関連のニュースリリース一覧 /news/list/category05/ も検索で存在を確認したが未取得。robots.txt と規約の取得は候補#2と共用

#### キリン 公式キャンペーン一覧（`kirin_campaign`）— 採用

- 理由：一覧のHTMLはJS描画だが、同じデータの公開JSON(JSONP)が200で取れる。robots.txtは404、規約に機械取得の禁止なし
- スコープ・ジャンル：B / drink
- 一覧ページ：https://www.kirin.co.jp/campaign/（200）
- 取得URL（json_api）：https://www.kirin.co.jp/campaign/json/campaign.js
- RSS/Atom：なし（<link rel=alternate>なし、ページ内RSSリンクなし）
- 公開JSON：https://www.kirin.co.jp/campaign/json/campaign.js（JSONP 形式 campaign([...])、491件、200、text/javascript。描画スクリプト campaign_render.js に書かれた /campaign/json/campaign.json は 301 でこの .js に転送される）
- sitemap：robots.txt が404のため記載なし
- robots.txt：https://www.kirin.co.jp/robots.txt（404）→ ALLOW（robots.txt 404（RFC 9309 では制限なし））
- 規約：https://www.kirinholdings.com/jp/sitepolicy/ → 禁止なし。禁止事項は「営利目的の行為」「円滑な運営を妨害、または他人に迷惑をかける行為」「有害なコンピュータプログラム等を使用…する行為」など。ロボット・クローラー・自動取得を禁じる条文なし（個人の非商用利用なので営利目的には当たらない）
- JSなしのリンク：可（491件、見方：`JSONP配列の各要素の link フィールド（HTMLの /campaign/ ではJSで描画されるため0件）`） 例：https://cp.kirin.jp/join/38879、https://cp.kirin.jp/story/38378、https://cp.kirin.jp/story/36941
- ログイン：不要　アクセス数：5
- メモ：/campaign/（ソフトドリンク他）と /campaign/alcohol/（お酒を含む全件、未取得）は同じ campaign.js を描画しているだけ。各要素の項目は title, start, end, close, link, image, zettai（絶対もらえる）, konyu（購入して応募）, imasugu（今すぐ応募）, hagaki, mail, tw, fb, ig, over20, kcDirectory（['alc'] 318件 / ['softdrink'] 131件 / 空 42件）, kcSite（false はページ側で非表示）, mykirin。実施中（start≦現在≦end）は15件で、うち zettai=true は1件（小岩井ヨーグルトマイレージキャンペーン）。全件で zettai=true は9件。抽選プレゼントが中心で、絶対もらえる型・購入応募型はフラグで判別できる。title に改行代わりの \u000b が入るので置換する。JSONP の外側 campaign( … ) を外してから JSON として読む。link の主なパターンは https://cp.kirin.jp/story/<数字>（194件）、/join/<数字>（71件）、/lot/<数字>（16件）で、ほかにブランドの特設サイトもある。サイズ約317KB。200応答に Last-Modified あり（If-Modified-Since が使える）、ETag はなし。2021年からの終了分も含む491件なので、差分は link か title+start で取る。地域キャンペーンは /area/json/area.json（未取得）

#### アサヒビール 公式キャンペーン一覧（候補「アサヒ（アサヒビール／アサヒ飲料）」の1/2）（`asahibeer_campaign`）— 採用

- 理由：実施中のキャンペーン12件が生HTMLにあり、robots許可・規約に機械取得の禁止なし。先着・絶対もらえる型も載る
- スコープ・ジャンル：B / drink
- 一覧ページ：https://www.asahibeer.co.jp/campaign/（200）
- 取得URL（html_diff）：https://www.asahibeer.co.jp/campaign/
- RSS/Atom：なし（<link rel=alternate>なし、ページ内RSSリンクなし）
- 公開JSON：なし（確認範囲で見当たらず）
- sitemap：https://www.asahibeer.co.jp/sitemap.xml, https://www.asahibeer.co.jp/cocktailguide/sitemap.xml（robots.txtに記載、未取得。HTMLで足りるため）
- robots.txt：https://www.asahibeer.co.jp/robots.txt（200）→ ALLOW（(no matching rule)（Disallow は /web-service/、/products/beertaste/dryzerofree/、/common/image/nav/ など））
- 規約：https://www.asahigroup-holdings.com/privacy_policy/terms.html → 禁止なし。フッターの「ご利用規約」(/privacy_policy/05/) は301でここへ転送。「掲載内容を私的利用など法律によって認められる範囲を超えて、使用（複製、改ざん、頒布などを含む。）することはできません」。ロボット・クローラー・自動取得を禁じる条文なし（アサヒビール・アサヒ飲料に共通のグループ規約）
- JSなしのリンク：可（12件、見方：`「詳細を見る」の <a>: asahibeer-cp\.jp/|/park/cp/|/cp/|clearasahi-cp\.jp`） 例：https://www.asahibeer-cp.jp/asahibeer_stamprally/2026/、https://www.asahibeer-cp.jp/mileage/261001-261130/tagsober/、https://www.asahibeer.co.jp/web-service/asahibeer/park/cp/261006-261027/form.wsp.html?CMD=onView
- ログイン：不要　アクセス数：3
- メモ：抽選プレゼントが中心（えらべるPay、商品ケース、グッズ）。全員もらえる・先着型もある：「アサヒのZEROを1本購入＆アンケート回答で先着30万名様にえらべるPay100円相当が絶対もらえる」、クリアアサヒ「絶対もらえる！」Aコース。マイレージ型・レシート応募型あり。「一口 100G 使用」はアサヒのポイント（G）を使って応募する型。個別エントリの URL パターンは https://www.asahibeer-cp.jp/<種別>/<yymmdd-yymmdd>/…（mileage・instantwin・survey・bts など）、https://www.asahibeer.co.jp/web-service/asahibeer/park/cp/<yymmdd-yymmdd>/form.wsp.html?CMD=onView、ブランド内 /clear/cp/<yymmdd-yymmdd>/、外部の clearasahi-cp.jp。/web-service/ は robots で Disallow なので、個別ページは取りに行かず一覧だけを監視する。ETag・Last-Modified なし → 本文ハッシュで判定。ページ下部に関連リンク（アサヒ飲料 /campaign/、アサヒグループ食品 /campaign/）があり、食品は別担当なので除外する。お酒のサイトだが、一覧は生HTMLに含まれていた（年齢確認の表示があるかどうかは未確認）

#### アサヒ飲料 公式キャンペーン一覧（候補「アサヒ（アサヒビール／アサヒ飲料）」の2/2）（`asahiinryo_campaign`）— 採用

- 理由：実施中のキャンペーン8件が生HTMLにあり、robots許可・規約に機械取得の禁止なし
- スコープ・ジャンル：B / drink
- 一覧ページ：https://www.asahiinryo.co.jp/campaign/（200）
- 取得URL（html_diff）：https://www.asahiinryo.co.jp/campaign/
- RSS/Atom：なし（<link rel=alternate>なし、ページ内RSSリンクなし）
- 公開JSON：なし（確認範囲で見当たらず）
- sitemap：robots.txtに記載なし
- robots.txt：https://www.asahiinryo.co.jp/robots.txt（200）→ ALLOW（(no matching rule)（Disallow: /guide/ のみ））
- 規約：https://www.asahigroup-holdings.com/privacy_policy/terms.html → 禁止なし。フッターの「ご利用規約」(/privacy_policy/05/) は301でここへ転送。「掲載内容を私的利用など法律によって認められる範囲を超えて、使用（複製、改ざん、頒布などを含む。）することはできません」。ロボット・クローラー・自動取得を禁じる条文なし（アサヒビール・アサヒ飲料に共通のグループ規約）
- JSなしのリンク：可（8件、見方：`「…で応募」を含む <a>（主に /entertainment/campaign/<brand>/<期間|slug>/）。HTMLコメントは除外して数えた`） 例：https://www.asahiinryo.co.jp/entertainment/campaign/brandall/261001-270331/、https://www.asahiinryo.co.jp/entertainment/campaign/oishiimizu/260414-261130/、https://www.asahiinryo.co.jp/anpanman/party/
- ログイン：不要　アクセス数：2
- メモ：抽選が中心（レシート応募、自販機の二次元コードでポイント、Amazon定期便、WEBゲーム）。「必ずもらえるコースも！」（ラク実感キャンペーン）や「当たる！もらえる！」（ECサイト限定トムとジェリー）もある。個別エントリの URL パターンは /entertainment/campaign/<ブランド>/<yymmdd-yymmdd>/（例: brandall、ochamizu、oishiimizu、26eclimited-tj）、季節名の slug（/brandall/summer2026/）、/anpanman/party/、外部の wonda.spexperts.jp。重要：ページ約248KBのうち約182KBが HTMLコメントで、終了した古いキャンペーン（/entertainment/campaign/ が約95件分）がコメントアウトされたまま残っている。差分を取る前に <!-- --> を除去すること（除去しないと終了分を新着と誤認する）。ETag あり、Last-Modified は 1970-01-01 の固定値で使えない → If-None-Match を使う

#### コカ・コーラ（日本コカ・コーラ） 公式キャンペーン一覧（`cocacola_jp_campaign`）— 不採用

- 理由：利用規約がロボット・スクレイピングによるアクセスや取得を明記して禁止している
- スコープ・ジャンル：B / drink
- 一覧ページ：https://www.coca-cola.com/jp/ja/brands/coca-cola/campaign（200）
- RSS/Atom：なし（<link rel=alternate>なし）
- 公開JSON：なし（確認範囲で見当たらず）
- sitemap：https://www.coca-cola.com/content/onexp.sitemap-index.xml（robots.txtに記載、未取得）
- robots.txt：https://www.coca-cola.com/robots.txt（200）→ ALLOW（(no matching rule)（Disallow は /*/configuration、/*/login、/*/token-exchange のみ））
- 規約：https://www.coca-cola.com/jp/ja/legal/terms-of-service → 禁止あり。禁止行為として「ロボット、スパイダー、検索アプリケーション、その他の自動化されたデバイス、プロセス、又は手段を使用して、本サービスのアクセス、取得、スクレイピング、又はインデックスを行うこと」（同じ趣旨の条文が2か所）
- JSなしのリンク：可（6件、見方：`「詳しくみる」の <a>`） 例：https://www.coca-cola.com/jp/ja/brands/coca-cola/campaign/2026karaagecoke、https://www.coca-cola.com/jp/ja/brands/coca-cola/campaign/bin-coke、https://lsp-campaign.com/coke-receiptcp-glass/lp.go?inflowid=owned_4&utm_source=bn11&utm_medium=owned_4&utm_campaign=coke
- ログイン：不要　アクセス数：5
- メモ：企業トップ https://www.coca-cola.com/jp/ja にはキャンペーン一覧がない。www.cocacola.jp は302を2回経て /jp/ja/brands/coca-cola に転送され（robots.txt を取りに行ってもブランドページが返る）、そこから「コカ・コーラ」ブランドのキャンペーンページ /jp/ja/brands/coca-cola/campaign に行ける。中身は6件で生HTMLにあり、一覧の閲覧にログインは不要。内容は「オリジナル乾杯ペアグラスが絶対もらえる」（レシート応募、もれなく）、ロケットナウ経由の「コカ･コーラ ゼロカフェインが無料でもらえる」、抽選（デジタルポイント・オリジナルアイテム）など。一部は Coke ON アプリが必要（「キャンペーン参加にはCoke ONアプリ（無料）が必要」）。ブランド単位のページで、ジョージア・い・ろ・は・す等は別ページらしい（未確認）。規約で禁止されているため、回避策は探していない

#### 伊藤園 公式キャンペーン一覧（`itoen_campaign`）— 採用

- 理由：実施中・終了のキャンペーン一覧が生HTMLにあり、robots許可・規約に機械取得の禁止なし
- スコープ・ジャンル：B / drink
- 一覧ページ：https://www.itoen.jp/campaign/（200）
- 取得URL（html_diff）：https://www.itoen.jp/campaign/
- RSS/Atom：なし（<link rel=alternate>なし、ページ内RSSリンクなし）
- 公開JSON：なし（確認範囲で見当たらず）
- sitemap：https://www.itoen.jp/wp-sitemap.xml（robots.txtに記載、未取得）
- robots.txt：https://www.itoen.jp/robots.txt（200）→ ALLOW（(no matching rule)（Disallow: /wp-admin/ のみ。転送元 www.itoen.co.jp の robots.txt も同じ内容で ALLOW））
- 規約：https://www.itoen.co.jp/agreement/ → 禁止なし。「個人的に楽しむ場合（著作権法第30条第1項の範囲での私的使用）を除き、これらの情報の全部または一部を伊藤園の事前の承諾を得ずに使用（複製、改変、頒布、転載など）、または商業目的で利用することは固く禁じられています」。自動取得を禁じる条文なし
- JSなしのリンク：可（1件、見方：`「実施中」欄の「キャンペーンに参加する」の <a>`） 例：https://sslcamp.jp/itoen-paycp/
- ログイン：不要　アクセス数：4
- メモ：https://www.itoen.co.jp/campaign/ は301で商品情報サイト www.itoen.jp/campaign/ へ転送されるので、転送先を直接監視する。WordPress のサイト。「実施中」は今は1件（TULLY’S COFFEE Seattle Styleキャンペーン、マストバイ、外部 sslcamp.jp）。「終了したキャンペーン」の一覧はタイトルと終了日だけでリンクはない。終了分には「健康ミネラルむぎ茶 暑さ対策グッズが絶対もらえる！キャンペーン THE FINAL」（全員もらえる型）があり、ほかは抽選（観戦チケット、MLBグッズなど）。更新は少なめで、終了一覧の日付から見ると1〜2か月に1件程度。個別エントリはほぼ外部のキャンペーン事務局ドメイン（sslcamp.jp/<名前>/ など）へのリンクなので、差分は「実施中」欄の <a> のタイトルとURLの組で取る。ETag（W/）・Last-Modified ともあり、条件付きGETが使える。キャンペーンのニュースリリースは企業サイト https://www.itoen.co.jp/news/release/?category=release&sub%5B0%5D=campaign（検索で確認、未取得）でも追える

### B 日用品

#### 花王 キャンペーン・イベント一覧（My Kao）（`kao_mykao_campaign`）— 不採用

- 理由：一覧は5つの空の<ul>をJS（mustacheテンプレート＋Vue）で埋める作りで、生HTMLにキャンペーンへのリンクがない
- スコープ・ジャンル：B / daily
- 一覧ページ：https://member.kao-kirei.com/jp/campaign/（200）
- RSS/Atom：なし（<link rel=alternate>なし、ページ内リンクなし）
- 公開JSON：未確認（一覧はJSで描画。データ取得先は /assets/js/bundle.js 内と思われるが、/assets/ は robots で Disallow のため取得していない）
- sitemap：https://member.kao-kirei.com/sitemap.xml, https://my.kao-kirei.com/sitemap.xml（robots.txtに記載、未取得。各キャンペーンのリンク先は複数ホストに散っており収集方法にならない見込み）
- robots.txt：https://member.kao-kirei.com/robots.txt（200）→ ALLOW（Allow: /jp/campaign/（同じグループに Disallow: / あり。許可は /jp/articles/ /jp/campaign/ /jp/information/ /jp/kbbplaypark/ のみ））
- 規約：https://www.kao.com/jp/terms-of-use/ → 禁止なし。ウェブサイト利用規定：本コンテンツは「自由に閲覧いただけますが、当社の文書による事前許諾がない限り…使用（複製、頒布、改変、公衆送信、再利用及び転送等を含む）することを禁止」。ただし「個人的、非営利的かつ家庭内利用のためであれば…一部のみダウンロードすることが出来ます」。クローラー・スクレイピングを名指しした条文はない。My Kao 利用規約（webmember.kao-kirei.com/jp/kirei/ruletouse/）は未取得
- JSなしのリンク：不可（0件、見方：`campaign|cp|present（一覧の <ul id="js-campaign401〜405"> が空）`）
- ログイン：不要　アクセス数：5
- メモ：花王の会社サイトには全社のキャンペーン一覧が見当たらず、My Kao のナビにある「キャンペーン・イベント」（member.kao-kirei.com/jp/campaign/）が公式の一覧。最初に試した https://my.kao-kirei.com/campaign/ は404（そのページのナビから正しいURLを特定した）。テンプレートの項目は link_url・title・explanatory_text・disp_start_datetime・disp_end_datetime・applied（応募済み）。どんなキャンペーンが載っているかは生HTMLから見えない。検索結果では、My Kaoプレゼントキャンペーン（アンケート回答で抽選30名など）や新規会員登録プレゼント（毎月20名、抽選）が中心で、抽選型が多い様子（未確認）。ブランド別ページ（例 www.kao.co.jp/8x4/cp/ の無料サンプルプレゼント）は検索で見えたが未取得。アクセス数の内訳：my.kao-kirei.com 2、member.kao-kirei.com 2、www.kao.com 1

#### ライオン キャンペーン一覧（Lidea）（`lion_lidea_campaign`）— 採用

- 理由：ライオン公式の一覧が生HTMLに載っている・robotsは全許可・規約に機械取得の禁止なし
- スコープ・ジャンル：B / daily
- 一覧ページ：https://lidea.today/all-campaign.php（200）
- 取得URL（html_diff）：https://lidea.today/all-campaign.php
- RSS/Atom：なし（<link rel=alternate>なし、ページ内リンクなし）
- 公開JSON：なし
- sitemap：https://lidea.today/sitemap2.xml, https://lidea.today/articles/sitemap.xml, https://lidea.today/projects/enman/sitemap.xml（robots.txtに記載、未取得）。www.lion.co.jp の robots.txt には http://www.lion.co.jp/sitemap.xml
- robots.txt：https://lidea.today/robots.txt（200）→ ALLOW（(no matching rule)（User-agent: * のグループに規則なし））
- 規約：https://www.lion.co.jp/ja/legal/tou.php → 禁止なし。利用規約（Lidea のフッター「利用規約」→ http://www.lion.co.jp/web.htm → ここへリダイレクト）：「個人または家庭内の限られた範囲内における私的利用以外の目的で複製、頒布、出版、公衆送信などしてはならない」、禁止事項は「営利を目的とする行為」「利用・アクセスを妨げる行為」など。機械取得を禁じる条文はない。Lidea会員規約（https://lidea.today/terms）にもなし
- JSなしのリンク：可（2件、見方：`^https://lidea\.today/campaign/[^/]+/index`） 例：https://lidea.today/campaign/lookplus_2607eraberupay/index?from=campaign_lookplus_2607eraberupay、https://lidea.today/campaign/lion_kusuriyanohitorigoto_2610/index?from=campaign_lion_kusuriyanohitorigoto_2610
- ログイン：不要　アクセス数：5
- メモ：https://www.lion.co.jp/ja/campaign/ は302で lidea.today/all-campaign.php へ転送される（ライオンの公式サイト Lidea）。転送後のページはこのリダイレクト経由の1回で取得し、ログ上は www.lion.co.jp に1回と数えられている。巡回は転送後のURLを直接取りに行くこと。見出しは「Lideaポイントがたまる対象キャンペーン」「その他のキャンペーン」「Lideaポイントプログラム」の3つ。今の掲載は2件だけ：トイレのまるごと除菌消臭くん煙剤ポイントバック（えらべるPay 100/300ポイントを全員にプレゼント、2026/7/1〜12/31）と、ライオン×『薬屋のひとりごと』（グッズが抽選で当たる、2026/10/1〜12/31）。全員もらえる型と抽選型が両方ある。各項目は article.listBlock__item にあり、h2.listBlock__ttl a がリンク、time.txt--update が期間、p.listBlock__preview が概要。終了した lion_shinchan2507 が HTMLコメント（<!-- -->）の中に残っているので、差分を取る前にコメントを除くこと。?from= は外してキーにする。そのほか /articles/002421（ポイントで応募する会員限定の抽選プレゼント、応募はログインが必要）と /point が常に載っている。ETag・Last-Modified がないので、条件付きGETは使えずハッシュ比較になる。更新は月に数回程度の見込み。キャンペーン数は少ない

#### P&G マイレピ お得なキャンペーン（`pg_myrepi_campaigns`）— 不採用

- 理由：P&Gの利用規約が「スクレイピング」や「ロボット、スパイダー、その他の自動化された手段」でのコピーを明示的に禁じている
- スコープ・ジャンル：B / daily
- 一覧ページ：https://www.myrepi.com/campaigns/（200）
- RSS/Atom：なし（<link rel=alternate>なし、ページ内リンクなし）
- 公開JSON：なし（ページ内の __NEXT_DATA__ に同じデータが埋め込まれているだけ）
- sitemap：https://www.myrepi.com/sitemap.xml（robots.txtに記載、未取得）
- robots.txt：https://www.myrepi.com/robots.txt（200）→ ALLOW（(no matching rule)（/campaigns/ は許可。*registration *login *search *terms-and-conditions などは Disallow））
- 規約：https://termsandconditions.pg.com/ja-clean/ → 禁止あり。「サイトの個人利用」：「いかなる方法でも、サイトのコンテンツを変更、コピー、配布、表示、派生物の作成、または販売することはできません。…「スクレイピング」またはロボット、スパイダー、またはその他の自動化された手段を使用したコピーを含みます。」（P&Gサイト利用規約、最終更新2024年3月。マイレピのフッター「利用規約」のリンク先）
- JSなしのリンク：可（9件、見方：`pgjapanbrands\.com/|/cpn-`） 例：https://www.pgjapanbrands.com/ptn2609cshbk?JC=myrepi、https://www.pgjapanbrands.com/whisper2607cb?JC=myrepi、https://www.pgjapanbrands.com/feb2609toiletcp?JC=myrepi
- ログイン：不要　アクセス数：3
- メモ：技術的には条件を満たす：Next.js のサーバー側描画で、生HTMLに <a href> で9件ある。中身は対象範囲にとても合っており、全額返金が2件（パンテーン「14日間使用して満足いただけなければ全額返金」申込 2026/9/15〜11/20、ウィスパー「満足いただけなければ全額返金」申込締切 2027/1/7）。ほかに全員もらえる型（トイレ用ファブリーズ＋トイレットペーパーで選べるポイント100pt、中部薬品限定 PayPay500pt、カインズ限定でジョイの最大10%還元）、キャッシュバック・無料（Oral-B 替えブラシ50%還元、替えブラシ1パック無料）、抽選型（ジレットで10,000名にポイントバック）がある。個別のキャンペーンページは www.pgjapanbrands.com/<slug>?JC=myrepi（同じP&G規約の対象と思われる）。ETag と Last-Modified あり。P&Gジャパンの会社サイト（jp.pg.com）にはアクセスしていない。マイレピの /terms-and-conditions は robots で Disallow のため取得せず、フッターのリンク先（termsandconditions.pg.com）を読んだ。全額返金キャンペーンはプレスリリースの経路で拾う必要がある

#### ユニ・チャーム キャンペーン（`unicharm_campaign`）— 採用

- 理由：公式の一覧が生HTMLに載っている・robots許可・規約に機械取得の禁止なし・先着で必ずもらえる型もある
- スコープ・ジャンル：B / daily
- 一覧ページ：https://www.unicharm.co.jp/ja/campaign.html（200）
- 取得URL（html_diff）：https://www.unicharm.co.jp/ja/campaign.html
- RSS/Atom：なし（<link rel=alternate>なし、ページ内リンクなし）
- 公開JSON：なし
- sitemap：https://www.unicharm.co.jp/ja/sitemap.xml, https://www.unicharm.co.jp/en/sitemap.xml（robots.txtに記載、未取得）
- robots.txt：https://www.unicharm.co.jp/robots.txt（200）→ ALLOW（(no matching rule)（Disallow は /shareparts/ のみ））
- 規約：https://www.unicharm.co.jp/ja/terms-of-use.html → 禁止なし。ウェブサイト利用規約：コンテンツの複製・改変・転載は事前の承諾が必要だが「個人的に、非営利の目的で利用する場合には…利用することができる」。禁止行為は「サーバーやネットワークに過大な負荷をかける」「営利又は事業の目的で当社ウェブサイトを利用する」など。クローラー・スクレイピングを名指しした条文はない
- JSなしのリンク：可（4件、見方：`li.uc-item > a[href]（ul.uc-mod-items 内。URLはまちまちなので構造で取る）`） 例：https://www.unicharm.co.jp/ja/mamypoko/presentcp2026.html、https://www.unicharm.co.jp/ja/member/present.html、https://ds.unicharm.com/cre/?enq=5Plc1bJznvI%3d
- ログイン：不要　アクセス数：3
- メモ：AEMで作られた静的ページ（JSなしで項目が出る）。上段の corp-list-link-cpn に2件：かんたん応募サービス限定プレゼント（毎月替わり、今月は72名に抽選。応募には会員登録が必要と思われるが一覧は誰でも見られる）、マミーポコ「先着で絶対もらえるキャンペーン」（ポイントを貯めて限定グッズ、締切 2027/1/5）。下段「その他のキャンペーンはこちら」の corp-list-link-pt1 に2件：ペットのアンケート回答で『銀のスプーン』試供品を総計20,000名にプレゼント（ds.unicharm.com、締切 2026/11/20）、ペット公式LINEの友だち登録＋アンケートで抽選（lin.ee）。抽選が中心だが、先着・全員型や試供品もある。項目の要素は div.uc-title p（件名）、div.uc-tag span（応募締切）、span.uc-lead（概要）、div.uc-date p（下段の掲載日）。リンク先は /ja/<ブランド>/...html、/ja/member/present.html、外部（ds.unicharm.com、lin.ee）が混在するため、URLの正規表現ではなく li.uc-item 単位で差分を取ること。ETag あり（Last-Modified なし）、cache-control max-age=300。件数が少なく、更新は月に数回程度の見込み

#### 小林製薬 キャンペーン情報（`kobayashi_campaign`）— 不採用

- 理由：一覧ページはあるが今は1件も載っておらず、項目リンクの形を確かめられない。更新もまれ
- スコープ・ジャンル：B / daily
- 一覧ページ：https://www.kobayashi.co.jp/seihin/campaign/（200）
- RSS/Atom：なし（<link rel=alternate>なし、ページ内リンクなし。/newsrelease/2026/ にもなし）
- 公開JSON：なし
- sitemap：robots.txtに記載なし
- robots.txt：https://www.kobayashi.co.jp/robots.txt（200）→ ALLOW（(no matching rule)（Disallow は /lp/ のみ））
- 規約：https://www.kobayashi.co.jp/use/ → 禁止なし。ご利用上の注意：事前の承諾なく「権利を侵害するような形で利用すること、内容に変更を加えること、複製すること、及び公衆送信等の利用」は禁止。禁止行為に「営業活動もしくは営利を目的とする行為」。機械取得を禁じる条文はない
- JSなしのリンク：不可（0件、見方：`campaign|cp|present|brand（本文の ModuleInner が空）`）
- ログイン：不要　アクセス数：4
- メモ：S3＋CloudFront の静的ページで、JSで後から描画する作りではない。本文のブロック（<!-- CMSパーツインクルード --> の間）が空で、掲載0件。Last-Modified は 2026-07-08（7/7に終わった『消臭元』30周年キャンペーンを外した日と思われる）。キャンペーンが載ったときに再確認すれば採用できる可能性はある（robots許可・規約に禁止なし・ETagあり）。代わりの候補として https://www.kobayashi.co.jp/newsrelease/2026/ を確認した（200、生HTMLに約61件分のリンク、/newsrelease/2026/YYYYMMDD_NN/ の形）。ただし2026年のキャンペーン告知は『消臭元』感謝還元キャンペーン（/newsrelease/2026/20260423_01/、抽選）の1件だけで、効率は低い。過去の例も「小林製薬フェア」など抽選型が中心

### B コンビニ

#### セブン‐イレブン セール・キャンペーン一覧（`sej_campaign`）— 採用

- 理由：一覧が素のHTMLに39件あり、無料クーポン系のキャンペーンを含む。robots制限なし・規約に機械取得の禁止なし
- スコープ・ジャンル：B / cvs
- 一覧ページ：https://www.sej.co.jp/cmp/（200）
- 取得URL（html_diff）：https://www.sej.co.jp/cmp/
- RSS/Atom：なし（/cmp/ に <link rel=alternate>なし、ページ内のRSSリンクなし）。別ページのニュースリリース一覧 https://www.sej.co.jp/company/news_release/news/2026.html に RSSボタン（/company/news_release/index.rss）があるが、ホストの予算5回を使い切ったため未取得＝未確認
- 公開JSON：なし
- sitemap：robots.txtなし（404）のため記載なし。/sitemap.html は人間向けHTMLで未取得
- robots.txt：https://www.sej.co.jp/robots.txt（404）→ ALLOW（robots.txt 404 → RFC 9309 により制限なし）
- 規約：https://www.sej.co.jp/rule.html → 禁止なし。2.禁止事項は「権利侵害」「迷惑・損害を与える行為」「本サイトを利用した営業行為、営利目的行為またはその準備を目的とした行為」「その他本サイトの運営を妨げ…るおそれのある行為」など。3.著作権「私的利用など法律によって認められる範囲を超えて…使用（複製、改ざん、頒布などを含む。）することはできません」。スクレイピング・クローラー・自動取得を禁じる条文はない
- JSなしのリンク：可（39件、見方：`^https://www\.sej\.co\.jp/cmp/(?!index\.html|snscmppdf\.html)[a-z0-9_]+\.html$`） 例：https://www.sej.co.jp/cmp/cmdr2610.html、https://www.sej.co.jp/cmp/app_iymn2610.html、https://www.sej.co.jp/cmp/ryomon_sports2610.html
- ログイン：不要　アクセス数：5
- メモ：ページ名は「セール・キャンペーン」。#cmp（セール・キャンペーン）/#app（アプリキャンペーン）/#localCampaign（地域限定）/#preCampaign（予告）の4区分がすべて素のHTMLに入っている（inspectの id="app" ヒントは区分の見出しで、JS描画ではない）。対象になるもの：「中華まん2個購入でドリンク無料クーポン」(cmdr2610)、「クイズ正解でポカリスエット無料クーポン」、「【アプリ限定】対象飲料を5本購入で1本無料クーポン！」(app_iymn2610, app_tks2610)、「セブンマイルで無料クーポンと交換」など。ファミマのような「1個買うと1個もらえる」という名前の企画は今回の一覧にはない。値引クーポン・ステッカー・抽選・予告も混ざるのでルールフィルタが必要。個別ページのURLは https://www.sej.co.jp/cmp/<略称><YYMM>.html（app_ で始まるものはアプリ限定）。検索結果では /cmp/app_member2509/ のようにディレクトリ形式も見たため（未確認）、collector の正規表現は ^https://www\.sej\.co\.jp/cmp/(?!index\.html|snscmppdf\.html)[A-Za-z0-9_-]+(\.html|/)$ に広げるのを勧める。plaichi.html・app_mlcp.html・app_campaign.html は常設URL。ETagあり（"9a712b76"）、Last-Modifiedなし → If-None-Match が使える。/company/news_release/news/index.html は 301 のあと JS（location.href）で 2026.html に飛ぶだけのページだった。ニュースリリースRSSは2026年分の「もらえる/無料」該当が3件しかなく、主な取得元には向かない見込み（RSS自体は未確認）

#### ファミリーマート キャンペーン一覧（`familymart_campaign`）— 採用

- 理由：一覧が素のHTMLにあり、「1個買うと、1個もらえる」「無料引換券がもらえる」を含む。robots制限なし・規約に機械取得の禁止なし
- スコープ・ジャンル：B / cvs
- 一覧ページ：https://www.family.co.jp/campaign.html（200）
- 取得URL（html_diff）：https://www.family.co.jp/campaign.html
- RSS/Atom：なし（campaign.html に <link rel=alternate>なし、ページ内のフィードリンクなし。ニュースリリース一覧 /company/news_releases/2026.html にもなし）
- 公開JSON：なし
- sitemap：robots.txtなし（404）のため記載なし
- robots.txt：https://www.family.co.jp/robots.txt（404）→ ALLOW（robots.txt 404（独自の404 HTMLが返る）→ RFC 9309 により制限なし）
- 規約：https://www.family.co.jp/other/how_to_use.html → 禁止なし。「ホームページのご利用について」。著作権・商標「無断での使用・複製はお控えください」。禁止事項は①権利侵害 ②迷惑・損害 ③公序良俗・法令違反 ④個人情報の不正使用 ⑤「本サイトを利用した営業行為、営利目的行為またはその準備を目的とした行為」⑥「本サイトの運営を妨げ…るおそれのある行為」。スクレイピング・クローラー・自動取得を禁じる条文はない
- JSなしのリンク：可（33件、見方：`^https://www\.family\.co\.jp/campaign/spot/[^/]+\.html$`） 例：https://www.family.co.jp/campaign/spot/2023_1buy1-receipt_cp.html、https://www.family.co.jp/campaign/spot/2610_bento-tea_cp.html、https://www.family.co.jp/campaign/spot/famipay_1buy1.html
- ログイン：不要　アクセス数：4
- メモ：「1個買うと、1個もらえる」が載っている（カードの文言「期間中に対象商品を1個買うと、対象商品の無料引換券がもらえる！ 10月6日（火）～10月12日（月）」）。ただしURLは毎週同じ常設の /campaign/spot/2023_1buy1-receipt_cp.html なので、URLが増えたかだけを見る差分では新しい回を拾えない。このURLだけは「URL＋カードの文言（期間）」の変化を新着として扱うのを勧める。ほかの対象例：「ファミマ・ザ・海苔弁当買うと対象の飲料いずれか1本の無料引換券がもらえる！」(2610_bento-tea_cp)、「ファミペイを提示して1個買うと、1個もらえる！」(famipay_1buy1、常設)、「ファミペイ新規会員登録で無料クーポン」。個別ページのURLは https://www.family.co.jp/campaign/spot/<YYMM>_<名前>_cp.html が中心。/campaign/spot/redirect/... は別ページへの転送用なので除外してよい（上の正規表現は / を含まないため自然に除外される）。外部（楽天など）へのリンクも混ざる。カードには「NEW」「予告」の表示と「一般/ファミペイ」の区分がある。カテゴリ絞り込み（campaign.html?q={"C]campaignCategory":["3"]}＝当たる・もらえる）と /campaign/archive.html はあるが未取得。ETagなし。Last-Modified は取得した時刻とほぼ同じで毎回変わるようなので（404ページ 01:16:02、campaign 01:16:03、how_to_use 01:20:50 GMT）、条件付きGETは効かない見込み。/company/news_releases.html は 302 で /company/news_releases/2026.html に転送される

#### ローソン お得なセール情報（もらえるキャンペーン一覧）（`lawson_sale`）— 採用

- 理由：「◯◯1本/1個もらえるキャンペーン」「無料券がもらえる」が個別URLつきで素のHTMLに28件。robots許可・規約に機械取得の禁止なし
- スコープ・ジャンル：B / cvs
- 一覧ページ：https://www.lawson.co.jp/recommend/sale/index.html（200）
- 取得URL（html_diff）：https://www.lawson.co.jp/recommend/sale/index.html
- RSS/Atom：なし（/recommend/sale/ と /campaign/ のどちらにも <link rel=alternate>なし、ページ内のフィードリンクなし）。ニュースリリースのRSSはフッターから一覧ページを辿れず未取得＝未確認
- 公開JSON：なし
- sitemap：robots.txtに記載なし
- robots.txt：https://www.lawson.co.jp/robots.txt（200）→ ALLOW（(no matching rule) — 中身は User-Agent:* / Disallow: /service/collaboration/ubereats/pharmaceuticals/ のみ）
- 規約：https://www.lawson.co.jp/kiyaku/rule.html → 禁止なし。禁止事項（6）「本サイトを利用した営業行為、営利目的行為またはその準備を目的とした行為」（7）「本サイトの運営を妨げ…るおそれのある行為」。5.「著作権法に定める個人の私的使用その他法律によって明示的に認められる範囲を超えて…利用、転載、複製、配布、改変等をすることはできません」。7.「原則として、どなたでもご自由にリンクしていただいて結構です」。スクレイピング・クローラー・自動取得を禁じる条文はない
- JSなしのリンク：可（28件、見方：`^https://www\.lawson\.co\.jp/recommend/sale/detail/\d+_\d+\.html$`） 例：https://www.lawson.co.jp/recommend/sale/detail/1532991_3677.html、https://www.lawson.co.jp/recommend/sale/detail/1532992_3677.html、https://www.lawson.co.jp/recommend/sale/detail/1532995_3677.html
- ログイン：不要　アクセス数：4
- メモ：ローソンでは /campaign/（エンタメ・キャンペーン）ではなく、このページが「もう1個もらえる」系の一覧にあたる。例：「飲料1本もらえるキャンペーン 開催期間2026.10.06 - 2026.10.26」(1532991_3677)、「アイス1個もらえるキャンペーン」(1532992_3677)、「ベーカリー300円(税込)購入ごとにマチカフェコーヒーSサイズ無料券がもらえるキャンペーン」(1532995_3677)、「ドリンク剤1本もらえるキャンペーン」。2個同時購入で◯円引などの値引セールも同じ一覧に混ざるので、ルールフィルタで「もらえる/無料券」を拾う。個別ページのURLは https://www.lawson.co.jp/recommend/sale/detail/<数字ID>_3677.html で、毎週の新しい回ごとに新しいIDになる（URLの差分で拾える）。開催期間は火曜始まりで、週1回更新とみられる。グローバルメニューに /lab/campaign/<slug>/ のリンクが全ページ共通で入っているため、collector はリンクを /recommend/sale/detail/ に絞ること。サーバーはAmazonS3で、ETagとLast-Modifiedがあり条件付きGETが効く。robots.txt は先頭にUTF-8のBOMがあり、robots.py がグループを0件と読んだ（結果はALLOW all）。手で読んでも Disallow は /service/collaboration/ubereats/pharmaceuticals/ だけなので、/recommend/sale/ と /campaign/ はどちらも許可。「お試し引換券」(/ponta/tsukau/otameshi/) はPonta/dポイントとの交換なので無料ではない。対象外として未取得。accesses はホスト全体の合計（robots・/campaign/・/recommend/sale/・規約）

#### ローソン エンタメ・キャンペーン一覧（補足）（`lawson_entame_campaign`）— 不採用

- 理由：取得はできるが、中身はコラボの購入特典グッズとLoppiの予約商品が中心で、無料引換・全額還元はほとんどない
- スコープ・ジャンル：B / cvs
- 一覧ページ：https://www.lawson.co.jp/campaign/（200）
- RSS/Atom：なし（<link rel=alternate>なし、ページ内のフィードリンクなし）
- 公開JSON：なし
- sitemap：robots.txtに記載なし
- robots.txt：https://www.lawson.co.jp/robots.txt（200）→ ALLOW（(no matching rule)）
- 規約：https://www.lawson.co.jp/kiyaku/rule.html → 禁止なし。lawson_sale と同じ規約。機械取得を禁じる条文はない
- JSなしのリンク：可（19件、見方：`^https://www\.lawson\.co\.jp/lab/campaign/[^/]+/$`） 例：https://www.lawson.co.jp/lab/campaign/lgacha/、https://www.lawson.co.jp/lab/campaign/tenipuriu17wp/、https://www.lawson.co.jp/lab/campaign/bluelock/
- ログイン：不要　アクセス数：1
- メモ：ページ名は「エンタメ・キャンペーン｜ローソン公式サイト」。本文は8件で、どれも「オリジナルグッズを手に入れよう！」という対象商品購入の特典（コラショ、mojojojo、ブルーロック、んぽちゃむ、ホロライブ予告、Mrs. GREEN APPLE予告）と「アプリでLガチャ」（Ponta/dポイント会員限定のスタンプ制ゲーム）。無料引換券の企画は /recommend/sale/ 側にある（lawson_sale を参照）。19件の中にはメニュー由来の重複と、クリスマス・おせち・ご予約弁当も入っている。Loppi限定グッズ（/campaign/lop_<名前>/?utm_...）は予約販売。必要なら html_diff で有効にでき、個別ページのURLは https://www.lawson.co.jp/lab/campaign/<slug>/（予告は文言に[予告]がつく）。アクセスは lawson_sale と共有（このページは1回）

### B ゲーム（無料配布）

#### Epic Games Store 無料ゲーム（freeGamesPromotions JSON）（`epic_free_games`）— 不採用

- 理由：認証なしのJSONは取れて robots.txt もないが、サイト利用規約がこちらのUAに403で読めず、検索結果の抜粋（未確認）に自動の手段で監視・分析などのためにデータを抽出すること（scraping）を禁じる条項がある可能性があるため、ユーザー判断で不採用（2026-10-09）
- スコープ・ジャンル：B / game
- 一覧ページ：未確認（200（JSON））
- 取得URL（json_api）：https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=ja&country=JP&allowCountries=JP
- RSS/Atom：なし（RSSは見当たらず）
- 公開JSON：https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=ja&country=JP&allowCountries=JP（認証なしで200、application/json、約8.5KB、12件）
- sitemap：robots.txtなし（404）
- robots.txt：https://store-site-backend-static.ak.epicgames.com/robots.txt（404）→ ALLOW（robots.txtなし＝制限なし（RFC 9309））
- 規約：https://www.epicgames.com/site/en-US/tos → 未確認（禁止条項の可能性あり）。読めた規約2つには禁止条項がない。Epic Games サービス利用規約（legal.epicgames.com/epicgames/tos、2026-09-10 更新）の『ボット』は『ライセンス製品の使用を自動化するためにボットソフトウェアを使うこと』の禁止で、ゲーム本体についての規定。Epic Games Store EULA（legal.epicgames.com/store/eula）には自動取得の条項がない。一方、サイトの利用規約 www.epicgames.com/site/en-US/tos は当方UAに 403（Cloudflare のチャレンジ）が返り、読めなかった。検索結果の抜粋（未確認）では『スクリプト・クローラー等の自動手段で…監視・測定・分析・複製…のためにデータを抽出すること（scraping）』を禁じる条項がある
- JSなしのリンク：可（12件、見方：`JSON data.Catalog.searchStore.elements[]（promotions.promotionalOffers[].promotionalOffers[].discountSetting.discountPercentage==0 が無料）`） 例：Out of Sight（productSlug: out-of-sight-b96ca8）2026-10-09 00:00〜10-16 00:00 JST 無料（¥1,700→¥0）、TerraScape（terrascape-2b12b1）同期間 無料、次回予定（upcomingPromotionalOffers）：Bad Cheese / Agent A - 偽装のパズル 10-16〜10-23 JST
- ログイン：不要　アクセス数：5
- メモ：【中身】Epic のストア画面が使っている JSON。12件のうち、今まさに無料なのは2件、次週の無料予定が2件。残りは関連タイトルやセール予定。無料の判定は promotionalOffers の discountPercentage==0（Epic の書き方では残る価格の割合）と price.totalPrice.discountPrice==0 の両方を見る。週1回（木曜 0:00 JST 前後）入れ替わるので、30分間隔より6時間間隔で十分。対象の割合は高く、無料の対象はほぼ毎週ある。【未確認の点】www.epicgames.com が当方UAに 403（Cloudflare）を返すため、サイト利用規約を読めていない。ストアの画面（www.epicgames.com/store/…）も同じホストなので、同じく 403 になる見込み。利用者がブラウザでサイト利用規約の scraping 条項を読み、JSON の定期取得が当たらないと確認できるまでは、不採用扱いを推奨する。この JSON には ETag・Last-Modified がない。

#### Steam 期間限定無料配布（Free to Keep）（`steam_free_to_keep`）— 不採用

- 理由：Steam 利用規約 4.C が、スクリプト・ボット等で Steam のコンテンツやサービスとやり取りすることを禁じている（例示に限定されない書き方）
- スコープ・ジャンル：B / game
- 一覧ページ：https://store.steampowered.com/search/?maxprice=free&specials=1（200）
- RSS/Atom：なし（検索ページに <link rel=alternate> なし。無料配布をまとめた公式フィードは見当たらない）
- 公開JSON：未確認（/search/results/ の JSON 応答は試していない。規約で不採用のため）
- sitemap：robots.txtに記載なし
- robots.txt：https://store.steampowered.com/robots.txt（200）→ ALLOW（(no matching rule)（/share/ /widget/ /email/ などのみDisallow））
- 規約：https://store.steampowered.com/subscriber_agreement/ → 禁止あり。Steam 利用規約 4.C 自動化：『ユーザーは、何らかの形式のスクリプト、ボット、マクロ、その他の人間によらない制御システム（以下を含みますがこれらに限定されず、これらを「自動化」といいます）を用いて、Steam 上の本コンテンツおよび本サービスとやり取りしてはなりません。』（例示はアカウント作成の自動化・統計の捏造など）
- JSなしのリンク：可（4件、見方：`^https://store\.steampowered\.com/(app|sub|bundle)/\d+`） 例：https://store.steampowered.com/app/2283211/World_of_Warships__Ning_Hai/?snr=1_7_7_2300_150_1、https://store.steampowered.com/app/5067220/Rotwood_Drakin_Armoury_Pack/?snr=1_7_7_2300_150_1
- ログイン：不要　アクセス数：4
- メモ：技術的には取得できる。検索ページ（価格上限＝無料・セール中のみ）の生HTMLに100%オフの4件があった（すべてDLC：World of Warships・Gear.Club・MXGP 26・Rotwood）。ゲーム本体の Free to Keep は月に数件程度で、DLCが多い。Steamworks の資料（検索で見ただけ、未取得）にも『Free to Keep をまとめて見られる場所は Steam 上にない』とある。各アプリのニュースRSSは公式にあるが、無料配布の一覧にはならない。フッターの『リーガル』www.valvesoftware.com/legal.htm は3回リダイレクトして /ja/（トップ）に着き、法務ページは読めなかった。規約の禁止は検索ページにも JSON 応答にも同じく当たると判断した。

#### GOG 無料配布（Giveaway）（`gog_giveaway`）— 不採用

- 理由：トップの生HTMLに配布の中身がない（Angular の JS 描画）。JSON は確認できず、規約ページは 403 で読めない
- スコープ・ジャンル：B / game
- 一覧ページ：https://www.gog.com/en/（200）
- RSS/Atom：なし（<link rel=alternate>なし、ページ内リンクなし）
- 公開JSON：未確認（検索で見た https://www.gog.com/giveaway/api/get は 404 の HTML。『配布中でなければ404』とされるので、配布がないのかURLが違うのか区別できない）
- sitemap：robots.txtに記載なし
- robots.txt：https://www.gog.com/robots.txt（200）→ ALLOW（(no matching rule)（/upload/ /www/ /profile などのみDisallow。content-type は text/html だが中身は robots.txt））
- 規約：https://support.gog.com/hc/en-us/articles/212632089-GOG-COM-User-Agreement → 未確認。GOG 利用規約（検索で見たURL）は当方UAに 403（Cloudflare『Just a moment… Enable JavaScript and cookies』）が返り、読めなかった。フッターの『Legal』は support.gog.com/hc/categories/201526109 で、これも同じホスト
- JSなしのリンク：不可（0件、見方：`giveaway|free`）
- ログイン：不要　アクセス数：4
- メモ：トップ（約1.4MB）にあるのは .giveaway__image という CSS と、エラー無視リストの 'Giveaway','404 OK' だけで、配布作品名・リンクはない。'{{ product.title }}' のようなテンプレートが残っているので、商品一覧も JS 描画。無料配布は年に数回〜月1回程度で、時期は不定。配布中に /giveaway/api/get を1回だけ試せば JSON があるか分かるが、support.gog.com が 403 で規約を確かめられないので、採用はできない。価格0・割引中の一覧（/en/games?priceRange=0,0&discounted=true など）は未確認。

#### Prime Gaming（Amazon）無料ゲーム（`prime_gaming`）— 不採用

- 理由：gaming.amazon.com は Amazon Luna の受け取りページに移っていて、生HTMLはリンク0件の JS アプリ（受け取りには Prime ログインが必要）
- スコープ・ジャンル：B / game
- 一覧ページ：未確認（302→200（https://luna.amazon.com/claims/?g=s、中身はJSアプリの殻））
- RSS/Atom：なし（<link rel=alternate>なし）
- 公開JSON：未確認
- sitemap：https://gaming.amazon.com/sitemap.xml（robots.txtに記載、未取得）
- robots.txt：https://gaming.amazon.com/robots.txt（302→https://luna.amazon.com/claims/static/seo/robots.txt?g=s）（200）→ ALLOW（(no matching rule)（/prime/status/ /oauth/ などのみDisallow））
- 規約：— → 未確認。JSのみで不採用が決まったため、Amazon の利用規約は取得していない
- JSなしのリンク：不可（0件、見方：`claims|loot|game`）
- ログイン：必要　アクセス数：2
- メモ：https://gaming.amazon.com/ は 302 で https://luna.amazon.com/claims/?g=s に移る。title は『Amazon Luna Cloud Gaming』、<a> は0件、id="root" と『You need to enable JavaScript to run this app.』だけ。取得時は『We're having technical difficulties』と出ていた。検索結果（未確認）によると、Prime Gaming は2025年末で終わり、無料ゲームの特典は Amazon Luna に移った。日本で Luna の特典が使えるかは未確認。

#### GamerPower 公開API（ゲームの無料配布の一覧）（`gamerpower_api`）— 不採用

- 理由：robots.txt が全UAに対して /api/* を Disallow しているため（説明ページはボットでの利用を案内しているが、robots.txt に従う）
- スコープ・ジャンル：B / game
- 一覧ページ：https://www.gamerpower.com/api-read（200）
- RSS/Atom：https://www.gamerpower.com/rss/giveaways（別の候補 gamerpower_rss として確認）
- 公開JSON：https://www.gamerpower.com/api/giveaways（説明ページに記載。robots.txt で Disallow のため取得していない）
- sitemap：https://www.gamerpower.com/sitemap.xml（robots.txtに記載、未取得）
- robots.txt：https://www.gamerpower.com/robots.txt（200）→ DISALLOW（Disallow: /api/*）
- 規約：https://www.gamerpower.com/terms-of-use → 禁止あり。Acceptable Use Policy (vi)「use software or automated agents or scripts to produce multiple accounts on the Site, or to generate automated searches, requests, or queries to the Site」。一方でAPIの説明ページ（/api-read）は「No API Key Required」「The API is free and only requires attribution to GamerPower.com」「Do not exceed 10 requests per second」として、アプリ・ボットへの組み込みを案内している
- JSなしのリンク：不可（0件、見方：`—（APIは取得していない）`）
- ログイン：不要　アクセス数：2
- メモ：説明ページによると、エンドポイントは /api/giveaways（platform・type・sort-by で絞り込み）、/api/giveaway?id=、/api/filter、/api/worth。上限は毎秒10回。運営は Digiwalls Media。robots.txt の Disallow は検索エンジン向けの意図とも読めるが、ルールどおり不採用とした

#### GamerPower 無料配布RSS（`gamerpower_rss`）— 採用

- 理由：robots.txtは許可。利用規約の Acceptable Use Policy に「自動のリクエスト・問い合わせの禁止」があるが、サイト自身がRSSを提供しボットでの利用も案内していることから、RSSの定期取得は想定内とみなしてユーザー判断で採用（2026-10-09）
- スコープ・ジャンル：B / game
- 一覧ページ：https://www.gamerpower.com/rss/giveaways（200）
- 取得URL（rss）：https://www.gamerpower.com/rss/giveaways
- RSS/Atom：https://www.gamerpower.com/rss/giveaways（RSS 2.0、14件、2026-10-01〜10-08 の約1週間分、英語。説明ページの <link rel=alternate> が指す。Last-Modified あり）
- 公開JSON：https://www.gamerpower.com/api/giveaways（robots.txt で Disallow。gamerpower_api を参照）
- sitemap：https://www.gamerpower.com/sitemap.xml（robots.txtに記載、未取得）
- robots.txt：https://www.gamerpower.com/robots.txt（200）→ ALLOW（(no matching rule)）
- 規約：https://www.gamerpower.com/terms-of-use → 禁止とも読める条文あり（ユーザー判断で採用）。Acceptable Use Policy (vi)「use software or automated agents or scripts to produce multiple accounts on the Site, or to generate automated searches, requests, or queries to the Site」。サイト自身がRSSを案内しているので矛盾した書き方だが、字面どおりに読むと定期取得も当たる
- JSなしのリンク：可（14件、見方：`RSS <item>`） 例：https://www.gamerpower.com/pony-island-steam-giveaway、https://www.gamerpower.com/out-of-sight-epic-games-giveaway
- ログイン：不要　アクセス数：2
- メモ：中身は14件すべてが無料配布（Steam・Epic・スマホ・DLC・プレイテストのキーなど）。title は「<タイトル> (<ストア>) Giveaway」、description に期限（例：free until October 15）が入ることがある。地域限定の注記あり。規約の解釈しだいで採用できる

#### Game*Spark 新着記事RSS（`gamespark_news`）— 採用

- 理由：取得・robots.txt・規約は問題なし。ニュース記事だが、今受け取れる無料配布を伝える記事は対象とする（2026-10-09 ユーザー判断）
- スコープ・ジャンル：B / game
- 一覧ページ：https://www.gamespark.jp/（200）
- 取得URL（rss）：https://www.gamespark.jp/rss20/index.rdf
- RSS/Atom：https://www.gamespark.jp/rss20/index.rdf（RSS 2.0、50件、2026-10-08 21:30〜10-09 12:00 JST の約14.5時間分、description は平均43字。トップの <link rel=alternate> が指す。ページ内に /rss/index.rdf へのリンクもある（未取得））
- 公開JSON：なし（確認範囲で見当たらず）
- sitemap：robots.txtに記載なし
- robots.txt：https://www.gamespark.jp/robots.txt（200）→ ALLOW（(no matching rule)）
- 規約：https://www.gamespark.jp/pages/info/terms.html → 禁止なし。「本サービス上で提供する情報は、利用者の私的利用の範囲内でご利用いただけます」。私的利用の範囲を超えた無断の複製・転載は禁止。禁止事項（権利侵害、運営妨害、アカウント共有、公序良俗違反など）に自動取得の項目はない
- JSなしのリンク：可（50件、見方：`RSS <item>`） 例：http://www.gamespark.jp/article/2026/10/09/173406.html、http://www.gamespark.jp/article/2026/10/09/173383.html
- ログイン：不要　アクセス数：4
- メモ：約14.5時間分50件のうち対象は2件：「【3,350円→0円】…『Out of Sight』＆…『TerraScape』Epic Gamesストアにて10月15日まで無料配布」と「【2,300円→0円】…『Conarium』Amazonプライム会員向けに無料配布」（後者は会員が条件なので requires_subscription で落ちる想定）。無料配布の記事は題名に「【◯円→0円】」「無料配布」が入る。robots.txt の crawl-delay 5 は bingbot・Baiduspider 向けだけ。フィード内の記事リンクは http:// で書かれている（URL正規化で https にそろえる必要あり）

#### AUTOMATON 新着記事RSS（`automaton_news`）— 採用

- 理由：取得・robots.txt・規約は問題なし。ニュース記事だが、今受け取れる無料配布を伝える記事は対象とする（2026-10-09 ユーザー判断）
- スコープ・ジャンル：B / game
- 一覧ページ：https://automaton-media.com/（200）
- 取得URL（rss）：https://automaton-media.com/feed/
- RSS/Atom：https://automaton-media.com/feed/（WordPress RSS 2.0、60件、2026-10-07 09:11〜10-09 12:00 JST の約2日分、description は平均77字。トップの <link rel=alternate> が指す）
- 公開JSON：WordPress REST（/wp-json/）が <link> にあるが未取得（RSSで足りるため）
- sitemap：robots.txtに記載なし
- robots.txt：https://automaton-media.com/robots.txt（200）→ ALLOW（(no matching rule)）
- 規約：https://automaton-media.com/terms-of-use/ → 禁止なし。禁止事項は「本ウェブサイトのサーバーに対し、大量の接続要求を行うなどして負荷・トラフィックを高め、ウェブサイトの運用を妨害する行為」など。コンテンツの無断転載・二次利用は禁止。自動取得を名指しで禁じる条文はない
- JSなしのリンク：可（60件、見方：`RSS <item>`） 例：https://automaton-media.com/articles/newsjp/pony-island-20261009-472712/
- ログイン：不要　アクセス数：4
- メモ：約2日分60件のうち対象は1件：「“ゲームに抵抗する”メタサスペンスゲーム『Pony Island』がSteamにて無料配布中」。無料体験版・基本プレイ無料の記事も多いので、AI判定で落とす必要がある。robots.txt の細かい Disallow は Googlebot-News 向けで、* 向けは /games/ /events/ など一部だけ（/feed/ は許可）

#### 4Gamer.net 新着記事RSS（`fourgamer_news`）— 不採用

- 理由：取得・robots.txt・規約は問題ないが、約2日分100件に、受け取って持ち続けられる無料配布の記事がなかった（Core Keeper のフリーウィークエンドなど、期間中に遊べるだけのもの）
- スコープ・ジャンル：B / game
- 一覧ページ：https://www.4gamer.net/rss/index.xml（200）
- RSS/Atom：https://www.4gamer.net/rss/index.xml（RSS、100件、2026-10-07 14:42〜10-09 12:00 JST の約2日分、description は平均110字。トップの <link rel=alternate> が指す）
- 公開JSON：なし（確認範囲で見当たらず）
- sitemap：robots.txtに記載なし
- robots.txt：https://www.4gamer.net/robots.txt（200）→ ALLOW（Disallow:（空）＝全許可）
- 規約：— → 規約ページなし。トップのフッターに利用規約へのリンクはなく、「本サイト『4Gamer.net』の内容は，すべて無断転載を禁止します。ただし商用利用を除き，リンクについてはその限りではありません」とあるだけ。プライバシーポリシー（https://www.4gamer.net/about/policy.shtml）にも自動取得の記載なし
- JSなしのリンク：可（100件、見方：`RSS <item>`） 例：https://www.4gamer.net/games/029/G002975/20260921064/、https://www.4gamer.net/games/008/G100845/20261008053/
- ログイン：不要　アクセス数：4
- メモ：ゲーム全般のニュースで件数が多く（1日約50件）、無料配布の記事はまれ。2章の「ニュース記事は除外」の扱いを決めたうえで、必要なら再検討する

### B 懸賞・キャンペーンまとめサイト

#### チャンスイット 懸賞情報（全員・先着）（`chanceit_present`）— 不採用

- 理由：規約で「提供されているインターフェイス以外の手段」でのアクセスと、承諾のない情報収集を禁止しているため
- スコープ・ジャンル：B / food, drink, daily, cvs
- 一覧ページ：未確認（トップ https://www.chance.com/ が200。一覧 /present/list/all-present-or-first-come/ は規約で禁止のため未取得）
- RSS/Atom：未確認（トップの <link rel=alternate> はスマホ版 /sp/ を指すだけで、フィードではない）
- 公開JSON：なし（確認範囲で見当たらず）
- sitemap：https://www.chance.com/sitemap.xml（robots.txtに記載、未取得）
- robots.txt：https://www.chance.com/robots.txt（200）→ ALLOW（(no matching rule) — User-agent:* は /go.srv /jump.srv /click /member/login.srv? などだけを禁止。/present/ は対象外）
- 規約：https://www.chance.com/terms.jsp → 禁止あり。第10条 財産権「会員は、チャンスイット によって会員に提供されているインターフェイス以外の手段を用いてチャンスイット にアクセスしないものとします。」「会員が前2項に違反した場合は、当社より、差止請求、損害賠償請求等を受けることがあります。」。禁止事項に「調査、相手の承諾のない情報収集…を行うこと」。冒頭で「チャンスイット」を利用するユーザ＝「会員」と定義しているので、未登録の閲覧者にも当てはまる
- JSなしのリンク：可（30件、見方：`^https://www\.chance\.com/present/detail/\d+$（トップページで確認）`） 例：https://www.chance.com/present/detail/720093、https://www.chance.com/present/detail/719893、https://www.chance.com/present/detail/719900
- ログイン：不要　アクセス数：3
- メモ：運営はインフォニア株式会社。内容は対象に近く、トップだけでも「ヨギボー サポート 他 全員 江崎グリコ」「えらべるPay 最大600ポイント 全員 ライオン」「デイリーヤマザキ専用QUOカードPay…全員 山崎製パン」など、メーカーの全員プレゼントがあった。トップには「全員・先着」の一覧 /present/list/all-present-or-first-come/ へのリンクがあるが、規約上の禁止がわかったので取得していない（未確認）。個別ページのURLは https://www.chance.com/present/detail/<数字ID>。robots.txt は許可だが、規約を優先して不採用とした。サイトのURLはWebSearchの上限（全エージェント共有の200回）に達したため記憶から選び、fetchでタイトル「…チャンスイット」を確認した

#### 懸賞にゃんダフル（`nyandaful`）— 不採用

- 理由：今は広告利用でポイントがたまるポイントサイトで、メーカーの懸賞やキャンペーンをまとめたものではない（対象を載せていない）
- スコープ・ジャンル：B / food, drink, daily, cvs
- 一覧ページ：https://www.nyandaful.jp/（200）
- RSS/Atom：なし（トップに <link rel=alternate>なし）
- 公開JSON：なし
- sitemap：https://www.nyandaful.jp/sitemap-list.xml（robots.txtに記載、未取得）
- robots.txt：https://www.nyandaful.jp/robots.txt（200）→ ALLOW（User-agent: * / Disallow:（空））
- 規約：https://www.nyandaful.jp/kiyaku.asp → 禁止なし。第12条（禁止事項）は「(7)当社に承認を得ずに行う営利を目的とする行為」「(8)当サービスの運営を妨害する行為」「(10)その他、当社が不適切と判断する行為」など。機械取得を禁じる条文はない（会員向けの規約）
- JSなしのリンク：不可（0件、見方：`全員|先着|プレゼント（トップ本文に0件）`）
- ログイン：不要　アクセス数：3
- メモ：タイトルは「懸賞にゃんダフル - ネット広告とユーザーをマッチングするお得なサイト！」。トップの項目は会員登録・アンケート・クレジットカードなどの案件（p_detail.asp?m=...）とポイントの種類（ログイン/アンケート/CM/ビンゴ）。「プレゼント」「全員」は本文に0件。Shift_JIS。WebSearchの上限に達したためURLは記憶から選び、fetchで確認した。ほかの懸賞まとめサイト（懸賞なび等）は検索ができず、見つけられていない

## 追加検証（2026-10-09 夕方、抽選（A）の情報源の補強）

フェーズ0と同じ手順（実際に取得して確認、1ホスト5回まで、回避はしない）で、抽選（A）の候補を追加で確かめた。大手の量販店・チェーンの抽選はアプリや店頭が中心で、公開のWebページで告知しているところは少なかった。

| 区分 | 候補 | 判定 | 方式 | 確認したURL | 理由 |
|---|---|---|---|---|---|
| A トレカ・ゲーム機（店舗・メーカー） | トイザらス（toysrus.co.jp）抽選販売・予約のお知らせ | 不採用 | — | 未確認 | サイト全体が Cloudflare のチャレンジで当方の UA をブロック（robots.txt・お知らせページとも 403） |
| A トレカ・ゲーム機（店舗・メーカー） | セブンネットショッピング（7net）抽選販売のお知らせ | 不採用 | — | 未確認 | 抽選の告知が載るヘルプセンター（Zendesk）は Cloudflare で 403。通販本体のキャンペーン一覧には抽選が載っていない |
| A トレカ・ゲーム機（店舗・メーカー） | ヤマダデンキ（ヤマダウェブコム／yamada-denki.jp）抽選販売のお知らせ | 不採用 | — | 未確認 | 公開ページに抽選販売の告知一覧がない（抽選はヤマダデジタル会員アプリ／ログイン後の商品ページで実施） |
| A トレカ・ゲーム機（店舗・メーカー） | ケーズデンキ 抽選販売のお知らせ | 不採用 | — | 未確認 | RSS・お知らせ一覧とも取得できるが、抽選販売の告知が 1 件もない |
| A トレカ・ゲーム機（店舗・メーカー） | TSUTAYA（ポータル tsutaya.tsite.jp）トレカ・ゲーム記事一覧 | 不採用 | — | https://tsutaya.tsite.jp/articles/category/trading-card | 技術的には取得できるが、トレカ・ゲームの記事一覧に抽選販売の記事が 0 件（大会・特典の記事のみ） |
| A トレカ・ゲーム機（店舗・メーカー） | SHIBUYA TSUTAYA（shibuyatsutaya.tsite.jp）POKÉMON CARD LOUNGE の抽選販売記事 | 未確認 | — | https://shibuyatsutaya.tsite.jp/event/?sort=new | ポケカの抽選販売記事は実在するが、それが載る一覧ページを今日の上限（5回）までに確認できなかった |
| A トレカ・ゲーム機（店舗・メーカー） | 遊戯王OCG（KONAMI 遊戯王カードゲーム総合サイト）ニュース一覧 | 不採用 | — | https://www.konami.com/yugioh/news/ | 技術的には取得できるが、直近30件（全ニュース15件＋商品情報15件）に抽選・数量限定販売の告知が 0 件 |
| A トレカ・ゲーム機（店舗・メーカー） | デュエル・マスターズ公式（タカラトミー）お知らせ | 不採用 | — | https://dm.takaratomy.co.jp/news/ | RSS で取得できるが、直近40件（8/17〜10/5）に抽選・数量限定販売の告知が 0 件（『〜を更新！』の告知ばかり） |
| A トレカ・ゲーム機（店舗・メーカー） | ポケモン公式サイト（pokemon.co.jp）ニュース | 不採用 | — | https://www.pokemon.co.jp/info/ | ニュース一覧は JS で描画（生の HTML は読み込み中のダミー枠だけ）。RSS なし、サイトマップに記事 URL なし |
| A ウイスキー（酒販店・百貨店） | 信濃屋（SHINANOYA NET SHOP）お知らせ一覧（ネット抽選販売の告知） | 不採用 | html_diff | https://www.shinanoya-tokyo.jp/view/news/list | 取得・robots.txt・規約は問題ないが、抽選の告知の見出しが「【ウイスキー予約・販売に関して】」で「抽選」の語がなく、一覧の文字だけではAIが抽選と判定できない（個別ページは取りに行かない方針） |
| A ウイスキー（酒販店・百貨店） | リカーマウンテン（リカマン）お知らせ・キャンペーン・イベント | 不採用 | — | https://www.likaman.co.jp/news | 公開ページに抽選販売の告知がない。お知らせはセール・新店・イベント、キャンペーン一覧は空、イベント一覧は試飲会・セミナー |
| A ウイスキー（酒販店・百貨店） | オーケー（OK）お知らせRSS（国産洋酒の抽選販売の告知） | 採用 | rss | http://ok-corporation.jp/rss2.xml | RSSあり。「国産洋酒の抽選販売実施について（オーケークラブ会員カードアプリ限定）」が月1〜2件載る。robotsなし（404）、規約ページなし |
| A ウイスキー（酒販店・百貨店） | 河内屋（酒のスーパー）ウイスキー抽選の告知 | 未確認 | — | 未確認 | Web検索2回で公式サイトの抽選告知ページが見つからなかった（結果はイオン・オーケーの記事ばかり）。アクセスしていない |
| A ウイスキー（酒販店・百貨店） | 東急百貨店オンラインストア ウイスキー抽選販売のご案内 | 採用 | html_diff | https://online.tokyu-dept.co.jp/sp/?fkey=lottery_sale | オンラインストア会員向けウイスキー抽選の専用ページ。生HTMLに抽選商品の枠と応募フォームへのリンクが出る。robotsなし（404）、規約に禁止なし。いまは「現在抽選販売はございません」 |
| A ウイスキー（酒販店・百貨店） | 小田急百貨店 新宿店（催し・イベント／今日の小田急）のウイスキー抽選販売会 | 不採用 | — | https://www.odakyu-dept.co.jp/shinjuku/today/index.html | ウイスキー抽選販売会は「夏トク」などの季節催事ページの中の一項目で、催し一覧・今日の小田急には独立した項目として出ていない（いまの23件は0件） |
| A ウイスキー（酒販店・百貨店） | 京王百貨店（京王ネットショッピング）のウイスキー抽選販売 | 未確認 | — | 未確認 | 検索で抽選販売の公開一覧が見つからなかった。京王ネットショッピングのウイスキーは京王カード会員向けの数量限定セット（先着）の例ばかり。アクセスしていない |
| A ウイスキー（酒販店・百貨店） | リカーズハセガワ本店（ウイスキー専門店）新着情報RSS | 不採用 | — | https://www.liquors-hasegawa.com/ | 取得手段（RSS）はあるが、抽選の告知がほとんど載らない。RSS19件・トップの新着情報に抽選は0件、確認できたのは過去1件（輸入ウイスキー）だけ |
| A ウイスキー（酒販店・百貨店） | 酒匠さんそう ニュース（ジャパニーズウイスキー抽選販売のお知らせ） | 不採用 | — | 未確認 | 2回目のリクエスト（/blogs/news）で 429（本文 local_rate_limited、Retry-After: 60）が返った。規則4によりブロック扱い |
| A ウイスキー（酒販店・百貨店） | リカーショップキナセ（水戸）ブログRSS（国産ウイスキー抽選販売会・イチローズモルト抽選の告知） | 保留 | rss | https://liquor-shop-kinase.co.jp/feed/ | 店主のブログで国産ウイスキー（イチローズモルト・マルスなど）の抽選販売会を年4〜6回告知している。RSSあり、robots許可、規約ページなし。水戸の店頭で応募する地域限定の抽選なので、sources.yaml には enabled: false で登録（使うかはユーザー判断） |
