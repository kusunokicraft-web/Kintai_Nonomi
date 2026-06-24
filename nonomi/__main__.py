"""ノノミ CLI。

  python -m nonomi clock-in  --project video:slug --memo "動画制作（…）"
  python -m nonomi clock-out
  python -m nonomi summary    [--month YYYY-MM]
  python -m nonomi validate
  python -m nonomi status
  python -m nonomi active add   --slug s --name 通称 --stage ①企画
  python -m nonomi active touch  --slug s [--stage ②撮影]
  python -m nonomi active close  --slug s
"""

from __future__ import annotations

import argparse
import sys

from . import active, clock, config, csv_io, summary, validate


def _today() -> str:
    return config.now_tokyo().strftime("%Y-%m-%d")


def cmd_clock_in(a: argparse.Namespace) -> None:
    row = clock.clock_in(project=a.project, memo=a.memo)
    print(f"始めました：{row['date']}({row['day']}) {row['start']}〜  {row['project']} / {row['memo']}")


def cmd_clock_out(a: argparse.Namespace) -> None:
    row = clock.clock_out()
    print(f"お疲れさまでした：{row['start']}〜{row['end']}  {row['work_hours']}h  {row['memo']}")


def cmd_summary(a: argparse.Namespace) -> None:
    print(summary.build(month=a.month))


def cmd_validate(a: argparse.Namespace) -> None:
    print(validate.report())


def cmd_status(a: argparse.Namespace) -> None:
    rows = csv_io.read_rows()
    idx = csv_io.open_session_index(rows)
    if idx is None:
        print("いまは進行中のセッションはありません。")
    else:
        r = rows[idx]
        print(f"進行中：{r['date']}({r['day']}) {r['start']}〜  {r['project']} / {r['memo']}")
    print("\n[進行中の動画案件]")
    for s in active.load():
        print(f"  slot{s['slot']}: {s['slug']}  {s.get('name','')}  {s.get('stage','')}  {s.get('last','')}")


def cmd_active(a: argparse.Namespace) -> None:
    if a.action == "add":
        active.add(slug=a.slug, name=a.name or "", stage=a.stage or "①", last=_today())
    elif a.action == "touch":
        active.touch(slug=a.slug, stage=a.stage, last=_today())
    elif a.action == "close":
        active.close(slug=a.slug)
    cmd_status(a)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="nonomi", description="勤怠記録・集計メイド ノノミ")
    sub = p.add_subparsers(dest="cmd", required=True)

    ci = sub.add_parser("clock-in", help="始める（起票）")
    ci.add_argument("--project", required=True, help="video:<slug> または youtube")
    ci.add_argument("--memo", required=True)
    ci.set_defaults(func=cmd_clock_in)

    co = sub.add_parser("clock-out", help="お疲れ（締め）")
    co.set_defaults(func=cmd_clock_out)

    sm = sub.add_parser("summary", help="集計")
    sm.add_argument("--month", help="YYYY-MM で絞り込み")
    sm.set_defaults(func=cmd_summary)

    va = sub.add_parser("validate", help="検証・未分類レポート")
    va.set_defaults(func=cmd_validate)

    st = sub.add_parser("status", help="進行中の様子")
    st.set_defaults(func=cmd_status)

    ac = sub.add_parser("active", help="進行中案件スロットの操作")
    ac.add_argument("action", choices=["add", "touch", "close"])
    ac.add_argument("--slug", required=True)
    ac.add_argument("--name")
    ac.add_argument("--stage")
    ac.set_defaults(func=cmd_active)

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        args.func(args)
    except ValueError as e:
        print(f"ごめんなさい、できませんでした：{e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
