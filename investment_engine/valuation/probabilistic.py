from investment_engine.models import Scenario


def probabilistic_valuation(scenarios: list[Scenario]) -> float:
    return sum(s.price * s.probability for s in scenarios)
