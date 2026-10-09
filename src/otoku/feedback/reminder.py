"""8.10 締切リマインド：⏰ が付いたものだけ、締切の before_hours 時間前に #行動 へ1回だけ（元メッセージへの返信）。

締切が不明なものはリマインドしない。✅ も付いているもの（応募済み）はしない（2026-10-09 ユーザー判断）。
リマインドは daily_cap に数えない。
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, TextIO

from ..db import Store
from ..notify.discord import DiscordClient, DiscordError
from ..notify.format import remind_message


@dataclass
class RemindResult:
    sent: list[int] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def remind(store: Store, client: Optional[DiscordClient], channel_id: str, now: datetime, before_hours: float,
           out: TextIO = sys.stdout) -> RemindResult:
    """client が None なら dry-run（送らずに標準出力へ）。"""
    res = RemindResult()
    for group_id, message_id, items in store.remind_targets(now, before_hours):
        text = remind_message(items, before_hours)
        if client is None:
            print("\n".join(f"#行動（返信） {line}" for line in text.splitlines()), file=out)
            res.sent.append(group_id)
            continue
        try:
            reply_id = client.post_message(channel_id, text, suppress_embeds=True, reply_to=message_id)
        except DiscordError as e:  # 送れなかったら記録しない → 次回もう一度
            res.errors.append(f"group {group_id}: {e}")
            continue
        store.add_notification(group_id, reply_id, now, "remind")
        store.commit()
        res.sent.append(group_id)
    return res
