from __future__ import annotations

from investment_engine.models import KillSwitch, StressTestFlag, ThesisStressTest


def stress_test(
    bull_points: list[str],
    bear_points: list[str],
    kill_switches: list[KillSwitch],
) -> ThesisStressTest:
    bull = len(bull_points)
    bear = len(bear_points)
    total_switches = len(kill_switches)
    fired = sum(1 for k in kill_switches if k.triggered)
    safe_switches = total_switches - fired

    score = 5.0
    score += min(safe_switches, 3)
    score -= 2 * fired

    if bear > 0 and bull > 0:
        ratio = bull / bear
        if 0.5 <= ratio <= 2.0:
            score += 1.0

    if bear >= 5:
        score += 2.0
    elif bear >= 3:
        score += 1.0

    score = max(0.0, min(10.0, score))

    flags: list[StressTestFlag] = []

    if bear == 0:
        flags.append(
            StressTestFlag(
                severity="alert",
                message="No red team — confirmation bias risk",
            )
        )
    elif bear < 2:
        flags.append(
            StressTestFlag(
                severity="warning",
                message=f"Thin red team — only {bear} bear point(s)",
            )
        )

    if bull == 0:
        flags.append(
            StressTestFlag(
                severity="warning",
                message="No blue team — negative thesis only",
            )
        )

    if bull > 0 and bear > 0:
        ratio = bull / bear
        if ratio > 3.0:
            flags.append(
                StressTestFlag(
                    severity="warning",
                    message=f"Bull-biased: {ratio:.1f}× bull-to-bear ratio",
                )
            )

    if fired > 0:
        flags.append(
            StressTestFlag(
                severity="alert",
                message=f"{fired} kill-switch(es) triggered — thesis violation",
            )
        )

    if not flags:
        flags.append(
            StressTestFlag(
                severity="info",
                message="No red flags — thesis well-balanced",
            )
        )

    return ThesisStressTest(
        bull_count=bull,
        bear_count=bear,
        kill_switches_triggered=fired,
        kill_switches_total=total_switches,
        conviction_score=round(score, 1),
        flags=flags,
    )
