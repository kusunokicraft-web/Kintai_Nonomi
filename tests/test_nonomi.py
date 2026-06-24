"""ノノミの「数字を大切にする約束」を守れているかのテスト。"""

from __future__ import annotations

from datetime import datetime

import pytest

from nonomi import clock, config, csv_io, summary, validate
from nonomi import active as active_mod


@pytest.fixture(autouse=True)
def tmp_csv(tmp_path, monkeypatch):
    csv_path = tmp_path / "kintai.csv"
    active_path = tmp_path / "active.md"
    monkeypatch.setattr(config, "CSV_PATH", csv_path)
    monkeypatch.setattr(config, "ACTIVE_PATH", active_path)
    return csv_path


def _at(date, hm):
    d = datetime.strptime(f"{date} {hm}", "%Y-%m-%d %H:%M")
    return d.replace(tzinfo=config.TOKYO)


def test_clock_in_creates_open_row():
    row = clock.clock_in("video:foo", "動画制作（フー・①企画）", when=_at("2026-06-24", "10:00"))
    assert row["day"] == "水"  # 2026-06-24 は水曜
    rows = csv_io.read_rows()
    assert len(rows) == 1
    assert rows[0]["end"] == "" and rows[0]["work_hours"] == ""


def test_clock_out_fills_work_hours():
    clock.clock_in("video:foo", "動画制作（フー・①企画）", when=_at("2026-06-24", "10:00"))
    row = clock.clock_out(when=_at("2026-06-24", "12:30"))
    assert row["end"] == "12:30"
    assert row["work_hours"] == "2.50"


def test_cannot_double_clock_in():
    clock.clock_in("video:foo", "動画制作（フー・①企画）", when=_at("2026-06-24", "10:00"))
    with pytest.raises(ValueError):
        clock.clock_in("video:bar", "動画制作（バー・①企画）", when=_at("2026-06-24", "11:00"))


def test_clock_out_without_open_raises():
    with pytest.raises(ValueError):
        clock.clock_out(when=_at("2026-06-24", "12:30"))


def test_past_rows_never_rewritten():
    clock.clock_in("video:foo", "動画制作（フー・①企画）", when=_at("2026-06-24", "10:00"))
    clock.clock_out(when=_at("2026-06-24", "11:00"))
    before = csv_io.read_rows()[0].copy()
    # 新しいセッションを足しても、過去行はそのまま
    clock.clock_in("youtube", "事務作業（連絡）", when=_at("2026-06-24", "13:00"))
    after = csv_io.read_rows()[0]
    assert after == before


def test_overnight_work_hours():
    assert clock.compute_work_hours("23:00", "01:30") == "2.50"


def test_validate_detects_unclassified():
    clock.clock_in("private", "私用（買い物）", when=_at("2026-06-24", "10:00"))
    rows = csv_io.read_rows()
    assert len(validate.unclassified(rows)) == 1


def test_summary_aggregates_by_project():
    clock.clock_in("video:foo", "動画制作（フー・①企画）", when=_at("2026-06-24", "10:00"))
    clock.clock_out(when=_at("2026-06-24", "12:00"))
    clock.clock_in("youtube", "事務作業（連絡）", when=_at("2026-06-24", "13:00"))
    clock.clock_out(when=_at("2026-06-24", "14:00"))
    out = summary.build()
    assert "video:foo" in out and "youtube" in out
    assert "3.00" in out  # 合計 2.0 + 1.0


def test_active_slots():
    active_mod.add("foo", "フー", "①企画", "2026-06-24")
    active_mod.add("bar", "バー", "①企画", "2026-06-24")
    slots = active_mod.load()
    assert slots[0]["slug"] == "foo" and slots[1]["slug"] == "bar"
    active_mod.touch("foo", "②撮影", "2026-06-25")
    assert active_mod.load()[0]["stage"] == "②撮影"
    active_mod.close("foo")
    assert active_mod.find("foo") is None


def test_active_slot_limit():
    active_mod.add("a", "A", "①", "2026-06-24")
    active_mod.add("b", "B", "①", "2026-06-24")
    active_mod.add("c", "C", "①", "2026-06-24")
    with pytest.raises(ValueError):
        active_mod.add("d", "D", "①", "2026-06-24")
