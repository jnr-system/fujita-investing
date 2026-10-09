"""#行動 と #ログ の書式（8.8）。"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from ..models import fmt_jst

if TYPE_CHECKING:
    from ..db import Candidate

TITLE_MAX = 80


def _short(s: str, n: int = TITLE_MAX) -> str:
    s = " ".join((s or "").split())
    return s if len(s) <= n else s[: n - 1] + "…"


def log_line(status: str, reason: Optional[str], title: str, source_id: str, score: Optional[float] = None) -> str:
    """score はフェーズ2で計算する。まだないときは「-」。"""
    tag = f"{status}: {reason}" if reason else status
    s = "-" if score is None else f"{score:.0f}"
    return f"[{tag}] {_short(title)} / {source_id} / {s}"


def error_line(where: str, message: str) -> str:
    return f"[error] {where}: {_short(message, 200)}"


def paused_line(source_id: str, streak: int, hours: int) -> str:
    return f"[paused] {source_id}: {streak}回続けて取得に失敗したため{hours}時間停止します"


# ---------------------------------------------------------------- #行動（1件3行、装飾なし）

_LABEL = {"refund_first": "先着・全額返金", "refund_all": "全額返金", "free_item": "無料", "free_game": "無料配布",
          "lottery": "抽選"}


def link_for(c: "Candidate") -> str:
    """AIが返した応募URLは、本文かタイトルに実際に書かれているときだけ使う（AIが作ったURLを送らないため）。"""
    if c.apply_url and (c.apply_url == c.url or c.apply_url in c.body or c.apply_url in c.title):
        return c.apply_url
    return c.url


def stores_of(items: list["Candidate"]) -> list[str]:
    """店舗（主催）の一覧。締切の早い順、重複なし。"""
    far = (1, None)
    ordered = sorted(items, key=lambda c: (0, c.deadline_at) if c.deadline_at else far)
    seen: dict[str, str] = {}
    for c in ordered:
        name = (c.organizer or "").strip()
        key = "".join(ch for ch in name.lower() if ch.isalnum())
        if name and key not in seen:
            seen[key] = name
    return list(seen.values())


def action_message(items) -> str:
    """1通分の本文（1件3行、装飾なし）。items は同じグループの候補（1件でもよい）。例：
    【先着・全額返金】◯◯ 新商品（実質0円）
    締切：10/15 23:59　条件：レシート応募、1人1回
    https://example.com/...

    【抽選】◯◯ BOX（定価7,200円）受付中3店
    締切：最短 10/12 16:59　店舗：A、B、C
    https://example.com/...
    """
    items = items if isinstance(items, list) else [items]
    best = max(items, key=lambda c: (c.score or 0.0, -c.id))
    stores = stores_of(items)
    if best.kind == "lottery" and len(stores) >= 2:
        cost = next((c.cost_yen for c in [best] + items if c.cost_yen), None)
        head = f"【抽選】{_short(best.product or best.title, 60)}" + (f"（定価{cost:,}円）" if cost else "") \
            + f"受付中{len(stores)}店"
        dated = [c for c in items if c.deadline_at]
        first = min(dated, key=lambda c: c.deadline_at) if dated else best
        deadline = f"最短 {fmt_jst(first.deadline_at)}" if dated else "不明"
        return "\n".join([head, f"締切：{deadline}　店舗：{_short('、'.join(stores), 80)}", link_for(first)])
    return _single(best)


def _single(c: "Candidate") -> str:
    label = _LABEL.get(c.kind, c.kind)
    if c.kind == "free_item" and c.first_come:
        label = "先着・無料"
    note = None
    if c.kind in ("refund_first", "refund_all"):
        note = "実質0円"
    elif c.kind == "lottery" and c.cost_yen:
        note = f"定価{c.cost_yen:,}円"
    elif c.kind in ("free_item", "free_game") and c.benefit_yen:
        note = f"{c.benefit_yen:,}円相当"
    head = f"【{label}】{_short(c.product or c.title, 60)}" + (f"（{note}）" if note else "")
    deadline = fmt_jst(c.deadline_at) if c.deadline_at else "不明"
    if c.kind == "lottery":
        second = f"締切：{deadline}　店舗：{_short(c.organizer or '不明', 40)}"
    else:
        second = f"締切：{deadline}　条件：{_short(c.conditions or '不明', 60)}"
    return "\n".join([head, second, link_for(c)])


def remind_message(items: list["Candidate"], hours: float = 24) -> str:
    """8.10：元メッセージへの返信として送る。例：
    【締切まで24時間以内】◯◯ 新商品
    締切：10/15 23:59
    https://example.com/...
    """
    best = max(items, key=lambda c: (c.score or 0.0, -c.id))
    dated = [c for c in items if c.deadline_at]
    first = min(dated, key=lambda c: c.deadline_at) if dated else best
    deadline = fmt_jst(first.deadline_at) if dated else "不明"
    return "\n".join([f"【締切まで{hours:g}時間以内】{_short(best.product or best.title, 60)}", f"締切：{deadline}",
                      link_for(first)])

