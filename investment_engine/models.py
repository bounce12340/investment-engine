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
