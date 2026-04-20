# Investment-Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)

**[English](../README.md)** | **[繁體中文](README.zh-TW.md)** | **[日本語](README.ja.md)** | **한국어**

고확신도 주식 테제를 추적하기 위한 경량 프레임워크입니다. **삼각 측량
밸류에이션**, **Kill-switch 모니터링**, **적대적 Red/Blue 테제 스트레스
테스트**, **Obsidian 연동 주간 리포트**를 제공합니다.

워크플로는 단순합니다. 티커별 테제를 담은 JSON 파일 (_모니터링 registry_)
하나만 관리하면, 엔진이 세 개의 독립적인 주가 목표를 계산하고, 반증
트리거를 점검하고, 테제를 0–10점으로 채점한 뒤, Markdown 메모를
Obsidian 볼트에 기록합니다. 선택적으로 macOS launchd 스케줄로 정기
실행할 수도 있습니다.

---

## 목차

- [기능](#기능)
- [설치](#설치)
- [빠른 시작](#빠른-시작)
- [CLI 레퍼런스](#cli-레퍼런스)
- [스케줄링 (macOS)](#스케줄링-macos)
- [Registry 포맷](#registry-포맷)
- [출력 예시](#출력-예시)
- [프로젝트 구조](#프로젝트-구조)
- [Scope](#scope)
- [개발](#개발)
- [라이선스](#라이선스)

---

## 기능

**1. 모니터링 registry.** 티커별 테제를 하나의 JSON 파일
(`data/monitor-registry.json`) 에 보관합니다. 단/중/장기 내러티브,
수동 관리하는 leading indicators, kill-switches, Red/Blue 논점,
밸류에이션 입력값을 포함합니다.

**2. 삼각 측량 밸류에이션.** 티커마다 세 개의 독립적인 가격 목표를
계산하여 하나의 삼각화 추정치로 평균냅니다.
- **Two-Stage DCF** — 고성장 기간 이후 terminal growth (Gordon growth 모델)
- **Probabilistic scenarios** — Bull / Base / Bear 확률 가중 (합 = 1.0)
- **Relative multiples** — 티커 지표 × 동종업계 중앙값 배수

**3. Kill-switches.** 임계값 기반 반증 체크. 각 스위치는 방향
(`below` / `above`) 과 현재값을 가지며, 임계값을 넘으면 발동되어
테제 위반을 알립니다.

**4. 테제 스트레스 테스트.** 각 리포트는 **Conviction score (0–10)** 과
프로세스 위생 flag 목록을 포함합니다. 채점은 결정론적이며 투명합니다.

| 요인 | 효과 |
|------|------|
| 안전한 kill-switch | 개당 +1 (최대 +3) |
| 발동된 kill-switch | 개당 −2 |
| Bull/Bear 비율 ∈ [0.5, 2.0] | +1 (균형) |
| Bear points ≥ 3 / ≥ 5 | +1 / +2 (Red 팀 강도) |

Flag (ℹ️ info / ⚠️ warning / 🔴 alert):
- `No red team — confirmation bias risk` (bear 없음)
- `Thin red team — only N bear point(s)` (bear < 2)
- `No blue team — negative thesis only` (bull 없음)
- `Bull-biased: N.N× bull-to-bear ratio` (비율 > 3×)
- `N kill-switch(es) triggered — thesis violation`
- `No red flags — thesis well-balanced` (다른 flag 없을 때만)

**5. Obsidian 리포트.** Markdown 메모는
`{vault}/Weekly_Reports/{TICKER}_{YYYY}-W{WW}.md` 에 저장됩니다.
ISO 주차 번호를 사용합니다.

**6. 역사적 성과.** 각 티커에 대해 Yahoo Finance 에서 3년치 일일 종가를
가져와, 1y / 3y 윈도우에서 **Sharpe, Sortino, 최대 낙폭, 연간 변동성,
VOO 대비 Jensen α / β** (무위험 수익률 = 4.0%) 를 계산합니다.
리포트와 `analyze` CLI 에 "Historical Performance" 섹션이 추가됩니다.

**7. 테크니컬 스냅샷.** 동일한 3년 종가로부터 **RSI(14), MACD (12/26/9),
50일 및 200일 이동 평균, MA 괴리율** 을 계산합니다. RSI ≥ 70 / ≤ 30 은
과매수 / 과매도로 자동 태그됩니다. 순수 pandas 구현 — 새 의존성 없음.

**8. 펀더멘털 대조.** 각 티커에 대해 yfinance 에서
**trailing/forward P/E, 시가총액, live β, 애널리스트 컨센서스 목표가, 의견,
배당수익률** 을 실시간으로 가져옵니다. 또한 registry 의 DCF 가정
(FCF, 발행 주식수) 을 live 값과 대조하여, FCF 편차가 25% 를 넘거나
주식수 편차가 5% 를 넘으면 경고 플래그를 띄워 등록값 노후화를 드러냅니다.

**9. 실시간 주가.** `yfinance` 를 통해 Yahoo Finance 에서 현재 가격을
가져오며, 오프라인 시에는 우아하게 폴백합니다.

**10. 스케줄링.** macOS `launchd` 로 일간 / 주간 / 월간 반복 실행.
대화형 프롬프트 또는 플래그로 설정.

---

## 설치

```bash
git clone https://github.com/bounce12340/investment-engine
cd investment-engine
python -m venv .venv && source .venv/bin/activate
pip install -e .

cp .env.example .env      # 필요 시 OBSIDIAN_VAULT 수정
```

Python 3.10+ 필요. 스케줄링은 macOS 전용입니다.

---

## 빠른 시작

```bash
# NVDA 콘솔 요약
investment-engine analyze NVDA

# Obsidian 볼트에 주간 리포트 작성
investment-engine weekly NVDA --vault /Users/chunghsutsai/Vault
```

오프라인에서는 `--no-price` 를 붙이면 yfinance 호출을 건너뜁니다.

---

## CLI 레퍼런스

### `analyze TICKER`
콘솔 요약 출력: 삼각 밸류에이션, kill-switch 상태, 역사적 성과, 테크니컬 스냅샷, 펀더멘털 대조, 테제 스트레스 테스트.

| 플래그 | 기본값 | 설명 |
|--------|--------|------|
| `--registry PATH` | `data/monitor-registry.json` | 사용자 정의 registry 파일 |
| `--no-price` | off | yfinance 실시간 가격 조회 건너뛰기 |
| `--no-performance` | off | 3년 히스토리 조회 (Sharpe / α / β) 건너뛰기 |
| `--no-technicals` | off | 테크니컬 지표 (RSI / MACD / MA) 건너뛰기 |
| `--no-fundamentals` | off | 펀더멘털 대조 건너뛰기 |

### `weekly TICKER`
Markdown 리포트를 생성하여 Obsidian 볼트에 기록합니다.

| 플래그 | 기본값 | 설명 |
|--------|--------|------|
| `--registry PATH` | `data/monitor-registry.json` | 사용자 정의 registry 파일 |
| `--vault PATH` | `$OBSIDIAN_VAULT` 또는 `/Users/chunghsutsai/Vault` | 대상 볼트 |
| `--no-price` | off | yfinance 실시간 가격 조회 건너뛰기 |
| `--no-performance` | off | 3년 히스토리 조회 (Sharpe / α / β) 건너뛰기 |
| `--no-technicals` | off | 테크니컬 지표 (RSI / MACD / MA) 건너뛰기 |
| `--no-fundamentals` | off | 펀더멘털 대조 건너뛰기 |

출력 경로: `{vault}/Weekly_Reports/{TICKER}_{YYYY}-W{WW}.md`.

### `schedule create` / `list` / `show` / `remove`
아래 [스케줄링 (macOS)](#스케줄링-macos) 참고.

---

## 스케줄링 (macOS)

`launchd` 를 통한 반복 실행. 기본값은 대화형 —
`investment-engine schedule create` 실행 시 빈도, 시간, 티커를 순차적으로
물어봅니다. 각 스케줄은 plist + 래퍼 스크립트 + 로그 파일을 한 세트로
생성합니다.

```bash
# 대화형
investment-engine schedule create

# 매일 09:00 에 registry 전체 티커 실행
investment-engine schedule create --name morning --frequency daily \
    --time 09:00 --yes

# 매주 월요일 08:30 에 특정 티커만
investment-engine schedule create --name mon-brief --frequency weekly \
    --time 08:30 --weekday 1 --tickers NVDA,TSM,GOOGL --yes

# 매월 1일 07:00
investment-engine schedule create --name month-end --frequency monthly \
    --time 07:00 --day 1 --yes

# 관리
investment-engine schedule list
investment-engine schedule show morning
investment-engine schedule remove morning
```

**`schedule create` 플래그:**

| 플래그 | 설명 |
|--------|------|
| `--name SLUG` | 짧은 식별자 (소문자 + 하이픈) |
| `--frequency daily\|weekly\|monthly` | |
| `--time HH:MM` | 24 시간 표기 |
| `--weekday 0..6` | 0=일 … 6=토 (weekly 전용, launchd 규약) |
| `--day 1..31` | (monthly 전용) |
| `--tickers A,B,C` | 부분집합 지정; 공백 = 전체 |
| `--command weekly\|analyze` | 기본값 `weekly` |
| `--vault PATH` | 볼트 재정의 |
| `--yes` / `-y` | launchd 로드 전 확인 생략 |

**생성되는 산출물:**
- 래퍼: `~/Library/Application Support/investment-engine/<name>.sh`
- Plist: `~/Library/LaunchAgents/com.investment-engine.<name>.plist`
- 로그: `~/Library/Logs/investment-engine-<name>.log`

래퍼는 `|| echo "[warn] X failed"` 로 모든 티커를 순회하므로,
하나의 yfinance 오류가 다른 티커 실행을 중단시키지 않습니다.

---

## Registry 포맷

`data/monitor-registry.json` 에는 NVDA 샘플과 함께 9개 티커
(PLTR, GOOGL, MP, NU, RCAT, TSLA, TSM, UUUU, VOO) 가 포함되어 있습니다.
최상위 키는 티커 심볼이며, 각 엔트리는 아래 스키마를 따릅니다.

| 필드 | 설명 |
|------|------|
| `ticker` | 티커 심볼 (키와 일치해야 함) |
| `name` | 표시 이름 (예: `NVIDIA Corporation`) |
| `sector` | 자유 형식 섹터 태그 |
| `thesis.short_term` / `medium_term` / `long_term` | 기간별 내러티브 |
| `leading_indicators[].{name,value,unit,description}` | 수동 관리 지표 |
| `kill_switches[].{name,metric,threshold,direction,current_value}` | `direction` 은 `below` 또는 `above` |
| `bull_points[]` / `bear_points[]` | Red/Blue 논점 (문자열 배열) |
| `valuation_inputs.dcf` | `fcf`, `growth_high`, `growth_terminal`, `years_high`, `wacc`, `shares` |
| `valuation_inputs.scenarios[]` | `name`, `price`, `probability` — 합 1.0 |
| `valuation_inputs.relative` | `ticker_metric`, `peer_median`, `target_metric` (예: `EPS × peer P/E`) |

Pydantic 이 로드 시 모든 엔트리를 검증합니다. 확률 합, DCF 수렴 조건
(WACC > terminal growth), direction 열거값은 모두 강제됩니다.

---

## 출력 예시

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

               Fundamentals Reality-Check
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Metric                     ┃                   Value ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Trailing P/E               │                   41.24 │
│ Forward P/E                │                   17.98 │
│ Market Cap                 │                $4911.1B │
│ Live β (yfinance)          │                    2.33 │
│ Analyst target (mean)      │                 $268.61 │
│ Analyst rec (1=SB/5=SS)    │                    1.29 │
│ FCF registry / live / Δ    │ $60.0B / $58.1B / -3.1% │
│ Shares registry / live / Δ │ 24.60B / 24.30B / -1.2% │
└────────────────────────────┴─────────────────────────┘
  ℹ️ Analyst consensus: $268.61 (+32.9% vs current, 56 analysts)

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

주간 Markdown 출력은 동일한 정보에 더해 Leading-Indicators 표,
Red/Blue 팀 논점, 테제 스트레스 테스트 flag 를 포함합니다.
Obsidian 볼트 내에서 인덱싱 및 양방향 링크에 적합한 형식입니다.

---

## 프로젝트 구조

```
investment-engine/
├── investment_engine/
│   ├── valuation/            # DCF, probabilistic, relative
│   ├── data_sources/         # yfinance 래퍼 + registry 로더
│   ├── analysis/             # kill_switches, leading_indicators, red_blue_team
│   ├── reports/              # Markdown 템플릿 + Obsidian writer
│   ├── models.py             # pydantic: Thesis, KillSwitch, StressTest, …
│   ├── watcher.py            # InvestmentWatcher 오케스트레이터
│   ├── scheduler.py          # launchd plist / 래퍼 생성
│   └── cli.py                # typer 엔트리 포인트
├── data/monitor-registry.json   # 샘플: 10개 티커
└── tests/                    # 각 모듈을 커버하는 36개 테스트
```

---

## Scope

**완료됨:**
- 삼각 측량 밸류에이션 (DCF + Probabilistic + Relative)
- 정적 kill-switch 체크
- 결정론적 Red/Blue 테제 스트레스 테스트 + Conviction score
- 역사적 성과 (Sharpe / Sortino / 최대 낙폭 / VOO 대비 α-β)
- 테크니컬 스냅샷 (RSI(14), MACD(12/26/9), 50일 / 200일 MA)
- 펀더멘털 대조 (registry 가정 vs live FCF / 주식수; 애널리스트 컨센서스)
- Obsidian Markdown 출력
- yfinance 실시간 주가
- macOS launchd 스케줄링

**범위 외 (향후 작업):**
- LLM 기반 정성 분석 (bull/bear 논점 자동 생성)
- 전략 지표의 실시간 수집 (CUDA 점유율, NdPr 가격 등)
- 마진 스트레스 테스트 (레버리지 / 유지 마진 시뮬레이션)
- Conviction score 시계열 추적
- Windows/Linux 스케줄링 (launchd 는 macOS 전용)

---

## 개발

```bash
pip install -e ".[dev]"
pytest tests/                 # 36 tests
```

테스트는 yfinance 를 모킹하여 실제 볼트나 launchd 에는 접근하지 않습니다.
전체 스위트가 부작용 없이 1초 이내에 실행됩니다.

---

## 라이선스

MIT — [LICENSE](../LICENSE) 참조.
