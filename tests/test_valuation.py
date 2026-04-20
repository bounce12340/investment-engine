import pytest

from investment_engine.models import DCFInputs, RelativeInputs, Scenario
from investment_engine.valuation import (
    probabilistic_valuation,
    relative_valuation,
    two_stage_dcf,
)


def test_two_stage_dcf_positive():
    inputs = DCFInputs(
        fcf=1000,
        growth_high=0.10,
        growth_terminal=0.03,
        years_high=5,
        wacc=0.09,
        shares=100,
    )
    price = two_stage_dcf(inputs)
    assert price > 0


def test_dcf_rejects_wacc_below_terminal():
    inputs = DCFInputs(
        fcf=1000,
        growth_high=0.10,
        growth_terminal=0.05,
        years_high=5,
        wacc=0.05,
        shares=100,
    )
    with pytest.raises(ValueError, match="WACC"):
        two_stage_dcf(inputs)


def test_dcf_higher_growth_raises_target():
    low = DCFInputs(fcf=1000, growth_high=0.05, growth_terminal=0.03, years_high=5, wacc=0.09, shares=100)
    high = DCFInputs(fcf=1000, growth_high=0.20, growth_terminal=0.03, years_high=5, wacc=0.09, shares=100)
    assert two_stage_dcf(high) > two_stage_dcf(low)


def test_probabilistic_weighted_mean():
    scenarios = [
        Scenario(name="Bull", price=200, probability=0.2),
        Scenario(name="Base", price=100, probability=0.6),
        Scenario(name="Bear", price=50, probability=0.2),
    ]
    assert probabilistic_valuation(scenarios) == pytest.approx(0.2 * 200 + 0.6 * 100 + 0.2 * 50)


def test_relative_simple_multiple():
    inputs = RelativeInputs(ticker_metric=10, peer_median=25, target_metric="EPS × peer P/E")
    assert relative_valuation(inputs) == 250
