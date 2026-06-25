"""打刻ロジック。「始める」→起票、「お疲れ」→締め。"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional

from . import config, csv_io


def _parse_hm(value: str) -> datetime:
    return datetime.strptime(value.strip(), "%H:%M")


def compute_work_hours(start: str, end: str) -> str:
    """end-start を小数 2 桁の時間で返す。日跨ぎは +24h で吸収。"""
    s = _parse_hm(start)
    e = _parse_hm(end)
    minutes = (e - s).total_seconds() / 60.0
    if minutes < 0:  # 日付をまたいだ夜更かし作業
        minutes += 24 * 60
    return f"{minutes / 60.0:.2f}"


def clock_in(
    channel: str, project: str, memo: str, when: Optional[datetime] = None
) -> Dict[str, str]:
    """新しいセッションを起票（end/work_hours は空欄）。"""
    when = when or config.now_tokyo()
    date_str = when.strftime("%Y-%m-%d")
    row = {
        "date": date_str,
        "day": config.jp_weekday(date_str),
        "start": when.strftime("%H:%M"),
        "end": "",
        "work_hours": "",
        "channel": channel,
        "project": project,
        "memo": memo,
    }
    csv_io.append_row(row)
    return row


def clock_out(when: Optional[datetime] = None) -> Dict[str, str]:
    """進行中セッションを締める（end/work_hours を記入）。"""
    when = when or config.now_tokyo()
    end = when.strftime("%H:%M")
    rows = csv_io.read_rows()
    idx = csv_io.open_session_index(rows)
    if idx is None:
        raise ValueError("進行中のセッションがありません。")
    start = rows[idx]["start"]
    work_hours = compute_work_hours(start, end)
    return csv_io.fill_open_session(end=end, work_hours=work_hours)
