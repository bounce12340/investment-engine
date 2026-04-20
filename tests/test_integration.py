from pathlib import Path

from investment_engine.watcher import InvestmentWatcher

REGISTRY = Path(__file__).resolve().parent.parent / "data" / "monitor-registry.json"


def test_end_to_end_build_report_without_price():
    watcher = InvestmentWatcher(REGISTRY)
    report = watcher.build_report("NVDA", fetch_price=False)

    assert report.ticker == "NVDA"
    assert report.current_price is None
    assert report.valuation.dcf_target > 0
    assert report.valuation.probabilistic_target > 0
    assert report.valuation.relative_target > 0
    assert report.valuation.triangulated > 0
    assert len(report.kill_switches) >= 1
    assert len(report.bull_points) >= 1
    assert len(report.bear_points) >= 1
    assert 0.0 <= report.stress_test.conviction_score <= 10.0
    assert len(report.stress_test.flags) >= 1


def test_build_report_tolerates_price_fetch_failure(monkeypatch):
    def boom(_ticker):
        raise RuntimeError("network down")

    monkeypatch.setattr(
        "investment_engine.watcher.get_current_price", boom
    )
    watcher = InvestmentWatcher(REGISTRY)
    report = watcher.build_report("NVDA", fetch_price=True)
    assert report.current_price is None
