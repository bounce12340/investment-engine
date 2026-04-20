# Investment-Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)

**[English](../README.md)** | **[繁體中文](README.zh-TW.md)** | **日本語** | **[한국어](README.ko.md)**

高確信度の株式テーゼを追跡するための軽量フレームワーク。**三角測量による
バリュエーション**、**Kill-switch 監視**、**敵対的 Red/Blue テーゼ・
ストレステスト**、**Obsidian 連携のウィークリーレポート**を提供します。

ワークフローはシンプルです。ティッカー単位のテーゼを記述した JSON ファイル
(_モニタリング registry_) を 1 つ保守するだけで、本エンジンが 3 つの独立した
株価ターゲットを算出し、反証トリガーをチェックし、テーゼを 0–10 でスコア化、
そして Markdown メモを Obsidian ボルトに書き込みます。
オプションで macOS launchd のスケジュールによる定期実行も可能です。

---

## 目次

- [機能](#機能)
- [インストール](#インストール)
- [クイックスタート](#クイックスタート)
- [CLI リファレンス](#cli-リファレンス)
- [スケジューリング（macOS）](#スケジューリングmacos)
- [Registry フォーマット](#registry-フォーマット)
- [出力例](#出力例)
- [プロジェクト構成](#プロジェクト構成)
- [Scope](#scope)
- [開発](#開発)
- [ライセンス](#ライセンス)

---

## 機能

**1. モニタリング registry。** 1 つの JSON ファイル
(`data/monitor-registry.json`) にティッカー単位のテーゼを格納します。
短・中・長期のナラティブ、手動管理の leading indicators、kill-switches、
Red/Blue 論点、バリュエーション入力を含みます。

**2. 三角測量バリュエーション。** ティッカーごとに 3 つの独立した価格
ターゲットを算出し、1 つの三角化推定値に平均します。
- **Two-Stage DCF** — 高成長期間の後に terminal growth（Gordon growth モデル）
- **Probabilistic scenarios** — Bull / Base / Bear の確率加重（確率合計 = 1.0）
- **Relative multiples** — ティッカー指標 × ピア中央値倍率

**3. Kill-switches。** 閾値ベースの反証チェック。各スイッチは方向
(`below` / `above`) と現在値を持ち、閾値を越えると発火してテーゼ違反を示します。

**4. テーゼ・ストレステスト。** 各レポートに **Conviction score (0–10)** と
プロセス衛生の flag 一覧を含めます。スコアリングは決定論的かつ透明です。

| 要因 | 影響 |
|------|------|
| 安全な kill-switch | +1（上限 +3） |
| 発火した kill-switch | −2 |
| Bull/Bear 比 ∈ [0.5, 2.0] | +1（バランス） |
| Bear points ≥ 3 / ≥ 5 | +1 / +2（Red チーム強度） |

Flag（ℹ️ info / ⚠️ warning / 🔴 alert）：
- `No red team — confirmation bias risk`（bear なし）
- `Thin red team — only N bear point(s)`（bear < 2）
- `No blue team — negative thesis only`（bull なし）
- `Bull-biased: N.N× bull-to-bear ratio`（比率 > 3×）
- `N kill-switch(es) triggered — thesis violation`
- `No red flags — thesis well-balanced`（他の flag が無い場合のみ）

**5. Obsidian レポート。** Markdown メモは
`{vault}/Weekly_Reports/{TICKER}_{YYYY}-W{WW}.md` に出力されます。
ISO 週番号を使用します。

**6. ヒストリカル・パフォーマンス。** 各ティッカーにつき 3 年分の日次終値を
Yahoo Finance から取得し、1y / 3y 窓での **Sharpe、Sortino、最大ドローダウン、
年率ボラティリティ、VOO 対比の Jensen α / β**（無リスク金利 = 4.0%）を算出します。
レポートと `analyze` CLI に「Historical Performance」セクションを追加します。

**7. テクニカル・スナップショット。** 同じ 3 年分の終値から
**RSI(14)、MACD (12/26/9)、50 日および 200 日移動平均、MA からの乖離率**
を計算します。RSI ≥ 70 / ≤ 30 は買われすぎ / 売られすぎとしてタグ付けされます。
純粋な pandas 実装 — 追加依存なし。

**8. リアルタイム株価。** `yfinance` 経由で Yahoo Finance から取得。
オフライン時は優雅にフォールバックします。

**9. スケジューリング。** macOS `launchd` による日次 / 週次 / 月次の
定期実行。対話プロンプトまたはフラグで設定可能。

---

## インストール

```bash
git clone https://github.com/bounce12340/investment-engine
cd investment-engine
python -m venv .venv && source .venv/bin/activate
pip install -e .

cp .env.example .env      # OBSIDIAN_VAULT を適宜編集
```

Python 3.10+ が必要。スケジューリング機能は macOS 限定です。

---

## クイックスタート

```bash
# NVDA のコンソール要約
investment-engine analyze NVDA

# Obsidian ボルトにウィークリーレポートを書き込み
investment-engine weekly NVDA --vault /Users/chunghsutsai/Vault
```

オフラインでは `--no-price` を付ければ yfinance 呼び出しをスキップします。

---

## CLI リファレンス

### `analyze TICKER`
コンソール要約を出力：三角化バリュエーション、kill-switch ステータス、
ヒストリカル・パフォーマンス、テクニカル・スナップショット、テーゼ・ストレステスト。

| フラグ | デフォルト | 説明 |
|--------|-----------|------|
| `--registry PATH` | `data/monitor-registry.json` | カスタム registry ファイル |
| `--no-price` | off | yfinance からの株価取得をスキップ |
| `--no-performance` | off | 3 年ヒストリー取得（Sharpe / α / β）をスキップ |
| `--no-technicals` | off | テクニカル指標（RSI / MACD / MA）をスキップ |

### `weekly TICKER`
Markdown レポートを生成し Obsidian ボルトに書き込みます。

| フラグ | デフォルト | 説明 |
|--------|-----------|------|
| `--registry PATH` | `data/monitor-registry.json` | カスタム registry ファイル |
| `--vault PATH` | `$OBSIDIAN_VAULT` または `/Users/chunghsutsai/Vault` | 対象ボルト |
| `--no-price` | off | yfinance からの株価取得をスキップ |
| `--no-performance` | off | 3 年ヒストリー取得（Sharpe / α / β）をスキップ |
| `--no-technicals` | off | テクニカル指標（RSI / MACD / MA）をスキップ |

出力先：`{vault}/Weekly_Reports/{TICKER}_{YYYY}-W{WW}.md`

### `schedule create` / `list` / `show` / `remove`
下記 [スケジューリング（macOS）](#スケジューリングmacos) を参照。

---

## スケジューリング（macOS）

`launchd` による定期実行。デフォルトは対話式 — `investment-engine schedule
create` を実行すると頻度、時刻、ティッカーを順に尋ねられます。
各スケジュールは plist + ラッパースクリプト + ログファイルを 1 セットずつ生成します。

```bash
# 対話式
investment-engine schedule create

# 毎日 09:00 に registry 全ティッカーを実行
investment-engine schedule create --name morning --frequency daily \
    --time 09:00 --yes

# 毎週月曜 08:30 に特定ティッカーのみ
investment-engine schedule create --name mon-brief --frequency weekly \
    --time 08:30 --weekday 1 --tickers NVDA,TSM,GOOGL --yes

# 毎月 1 日 07:00
investment-engine schedule create --name month-end --frequency monthly \
    --time 07:00 --day 1 --yes

# 管理
investment-engine schedule list
investment-engine schedule show morning
investment-engine schedule remove morning
```

**`schedule create` のフラグ：**

| フラグ | 説明 |
|--------|------|
| `--name SLUG` | 短い識別名（小文字＋ハイフン） |
| `--frequency daily\|weekly\|monthly` | |
| `--time HH:MM` | 24 時間表記 |
| `--weekday 0..6` | 0=日 … 6=土（weekly のみ、launchd 規約） |
| `--day 1..31` | （monthly のみ） |
| `--tickers A,B,C` | サブセット指定；空白 = 全て |
| `--command weekly\|analyze` | デフォルト `weekly` |
| `--vault PATH` | ボルトの上書き |
| `--yes` / `-y` | launchd ロード前の確認をスキップ |

**生成される成果物：**
- ラッパー：`~/Library/Application Support/investment-engine/<name>.sh`
- Plist：`~/Library/LaunchAgents/com.investment-engine.<name>.plist`
- ログ：`~/Library/Logs/investment-engine-<name>.log`

ラッパーは `|| echo "[warn] X failed"` で全ティッカーをループするため、
1 つの yfinance エラーが他のティッカーを中断することはありません。

---

## Registry フォーマット

`data/monitor-registry.json` には NVDA のサンプルに加え、9 ティッカー
(PLTR、GOOGL、MP、NU、RCAT、TSLA、TSM、UUUU、VOO) が含まれます。
トップレベルのキーはティッカーシンボルで、各エントリは下記スキーマに従います。

| フィールド | 説明 |
|-----------|------|
| `ticker` | ティッカーシンボル（キーと一致必須） |
| `name` | 表示名（例：`NVIDIA Corporation`） |
| `sector` | 自由形式のセクタータグ |
| `thesis.short_term` / `medium_term` / `long_term` | 期間別ナラティブ |
| `leading_indicators[].{name,value,unit,description}` | 手動管理の指標値 |
| `kill_switches[].{name,metric,threshold,direction,current_value}` | `direction` は `below` または `above` |
| `bull_points[]` / `bear_points[]` | Red/Blue 論点（文字列配列） |
| `valuation_inputs.dcf` | `fcf`, `growth_high`, `growth_terminal`, `years_high`, `wacc`, `shares` |
| `valuation_inputs.scenarios[]` | `name`, `price`, `probability` — 合計 1.0 |
| `valuation_inputs.relative` | `ticker_metric`, `peer_median`, `target_metric` (例: `EPS × peer P/E`) |

Pydantic がロード時に全エントリを検証します。確率合計、DCF 収束条件
(WACC > terminal growth)、direction の列挙値はすべて強制されます。

---

## 出力例

```
$ investment-engine analyze NVDA
NVDA — NVIDIA Corporation (2026-W17)  |  price $202.06

  Valuation Triangulation
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Model         ┃   Target ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ Two-Stage DCF │  $101.79 │
│ Probabilistic │ $1074.00 │
│ Relative      │  $969.00 │
│ Triangulated  │  $714.93 │
└───────────────┴──────────┘
Upside vs current price: +253.8%

               Historical Performance
┏━━━━━━━━┳━━━━━━━━━┳━━━━━━━┳━━━━━━━━┳━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━━┓
┃ Period ┃  Return ┃   Vol ┃ Sharpe ┃ Sortino ┃ Max DD ┃ α vs VOO ┃    β ┃
┡━━━━━━━━╇━━━━━━━━━╇━━━━━━━╇━━━━━━━━╇━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━━┩
│ 1y     │ +121.9% │ 33.7% │   3.50 │    5.71 │ -20.2% │   +52.9% │ 1.75 │
│ 3y     │ +120.8% │ 48.8% │   2.39 │    3.72 │ -36.9% │   +76.2% │ 2.13 │
└────────┴─────────┴───────┴────────┴─────────┴────────┴──────────┴──────┘

          Technical Snapshot
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┓
┃ Indicator      ┃             Value ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━┩
│ Price          │           $202.06 │
│ RSI(14)        │ 71.6 (overbought) │
│ MACD           │             5.344 │
│ MACD signal    │             2.437 │
│ MACD histogram │            +2.907 │
│ 50-day MA      │   $183.90 (+9.9%) │
│ 200-day MA     │  $181.98 (+11.0%) │
└────────────────┴───────────────────┘

          Thesis Stress Test
┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Metric                  ┃     Value ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ Conviction score        │ 10.0 / 10 │
│ Bull / Bear             │     5 / 5 │
│ Kill-switches triggered │     0 / 4 │
│ Bull/Bear ratio         │      1.00 │
└─────────────────────────┴───────────┘
ℹ️  No red flags — thesis well-balanced
```

ウィークリー Markdown 出力には同じ情報に加え、Leading-Indicators テーブル、
Red/Blue チームの論点、テーゼ・ストレステストの flag が含まれます。
Obsidian ボルト内でインデックス化・双方向リンクに適した形式です。

---

## プロジェクト構成

```
investment-engine/
├── investment_engine/
│   ├── valuation/            # DCF、probabilistic、relative
│   ├── data_sources/         # yfinance ラッパー + registry loader
│   ├── analysis/             # kill_switches、leading_indicators、red_blue_team
│   ├── reports/              # Markdown テンプレート + Obsidian writer
│   ├── models.py             # pydantic: Thesis, KillSwitch, StressTest, …
│   ├── watcher.py            # InvestmentWatcher 主オーケストレーター
│   ├── scheduler.py          # launchd plist / wrapper 生成
│   └── cli.py                # typer エントリポイント
├── data/monitor-registry.json   # サンプル：10 ティッカー
└── tests/                    # 各モジュールをカバーする 36 テスト
```

---

## Scope

**対応済み：**
- 三角測量バリュエーション（DCF + Probabilistic + Relative）
- 静的 kill-switch チェック
- 決定論的 Red/Blue テーゼ・ストレステスト + Conviction score
- ヒストリカル・パフォーマンス（Sharpe / Sortino / 最大 DD / VOO 対比 α-β）
- テクニカル・スナップショット（RSI(14)、MACD(12/26/9)、50日 / 200日 MA）
- Obsidian Markdown 出力
- yfinance リアルタイム株価
- macOS launchd スケジューリング

**対象外（将来の作業）：**
- LLM 駆動の定性分析（bull/bear 論点自動生成）
- 戦略指標のリアルタイム取得（CUDA シェア、NdPr 価格等）
- マージン・ストレステスト（レバレッジ / 維持証拠金シミュレーション）
- Conviction score の時系列トラッキング
- Windows/Linux スケジューリング（launchd は macOS のみ）

---

## 開発

```bash
pip install -e ".[dev]"
pytest tests/                 # 36 テスト
```

テストは yfinance をモック化しており、実ボルトや launchd には触れません。
フルスイートは副作用なく 1 秒未満で実行されます。

---

## ライセンス

MIT — [LICENSE](../LICENSE) を参照。
