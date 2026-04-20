from __future__ import annotations

import json
from pathlib import Path

from investment_engine.models import TickerThesis


def load_registry(path: str | Path) -> dict[str, TickerThesis]:
    raw = json.loads(Path(path).read_text())
    return {ticker: TickerThesis(**data) for ticker, data in raw.items()}


def load_ticker(path: str | Path, ticker: str) -> TickerThesis:
    registry = load_registry(path)
    if ticker not in registry:
        raise KeyError(f"ticker {ticker!r} not found in registry at {path}")
    return registry[ticker]
