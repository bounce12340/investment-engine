from pathlib import Path

from investment_engine.analysis.fundamentals import compute_fundamentals_check
from investment_engine.data_sources.registry import load_ticker

REGISTRY = Path(__file__).resolve().parent.parent / "data" / "monitor-registry.json"


def _nvda():
    return load_ticker(REGISTRY, "NVDA")


def _complete_info_dict() -> dict:
    return {
        "trailingPE": 65.2,
        "forwardPE": 42.1,
        "marketCap": 5_000_000_000_000,
        "beta": 2.1,
        "dividendYield": 0.0002,
        "targetMeanPrice": 230.0,
        "targetMedianPrice": 225.0,
        "numberOfAnalystOpinions": 48,
        "recommendationMean": 1.8,
        "freeCashflow": 60_000_000_000,   # aligned with registry's 60B
        "sharesOutstanding": 24_600_000_000,  # aligned with registry
    }


def test_complete_info_populates_all_fields():
    nvda = _nvda()
    result = compute_fundamentals_check(nvda, _complete_info_dict(), current_price=200.0)
    assert result.trailing_pe == 65.2
    assert result.forward_pe == 42.1
    assert result.market_cap == 5_000_000_000_000
    assert result.live_beta == 2.1
    assert result.dividend_yield_pct == 0.02
    assert result.analyst_target_mean == 230.0
    assert result.analyst_count == 48
    assert result.registry_fcf == 60_000_000_000
    assert result.live_fcf == 60_000_000_000
    assert result.fcf_delta_pct == 0.0


def test_missing_keys_return_none():
    nvda = _nvda()
    result = compute_fundamentals_check(nvda, {}, current_price=None)
    assert result.trailing_pe is None
    assert result.forward_pe is None
    assert result.live_fcf is None
    assert result.fcf_delta_pct is None
    assert result.analyst_target_mean is None
    assert any("No live fundamentals" in f for f in result.flags)


def test_stale_fcf_emits_warning():
    nvda = _nvda()  # registry.fcf = 60B
    info = _complete_info_dict()
    info["freeCashflow"] = 90_000_000_000  # +50% from registry
    result = compute_fundamentals_check(nvda, info, current_price=200.0)
    assert result.fcf_delta_pct is not None
    assert result.fcf_delta_pct > 25
    assert any("FCF assumption stale" in f for f in result.flags)


def test_aligned_fcf_no_stale_flag():
    nvda = _nvda()  # registry.fcf = 60B
    info = _complete_info_dict()
    info["freeCashflow"] = 65_000_000_000  # +8.3% from registry, within 25%
    result = compute_fundamentals_check(nvda, info, current_price=200.0)
    assert not any("FCF assumption stale" in f for f in result.flags)


def test_shares_drift_emits_warning():
    nvda = _nvda()  # registry.shares = 24.6B
    info = _complete_info_dict()
    info["sharesOutstanding"] = 26_000_000_000  # +5.7%, over 5% threshold
    result = compute_fundamentals_check(nvda, info, current_price=200.0)
    assert any("Shares outstanding drift" in f for f in result.flags)


def test_analyst_target_produces_upside_flag():
    nvda = _nvda()
    info = _complete_info_dict()
    info["targetMeanPrice"] = 250.0
    result = compute_fundamentals_check(nvda, info, current_price=200.0)
    flag = next(f for f in result.flags if "Analyst consensus" in f)
    assert "+25.0%" in flag
    assert "48 analysts" in flag


def test_garbage_values_dont_crash():
    nvda = _nvda()
    info = {
        "trailingPE": "not a number",
        "freeCashflow": None,
        "sharesOutstanding": "???",
        "numberOfAnalystOpinions": "N/A",
    }
    result = compute_fundamentals_check(nvda, info, current_price=200.0)
    assert result.trailing_pe is None
    assert result.live_fcf is None
    assert result.live_shares is None
    assert result.analyst_count is None


def test_all_aligned_emits_aligned_flag():
    nvda = _nvda()
    info = {
        "trailingPE": 65.0,
        "freeCashflow": 62_000_000_000,  # within 25%
        "sharesOutstanding": 24_600_000_000,  # exact
    }
    result = compute_fundamentals_check(nvda, info, current_price=200.0)
    assert any("aligned with live" in f for f in result.flags)
