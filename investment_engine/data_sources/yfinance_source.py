from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def get_current_price(ticker: str) -> float | None:
    import yfinance as yf

    info = yf.Ticker(ticker).fast_info
    price = getattr(info, "last_price", None)
    if price is None:
        return None
    return float(price)


def get_price_history(ticker: str, period: str = "3y") -> "pd.Series | None":
    """Return daily close price series. Returns None on any failure."""
    import yfinance as yf

    try:
        df = yf.Ticker(ticker).history(period=period, auto_adjust=True)
    except Exception:
        return None
    if df is None or df.empty or "Close" not in df.columns:
        return None
    series = df["Close"].dropna()
    if series.empty:
        return None
    return series
