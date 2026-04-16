# 🛡️ Investment-Engine: 기관급 퀀트-펀더멘털 하이브리드 플랫폼

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)

기관급 투자 모니터링 및 밸류에이션 프레임워크. 정량적 리스크 센싱과 정성적 펀더멘털 분석을 결합.

후행 지표(주가수익비율 등)에 의존하는 전통적 포트폴리오와 달리, **Investment-Engine**은**선행 지표**, **패러다임 시프트**, **확률적 밸류에이션**에 집중하여 시장 가격 반영 전에 움직임을 예측합니다.

**[English](../README.md)** | **[繁體中文](README.zh-TW.md)** | **[日本語](README.ja.md)**

---

## 🚀 핵심 아키텍처

엔진은 3계층 인텔리전스 스택으로 작동:

### 1. 호라이즌 센싱 계층 (멀티 타임프레임)
세 가지 시간 지평에서 자산을 모니터링:
- **단기**: 유동성, 센티먼트, 옵션 스큐
- **중기**: 펀더멘털 전환점 (예: AI ROI, 추론 전환)
- **장기**: 패러다임 시프트 (예: 알고리즘 효율성, 해자 침식)

### 2. 리스크 완화 계층 (레드-블루 팀 분석)
확증 편향에 대항하기 위해 "레드-블루 팀" 분석 사용:
- **블루 팀**: 투자 논제를 지지하는 증거 수집
- **레드 팀**: 강제 청산을 트리거하는 "킬 스위치"(반증 거)를 적극적으로 탐색

### 3. 밸류에이션 계층 (삼각 측량)
단일 포인트 가격 목표 대신 세 가지 모델의 삼각 측량 사용:
- **확률 시나리오 모델**: 여러 결과(강세/기준/약세) 가중
- **2단계 DCF**: 성장 감쇠 기반 내재 가치 예측
- **상대적 배수**: 업계 피어와 비교

---

## 🛠️ 주요 기능

| 기능 | 설명 |
|------|------|
| **전략적 선행 지표** | 고영향 지표 전문 추적 (CUDA 지배력, 클라우드 CapEx ROI) |
| **마진 스트레스 테스트** | 레버리지/마진 데이터 통합으로 유지 마진 및 마진콜 리스크 모니터링 |
| **Obsidian 통합** | 구조화된 주간 보고서를 개인 지식 베이스에 자동 생성 |
| **정량적 그라데이션** | 이진 트리거 대신 녹→황→적 그라데이션으로 트렌드 감쇠 감지 |
| **레드-블루 팀 분석** | 적대적 논제 테스트로 확증 편향에 대항 |
| **멀티 모델 밸류에이션** | DCF, 확률 시나리오, 상대적 배수 삼각 측량 |

---

## 📂 프로젝트 구조

```
investment-engine/
├── investment_watcher.py      # 주간 센싱 코어 오케스트레이터
├── valuation_engine.py       # 수학 코어 (DCF/확률/상대)
├── data/
│   └── monitor-registry.json # "뇌" - 티커별 논제와 킬 스위치
├── Weekly_Reports/           # AI 생성 기관 메모
└── docs/
    ├── README.zh-TW.md       # 繁體中文
    ├── README.ja.md          # 日本語
    └── README.ko.md          # 한국어 (여기)
```

---

## 🎯 타겟 전략

고확신, 고성장 포트폴리오에 최적화:

| 섹터 | 집중 영역 |
|------|-----------|
| **AI 인프라** | 컴퓨트, 네트워킹, 소프트웨어 해자 |
| **전략 자원** | 에너지, 희토류 |
| **파괴적 기술** | 로봇공학, 핀테크, 우주 |

---

## 🚦 빠른 시작

### 전제 조건

- Python 3.10+
- Node.js (Obsidian 통합용)

### 설치

```bash
# 리포지토리 클론
git clone https://github.com/bounce12340/investment-engine.git
cd investment-engine

# 의존성 설치
pip install -r requirements.txt

# 환경 설정
cp .env.example .env
# .env 편집하여 API 키 설정
```

### 빠른 시작

```python
from investment_watcher import InvestmentWatcher

# 엔진 초기화
watcher = InvestmentWatcher(config_path="data/monitor-registry.json")

# 주간 분석 실행
report = watcher.run_weekly_analysis()

# Obsidian으로 내보내기
watcher.export_to_obsidian(vault_path="~/Documents/Vault")
```

---

## 📊 출력 예시

### 주간 보고서 구조

```
# NVDA 주간 분석 - 2026-W15

## 🟢 상태: 강세 (점수: 8.2/10)

### 선행 지표
- CUDA 지배력: 92% (↑ +2%)
- 데이터센터 매출 성장: 전년비 +217%
- Blackwell 채택: 신규 배포의 45%

### 레드 팀 알림
- ⚠️ 중국 수출 제재 영향: Q2 매출 -$2B
- ⚠️ 엔터프라이즈에서 AMD MI300X 경쟁 압력

### 밸류에이션 삼각 측량
| 모델 | 목표가 | 신뢰도 |
|------|--------|--------|
| DCF (2단계) | $1,150 | 높음 |
| 확률적 | $1,080 | 중간 |
| 상대적 | $950 | 중간 |

### 킬 스위치 상태
| 트리거 | 현재 | 임계값 | 상태 |
|--------|------|--------|------|
| CUDA 점유율 < 80% | 92% | 80% | 🟢 안전 |
| GM% < 60% | 75.5% | 60% | 🟢 안전 |
```

---

## 🧪 테스트

```bash
# 테스트 스위트 실행
pytest tests/

# 마진 스트레스 테스트 실행
python -m tests.stress_test --ticker NVDA
```

---

## 📄 라이선스

MIT License - [LICENSE](../LICENSE) 참조.

---

## 🤝 기여

기여를 환영합니다! [CONTRIBUTING.md](../CONTRIBUTING.md)를 참조하세요.

---

## 📚 문서

- **[English](../README.md)** - 영어
- **[繁體中文](README.zh-TW.md)** - 번체 중국어
- **[日本語](README.ja.md)** - 일본어
- **한국어** - 여기

---

*고정밀 리스크 관리와 전략적 알파 창출을 위해 개발.*