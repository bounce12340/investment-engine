from __future__ import annotations

from investment_engine.models import FundamentalsCheck, TickerThesis

FCF_STALE_THRESHOLD = 0.25  # 25%
SHARES_DRIFT_THRESHOLD = 0.05  # 5%


def _safe_float(value) -> float | None:
    if value is None:
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if result != result:  # NaN
        return None
    return result


def _safe_int(value) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _pct_delta(registry: float | None, live: float | None) -> float | None:
    if registry is None or live is None or registry == 0:
        return None
    return (live - registry) / registry


def _format_billions(value: float) -> str:
    abs_v = abs(value)
    if abs_v >= 1e12:
        return f"${value / 1e12:.2f}T"
    if abs_v >= 1e9:
        return f"${value / 1e9:.2f}B"
    if abs_v >= 1e6:
        return f"${value / 1e6:.1f}M"
    return f"${value:,.0f}"


def _format_share_count(value: float) -> str:
    if abs(value) >= 1e9:
        return f"{value / 1e9:.2f}B"
    if abs(value) >= 1e6:
        return f"{value / 1e6:.1f}M"
    return f"{value:,.0f}"


def compute_fundamentals_check(
    thesis: TickerThesis,
    info: dict,
    current_price: float | None = None,
) -> FundamentalsCheck:
    trailing_pe = _safe_float(info.get("trailingPE"))
    forward_pe = _safe_float(info.get("forwardPE"))
    market_cap = _safe_float(info.get("marketCap"))
    live_beta = _safe_float(info.get("beta"))
    div_yield = _safe_float(info.get("dividendYield"))
    dividend_yield_pct = div_yield * 100 if div_yield is not None else None

    analyst_target_mean = _safe_float(info.get("targetMeanPrice"))
    analyst_target_median = _safe_float(info.get("targetMedianPrice"))
    analyst_count = _safe_int(info.get("numberOfAnalystOpinions"))
    analyst_recommendation = _safe_float(info.get("recommendationMean"))

    registry_fcf = float(thesis.valuation_inputs.dcf.fcf)
    live_fcf = _safe_float(info.get("freeCashflow"))
    fcf_delta = _pct_delta(registry_fcf, live_fcf)

    registry_shares = float(thesis.valuation_inputs.dcf.shares)
    live_shares = _safe_float(info.get("sharesOutstanding"))
    shares_delta = _pct_delta(registry_shares, live_shares)

    flags: list[str] = []

    if fcf_delta is not None and abs(fcf_delta) > FCF_STALE_THRESHOLD:
        flags.append(
            f"⚠️ FCF assumption stale: registry {_format_billions(registry_fcf)} "
            f"vs live {_format_billions(live_fcf)} ({fcf_delta * 100:+.1f}%)"
        )

    if shares_delta is not None and abs(shares_delta) > SHARES_DRIFT_THRESHOLD:
        flags.append(
            f"⚠️ Shares outstanding drift: registry {_format_share_count(registry_shares)} "
            f"vs live {_format_share_count(live_shares)} ({shares_delta * 100:+.1f}%)"
        )

    if analyst_target_mean is not None and analyst_count is not None and analyst_count > 0:
        if current_price is not None and current_price > 0:
            upside = (analyst_target_mean - current_price) / current_price * 100
            flags.append(
                f"ℹ️ Analyst consensus: ${analyst_target_mean:,.2f} "
                f"({upside:+.1f}% vs current, {analyst_count} analysts)"
            )
        else:
            flags.append(
                f"ℹ️ Analyst consensus: ${analyst_target_mean:,.2f} "
                f"({analyst_count} analysts)"
            )

    if not flags:
        has_any_live_data = any(
            v is not None
            for v in (trailing_pe, forward_pe, market_cap, live_fcf, live_shares)
        )
        if has_any_live_data:
            flags.append("✓ Registry aligned with live fundamentals")
        else:
            flags.append("ℹ️ No live fundamentals available")

    return FundamentalsCheck(
        trailing_pe=trailing_pe,
        forward_pe=forward_pe,
        market_cap=market_cap,
        live_beta=live_beta,
        dividend_yield_pct=dividend_yield_pct,
        analyst_target_mean=analyst_target_mean,
        analyst_target_median=analyst_target_median,
        analyst_count=analyst_count,
        analyst_recommendation=analyst_recommendation,
        registry_fcf=registry_fcf,
        live_fcf=live_fcf,
        fcf_delta_pct=(fcf_delta * 100) if fcf_delta is not None else None,
        registry_shares=registry_shares,
        live_shares=live_shares,
        shares_delta_pct=(shares_delta * 100) if shares_delta is not None else None,
        flags=flags,
    )
