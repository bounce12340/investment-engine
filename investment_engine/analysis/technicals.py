from __future__ import annotations

from typing import TYPE_CHECKING

from investment_engine.models import TechnicalSnapshot

if TYPE_CHECKING:
    import pandas as pd

MIN_HISTORY = 200  # need 200 bars for MA200


def _rsi(prices: "pd.Series", window: int = 14) -> "pd.Series":
    delta = prices.diff()
    gains = delta.clip(lower=0.0)
    losses = -delta.clip(upper=0.0)
    avg_gain = gains.ewm(alpha=1.0 / window, adjust=False, min_periods=window).mean()
    avg_loss = losses.ewm(alpha=1.0 / window, adjust=False, min_periods=window).mean()
    rs = avg_gain / avg_loss
    return 100 - 100 / (1 + rs)


def _macd(
    prices: "pd.Series",
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> tuple["pd.Series", "pd.Series", "pd.Series"]:
    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def compute_technical_snapshot(prices: "pd.Series") -> TechnicalSnapshot:
    if len(prices) < MIN_HISTORY:
        raise ValueError(
            f"need at least {MIN_HISTORY} daily closes for MA200; got {len(prices)}"
        )

    rsi = _rsi(prices, 14)
    macd_line, signal_line, histogram = _macd(prices)
    ma_50 = prices.rolling(window=50).mean()
    ma_200 = prices.rolling(window=200).mean()

    latest_price = float(prices.iloc[-1])
    ma_50_val = float(ma_50.iloc[-1])
    ma_200_val = float(ma_200.iloc[-1])

    return TechnicalSnapshot(
        price=latest_price,
        rsi_14=float(rsi.iloc[-1]),
        macd=float(macd_line.iloc[-1]),
        macd_signal=float(signal_line.iloc[-1]),
        macd_histogram=float(histogram.iloc[-1]),
        ma_50=ma_50_val,
        ma_200=ma_200_val,
        distance_from_ma50_pct=(latest_price - ma_50_val) / ma_50_val * 100,
        distance_from_ma200_pct=(latest_price - ma_200_val) / ma_200_val * 100,
    )
