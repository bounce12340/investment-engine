import plistlib
from pathlib import Path

import pytest

from investment_engine.scheduler import (
    ScheduleSpec,
    build_calendar_interval,
    build_plist_bytes,
    build_wrapper_script,
    tickers_from_registry,
)

REGISTRY = Path(__file__).resolve().parent.parent / "data" / "monitor-registry.json"


def _spec(**overrides):
    base = dict(
        name="morning-check",
        frequency="daily",
        hour=9,
        minute=30,
        vault=Path("/tmp/vault"),
    )
    base.update(overrides)
    return ScheduleSpec(**base)


def test_spec_rejects_bad_name():
    with pytest.raises(ValueError):
        _spec(name="Bad Name!")


def test_spec_rejects_weekly_without_weekday():
    with pytest.raises(ValueError):
        _spec(frequency="weekly")


def test_spec_rejects_monthly_without_day():
    with pytest.raises(ValueError):
        _spec(frequency="monthly")


def test_spec_rejects_bad_hour():
    with pytest.raises(ValueError):
        _spec(hour=25)


def test_calendar_interval_daily():
    assert build_calendar_interval(_spec()) == {"Hour": 9, "Minute": 30}


def test_calendar_interval_weekly():
    spec = _spec(frequency="weekly", weekday=1)
    assert build_calendar_interval(spec) == {"Hour": 9, "Minute": 30, "Weekday": 1}


def test_calendar_interval_monthly():
    spec = _spec(frequency="monthly", day=15)
    assert build_calendar_interval(spec) == {"Hour": 9, "Minute": 30, "Day": 15}


def test_build_plist_bytes_parses_back(tmp_path: Path):
    spec = _spec()
    script = tmp_path / "wrapper.sh"
    script.write_text("#!/bin/bash\necho hi\n")

    raw = build_plist_bytes(spec, script)
    parsed = plistlib.loads(raw)
    assert parsed["Label"] == "com.investment-engine.morning-check"
    assert parsed["ProgramArguments"] == ["/bin/bash", str(script)]
    assert parsed["StartCalendarInterval"] == {"Hour": 9, "Minute": 30}
    assert parsed["RunAtLoad"] is False


def test_wrapper_script_loops_tickers():
    spec = _spec()
    script = build_wrapper_script(spec, "/usr/local/bin/investment-engine", ["NVDA", "PLTR"])
    assert "#!/bin/bash" in script
    assert "weekly NVDA" in script
    assert "weekly PLTR" in script
    assert "--vault /tmp/vault" in script
    assert "[warn] NVDA failed" in script


def test_wrapper_script_shell_quotes_paths():
    spec = _spec(vault=Path("/tmp/my vault"))
    script = build_wrapper_script(spec, "/usr/local/bin/investment-engine", ["NVDA"])
    assert "'/tmp/my vault'" in script


def test_tickers_from_registry_includes_all_sample_entries():
    tickers = tickers_from_registry(REGISTRY)
    for t in ("NVDA", "PLTR", "GOOGL", "MP", "NU", "RCAT", "TSLA", "TSM", "UUUU", "VOO"):
        assert t in tickers
