"""CSV 入出力。過去行の改変を「仕組み」で禁止する追記重視レイヤ。

許されるのは 2 つだけ:
  1. 新しい行を末尾に足す（append_row）
  2. 進行中（end が空）の 1 行だけ、end/work_hours の空欄を埋める（fill_open_session）

すでに完了している行（end が埋まっている行）は、決して書き換えません。
"""

from __future__ import annotations

import csv
from typing import Dict, List, Optional

from . import config


def read_rows(path=None) -> List[Dict[str, str]]:
    """CSV を辞書のリストで読み込む。ファイルが無ければ空リスト。"""
    path = path or config.CSV_PATH
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write_all(rows: List[Dict[str, str]], path=None) -> None:
    """内部専用。全行を書き出す（追記/空欄補完の結果反映にのみ使う）。"""
    path = path or config.CSV_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=config.COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({c: row.get(c, "") for c in config.COLUMNS})


def open_session_index(rows: List[Dict[str, str]]) -> Optional[int]:
    """end が空＝進行中セッションの行番号。無ければ None。複数あれば例外。"""
    open_idx = [i for i, r in enumerate(rows) if not (r.get("end") or "").strip()]
    if not open_idx:
        return None
    if len(open_idx) > 1:
        raise ValueError(
            f"進行中セッションが {len(open_idx)} 件あります。先にお疲れ（clock-out）してください。"
        )
    return open_idx[0]


def append_row(row: Dict[str, str], path=None) -> None:
    """新しい行を末尾に追記する（既存行は一切触らない）。"""
    rows = read_rows(path)
    if open_session_index(rows) is not None:
        raise ValueError("まだ進行中のセッションがあります。先にお疲れ（clock-out）してください。")
    rows.append({c: row.get(c, "") for c in config.COLUMNS})
    _write_all(rows, path)


def fill_open_session(end: str, work_hours: str, path=None) -> Dict[str, str]:
    """進行中の 1 行だけ、空の end/work_hours を埋める。完了済み行は守る。"""
    rows = read_rows(path)
    idx = open_session_index(rows)
    if idx is None:
        raise ValueError("進行中のセッションがありません。先に始める（clock-in）してください。")
    row = rows[idx]
    # 念のため二重ガード: 完了済みの値は上書きしない
    if (row.get("end") or "").strip():
        raise ValueError("この行はすでに完了しています。書き換えはしません。")
    row["end"] = end
    row["work_hours"] = work_hours
    _write_all(rows, path)
    return row
