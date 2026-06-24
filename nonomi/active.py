"""進行中の動画案件（active.md・最大3スロット）の読み書き。

事務作業（project=youtube）はスロットを使いません。動画案件だけが対象です。
"""

from __future__ import annotations

from typing import Dict, List, Optional

from . import config

MAX_SLOTS = 3
EMPTY = "（空き）"
_HEADER = "# 進行中の動画案件（最大3スロット）"


def _empty_slot(n: int) -> Dict[str, str]:
    return {"slot": str(n), "slug": EMPTY, "name": "", "stage": "", "last": ""}


def load(path=None) -> List[Dict[str, str]]:
    """3 スロットを必ず返す（足りなければ空きで補う）。"""
    path = path or config.ACTIVE_PATH
    slots: List[Dict[str, str]] = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) < 5 or cells[0] in ("slot", "") or set(cells[0]) <= set("-"):
                continue
            slots.append(
                {
                    "slot": cells[0],
                    "slug": cells[1],
                    "name": cells[2],
                    "stage": cells[3],
                    "last": cells[4],
                }
            )
    # 3 スロットに整える
    while len(slots) < MAX_SLOTS:
        slots.append(_empty_slot(len(slots) + 1))
    return slots[:MAX_SLOTS]


def save(slots: List[Dict[str, str]], path=None) -> None:
    path = path or config.ACTIVE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        _HEADER,
        "",
        "| slot | slug | 通称 | 現在の工程 | 最終作業日 |",
        "|------|--------|--------|------------|------------|",
    ]
    for s in slots:
        lines.append(
            f"| {s['slot']} | {s.get('slug') or EMPTY} | {s.get('name','')} | {s.get('stage','')} | {s.get('last','')} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _is_empty(slot: Dict[str, str]) -> bool:
    return not slot.get("slug") or slot["slug"] == EMPTY


def find(slug: str, slots: Optional[List[Dict[str, str]]] = None) -> Optional[int]:
    slots = slots if slots is not None else load()
    for i, s in enumerate(slots):
        if s.get("slug") == slug:
            return i
    return None


def add(slug: str, name: str, stage: str, last: str, path=None) -> List[Dict[str, str]]:
    """空きスロットに新案件を追加。空きが無ければ例外。"""
    slots = load(path)
    if find(slug, slots) is not None:
        raise ValueError(f"案件 {slug} はすでに進行中です。")
    for i, s in enumerate(slots):
        if _is_empty(s):
            slots[i] = {"slot": str(i + 1), "slug": slug, "name": name, "stage": stage, "last": last}
            save(slots, path)
            return slots
    raise ValueError("3スロットが埋まっています。どれかを一区切りにしてからにしませんか？")


def touch(slug: str, stage: Optional[str], last: str, path=None) -> List[Dict[str, str]]:
    """既存案件の工程・最終作業日を更新。"""
    slots = load(path)
    i = find(slug, slots)
    if i is None:
        raise ValueError(f"案件 {slug} は進行中スロットにありません。")
    if stage:
        slots[i]["stage"] = stage
    slots[i]["last"] = last
    save(slots, path)
    return slots


def close(slug: str, path=None) -> List[Dict[str, str]]:
    """案件を完成扱いにしてスロットを空ける。"""
    slots = load(path)
    i = find(slug, slots)
    if i is None:
        raise ValueError(f"案件 {slug} は進行中スロットにありません。")
    slots[i] = _empty_slot(i + 1)
    save(slots, path)
    return slots
