"""共通設定・時刻ユーティリティ。"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

try:
    from zoneinfo import ZoneInfo

    TOKYO = ZoneInfo("Asia/Tokyo")
except Exception:  # pragma: no cover - zoneinfo は標準だが念のため
    from datetime import timezone, timedelta

    TOKYO = timezone(timedelta(hours=9), name="Asia/Tokyo")

# プロジェクトルート（このファイルの 1 つ上の親）
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
CSV_PATH = DATA_DIR / "kintai.csv"
ACTIVE_PATH = DATA_DIR / "active.md"

# CSV の列（1 セッション＝1 行）
COLUMNS = ["date", "day", "start", "end", "work_hours", "project", "memo"]

# 月=0 … 日=6
JP_WEEKDAYS = ["月", "火", "水", "木", "金", "土", "日"]


def now_tokyo() -> datetime:
    """東京の現在時刻（実測）。"""
    return datetime.now(TOKYO)


def jp_weekday(date_str: str) -> str:
    """'YYYY-MM-DD' から日本語の曜日を返す。"""
    d = datetime.strptime(date_str, "%Y-%m-%d")
    return JP_WEEKDAYS[d.weekday()]
