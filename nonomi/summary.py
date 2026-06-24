"""集計。日次／project別／作業別を表で。"""

from __future__ import annotations

from collections import OrderedDict
from typing import Dict, List, Optional, Tuple

from . import csv_io, validate


def _completed(rows: List[Dict[str, str]], month: Optional[str]) -> List[Dict[str, str]]:
    out = []
    for r in rows:
        if not (r.get("work_hours") or "").strip():
            continue  # 進行中は集計に含めない
        if month and not r.get("date", "").startswith(month):
            continue
        out.append(r)
    return out


def _hours(r: Dict[str, str]) -> float:
    try:
        return float(r.get("work_hours") or 0)
    except ValueError:
        return 0.0


def _work_kind(r: Dict[str, str]) -> str:
    """memo 先頭の括弧前を作業種別として拾う（動画制作/事務作業 など）。"""
    memo = (r.get("memo") or "").strip()
    if memo.startswith("動画制作"):
        return "動画制作"
    if memo.startswith("事務作業"):
        return "事務作業"
    return "その他"


def _aggregate(rows, keyfn) -> "OrderedDict[str, float]":
    acc: "OrderedDict[str, float]" = OrderedDict()
    for r in rows:
        k = keyfn(r)
        acc[k] = acc.get(k, 0.0) + _hours(r)
    return acc


def _table(title: str, data: "OrderedDict[str, float]", key_header: str) -> str:
    lines = [f"### {title}", f"| {key_header} | 時間(h) |", "|---|---|"]
    total = 0.0
    for k, v in data.items():
        lines.append(f"| {k} | {v:.2f} |")
        total += v
    lines.append(f"| **合計** | **{total:.2f}** |")
    return "\n".join(lines)


def build(path=None, month: Optional[str] = None) -> str:
    rows = csv_io.read_rows(path)
    target = _completed(rows, month)
    header = f"## 集計{f'（{month}）' if month else ''}"
    if not target:
        return header + "\n\nまだ集計できる完了セッションがありません。"

    daily = _aggregate(target, lambda r: r.get("date", "?"))
    by_project = _aggregate(target, lambda r: r.get("project", "?"))
    by_kind = _aggregate(target, _work_kind)

    parts = [
        header,
        _table("日次", daily, "date"),
        _table("project別", by_project, "project"),
        _table("作業別", by_kind, "種別"),
    ]
    unc = validate.unclassified(target)
    if unc:
        parts.append(f"> 未分類が {len(unc)} 件あります。あとでそっと直しましょうね。")
    return "\n\n".join(parts)
