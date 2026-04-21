import numpy as np
import pandas as pd
import pytest

from investment_engine.analysis.technicals import (
    MIN_HISTORY,
    compute_technical_snapshot,
)


def _series(values: list[float]) -> pd.Series:
    dates = pd.date_range(end="2026-04-20", periods=len(values), freq="B")
    return pd.Series(values, index=dates, dtype=float)


def test_rejects_too_short_history():
    prices = _series([100.0] * 100)
    with pytest.raises(ValueError, match="at least"):
        compute_technical_snapshot(prices)


def test_monotonic_uptrend_rsi_near_100_and_above_mas():
    prices = _series(list(np.linspace(100, 300, MIN_HISTORY + 20)))
    snap = compute_technical_snapshot(prices)
    assert snap.rsi_14 > 95
    assert snap.distance_from_ma50_pct > 0
    assert snap.distance_from_ma200_pct > 0
    assert snap.macd > 0


def test_monotonic_downtrend_rsi_near_0_and_below_mas():
    prices = _series(list(np.linspace(300, 100, MIN_HISTORY + 20)))
    snap = compute_technical_snapshot(prices)
    assert snap.rsi_14 < 5
    assert snap.distance_from_ma50_pct < 0
    assert snap.distance_from_ma200_pct < 0
    assert snap.macd < 0


def test_flat_prices_rsi_is_nan_safe():
    # Flat series: zero gains and zero losses → RSI degenerates, but the
    # snapshot must still produce finite, displayable numbers.
    prices = _series([100.0] * (MIN_HISTORY + 20))
    snap = compute_technical_snapshot(prices)
    assert snap.ma_50 == pytest.approx(100.0)
    assert snap.ma_200 == pytest.approx(100.0)
    assert snap.distance_from_ma50_pct == pytest.approx(0.0)
    assert snap.distance_from_ma200_pct == pytest.approx(0.0)
    assert snap.macd == pytest.approx(0.0, abs=1e-9)
    # RSI must be a finite number (50.0 is the canonical neutral value), not NaN.
    assert snap.rsi_14 == pytest.approx(50.0)


def test_zero_prices_do_not_divide_by_zero():
    # Pathological input: all-zero prices would make the MAs zero and the
    # old distance-from-MA calculation raise ZeroDivisionError.
    prices = _series([0.0] * (MIN_HISTORY + 20))
    snap = compute_technical_snapshot(prices)
    assert snap.ma_50 == pytest.approx(0.0)
    assert snap.ma_200 == pytest.approx(0.0)
    assert snap.distance_from_ma50_pct == pytest.approx(0.0)
    assert snap.distance_from_ma200_pct == pytest.approx(0.0)


def test_ma50_and_ma200_are_actually_the_means():
    n = MIN_HISTORY + 50
    rng = np.random.default_rng(42)
    prices = _series(list(100 + rng.normal(0, 1, n).cumsum()))
    snap = compute_technical_snapshot(prices)
    assert snap.ma_50 == pytest.approx(prices.iloc[-50:].mean(), abs=1e-6)
    assert snap.ma_200 == pytest.approx(prices.iloc[-200:].mean(), abs=1e-6)


def test_recent_spike_lifts_price_above_ma50():
    n = MIN_HISTORY + 10
    prices_list = [100.0] * (n - 5) + [150.0] * 5
    prices = _series(prices_list)
    snap = compute_technical_snapshot(prices)
    assert snap.price == 150.0
    assert snap.distance_from_ma50_pct > 0
