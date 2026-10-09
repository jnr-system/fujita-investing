"""設定・.env の読み込み。"""
import argparse

from otoku.cli import cmd_collect
from otoku.models import Env, load_env, load_sources, parse_jst

from .conftest import ROOT


def test_env_reads_only_dotenv_file(tmp_path, monkeypatch):
    p = tmp_path / ".env"
    p.write_text('GEMINI_API_KEY="abc"\nCONTACT=me@example.invalid   # 連絡先\nDISCORD_CHANNEL_LOG=\n# コメント\n',
                 encoding="utf-8")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "from-shell")  # シェルの環境変数は使わない
    env = load_env(p)
    assert env.gemini_api_key == "abc"
    assert env.contact == "me@example.invalid"
    assert env.discord_channel_log == "" and env.discord_bot_token == ""


def test_missing_env_file_gives_empty_values(tmp_path):
    assert load_env(tmp_path / ".env") == Env()


def test_real_run_requires_keys_and_contact(cfg, capsys):
    code = cmd_collect(argparse.Namespace(dry_run=False), cfg, [], Env(gemini_api_key="k"))
    assert code == 2
    err = capsys.readouterr().err
    assert "DISCORD_BOT_TOKEN" in err and "CONTACT" in err


def test_project_sources_yaml_loads():
    sources = load_sources(ROOT / "config" / "sources.yaml")
    assert any(s.id == "prtimes_all" and s.scope == ["A", "B"] for s in sources)
    assert all(s.url.startswith("http") for s in sources if s.enabled)


def test_parse_jst():
    assert parse_jst("2026-10-15").isoformat() == "2026-10-15T00:00:00+09:00"
    assert parse_jst("2026-10-15", end_of_day=True).isoformat() == "2026-10-15T23:59:00+09:00"
    assert parse_jst("2026-10-12 23:59:00").isoformat() == "2026-10-12T23:59:00+09:00"
    assert parse_jst("2026-10-12T14:59:00Z").isoformat() == "2026-10-12T14:59:00+00:00"


def test_phase1_db_gets_first_come_column(tmp_path):
    import sqlite3

    from otoku.db import SCHEMA, Store
    p = tmp_path / "old.db"
    conn = sqlite3.connect(p)
    conn.executescript(SCHEMA.replace("  first_come INTEGER,\n", ""))  # フェーズ1の形
    conn.close()
    ro = Store(p, dry_run=True)  # dry-run は書き換えずに読める
    assert ro.candidates() == []
    ro.close()
    s = Store(p)
    assert "first_come" in {r[1] for r in s.conn.execute("PRAGMA table_info(items)")}
    s.close()


def test_lock_waits_for_the_other_run(tmp_path):
    import fcntl

    from otoku.cli import _lock
    p = tmp_path / "otoku.lock"
    holder = open(p, "w")
    fcntl.flock(holder, fcntl.LOCK_EX)
    waited = []

    def sleep(s):
        waited.append(s)
        if len(waited) == 3:  # 3秒後に先の実行が終わる
            holder.close()

    f = _lock(p, 10, sleep=sleep)
    assert f is not None and len(waited) == 3
    f.close()
    holder2 = open(p, "w")
    fcntl.flock(holder2, fcntl.LOCK_EX)
    assert _lock(p, 0, sleep=lambda s: None) is None  # 待つ時間が尽きたら None
    holder2.close()


def test_real_send_requires_discord_settings(cfg, capsys):
    from otoku.cli import cmd_send
    code = cmd_send(argparse.Namespace(dry_run=False, urgent_only=False), cfg, Env(discord_bot_token="t"))
    assert code == 2
    assert "DISCORD_CHANNEL_ACTION" in capsys.readouterr().err
