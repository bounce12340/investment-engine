# Investment-Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)

**English** | **[繁體中文](docs/README.zh-TW.md)** | **[日本語](docs/README.ja.md)** | **[한국어](docs/README.ko.md)**

A lightweight framework for tracking high-conviction equity theses with
**triangulation valuation**, **kill-switch monitoring**, an **adversarial
Red/Blue thesis stress test**, and **Obsidian-integrated weekly reports**.

The workflow is simple: you maintain one JSON file (your _monitor registry_)
with a thesis per ticker. The engine computes three independent price targets,
checks falsification triggers, scores the thesis 0–10, and writes a Markdown
memo into your Obsidian vault. Optionally, a macOS launchd schedule runs it on
a cadence.

---

## Contents

- [Features](#features)
- [Install](#install)
- [Quickstart](#quickstart)
- [CLI reference](#cli-reference)
- [Scheduling (macOS)](#scheduling-macos)
- [Registry format](#registry-format)
- [Sample output](#sample-output)
- [Project layout](#project-layout)
- [Scope](#scope)
- [Development](#development)
- [License](#license)

---

## Features

**1. Monitor registry.** One JSON file (`data/monitor-registry.json`) holds a
thesis per ticker — narrative across short/medium/long horizons, leading
indicators (manually maintained), kill-switches, Red/Blue arguments, and
valuation inputs.

**2. Triangulation valuation.** Three independent price targets per ticker,
averaged into a single triangulated estimate:
- **Two-Stage DCF** — high-growth period then terminal growth (Gordon growth).
- **Probabilistic scenarios** — probability-weighted Bull / Base / Bear targets
  (probabilities must sum to 1.0).
- **Relative multiples** — ticker metric × peer-median multiple.

**3. Kill-switches.** Threshold-based falsification checks. Each has a
direction (`below` / `above`) and a current value; crossing the threshold fires
the trigger, flagging thesis violation.

**4. Thesis stress test.** Every report includes a **conviction score (0–10)**
and a list of process-hygiene flags. Scoring is deterministic and transparent:

| Factor | Effect |
|--------|--------|
| Safe kill-switch | +1 each (capped at +3) |
| Triggered kill-switch | −2 each |
| Bull/bear ratio ∈ [0.5, 2.0] | +1 (balanced) |
| Bear points ≥ 3 / ≥ 5 | +1 / +2 (red-team strength) |

Flags (ℹ️ info / ⚠️ warning / 🔴 alert):
- `No red team — confirmation bias risk` (no bear points)
- `Thin red team — only N bear point(s)` (< 2 bear)
- `No blue team — negative thesis only` (no bull)
- `Bull-biased: N.N× bull-to-bear ratio` (> 3×)
- `N kill-switch(es) triggered — thesis violation`
- `No red flags — thesis well-balanced` (only when no other flags)

**5. Obsidian reports.** Markdown memos written to
`{vault}/Weekly_Reports/{TICKER}_{YYYY}-W{WW}.md`, suitable for your knowledge
base. ISO week numbering.

**6. Historical performance.** For every ticker, the engine pulls 3 years of
daily closes from Yahoo Finance and computes **Sharpe, Sortino, max drawdown,
annualized volatility, and Jensen's α / β vs VOO** over 1y and 3y windows
(risk-free rate = 4.0%). Adds a `## Historical Performance` section to every
report and a Rich table in `analyze`.

**7. Live prices.** Current price fetched from Yahoo Finance via `yfinance`,
with graceful fallback when offline.

**8. Scheduling.** Daily / weekly / monthly recurring runs via macOS
`launchd`. Interactive prompts or flags.

---

## Install

```bash
git clone https://github.com/bounce12340/investment-engine
cd investment-engine
python -m venv .venv && source .venv/bin/activate
pip install -e .

cp .env.example .env      # edit OBSIDIAN_VAULT if different
```

Requires Python 3.10+. Scheduling requires macOS.

---

## Quickstart

```bash
# Console summary for NVDA
investment-engine analyze NVDA

# Weekly Markdown report into your Obsidian vault
investment-engine weekly NVDA --vault /Users/chunghsutsai/Vault
```

Works offline with `--no-price` (skips the yfinance call).

---

## CLI reference

### `analyze TICKER`
Prints a console summary: triangulated valuation, kill-switch status,
historical performance, and thesis stress test.

| Flag | Default | Description |
|------|---------|-------------|
| `--registry PATH` | `data/monitor-registry.json` | Custom registry file |
| `--no-price` | off | Skip fetching live price from yfinance |
| `--no-performance` | off | Skip fetching 3y history for Sharpe/α/β stats |

### `weekly TICKER`
Generates a Markdown report and writes it into the Obsidian vault.

| Flag | Default | Description |
|------|---------|-------------|
| `--registry PATH` | `data/monitor-registry.json` | Custom registry file |
| `--vault PATH` | `$OBSIDIAN_VAULT` or `/Users/chunghsutsai/Vault` | Target vault |
| `--no-price` | off | Skip fetching live price from yfinance |
| `--no-performance` | off | Skip fetching 3y history for Sharpe/α/β stats |

Output path: `{vault}/Weekly_Reports/{TICKER}_{YYYY}-W{WW}.md`.

### `schedule create` / `list` / `show` / `remove`
See [Scheduling](#scheduling-macos) below.

---

## Scheduling (macOS)

Recurring runs via `launchd`. Interactive by default — run
`investment-engine schedule create` and you'll be prompted for frequency,
time, and tickers. Each schedule creates one plist + wrapper script + log file.

```bash
# Interactive
investment-engine schedule create

# Daily at 09:00 for all tickers in the registry
investment-engine schedule create --name morning --frequency daily \
    --time 09:00 --yes

# Weekly Mondays at 08:30 for a subset
investment-engine schedule create --name mon-brief --frequency weekly \
    --time 08:30 --weekday 1 --tickers NVDA,TSM,GOOGL --yes

# Monthly on the 1st at 07:00
investment-engine schedule create --name month-end --frequency monthly \
    --time 07:00 --day 1 --yes

# Manage
investment-engine schedule list
investment-engine schedule show morning
investment-engine schedule remove morning
```

**Flags for `schedule create`:**

| Flag | Description |
|------|-------------|
| `--name SLUG` | Short lowercase-hyphen name |
| `--frequency daily\|weekly\|monthly` | |
| `--time HH:MM` | 24-hour clock |
| `--weekday 0..6` | 0=Sun … 6=Sat (weekly only, launchd convention) |
| `--day 1..31` | (monthly only) |
| `--tickers A,B,C` | Subset of registry; blank = all |
| `--command weekly\|analyze` | Default `weekly` |
| `--vault PATH` | Vault override |
| `--yes` / `-y` | Skip confirmation before loading into launchd |

**Generated artifacts:**
- Wrapper: `~/Library/Application Support/investment-engine/<name>.sh`
- Plist:   `~/Library/LaunchAgents/com.investment-engine.<name>.plist`
- Log:     `~/Library/Logs/investment-engine-<name>.log`

The wrapper loops all tickers with `|| echo "[warn] X failed"` so one
ticker's yfinance blip won't abort the rest.

---

## Registry format

See `data/monitor-registry.json` for the NVDA sample and 9 other tickers
(PLTR, GOOGL, MP, NU, RCAT, TSLA, TSM, UUUU, VOO). Top-level keys are ticker
symbols; each entry matches this schema:

| Field | Description |
|-------|-------------|
| `ticker` | Ticker symbol (must match the key) |
| `name` | Display name (e.g. `NVIDIA Corporation`) |
| `sector` | Free-form sector tag |
| `thesis.short_term` / `medium_term` / `long_term` | Narrative per horizon |
| `leading_indicators[].{name,value,unit,description}` | Manually maintained values |
| `kill_switches[].{name,metric,threshold,direction,current_value}` | `direction`: `below` or `above` |
| `bull_points[]` / `bear_points[]` | Red/Blue team arguments (strings) |
| `valuation_inputs.dcf` | `fcf`, `growth_high`, `growth_terminal`, `years_high`, `wacc`, `shares` |
| `valuation_inputs.scenarios[]` | `name`, `price`, `probability` — probabilities must sum to 1.0 |
| `valuation_inputs.relative` | `ticker_metric`, `peer_median`, `target_metric` (e.g. `EPS × peer P/E`) |

Pydantic validates every entry at load time. Probability sums, DCF convergence
(WACC > terminal growth), and direction enum are all enforced.

---

## Sample output

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

The `weekly` Markdown output includes the same information plus a
Leading-Indicators table, Red/Blue team points, and the Thesis Stress Test
flags, ready to be indexed and linked inside an Obsidian vault.

---

## Project layout

```
investment-engine/
├── investment_engine/
│   ├── valuation/            # DCF, probabilistic, relative
│   ├── data_sources/         # yfinance wrapper + registry loader
│   ├── analysis/             # kill_switches, leading_indicators, red_blue_team
│   ├── reports/              # Markdown template + Obsidian writer
│   ├── models.py             # pydantic: Thesis, KillSwitch, StressTest, …
│   ├── watcher.py            # InvestmentWatcher orchestrator
│   ├── scheduler.py          # launchd plist / wrapper generation
│   └── cli.py                # typer entry point
├── data/monitor-registry.json   # sample: 10 tickers
└── tests/                    # 36 tests covering each module
```

---

## Scope

**In scope:**
- Triangulation valuation (DCF + Probabilistic + Relative)
- Static kill-switch checks
- Deterministic Red/Blue thesis stress test with conviction score
- Historical performance (Sharpe / Sortino / max drawdown / α-β vs VOO)
- Obsidian Markdown output
- Live prices via yfinance
- macOS launchd scheduling

**Out of scope (future work):**
- LLM-driven qualitative analysis (generating bull/bear arguments)
- Live scraping of strategic indicators (CUDA share, NdPr price, etc.)
- Margin stress testing (leverage / maintenance-margin simulations)
- Conviction-score history tracking over time
- Windows/Linux scheduling (launchd is macOS-only)

---

## Development

```bash
pip install -e ".[dev]"
pytest tests/                 # 36 tests
```

Tests use mocked yfinance and never touch the real vault or launchd, so the
full suite runs in under a second with no side effects.

---

## License

MIT — see [LICENSE](LICENSE).
