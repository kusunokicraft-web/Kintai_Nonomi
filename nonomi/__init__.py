"""ノノミ - 勤怠記録・集計エンジン（ステートレス・追記重視）。

CLAUDE.md の仕様を「仕組み」で守るための最小コア。
- 過去の記録は書き換えない（訂正は新しい行を足す）
- work_hours は end-start を自動計算、day は date から自動補完
- 時刻は実測（Asia/Tokyo）。推測しない。
"""

__all__ = ["config", "csv_io", "clock", "summary", "validate", "active"]
