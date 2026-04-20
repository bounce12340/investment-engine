from pathlib import Path

from investment_engine.data_sources.registry import load_registry, load_ticker

REGISTRY = Path(__file__).resolve().parent.parent / "data" / "monitor-registry.json"


def test_load_registry_contains_nvda():
    registry = load_registry(REGISTRY)
    assert "NVDA" in registry
    nvda = registry["NVDA"]
    assert nvda.ticker == "NVDA"
    assert nvda.valuation_inputs.dcf.shares > 0
    assert len(nvda.kill_switches) > 0


def test_load_ticker_direct():
    nvda = load_ticker(REGISTRY, "NVDA")
    assert nvda.name == "NVIDIA Corporation"


def test_scenario_probabilities_sum_to_one():
    nvda = load_ticker(REGISTRY, "NVDA")
    total = sum(s.probability for s in nvda.valuation_inputs.scenarios)
    assert abs(total - 1.0) < 1e-6
