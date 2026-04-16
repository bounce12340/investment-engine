# 🛡️ Investment-Engine: Institutional Quant-Mental Hybrid Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)

An institutional-grade investment monitoring and valuation framework designed to combine quantitative risk sensing with qualitative fundamental analysis.

Unlike traditional portfolios that rely on lagging indicators (price/earnings), **Investment-Engine** focuses on **Leading Indicators**, **Paradigm Shifts**, and **Probabilistic Valuation** to anticipate market moves before they are priced in.

**[繁體中文](docs/README.zh-TW.md)** | **[日本語](docs/README.ja.md)** | **[한국어](docs/README.ko.md)**

---

## 🚀 Core Architecture

The engine operates on a three-layer intelligence stack:

### 1. Horizon Sensing Layer (Multi-Timeframe)
The system monitors assets across three distinct time horizons:
- **Short-Term**: Liquidity, Sentiment, and Option Skew.
- **Medium-Term**: Fundamental Pivots (e.g., AI ROI, Inference Transition).
- **Long-Term**: Paradigm Shifts (e.g., Algorithmic Efficiency, Moat Erosion).

### 2. Risk Mitigation Layer (Red-Blue Teaming)
To combat confirmation bias, the engine employs a "Red-Blue Team" analysis:
- **Blue Team**: Gathers evidence supporting the investment thesis.
- **Red Team**: Actively searches for "Kill-Switches" (falsification evidence) that would trigger a mandatory exit.

### 3. Valuation Layer (Triangulation)
The system avoids single-point price targets, instead using a triangulation of three models:
- **Probabilistic Scenario Model**: Weights multiple outcomes (Bull/Base/Bear).
- **Two-Stage DCF**: Projects intrinsic value based on growth decay.
- **Relative Multiples**: Benchmarks against industry peers.

---

## 🛠️ Key Features

| Feature | Description |
|---------|-------------|
| **Strategic Leading Indicators** | Specialized tracking of high-impact metrics (CUDA Dominance, Cloud CapEx ROI) |
| **Margin Stress Testing** | Integration of leverage/margin data to monitor Maintenance Margin and Margin Call risks |
| **Obsidian Integration** | Automated generation of structured weekly reports directly into a personal knowledge base |
| **Quantitative Gradients** | Uses a Green → Yellow → Red gradient system instead of binary triggers to sense trend decay |
| **Red-Blue Team Analysis** | Counteracts confirmation bias through adversarial thesis testing |
| **Multi-Model Valuation** | Triangulates DCF, Probabilistic Scenarios, and Relative Multiples |

---

## 📂 Project Structure

```
investment-engine/
├── investment_watcher.py      # Core orchestrator for weekly sensing
├── valuation_engine.py       # Mathematical core (DCF/Probabilistic/Relative)
├── data/
│   └── monitor-registry.json # The "Brain" - ticker theses & kill-switches
├── Weekly_Reports/           # AI-generated institutional memos
└── docs/
    ├── README.zh-TW.md       # 繁體中文文檔
    ├── README.ja.md          # 日本語ドキュメント
    └── README.ko.md          # 한국어 문서
```

---

## 🎯 Target Strategy

Optimized for high-conviction, high-growth portfolios focusing on:

| Sector | Focus Areas |
|--------|-------------|
| **AI Infrastructure** | Compute, Networking, Software Moats |
| **Strategic Resources** | Energy, Rare Earths |
| **Disruptive Tech** | Robotics, FinTech, Space |

---

## 🚦 Getting Started

### Prerequisites

- Python 3.10+
- Node.js (for Obsidian integration)

### Installation

```bash
# Clone the repository
git clone https://github.com/bounce12340/investment-engine.git
cd investment-engine

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API keys
```

### Quick Start

```python
from investment_watcher import InvestmentWatcher

# Initialize the engine
watcher = InvestmentWatcher(config_path="data/monitor-registry.json")

# Run weekly sensing
report = watcher.run_weekly_analysis()

# Generate Obsidian report
watcher.export_to_obsidian(vault_path="~/Documents/Vault")
```

---

## 📊 Example Output

### Weekly Report Structure

```
# NVDA Weekly Analysis - 2026-W15

## 🟢 Status: Bullish (Score: 8.2/10)

### Leading Indicators
- CUDA Dominance: 92% (↑ +2%)
- Data Center Revenue Growth: +217% YoY
- Blackwell Adoption: 45% of new deployments

### Red Team Alerts
- ⚠️ China export restrictions impact: -$2B Q2 revenue
- ⚠️ AMD MI300X competitive pressure in enterprise

### Valuation Triangulation
| Model | Price Target | Confidence |
|-------|--------------|------------|
| DCF (Two-Stage) | $1,150 | High |
| Probabilistic | $1,080 | Medium |
| Relative | $950 | Medium |

### Kill-Switch Status
| Trigger | Current | Threshold | Status |
|---------|---------|-----------|--------|
| CUDA Share < 80% | 92% | 80% | 🟢 Safe |
| GM% < 60% | 75.5% | 60% | 🟢 Safe |
```

---

## 🧪 Testing

```bash
# Run test suite
pytest tests/

# Run margin stress test
python -m tests.stress_test --ticker NVDA
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📚 Documentation

- **English**: You are here
- **[繁體中文](docs/README.zh-TW.md)** - Traditional Chinese
- **[日本語](docs/README.ja.md)** - Japanese
- **[한국어](docs/README.ko.md)** - Korean

---

*Developed for high-precision risk management and strategic alpha generation.*