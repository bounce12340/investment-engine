import numpy as np
import pandas as pd
import pytest

from investment_engine.analysis.performance import (
    compute_performance_stats,
    compute_period_performance,
)
from investment_engine.models import PerformanceStats, PeriodPerformance


def _price_series(n_days: int, daily_return: float = 0.0005, seed: int = 0) -> pd.Series:
    rng = np.random.default_rng(seed)
    shocks = rng.normal(loc=daily_return, scale=0.01, size=n_days)
    prices = 100 * np.cumprod(1 + shocks)
    dates = pd.date_range(end="2026-04-20", periods=n_days, freq="B")
    return pd.Series(prices, index=dates)


def test_compute_period_performance_produces_sensible_values():
    prices = _price_series(252)
    bench = _price_series(252, daily_return=0.0003, seed=1)
    result = compute_period_performance("1y", prices, bench)
    assert isinstance(result, PeriodPerformance)
    assert result.period == "1y"
    assert -1.0 < result.annualized_return < 5.0
    assert 0.0 < result.annualized_volatility < 2.0
    assert result.max_drawdown <= 0.0
    assert result.max_drawdown >= -1.0


def test_higher_return_gives_higher_sharpe():
    bench = _price_series(252, daily_return=0.0003, seed=99)
    low = _price_series(252, daily_return=0.0001, seed=11)
    high = _price_series(252, daily_return=0.0015, seed=11)
    low_result = compute_period_performance("1y", low, bench)
    high_result = compute_period_performance("1y", high, bench)
    assert high_result.sharpe > low_result.sharpe


def test_zero_volatility_returns_zero_sharpe():
    dates = pd.date_range(end="2026-04-20", periods=252, freq="B")
    flat_prices = pd.Series(np.ones(252) * 100.0, index=dates)
    bench = _price_series(252, seed=5)
    result = compute_period_performance("1y", flat_prices, bench)
    assert result.sharpe == 0.0
    assert result.sortino == 0.0


def test_max_drawdown_on_monotonic_decline():
    dates = pd.date_range(end="2026-04-20", periods=60, freq="B")
    declining = pd.Series(np.linspace(100, 50, 60), index=dates)
    bench = _price_series(60, seed=3)
    result = compute_period_performance("1y", declining, bench)
    assert result.max_drawdown == pytest.approx(-0.5, abs=1e-6)


def test_compute_performance_stats_returns_two_periods():
    # Need >= 3y of data so both 1y and 3y windows populate
    prices = _price_series(252 * 3 + 50, seed=7)
    bench = _price_series(252 * 3 + 50, seed=8)
    stats = compute_performance_stats(prices, bench)
    assert isinstance(stats, PerformanceStats)
    labels = [p.period for p in stats.periods]
    assert labels == ["1y", "3y"]


def test_compute_performance_stats_skips_period_with_too_little_data():
    # Only ~6 months of data — 1y and 3y slices will both be under 20 points after slicing? No:
    # _slice_period returns whatever falls within the window. For 6 months of data,
    # a 1y window covers everything (~125 points) and a 3y window also covers everything.
    # Use a single day instead to force skip.
    dates = pd.date_range(end="2026-04-20", periods=10, freq="B")
    prices = pd.Series(np.linspace(100, 110, 10), index=dates)
    bench = pd.Series(np.linspace(100, 105, 10), index=dates)
    stats = compute_performance_stats(prices, bench)
    assert stats.periods == []


def test_alpha_is_positive_when_ticker_outperforms_benchmark():
    high = _price_series(252 * 2, daily_return=0.002, seed=1)
    low_bench = _price_series(252 * 2, daily_return=0.0005, seed=2)
    stats = compute_performance_stats(high, low_bench)
    assert any(p.alpha_vs_voo > 0 for p in stats.periods)
