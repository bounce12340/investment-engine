from investment_engine.models import KillSwitch


def triggered(switches: list[KillSwitch]) -> list[KillSwitch]:
    return [s for s in switches if s.triggered]


def safe(switches: list[KillSwitch]) -> list[KillSwitch]:
    return [s for s in switches if not s.triggered]
