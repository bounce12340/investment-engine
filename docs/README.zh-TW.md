# Investment-Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)

**[English](../README.md)** | **繁體中文** | **[日本語](README.ja.md)** | **[한국어](README.ko.md)**

一個輕量級的股票論點追蹤框架，提供 **三角估值**、**Kill-Switch 監控**、
**對抗式 Red/Blue 論點壓力測試**，以及 **Obsidian 整合週報**。

流程很簡單：你維護一份 JSON 檔（_監控 registry_），每個 ticker 有一組 thesis。
引擎會計算三個獨立的價格目標、檢查證偽觸發條件、給論點 0–10 分的信心評分，
並把 Markdown 週報寫進你的 Obsidian vault。也可以用 macOS launchd 排程自動執行。

---

## 目錄

- [功能](#功能)
- [安裝](#安裝)
- [快速開始](#快速開始)
- [CLI 指令參考](#cli-指令參考)
- [排程（macOS）](#排程macos)
- [Registry 格式](#registry-格式)
- [輸出範例](#輸出範例)
- [專案結構](#專案結構)
- [Scope](#scope)
- [開發](#開發)
- [授權](#授權)

---

## 功能

**1. 監控 registry。** 一份 JSON 檔（`data/monitor-registry.json`）存放每個
ticker 的 thesis — 短中長三個時間維度的敘事、手動維護的 leading indicators、
kill-switches、Red/Blue 論點、估值輸入。

**2. 三角估值。** 每檔 ticker 獨立計算三個價格目標，再平均成一個三角化估計：
- **Two-Stage DCF** — 高成長期後進入 terminal growth（Gordon growth 模型）
- **Probabilistic scenarios** — Bull / Base / Bear 情境機率加權（機率總和必為 1.0）
- **Relative multiples** — ticker 指標 × 同業中位倍數

**3. Kill-switches。** 門檻式證偽檢查。每個 switch 有方向（`below` / `above`）
和當前值；跨過門檻即觸發，代表 thesis 遭破壞。

**4. 論點壓力測試（Thesis stress test）。** 每份報告都有一個 **信心評分 (0–10)**
和一串流程衛生 flag。評分完全確定性、公式透明：

| 因子 | 影響 |
|------|------|
| 未觸發的 kill-switch | 每個 +1（上限 +3） |
| 已觸發的 kill-switch | 每個 −2 |
| Bull/Bear 比 ∈ [0.5, 2.0] | +1（平衡） |
| Bear points ≥ 3 / ≥ 5 | +1 / +2（紅隊強度） |

Flag（ℹ️ info / ⚠️ warning / 🔴 alert）：
- `No red team — confirmation bias risk`（沒有 bear points）
- `Thin red team — only N bear point(s)`（bear < 2）
- `No blue team — negative thesis only`（沒有 bull）
- `Bull-biased: N.N× bull-to-bear ratio`（比率 > 3×）
- `N kill-switch(es) triggered — thesis violation`
- `No red flags — thesis well-balanced`（其他 flag 都未觸發時）

**5. Obsidian 報告。** Markdown 週報寫到
`{vault}/Weekly_Reports/{TICKER}_{YYYY}-W{WW}.md`，直接進你的知識庫。
採 ISO 週數編號。

**6. 歷史績效。** 對每個 ticker 抓 3 年日線收盤，計算 1y / 3y 的
**Sharpe、Sortino、最大回撤、年化波動率、對 VOO 的 Jensen α / β**
（risk-free rate = 4.0%）。報告和 `analyze` CLI 都會多一個
「Historical Performance」區塊。

**7. 技術指標快照。** 用同一份 3 年日線計算 **RSI(14)、MACD (12/26/9)、
50 日與 200 日均線、距 MA 百分比**。RSI ≥ 70 或 ≤ 30 自動標註
超買 / 超賣。純 pandas 實作，沒有新依賴。

**8. 即時股價。** 透過 `yfinance` 抓 Yahoo Finance 當前價格，離線時會 fallback。

**9. 排程。** macOS `launchd` 支援日 / 週 / 月循環執行，可互動選項或用 flag。

---

## 安裝

```bash
git clone https://github.com/bounce12340/investment-engine
cd investment-engine
python -m venv .venv && source .venv/bin/activate
pip install -e .

cp .env.example .env      # 需要時編輯 OBSIDIAN_VAULT
```

需要 Python 3.10+。排程功能僅限 macOS。

---

## 快速開始

```bash
# NVDA 的 console 摘要
investment-engine analyze NVDA

# 產生週報並寫入 Obsidian vault
investment-engine weekly NVDA --vault /Users/chunghsutsai/Vault
```

離線時加 `--no-price` 可跳過 yfinance 呼叫。

---

## CLI 指令參考

### `analyze TICKER`
輸出 console 摘要：三角估值、kill-switch 狀態、歷史績效、技術指標、論點壓力測試。

| 參數 | 預設 | 說明 |
|------|------|------|
| `--registry PATH` | `data/monitor-registry.json` | 自訂 registry 檔 |
| `--no-price` | off | 跳過 yfinance 即時股價抓取 |
| `--no-performance` | off | 跳過 3 年歷史抓取（Sharpe / α / β） |
| `--no-technicals` | off | 跳過技術指標（RSI / MACD / MA） |

### `weekly TICKER`
產生 Markdown 週報並寫進 Obsidian vault。

| 參數 | 預設 | 說明 |
|------|------|------|
| `--registry PATH` | `data/monitor-registry.json` | 自訂 registry 檔 |
| `--vault PATH` | `$OBSIDIAN_VAULT` 或 `/Users/chunghsutsai/Vault` | Vault 路徑 |
| `--no-price` | off | 跳過 yfinance 即時股價抓取 |
| `--no-performance` | off | 跳過 3 年歷史抓取（Sharpe / α / β） |
| `--no-technicals` | off | 跳過技術指標（RSI / MACD / MA） |

輸出路徑：`{vault}/Weekly_Reports/{TICKER}_{YYYY}-W{WW}.md`。

### `schedule create` / `list` / `show` / `remove`
見下方 [排程（macOS）](#排程macos)。

---

## 排程（macOS）

透過 `launchd` 執行循環任務。不帶參數時互動式詢問頻率、時間、tickers。
每個 schedule 產生一個 plist + wrapper 腳本 + log。

```bash
# 互動式
investment-engine schedule create

# 每天 09:00 跑 registry 全部 ticker
investment-engine schedule create --name morning --frequency daily \
    --time 09:00 --yes

# 每週一 08:30 跑指定 tickers
investment-engine schedule create --name mon-brief --frequency weekly \
    --time 08:30 --weekday 1 --tickers NVDA,TSM,GOOGL --yes

# 每月 1 號 07:00
investment-engine schedule create --name month-end --frequency monthly \
    --time 07:00 --day 1 --yes

# 管理
investment-engine schedule list
investment-engine schedule show morning
investment-engine schedule remove morning
```

**`schedule create` 的參數：**

| 參數 | 說明 |
|------|------|
| `--name SLUG` | 短識別名（小寫+連字號） |
| `--frequency daily\|weekly\|monthly` | 頻率 |
| `--time HH:MM` | 24 小時制 |
| `--weekday 0..6` | 0=週日 … 6=週六（weekly 才用，launchd 慣例） |
| `--day 1..31` | （monthly 才用） |
| `--tickers A,B,C` | 子集；留空 = 全部 |
| `--command weekly\|analyze` | 預設 `weekly` |
| `--vault PATH` | Vault 覆寫 |
| `--yes` / `-y` | 跳過 launchd 載入前的確認 |

**產生的檔案：**
- Wrapper：`~/Library/Application Support/investment-engine/<name>.sh`
- Plist：`~/Library/LaunchAgents/com.investment-engine.<name>.plist`
- Log：`~/Library/Logs/investment-engine-<name>.log`

Wrapper 會用 `|| echo "[warn] X failed"` 逐一跑每個 ticker，
任何一個 yfinance 出錯都不會中斷其他。

---

## Registry 格式

`data/monitor-registry.json` 目前包含 NVDA 以及另外 9 檔範例
（PLTR、GOOGL、MP、NU、RCAT、TSLA、TSM、UUUU、VOO）。頂層 key 是 ticker 符號，
每個 entry 符合下列 schema：

| 欄位 | 說明 |
|------|------|
| `ticker` | Ticker 符號（必須與 key 一致） |
| `name` | 顯示名稱（如 `NVIDIA Corporation`） |
| `sector` | 自由格式的產業標籤 |
| `thesis.short_term` / `medium_term` / `long_term` | 各時間維度的敘事 |
| `leading_indicators[].{name,value,unit,description}` | 手動維護的指標值 |
| `kill_switches[].{name,metric,threshold,direction,current_value}` | `direction` 為 `below` 或 `above` |
| `bull_points[]` / `bear_points[]` | Red/Blue 論點（字串陣列） |
| `valuation_inputs.dcf` | `fcf`、`growth_high`、`growth_terminal`、`years_high`、`wacc`、`shares` |
| `valuation_inputs.scenarios[]` | `name`、`price`、`probability` — 機率總和必為 1.0 |
| `valuation_inputs.relative` | `ticker_metric`、`peer_median`、`target_metric`（例如 `EPS × peer P/E`） |

Pydantic 會在載入時驗證每一筆。機率總和、DCF 收斂條件（WACC > terminal growth）、
direction 列舉值都會強制檢查。

---

## 輸出範例

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

週報 Markdown 包含相同資訊，外加 Leading-Indicators 表、Red/Blue 論點、
以及論點壓力測試 flag，適合在 Obsidian 內索引與雙向連結。

---

## 專案結構

```
investment-engine/
├── investment_engine/
│   ├── valuation/            # DCF、probabilistic、relative
│   ├── data_sources/         # yfinance wrapper + registry loader
│   ├── analysis/             # kill_switches、leading_indicators、red_blue_team
│   ├── reports/              # Markdown template + Obsidian writer
│   ├── models.py             # pydantic：Thesis、KillSwitch、StressTest……
│   ├── watcher.py            # InvestmentWatcher 主流程
│   ├── scheduler.py          # launchd plist / wrapper 產生
│   └── cli.py                # typer 進入點
├── data/monitor-registry.json   # 範例：10 檔 ticker
└── tests/                    # 36 個測試，涵蓋每個模組
```

---

## Scope

**已完成：**
- 三角估值（DCF + Probabilistic + Relative）
- 靜態 kill-switch 檢查
- 確定性 Red/Blue 論點壓力測試 + 信心評分
- 歷史績效（Sharpe / Sortino / 最大回撤 / 對 VOO 的 α-β）
- 技術指標快照（RSI(14)、MACD(12/26/9)、50 日 / 200 日均線）
- Obsidian Markdown 輸出
- 即時股價（yfinance）
- macOS launchd 排程

**未納入（未來工作）：**
- LLM 驅動的質化分析（自動產生 bull/bear 論點）
- 策略型指標即時抓取（CUDA 市佔、NdPr 價格等）
- Margin stress test（槓桿 / 維持保證金模擬）
- 信心評分的時間序列追蹤
- Windows/Linux 排程（launchd 僅 macOS）

---

## 開發

```bash
pip install -e ".[dev]"
pytest tests/                 # 36 tests
```

測試使用 mock 的 yfinance，完全不碰真實 vault 或 launchd，
整套測試在一秒內跑完、無副作用。

---

## 授權

MIT — 詳見 [LICENSE](../LICENSE)。
