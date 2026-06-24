# ノノミ — 勤怠記録・集計メイド（Python CLI）

ご主人様の副業（個人事業）の勤怠を、やさしく・厳格に記録／集計するエンジンです。
人格はステートレス。データは `data/` のファイルだけに残します。

## 構成

```
data/
  kintai.csv        # 勤怠データ（1セッション＝1行・追記重視）
  active.md         # 進行中の動画案件（最大3スロット）
nonomi/
  config.py         # 時刻(Asia/Tokyo)・パス・曜日
  csv_io.py         # CSV入出力。過去行の改変を仕組みで禁止
  clock.py          # 始める/お疲れ（work_hours自動計算）
  summary.py        # 日次/project別/作業別の集計
  validate.py       # 書式・整合性チェック＋未分類レポート
  active.py         # 進行中案件スロットの読み書き
  __main__.py       # CLI
tests/              # pytest（約束を守れているかの検証）
```

## 使い方

```bash
# 始める（起票）
python -m nonomi clock-in --project video:fren --memo "動画制作（フレンとこ・①企画）"

# お疲れ（締め：end と work_hours を自動記入）
python -m nonomi clock-out

# 集計（月で絞るなら --month 2026-06）
python -m nonomi summary

# 検証・未分類のお知らせ
python -m nonomi validate

# 進行中の様子
python -m nonomi status

# 進行中案件スロット
python -m nonomi active add   --slug fren --name フレンとこ --stage ①企画
python -m nonomi active touch  --slug fren --stage ⑥誤字修正
python -m nonomi active close  --slug fren
```

## 守っている約束（信頼の核）

- 過去の記録は書き換えません。訂正は新しい行を足す方針です。
- `work_hours` は `end - start` を小数2桁で自動計算（日跨ぎは +24h）。
- `day` は `date` から自動補完。
- `project` は `video:<slug>` か `youtube` の2値のみ。外れた行は「未分類」として正直にお知らせします。

## CSV仕様

```
date,day,start,end,work_hours,project,memo
```

## 開発

```bash
pip install -r requirements-dev.txt
pytest -q
```
