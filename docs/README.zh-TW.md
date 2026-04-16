# 🛡️ Investment-Engine: 機構級量化-基本面混合平台

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)

一個機構級的投資監控與估值框架，結合量化風險感測與基本面質性分析。

不同於依賴滯後指標（本益比）的傳統投資組合，**Investment-Engine** 專注於**領先指標**、**範式轉移**與**機率估值**，在市場定價之前預判趨勢。

**[English](../README.md)** | **[日本語](README.ja.md)** | **[한국어](README.ko.md)**

---

## 🚀 核心架構

引擎運作於三層智慧堆疊：

### 1. 時間視野感測層（多時間框架）
系統跨三個時間視野監控資產：
- **短期**：流動性、市場情緒、選擇權偏度
- **中期**：基本面轉折點（如 AI ROI、推論轉型）
- **長期**：範式轉移（如演算法效率、護城河侵蝕）

### 2. 風險緩解層（紅藍隊對抗）
為對抗確認偏誤，引擎採用「紅藍隊」分析：
- **藍隊**：收集支持投資論點的證據
- **紅隊**：主動搜尋「熔斷開關」（證偽證據），觸發強制退出

### 3. 估值層（三角驗證）
系統避免單點價格目標，採用三種模型的三角驗證：
- **機率情境模型**：加權多種結果（牛市/基準/熊市）
- **兩階段 DCF**：基於成長衰減預測內在價值
- **相對倍數法**：與同業基準比較

---

## 🛠️ 核心功能

| 功能 | 說明 |
|------|------|
| **策略性領先指標** | 專門追蹤高影響力指標（CUDA 主導地位、雲端資本支出 ROI） |
| **保證金壓力測試** | 整合槓桿/保證金數據，監控維持保證金與追繳風險 |
| **Obsidian 整合** | 自動生成結構化週報至個人知識庫 |
| **量化梯度** | 使用綠→黃→紅梯度系統，取代二元觸發器感測趨勢衰減 |
| **紅藍隊分析** | 透過對抗性論點測試，對抗確認偏誤 |
| **多模型估值** | 三角驗證 DCF、機率情境、相對倍數 |

---

## 📂 專案結構

```
investment-engine/
├── investment_watcher.py      # 週度感測核心協調器
├── valuation_engine.py       # 數學核心（DCF/機率/相對）
├── data/
│   └── monitor-registry.json # 「大腦」- 標的論點與熔斷開關
├── Weekly_Reports/           # AI 生成的機構備忘錄
└── docs/
    ├── README.zh-TW.md       # 繁體中文文檔
    ├── README.ja.md          # 日本語ドキュメント
    └── README.ko.md          # 한국어 문서
```

---

## 🎯 目標策略

專為高確信度、高成長投資組合優化：

| 產業 | 關注領域 |
|------|---------|
| **AI 基礎設施** | 運算、網路、軟體護城河 |
| **戰略資源** | 能源、稀土 |
| **顛覆性科技** | 機器人、金融科技、太空 |

---

## 🚦 快速開始

### 系統需求

- Python 3.10+
- Node.js（用於 Obsidian 整合）

### 安裝

```bash
# 複製專案
git clone https://github.com/bounce12340/investment-engine.git
cd investment-engine

# 安裝依賴
pip install -r requirements.txt

# 設定環境
cp .env.example .env
# 編輯 .env 填入 API 金鑰
```

### 快速啟動

```python
from investment_watcher import InvestmentWatcher

# 初始化引擎
watcher = InvestmentWatcher(config_path="data/monitor-registry.json")

# 執行週度分析
report = watcher.run_weekly_analysis()

# 匯出至 Obsidian
watcher.export_to_obsidian(vault_path="~/Documents/Vault")
```

---

## 📊 輸出範例

### 週報結構

```
# NVDA 週度分析 - 2026-W15

## 🟢 狀態：看漲（評分：8.2/10）

### 領先指標
- CUDA 主導地位：92%（↑ +2%）
- 資料中心營收成長：年增 +217%
- Blackwell 採用率：佔新部署 45%

### 紅隊警報
- ⚠️ 中國出口限制影響：Q2 營收 -$2B
- ⚠️ AMD MI300X 在企業市場的競爭壓力

### 估值三角驗證
| 模型 | 目標價 | 信心度 |
|------|--------|--------|
| DCF（兩階段）| $1,150 | 高 |
| 機率情境 | $1,080 | 中 |
| 相對倍數 | $950 | 中 |

### 熔斷開關狀態
| 觸發條件 | 目前 | 閾值 | 狀態 |
|----------|------|------|------|
| CUDA 份額 < 80% | 92% | 80% | 🟢 安全 |
| 毛利率 < 60% | 75.5% | 60% | 🟢 安全 |
```

---

## 🧪 測試

```bash
# 執行測試套件
pytest tests/

# 執行保證金壓力測試
python -m tests.stress_test --ticker NVDA
```

---

## 📄 授權

MIT License - 詳見 [LICENSE](../LICENSE)。

---

## 🤝 貢獻

歡迎貢獻！請閱讀 [CONTRIBUTING.md](../CONTRIBUTING.md) 了解規範。

---

## 📚 文檔

- **[English](../README.md)** - 英文
- **繁體中文** - 你在這裡
- **[日本語](README.ja.md)** - 日文
- **[한국어](README.ko.md)** - 韓文

---

*專為高精度風險管理與策略性超額報酬而開發。*