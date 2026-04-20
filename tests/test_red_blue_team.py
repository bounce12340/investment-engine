from investment_engine.analysis.red_blue_team import stress_test
from investment_engine.models import KillSwitch


def _ks(name: str, triggered: bool) -> KillSwitch:
    if triggered:
        return KillSwitch(name=name, metric="m", threshold=10, direction="below", current_value=5)
    return KillSwitch(name=name, metric="m", threshold=10, direction="below", current_value=20)


def test_empty_bear_emits_alert():
    result = stress_test(["moat", "growth"], [], [_ks("a", False)])
    severities = [f.severity for f in result.flags]
    messages = " | ".join(f.message for f in result.flags)
    assert "alert" in severities
    assert "confirmation bias" in messages.lower()


def test_thin_bear_emits_warning():
    result = stress_test(["a", "b"], ["c"], [])
    assert any(f.severity == "warning" and "Thin red team" in f.message for f in result.flags)


def test_empty_bull_emits_warning():
    result = stress_test([], ["a", "b"], [])
    assert any(f.severity == "warning" and "No blue team" in f.message for f in result.flags)


def test_balanced_thesis_scores_high():
    bull = ["a", "b", "c"]
    bear = ["x", "y", "z"]
    switches = [_ks("k1", False), _ks("k2", False), _ks("k3", False)]
    result = stress_test(bull, bear, switches)
    assert result.conviction_score >= 7.0
    assert any(f.severity == "info" and "well-balanced" in f.message for f in result.flags)


def test_all_killswitches_triggered_drops_score_and_alerts():
    bull = ["a", "b", "c"]
    bear = ["x", "y", "z"]
    switches = [_ks("k1", True), _ks("k2", True)]
    result = stress_test(bull, bear, switches)
    assert result.kill_switches_triggered == 2
    assert result.conviction_score < 5.0
    assert any(f.severity == "alert" and "triggered" in f.message for f in result.flags)


def test_bull_bias_warning():
    bull = ["a", "b", "c", "d", "e"]
    bear = ["x"]
    result = stress_test(bull, bear, [])
    assert any(f.severity == "warning" and "Bull-biased" in f.message for f in result.flags)


def test_conviction_score_always_in_range():
    for b in range(0, 10):
        for br in range(0, 10):
            for fired in range(0, 5):
                switches = [_ks(f"k{i}", i < fired) for i in range(fired + 2)]
                r = stress_test(["x"] * b, ["y"] * br, switches)
                assert 0.0 <= r.conviction_score <= 10.0, (b, br, fired, r.conviction_score)


def test_bull_bear_ratio_division_by_zero_safe():
    r = stress_test(["a", "b"], [], [])
    assert r.bull_bear_ratio is None


def test_bull_bear_ratio_basic():
    r = stress_test(["a", "b"], ["x"], [])
    assert r.bull_bear_ratio == 2.0
