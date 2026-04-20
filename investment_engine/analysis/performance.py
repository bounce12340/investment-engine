from __future__ import annotations

import math
from typing import TYPE_CHECKING

from investment_engine.models import PerformanceStats, PeriodPerformance

if TYPE_CHECKING:
    import pandas as pd

TRADING_DAYS_PER_YEAR = 252
DEFAULT_RISK_FREE_RATE = 0.04


def _annualized_return(daily_returns: "pd.Series") -> float:
    mean_daily = float(daily_returns.mean())
    return (1.0 + mean_daily) ** TRADING_DAYS_PER_YEAR - 1.0


def _annualized_vol(daily_returns: "pd.Series") -> float:
    return float(daily_returns.std(ddof=1)) * math.sqrt(TRADING_DAYS_PER_YEAR)


def _sharpe(ann_return: float, ann_vol: float, rf: float) -> float:
    if ann_vol == 0:
        return 0.0
    return (ann_return - rf) / ann_vol


def _sortino(daily_returns: "pd.Series", ann_return: float, rf: float) -> float:
    downside = daily_returns[daily_returns < 0]
    if len(downside) == 0:
        return 0.0
    downside_vol = float(downside.std(ddof=1)) * math.sqrt(TRADING_DAYS_PER_YEAR)
    if downside_vol == 0:
        return 0.0
    return (ann_return - rf) / downside_vol


def _max_drawdown(prices: "pd.Series") -> float:
    cumulative = prices / prices.iloc[0]
    running_peak = cumulative.cummax()
    drawdown = cumulative / running_peak - 1.0
    return float(drawdown.min())


def _alpha_beta(
    ticker_returns: "pd.Series",
    benchmark_returns: "pd.Series",
    rf: float,
) -> tuple[float, float]:
    import pandas as pd

    aligned = pd.concat([ticker_returns, benchmark_returns], axis=1, join="inner").dropna()
    if len(aligned) < 20:
        return 0.0, 0.0
    t, b = aligned.iloc[:, 0], aligned.iloc[:, 1]
    var_b = float(b.var(ddof=1))
    if var_b == 0:
        return 0.0, 0.0
    beta = float(t.cov(b)) / var_b
    ann_t = (1.0 + float(t.mean())) ** TRADING_DAYS_PER_YEAR - 1.0
    ann_b = (1.0 + float(b.mean())) ** TRADING_DAYS_PER_YEAR - 1.0
    alpha = ann_t - (rf + beta * (ann_b - rf))
    return alpha, beta


def compute_period_performance(
    period: str,
    prices: "pd.Series",
    benchmark_prices: "pd.Series",
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
) -> PeriodPerformance:
    ticker_returns = prices.pct_change().dropna()
    benchmark_returns = benchmark_prices.pct_change().dropna()

    ann_return = _annualized_return(ticker_returns)
    ann_vol = _annualized_vol(ticker_returns)
    sharpe = _sharpe(ann_return, ann_vol, risk_free_rate)
    sortino = _sortino(ticker_returns, ann_return, risk_free_rate)
    max_dd = _max_drawdown(prices)
    alpha, beta = _alpha_beta(ticker_returns, benchmark_returns, risk_free_rate)

    return PeriodPerformance(
        period=period,
        annualized_return=ann_return,
        annualized_volatility=ann_vol,
        sharpe=sharpe,
        sortino=sortino,
        max_drawdown=max_dd,
        alpha_vs_voo=alpha,
        beta_vs_voo=beta,
    )


def _slice_period(prices: "pd.Series", years: int) -> "pd.Series":
    import pandas as pd

    if len(prices) == 0:
        return prices
    cutoff = prices.index[-1] - pd.DateOffset(years=years)
    return prices[prices.index >= cutoff]


def compute_performance_stats(
    prices: "pd.Series",
    benchmark_prices: "pd.Series",
    periods: tuple[tuple[str, int], ...] = (("1y", 1), ("3y", 3)),
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
) -> PerformanceStats:
    results: list[PeriodPerformance] = []
    for label, years in periods:
        sliced = _slice_period(prices, years)
        sliced_bench = _slice_period(benchmark_prices, years)
        if len(sliced) < 20 or len(sliced_bench) < 20:
            continue
        results.append(
            compute_period_performance(label, sliced, sliced_bench, risk_free_rate)
        )
    return PerformanceStats(periods=results)
