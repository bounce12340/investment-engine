from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class LeadingIndicator(BaseModel):
    name: str
    value: float
    unit: str = ""
    description: str = ""


class KillSwitch(BaseModel):
    name: str
    metric: str
    threshold: float
    direction: Literal["below", "above"]
    current_value: float

    @property
    def triggered(self) -> bool:
        if self.direction == "below":
            return self.current_value < self.threshold
        return self.current_value > self.threshold


class Scenario(BaseModel):
    name: str
    price: float
    probability: float = Field(ge=0.0, le=1.0)


class DCFInputs(BaseModel):
    fcf: float
    growth_high: float
    growth_terminal: float
    years_high: int = Field(ge=1)
    wacc: float
    shares: float = Field(gt=0)


class RelativeInputs(BaseModel):
    ticker_metric: float
    peer_median: float
    target_metric: str


class ValuationInputs(BaseModel):
    dcf: DCFInputs
    scenarios: list[Scenario]
    relative: RelativeInputs

    @field_validator("scenarios")
    @classmethod
    def _probabilities_sum_to_one(cls, scenarios: list[Scenario]) -> list[Scenario]:
        total = sum(s.probability for s in scenarios)
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"scenario probabilities must sum to 1.0, got {total}")
        return scenarios


class ThesisNarrative(BaseModel):
    short_term: str
    medium_term: str
    long_term: str


class TickerThesis(BaseModel):
    ticker: str
    name: str
    sector: str
    thesis: ThesisNarrative
    leading_indicators: list[LeadingIndicator]
    kill_switches: list[KillSwitch]
    bull_points: list[str]
    bear_points: list[str]
    valuation_inputs: ValuationInputs


class ValuationResult(BaseModel):
    dcf_target: float
    probabilistic_target: float
    relative_target: float

    @property
    def triangulated(self) -> float:
        return (self.dcf_target + self.probabilistic_target + self.relative_target) / 3


class StressTestFlag(BaseModel):
    severity: Literal["info", "warning", "alert"]
    message: str


class ThesisStressTest(BaseModel):
    bull_count: int
    bear_count: int
    kill_switches_triggered: int
    kill_switches_total: int
    conviction_score: float
    flags: list[StressTestFlag]

    @property
    def bull_bear_ratio(self) -> float | None:
        if self.bear_count == 0:
            return None
        return self.bull_count / self.bear_count


class PeriodPerformance(BaseModel):
    period: str  # e.g. "1y", "3y"
    annualized_return: float
    annualized_volatility: float
    sharpe: float
    sortino: float
    max_drawdown: float
    alpha_vs_voo: float
    beta_vs_voo: float


class PerformanceStats(BaseModel):
    periods: list[PeriodPerformance]


class TechnicalSnapshot(BaseModel):
    price: float
    rsi_14: float
    macd: float
    macd_signal: float
    macd_histogram: float
    ma_50: float
    ma_200: float
    distance_from_ma50_pct: float
    distance_from_ma200_pct: float


class FundamentalsCheck(BaseModel):
    trailing_pe: float | None = None
    forward_pe: float | None = None
    market_cap: float | None = None
    live_beta: float | None = None
    dividend_yield_pct: float | None = None

    analyst_target_mean: float | None = None
    analyst_target_median: float | None = None
    analyst_count: int | None = None
    analyst_recommendation: float | None = None

    registry_fcf: float | None = None
    live_fcf: float | None = None
    fcf_delta_pct: float | None = None

    registry_shares: float | None = None
    live_shares: float | None = None
    shares_delta_pct: float | None = None

    flags: list[str] = []


class WeeklyReport(BaseModel):
    ticker: str
    name: str
    as_of: date
    year: int
    week: int
    current_price: float | None
    valuation: ValuationResult
    thesis: ThesisNarrative
    leading_indicators: list[LeadingIndicator]
    kill_switches: list[KillSwitch]
    bull_points: list[str]
    bear_points: list[str]
    stress_test: ThesisStressTest
    performance: PerformanceStats | None = None
    technicals: TechnicalSnapshot | None = None
    fundamentals: FundamentalsCheck | None = None
