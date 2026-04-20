from __future__ import annotations

from pathlib import Path

from investment_engine.models import WeeklyReport
from investment_engine.reports.markdown import render_weekly


def write_to_vault(report: WeeklyReport, vault_path: str | Path) -> Path:
    vault = Path(vault_path).expanduser()
    target_dir = vault / "Weekly_Reports"
    target_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{report.ticker}_{report.year}-W{report.week:02d}.md"
    target = target_dir / filename
    target.write_text(render_weekly(report))
    return target
