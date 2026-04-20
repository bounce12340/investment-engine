from investment_engine.models import LeadingIndicator


def summarize(indicators: list[LeadingIndicator]) -> list[dict]:
    return [
        {"name": i.name, "value": i.value, "unit": i.unit, "description": i.description}
        for i in indicators
    ]
