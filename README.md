# otoku（お得情報収集システム）

個人用。限定品の抽選と100%還元キャンペーンを集めて厳選し、Discord に通知する。仕様は [DESIGN.md](DESIGN.md)。

## セットアップ

```sh
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
cp .env.example .env   # 値を入れる（.env は Git に含めない）
```

- 鍵は `.env` だけから読む（シェルの環境変数は見ない）。
- 本番の実行（`--dry-run` なし）には、collect は `GEMINI_API_KEY`・`DISCORD_BOT_TOKEN`・`DISCORD_CHANNEL_LOG`・`CONTACT`、send は `DISCORD_BOT_TOKEN`・`DISCORD_CHANNEL_ACTION`・`DISCORD_CHANNEL_LOG` が必要。

## 使い方

```sh
.venv/bin/python -m otoku collect --dry-run   # Discord送信とDB書き込みをせず、標準出力に出す
.venv/bin/python -m otoku collect             # 収集〜候補登録まで。#ログ に1候補1行で記録
.venv/bin/python -m otoku send --dry-run      # 送信選定の結果を標準出力に出す（時刻に関係なく通常の選定を試す）
.venv/bin/python -m otoku send                # 選定枠（12:00・19:00）なら通常の選定、それ以外は緊急のみ。#行動 に送る
.venv/bin/python -m otoku send --urgent-only  # 緊急（先着・締切24時間以内）だけ送る
.venv/bin/python -m otoku sync                # #行動 のリアクション（✅⏰❌）を読んで記録する
.venv/bin/python -m otoku sync --weekly-report  # さらに情報源の重みを調整し、#ログ に週次報告
.venv/bin/python -m otoku remind              # ⏰ が付いたものを、締切24時間前に1回だけ知らせる
.venv/bin/python -m otoku check-sources       # 情報源の疎通と robots.txt を確認（--report で #ログ に稼働報告）
```

どのコマンドも `--dry-run` で、Discord への送信と DB への書き込みをせずに結果を標準出力に出す。

cron の例は [crontab.example](crontab.example)。

- 設定は `config/config.yaml`（上限・閾値・キーワードなど）、情報源は `config/sources.yaml`、AIへの指示は `config/prompts/extract.md`。
- データは `data/`（`otoku.db`、`logs/`、ロックファイル、#ログ に送れなかったメッセージ）。

## テスト

```sh
.venv/bin/python -m pytest
```

外部への通信（取得・Gemini・Discord）はすべて偽物に置き換え、`tests/fixtures/` の保存データで動かす。

## 進み具合

| フェーズ | 内容 | 状態 |
|---|---|---|
| 0 | 情報源の検証（[docs/sources_review.md](docs/sources_review.md)） | 済み |
| 1 | RSS・JSON収集 → ルール → AI構造化 → 検証 → #ログ | 済み |
| 2 | スコア・上限・静音時間・#行動 | 済み |
| 3 | HTML差分・サイトマップ、グルーピング | 済み |
| 4 | リアクション、重み調整、締切リマインド、週次報告（＋check-sources・稼働報告） | 実装済み（確認待ち） |
