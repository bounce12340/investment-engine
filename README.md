# Investment-Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)

A lightweight framework for tracking high-conviction equity theses using **triangulation valuation**, **kill-switch monitoring**, and **Obsidian-integrated weekly reports**.

## Architecture

**1. Registry (`data/monitor-registry.json`)**
Each ticker has a thesis file with: narrative (short/medium/long horizon), leading indicators, kill-switches, bull/bear points, and valuation inputs.

**2. Valuation Triangulation**
Instead of a single price target, the engine computes three independent estimates:
- **Two-Stage DCF** — high-growth period then terminal growth
- **Probabilistic Scenarios** — probability-weighted Bull / Base / Bear targets
- **Relative Multiples** — peer-median multiple applied to the ticker's metric

**3. Kill-Switches**
Threshold-based falsification checks. If a metric crosses its threshold, the trigger fires — signalling thesis violation.

**4. Reports**
Markdown weekly reports written directly into an Obsidian vault under `Weekly_Reports/`.

## Install

```bash
git clone https://github.com/bounce12340/investment-engine
cd investment-engine
pip install -e .
cp .env.example .env      # edit OBSIDIAN_VAULT if different
```

## Usage

```bash
# Console summary
investment-engine analyze NVDA

# Write weekly report into Obsidian vault
investment-engine weekly NVDA --vault /Users/chunghsutsai/Vault
```

## Registry format

See `data/monitor-registry.json` for the NVDA sample. Fields:

| Field | Description |
|-------|-------------|
| `thesis.short_term` / `medium_term` / `long_term` | Narrative per horizon |
| `leading_indicators[]` | Name, current value, description (manually maintained) |
| `kill_switches[]` | Name, metric, threshold, direction (`below`/`above`), current value |
| `bull_points[]` / `bear_points[]` | Pre-written Red/Blue team arguments |
| `valuation_inputs.dcf` | `fcf`, `growth_high`, `growth_terminal`, `years_high`, `wacc`, `shares` |
| `valuation_inputs.scenarios[]` | `name`, `price`, `probability` (sum must equal 1.0) |
| `valuation_inputs.relative` | `ticker_metric`, `peer_median`, `target_metric` (e.g. EPS × peer P/E) |

## Scope

**In scope (MVP):**
- Triangulation valuation
- Static kill-switch checks
- Static Red/Blue points from registry
- Obsidian Markdown output

**Out of scope (future work):**
- LLM-driven qualitative analysis
- Live scraping of strategic indicators (CUDA share, etc.)
- Margin stress testing
- Batch multi-ticker runs

## Testing

```bash
pytest tests/
```

## License

MIT — see [LICENSE](LICENSE).
