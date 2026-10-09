"""SQLite（7章）。日時はUTCのISO 8601文字列で保存する。

7章からの追加（2026-10-09 ユーザー確認済み）
- items.status に waiting（開始前の待機状態、8.4）
- items に first_come（先着かどうか。AI出力に追加したもの、8.6・8.7）
- source_stats に last_fetched_at・etag・last_modified（6.5 の最短間隔と条件付きGET）

groups の key は 8.5 の「scope:正規化した商品名」。商品名が空でまとめられない候補は、送るときに key を item:<id> にする。
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from .models import RawItem, from_iso, to_iso

SCHEMA = """
CREATE TABLE IF NOT EXISTS raw_items(
  id INTEGER PRIMARY KEY,
  source_id TEXT NOT NULL,
  url TEXT NOT NULL,
  url_hash TEXT NOT NULL UNIQUE,
  title TEXT,
  body TEXT,
  fetched_at TEXT NOT NULL,
  content_hash TEXT
);
CREATE TABLE IF NOT EXISTS items(
  id INTEGER PRIMARY KEY,
  raw_item_id INTEGER NOT NULL REFERENCES raw_items(id),
  scope TEXT,
  kind TEXT NOT NULL,
  genre TEXT,
  product TEXT,
  organizer TEXT,
  start_at TEXT,
  deadline_at TEXT,
  conditions TEXT,
  cost_yen INTEGER,
  benefit_yen INTEGER,
  apply_url TEXT,
  first_come INTEGER,
  confidence REAL,
  exclude_reason TEXT,
  group_id INTEGER,
  score REAL,
  status TEXT NOT NULL CHECK (status IN ('candidate', 'sent', 'dropped', 'expired', 'waiting')),
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS groups(
  id INTEGER PRIMARY KEY,
  scope TEXT,
  key TEXT UNIQUE,
  title TEXT,
  best_score REAL,
  discord_message_id TEXT,
  first_sent_at TEXT,
  updated_at TEXT
);
CREATE TABLE IF NOT EXISTS notifications(
  id INTEGER PRIMARY KEY,
  group_id INTEGER,
  channel TEXT,
  discord_message_id TEXT,
  sent_at TEXT,
  kind TEXT
);
CREATE TABLE IF NOT EXISTS feedback(
  id INTEGER PRIMARY KEY,
  group_id INTEGER,
  reaction TEXT,
  recorded_at TEXT
);
CREATE TABLE IF NOT EXISTS source_stats(
  source_id TEXT PRIMARY KEY,
  sent_count INTEGER NOT NULL DEFAULT 0,
  applied_count INTEGER NOT NULL DEFAULT 0,
  reject_count INTEGER NOT NULL DEFAULT 0,
  fail_streak INTEGER NOT NULL DEFAULT 0,
  paused_until TEXT,
  weight REAL NOT NULL DEFAULT 0,
  last_fetched_at TEXT,
  etag TEXT,
  last_modified TEXT
);
"""


@dataclass
class SourceState:
    fail_streak: int = 0
    paused_until: Optional[datetime] = None
    last_fetched_at: Optional[datetime] = None
    etag: Optional[str] = None
    last_modified: Optional[str] = None


@dataclass
class Candidate:
    id: int
    source_id: str
    title: str
    url: str
    body: str
    scope: Optional[str]
    kind: str
    genre: Optional[str]
    product: Optional[str]
    organizer: Optional[str]
    start_at: Optional[datetime]
    deadline_at: Optional[datetime]
    conditions: Optional[str]
    cost_yen: Optional[int]
    benefit_yen: Optional[int]
    apply_url: Optional[str]
    first_come: bool
    group_id: Optional[int] = None
    group_message_id: Optional[str] = None  # グループが #行動 に送信済みなら、そのメッセージID
    score: Optional[float] = None
    urgent: bool = False


@dataclass
class WaitingItem:
    id: int
    title: str
    source_id: str
    start_at: Optional[datetime]
    deadline_at: Optional[datetime]


class Store:
    """dry_run のときは読むだけで、書き込みは一切しない（DBファイルも作らない）。"""

    def __init__(self, path: Path, dry_run: bool = False):
        self.dry_run = dry_run
        self._seen_in_run: set[str] = set()
        if dry_run:
            if path.exists():
                self.conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
            else:
                self.conn = sqlite3.connect(":memory:")
                self.conn.executescript(SCHEMA)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            self.conn = sqlite3.connect(path)
            self.conn.executescript(SCHEMA)
            self._migrate()
        self.conn.row_factory = sqlite3.Row
        self._item_cols = {r[1] for r in self.conn.execute("PRAGMA table_info(items)")}

    def _migrate(self) -> None:
        """フェーズ1で作ったDBに、あとから足した列を加える。"""
        cols = {r[1] for r in self.conn.execute("PRAGMA table_info(items)")}
        if "first_come" not in cols:
            self.conn.execute("ALTER TABLE items ADD COLUMN first_come INTEGER")
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def commit(self) -> None:
        if not self.dry_run:
            self.conn.commit()

    # ---- raw_items / items

    def seen(self, url_hash: str) -> bool:
        if url_hash in self._seen_in_run:
            return True
        return self.conn.execute("SELECT 1 FROM raw_items WHERE url_hash = ?", (url_hash,)).fetchone() is not None

    def add_raw(self, raw: RawItem, url_hash: str, content_hash: str, fetched_at: datetime) -> Optional[int]:
        self._seen_in_run.add(url_hash)
        if self.dry_run:
            return None
        cur = self.conn.execute(
            "INSERT INTO raw_items(source_id, url, url_hash, title, body, fetched_at, content_hash) VALUES (?,?,?,?,?,?,?)",
            (raw.source_id, raw.url, url_hash, raw.title, raw.body, to_iso(fetched_at), content_hash))
        return cur.lastrowid

    def add_item(self, raw_item_id: Optional[int], *, scope, kind, status, created_at: datetime, genre=None,
                 product=None, organizer=None, start_at: Optional[datetime] = None,
                 deadline_at: Optional[datetime] = None, conditions=None, cost_yen=None, benefit_yen=None,
                 apply_url=None, first_come=None, confidence=None, exclude_reason=None) -> Optional[int]:
        if self.dry_run:
            return None
        cur = self.conn.execute(
            """INSERT INTO items(raw_item_id, scope, kind, genre, product, organizer, start_at, deadline_at, conditions,
                                 cost_yen, benefit_yen, apply_url, first_come, confidence, exclude_reason, status,
                                 created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (raw_item_id, scope, kind, genre, product, organizer, to_iso(start_at), to_iso(deadline_at), conditions,
             cost_yen, benefit_yen, apply_url, None if first_come is None else int(first_come), confidence,
             exclude_reason, status, to_iso(created_at)))
        return cur.lastrowid

    def assign_group(self, item_id: Optional[int], scope: str, key: str, title: str, at: datetime,
                     source_id: str = "") -> Optional[int]:
        """8.5：同じ key のグループに入れる（なければ作る）。
        B（還元・無料）は、同じ情報源のURL違いは別の企画とみなしてまとめない（「飲料1本もらえるキャンペーン」のように
        同じ名前で期間や対象の違う企画があるため）。まとめるのは別々の情報源から同じ企画が来たときだけ。"""
        if self.dry_run or item_id is None:
            return None
        if scope == "B" and self.conn.execute(
                "SELECT 1 FROM items i JOIN raw_items r ON r.id = i.raw_item_id JOIN groups g ON g.id = i.group_id "
                "WHERE g.key = ? AND r.source_id = ? AND i.id != ?", (key, source_id, item_id)).fetchone():
            key = f"{key}#item:{item_id}"
        self.conn.execute("INSERT OR IGNORE INTO groups(scope, key, title, updated_at) VALUES (?,?,?,?)",
                          (scope, key, title, to_iso(at)))
        group_id = self.conn.execute("SELECT id FROM groups WHERE key = ?", (key,)).fetchone()[0]
        self.conn.execute("UPDATE items SET group_id = ? WHERE id = ?", (group_id, item_id))
        return group_id

    def waiting_items(self) -> list[WaitingItem]:
        rows = self.conn.execute(
            """SELECT i.id, r.title, r.source_id, i.start_at, i.deadline_at
               FROM items i JOIN raw_items r ON r.id = i.raw_item_id WHERE i.status = 'waiting'""").fetchall()
        return [WaitingItem(r["id"], r["title"], r["source_id"], from_iso(r["start_at"]), from_iso(r["deadline_at"]))
                for r in rows]

    def set_item_status(self, item_id: int, status: str, reason: Optional[str] = None) -> None:
        if self.dry_run:
            return
        if reason is None:
            self.conn.execute("UPDATE items SET status = ? WHERE id = ?", (status, item_id))
        else:
            self.conn.execute("UPDATE items SET status = ?, exclude_reason = ? WHERE id = ?", (status, reason, item_id))

    # ---- 送信（フェーズ2）

    _CANDIDATE_SQL = """
        SELECT i.id, r.source_id, r.title, r.url, r.body, i.scope, i.kind, i.genre, i.product, i.organizer,
               i.start_at, i.deadline_at, i.conditions, i.cost_yen, i.benefit_yen, i.apply_url,
               {first_come} AS first_come, i.group_id, g.discord_message_id AS group_message_id, i.score
        FROM items i JOIN raw_items r ON r.id = i.raw_item_id LEFT JOIN groups g ON g.id = i.group_id
        WHERE {where} ORDER BY i.id"""

    def _candidates(self, where: str, params=()) -> list[Candidate]:
        first_come = "i.first_come" if "first_come" in self._item_cols else "NULL"  # dry-run で古いDBを読むとき
        rows = self.conn.execute(self._CANDIDATE_SQL.format(first_come=first_come, where=where), params).fetchall()
        return [Candidate(r["id"], r["source_id"], r["title"] or "", r["url"], r["body"] or "", r["scope"], r["kind"],
                          r["genre"], r["product"], r["organizer"], from_iso(r["start_at"]), from_iso(r["deadline_at"]),
                          r["conditions"], r["cost_yen"], r["benefit_yen"], r["apply_url"],
                          bool(r["first_come"]) or r["kind"] == "refund_first", r["group_id"], r["group_message_id"],
                          r["score"])
                for r in rows]

    def candidates(self) -> list[Candidate]:
        return self._candidates("i.status = 'candidate'")

    def sent_in_group(self, group_id: int) -> list[Candidate]:
        return self._candidates("i.status = 'sent' AND i.group_id = ?", (group_id,))

    def set_score(self, item_id: int, score: float) -> None:
        if not self.dry_run:
            self.conn.execute("UPDATE items SET score = ? WHERE id = ?", (score, item_id))

    def count_sent(self, start: datetime, end: datetime) -> int:
        """#行動 への新規通知の数（リマインドとメッセージの編集は数えない）。"""
        return self.conn.execute(
            "SELECT COUNT(*) FROM notifications WHERE channel = 'action' AND kind = 'new' AND sent_at >= ? AND sent_at < ?",
            (to_iso(start), to_iso(end))).fetchone()[0]

    def mark_sent(self, items: list[Candidate], message_id: str, at: datetime, score: float) -> None:
        """同じグループの候補をまとめて1通として記録する（8.5・8.7）。"""
        if self.dry_run:
            return
        group_id = next((c.group_id for c in items if c.group_id), None)
        if group_id is None:
            first = min(items, key=lambda c: c.id)
            group_id = self.conn.execute(
                "INSERT INTO groups(scope, key, title, updated_at) VALUES (?,?,?,?)",
                (first.scope, f"item:{first.id}", first.product or first.title, to_iso(at))).lastrowid
        self.conn.execute("UPDATE groups SET best_score = ?, discord_message_id = ?, first_sent_at = ?, updated_at = ? "
                          "WHERE id = ?", (score, message_id, to_iso(at), to_iso(at), group_id))
        for c in items:
            self.conn.execute("UPDATE items SET status = 'sent', group_id = ?, score = ? WHERE id = ?",
                              (group_id, c.score, c.id))
        self.conn.execute("INSERT INTO notifications(group_id, channel, discord_message_id, sent_at, kind) "
                          "VALUES (?, 'action', ?, ?, 'new')", (group_id, message_id, to_iso(at)))
        for source_id in {c.source_id for c in items}:
            self.conn.execute("INSERT OR IGNORE INTO source_stats(source_id) VALUES (?)", (source_id,))
            self.conn.execute("UPDATE source_stats SET sent_count = sent_count + 1 WHERE source_id = ?", (source_id,))

    def mark_updated(self, items: list[Candidate], group_id: int, message_id: str, at: datetime) -> None:
        """送信済みのメッセージを編集して、店舗を追記したことを記録する（上限には数えない）。"""
        if self.dry_run:
            return
        for c in items:
            self.conn.execute("UPDATE items SET status = 'sent', score = ? WHERE id = ?", (c.score, c.id))
        self.conn.execute("UPDATE groups SET updated_at = ? WHERE id = ?", (to_iso(at), group_id))
        self.conn.execute("INSERT INTO notifications(group_id, channel, discord_message_id, sent_at, kind) "
                          "VALUES (?, 'action', ?, ?, 'update')", (group_id, message_id, to_iso(at)))

    # ---- フィードバック・リマインド・報告（フェーズ4）

    def sent_groups(self, since: datetime) -> list[tuple[int, str]]:
        """since 以降に #行動 へ送ったグループ（id, メッセージID）。"""
        return [(r[0], r[1]) for r in self.conn.execute(
            "SELECT id, discord_message_id FROM groups WHERE discord_message_id IS NOT NULL AND first_sent_at >= ? "
            "ORDER BY id", (to_iso(since),))]

    def feedback_of(self, group_id: int) -> set[str]:
        return {r[0] for r in self.conn.execute("SELECT reaction FROM feedback WHERE group_id = ?", (group_id,))}

    def set_feedback(self, group_id: int, reactions: set[str], at: datetime) -> tuple[set[str], set[str]]:
        """いま付いているリアクションに合わせる（外されたものは消す）。(付いたもの, 外されたもの) を返す。"""
        current = self.feedback_of(group_id)
        added, removed = reactions - current, current - reactions
        if not self.dry_run:
            for r in added:
                self.conn.execute("INSERT INTO feedback(group_id, reaction, recorded_at) VALUES (?,?,?)",
                                  (group_id, r, to_iso(at)))
            for r in removed:
                self.conn.execute("DELETE FROM feedback WHERE group_id = ? AND reaction = ?", (group_id, r))
        return added, removed

    def refresh_feedback_counts(self) -> None:
        """source_stats の applied_count・reject_count を feedback から数え直す（グループ単位）。"""
        if self.dry_run:
            return
        for col, reaction in (("applied_count", "applied"), ("reject_count", "reject")):
            self.conn.execute(
                f"""UPDATE source_stats SET {col} = (
                      SELECT COUNT(DISTINCT f.group_id) FROM feedback f
                      JOIN items i ON i.group_id = f.group_id JOIN raw_items r ON r.id = i.raw_item_id
                      WHERE r.source_id = source_stats.source_id AND i.status = 'sent' AND f.reaction = ?)""",
                (reaction,))

    def sources_with_sent(self) -> list[str]:
        return [r[0] for r in self.conn.execute(
            "SELECT DISTINCT r.source_id FROM items i JOIN raw_items r ON r.id = i.raw_item_id "
            "WHERE i.status = 'sent' ORDER BY r.source_id")]

    def recent_feedback(self, source_id: str, window: int) -> list[set[str]]:
        """その情報源の候補を含む直近 window 件の通知（グループ）ごとのリアクション。"""
        groups = [r[0] for r in self.conn.execute(
            """SELECT g.id FROM groups g WHERE g.first_sent_at IS NOT NULL AND EXISTS (
                 SELECT 1 FROM items i JOIN raw_items r ON r.id = i.raw_item_id
                 WHERE i.group_id = g.id AND i.status = 'sent' AND r.source_id = ?)
               ORDER BY g.first_sent_at DESC, g.id DESC LIMIT ?""", (source_id, window))]
        return [self.feedback_of(g) for g in groups]

    def set_weight(self, source_id: str, weight: float) -> None:
        self._upsert_source(source_id, weight=weight)

    def remind_targets(self, now: datetime, before_hours: float) -> list[tuple[int, str, list[Candidate]]]:
        """⏰ が付いていて ✅ がなく、まだリマインドしておらず、締切（グループ内で最短）まで before_hours 以内のもの。"""
        out = []
        rows = self.conn.execute(
            """SELECT g.id, g.discord_message_id FROM groups g
               WHERE g.discord_message_id IS NOT NULL
                 AND EXISTS (SELECT 1 FROM feedback f WHERE f.group_id = g.id AND f.reaction = 'later')
                 AND NOT EXISTS (SELECT 1 FROM feedback f WHERE f.group_id = g.id AND f.reaction = 'applied')
                 AND NOT EXISTS (SELECT 1 FROM notifications n WHERE n.group_id = g.id AND n.kind = 'remind')
               ORDER BY g.id""").fetchall()
        for group_id, message_id in rows:
            items = self.sent_in_group(group_id)
            deadlines = [c.deadline_at for c in items if c.deadline_at]
            if deadlines and now < min(deadlines) <= now + timedelta(hours=before_hours):
                out.append((group_id, message_id, items))
        return out

    def add_notification(self, group_id: int, message_id: str, at: datetime, kind: str) -> None:
        if not self.dry_run:
            self.conn.execute("INSERT INTO notifications(group_id, channel, discord_message_id, sent_at, kind) "
                              "VALUES (?, 'action', ?, ?, ?)", (group_id, message_id, to_iso(at), kind))

    def period_counts(self, start: datetime, end: datetime) -> dict:
        """報告用：期間中の新規取得・AI判定・候補・送信の件数。"""
        rng = (to_iso(start), to_iso(end))
        one = lambda sql: self.conn.execute(sql, rng).fetchone()[0]  # noqa: E731
        return {
            "new": one("SELECT COUNT(*) FROM raw_items WHERE fetched_at >= ? AND fetched_at < ?"),
            "ai": one("SELECT COUNT(*) FROM items WHERE created_at >= ? AND created_at < ?"),
            # 検証を通ったもの（あとで重複・上限超過で外れたものも含む）
            "candidates": one("SELECT COUNT(*) FROM items WHERE created_at >= ? AND created_at < ? AND "
                              "(status != 'dropped' OR exclude_reason = '重複（通知済み）')"),
            "sent": one("SELECT COUNT(*) FROM notifications WHERE kind = 'new' AND sent_at >= ? AND sent_at < ?"),
        }

    def sent_groups_between(self, start: datetime, end: datetime) -> list[tuple[int, set[str], set[str]]]:
        """期間中に送った通知（グループ）ごとの (id, リアクション, 情報源)。"""
        out = []
        for (group_id,) in self.conn.execute(
                "SELECT group_id FROM notifications WHERE kind = 'new' AND sent_at >= ? AND sent_at < ? ORDER BY id",
                (to_iso(start), to_iso(end))).fetchall():
            sources = {r[0] for r in self.conn.execute(
                "SELECT DISTINCT r.source_id FROM items i JOIN raw_items r ON r.id = i.raw_item_id "
                "WHERE i.group_id = ? AND i.status = 'sent'", (group_id,))}
            out.append((group_id, self.feedback_of(group_id), sources))
        return out

    def source_weight(self, source_id: str) -> float:
        r = self.conn.execute("SELECT weight FROM source_stats WHERE source_id = ?", (source_id,)).fetchone()
        return float(r["weight"]) if r else 0.0

    # ---- source_stats

    def source_state(self, source_id: str) -> SourceState:
        r = self.conn.execute("SELECT * FROM source_stats WHERE source_id = ?", (source_id,)).fetchone()
        if r is None:
            return SourceState()
        return SourceState(r["fail_streak"], from_iso(r["paused_until"]), from_iso(r["last_fetched_at"]),
                           r["etag"], r["last_modified"])

    def _upsert_source(self, source_id: str, **cols) -> None:
        if self.dry_run:
            return
        self.conn.execute("INSERT OR IGNORE INTO source_stats(source_id) VALUES (?)", (source_id,))
        sets = ", ".join(f"{k} = ?" for k in cols)
        self.conn.execute(f"UPDATE source_stats SET {sets} WHERE source_id = ?", (*cols.values(), source_id))

    def mark_fetched(self, source_id: str, at: datetime, etag: Optional[str], last_modified: Optional[str]) -> None:
        self._upsert_source(source_id, last_fetched_at=to_iso(at), etag=etag, last_modified=last_modified,
                            fail_streak=0)

    def reset_fail_streak(self, source_id: str) -> None:
        self._upsert_source(source_id, fail_streak=0)

    def set_fail_streak(self, source_id: str, streak: int) -> None:
        self._upsert_source(source_id, fail_streak=streak)

    def pause(self, source_id: str, until: datetime) -> None:
        # 停止したら連続失敗の数え直し。再開後にまた3回続けて失敗したら、もう一度止めて報告する
        self._upsert_source(source_id, paused_until=to_iso(until), fail_streak=0)
