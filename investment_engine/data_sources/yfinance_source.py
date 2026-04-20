from __future__ import annotations


def get_current_price(ticker: str) -> float | None:
    import yfinance as yf

    info = yf.Ticker(ticker).fast_info
    price = getattr(info, "last_price", None)
    if price is None:
        return None
    return float(price)
