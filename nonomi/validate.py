"""検証。書式・整合性チェックと「未分類」の正直なレポート。

過去を勝手に直したりはしません。おかしな点を見つけて、そっとお知らせするだけ。
"""

from __future__ import annotations

import re
from typing import Dict, List

from . import clock, config, csv_io

_HM = re.compile(r"^\d{2}:\d{2}$")
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# project は 2 値のみ: video:<slug> / youtube
_PROJECT = re.compile(r"^(video:[A-Za-z0-9._-]+|youtube)$")


def validate_rows(rows: List[Dict[str, str]]) -> List[str]:
    """書式・整合性の問題点を文章で返す（空なら問題なし）。"""
    problems: List[str] = []
    for i, r in enumerate(rows, start=1):
        loc = f"{i}行目({r.get('date','?')} {r.get('memo','')})"

        if not _DATE.match(r.get("date", "")):
            problems.append(f"{loc}: date の書式が変です。")
            continue
        if r.get("day") != config.jp_weekday(r["date"]):
            problems.append(f"{loc}: day が date と一致しません。")
        if (r.get("channel") or "").strip() not in config.CHANNEL_KEYS:
            problems.append(
                f"{loc}: channel が未設定/不明です（{r.get('channel')!r}）。"
            )
        if not _HM.match(r.get("start", "")):
            problems.append(f"{loc}: start の時刻書式が変です。")

        end = (r.get("end") or "").strip()
        if not end:
            continue  # 進行中セッション（未締め）はここまで
        if not _HM.match(end):
            problems.append(f"{loc}: end の時刻書式が変です。")
            continue
        expected = clock.compute_work_hours(r["start"], end)
        if (r.get("work_hours") or "").strip() != expected:
            problems.append(
                f"{loc}: work_hours が end-start と合いません（記録={r.get('work_hours')} / 計算={expected}）。"
            )
    return problems


def unclassified(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """project が 2 値ルールから外れている＝未分類の行。"""
    return [r for r in rows if not _PROJECT.match((r.get("project") or "").strip())]


def report(path=None) -> str:
    """人にやさしい検証レポート文字列を返す。"""
    rows = csv_io.read_rows(path)
    lines: List[str] = []
    problems = validate_rows(rows)
    unc = unclassified(rows)

    if not problems and not unc:
        lines.append("記録はぜんぶ整っていますよ。安心してくださいね。")
    if problems:
        lines.append(f"気になる点が {len(problems)} 件ありました：")
        lines.extend(f"  ・{p}" for p in problems)
    if unc:
        lines.append(f"未分類が {len(unc)} 件ありますね（project が video:<slug>/youtube 以外）：")
        lines.extend(f"  ・{r.get('date')} {r.get('memo')}（project={r.get('project')}）" for r in unc)
    return "\n".join(lines)
