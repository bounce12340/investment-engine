from investment_engine.analysis.kill_switches import safe, triggered
from investment_engine.models import KillSwitch


def test_below_direction_triggers_when_under_threshold():
    k = KillSwitch(name="t", metric="m", threshold=50, direction="below", current_value=40)
    assert k.triggered is True


def test_below_direction_safe_when_above_threshold():
    k = KillSwitch(name="t", metric="m", threshold=50, direction="below", current_value=60)
    assert k.triggered is False


def test_above_direction_triggers_when_over_threshold():
    k = KillSwitch(name="t", metric="m", threshold=100, direction="above", current_value=150)
    assert k.triggered is True


def test_triggered_and_safe_partition():
    ks = [
        KillSwitch(name="a", metric="m", threshold=50, direction="below", current_value=40),
        KillSwitch(name="b", metric="m", threshold=50, direction="below", current_value=60),
    ]
    assert [x.name for x in triggered(ks)] == ["a"]
    assert [x.name for x in safe(ks)] == ["b"]
