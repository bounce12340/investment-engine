from investment_engine.models import RelativeInputs


def relative_valuation(inputs: RelativeInputs) -> float:
    return inputs.ticker_metric * inputs.peer_median
