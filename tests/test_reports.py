from datetime import date
from pathlib import Path

from investment_engine.models import (
    DCFInputs,
    KillSwitch,
    LeadingIndicator,
    RelativeInputs,
    Scenario,
    ThesisNarrative,
    ValuationInputs,
    ValuationResult,
    WeeklyReport,
)
from investment_engine.reports.markdown import render_weekly
from investment_engine.reports.obsidian import write_to_vault


def _sample_report() -> WeeklyReport:
    return WeeklyReport(
        ticker="NVDA",
        name="NVIDIA",
        as_of=date(2026, 4, 21),
        year=2026,
        week=17,
        current_price=1000.0,
        valuation=ValuationResult(dcf_target=1150, probabilistic_target=1080, relative_target=950),
        thesis=ThesisNarrative(short_term="ST", medium_term="MT", long_term="LT"),
        leading_indicators=[LeadingIndicator(name="CUDA", value=92.0, unit="%", description="d")],
        kill_switches=[
            KillSwitch(name="cuda", metric="CUDA %", threshold=80, direction="below", current_value=92),
            KillSwitch(name="gm", metric="GM %", threshold=60, direction="below", current_value=50),
        ],
        bull_points=["Moat intact"],
        bear_points=["Concentration risk"],
    )


def test_render_weekly_contains_key_sections():
    md = render_weekly(_sample_report())
    assert "# NVDA Weekly Analysis" in md
    assert "Two-Stage DCF" in md
    assert "🟢 Safe" in md
    assert "🔴 TRIGGERED" in md
    assert "Moat intact" in md
    assert "Concentration risk" in md


def test_write_to_vault_creates_file(tmp_path: Path):
    report = _sample_report()
    path = write_to_vault(report, tmp_path)
    assert path.exists()
    assert path.parent.name == "Weekly_Reports"
    assert path.name == "NVDA_2026-W17.md"
    assert "# NVDA Weekly Analysis" in path.read_text()
