from __future__ import annotations

from datetime import date
from pathlib import Path

from investment_engine.analysis.performance import compute_performance_stats
from investment_engine.analysis.red_blue_team import stress_test
from investment_engine.analysis.technicals import MIN_HISTORY, compute_technical_snapshot
from investment_engine.data_sources.registry import load_ticker
from investment_engine.data_sources.yfinance_source import (
    get_current_price,
    get_price_history,
)
from investment_engine.models import (
    PerformanceStats,
    TechnicalSnapshot,
    TickerThesis,
    ValuationResult,
    WeeklyReport,
)
from investment_engine.valuation import (
    probabilistic_valuation,
    relative_valuation,
    two_stage_dcf,
)

BENCHMARK_TICKER = "VOO"


class InvestmentWatcher:
    def __init__(self, registry_path: str | Path):
        self.registry_path = Path(registry_path)

    def load(self, ticker: str) -> TickerThesis:
        return load_ticker(self.registry_path, ticker)

    def valuate(self, thesis: TickerThesis) -> ValuationResult:
        v = thesis.valuation_inputs
        return ValuationResult(
            dcf_target=two_stage_dcf(v.dcf),
            probabilistic_target=probabilistic_valuation(v.scenarios),
            relative_target=relative_valuation(v.relative),
        )

    def build_report(
        self,
        ticker: str,
        as_of: date | None = None,
        fetch_price: bool = True,
        fetch_performance: bool = True,
        fetch_technicals: bool = True,
    ) -> WeeklyReport:
        thesis = self.load(ticker)
        valuation = self.valuate(thesis)

        today = as_of or date.today()
        iso_year, iso_week, _ = today.isocalendar()

        price: float | None = None
        if fetch_price:
            try:
                price = get_current_price(ticker)
            except Exception:
                price = None

        performance: PerformanceStats | None = None
        technicals: TechnicalSnapshot | None = None

        if fetch_performance or fetch_technicals:
            try:
                prices = get_price_history(ticker, period="3y")
            except Exception:
                prices = None

            bench = None
            if fetch_performance and prices is not None:
                try:
                    bench = get_price_history(BENCHMARK_TICKER, period="3y")
                except Exception:
                    bench = None

            if fetch_performance and prices is not None and bench is not None:
                try:
                    stats = compute_performance_stats(prices, bench)
                    if stats.periods:
                        performance = stats
                except Exception:
                    performance = None

            if fetch_technicals and prices is not None and len(prices) >= MIN_HISTORY:
                try:
                    technicals = compute_technical_snapshot(prices)
                except Exception:
                    technicals = None

        return WeeklyReport(
            ticker=thesis.ticker,
            name=thesis.name,
            as_of=today,
            year=iso_year,
            week=iso_week,
            current_price=price,
            valuation=valuation,
            thesis=thesis.thesis,
            leading_indicators=thesis.leading_indicators,
            kill_switches=thesis.kill_switches,
            bull_points=thesis.bull_points,
            bear_points=thesis.bear_points,
            stress_test=stress_test(
                thesis.bull_points, thesis.bear_points, thesis.kill_switches
            ),
            performance=performance,
            technicals=technicals,
        )
