from investment_engine.models import DCFInputs


def two_stage_dcf(inputs: DCFInputs) -> float:
    if inputs.wacc <= inputs.growth_terminal:
        raise ValueError(
            f"WACC ({inputs.wacc}) must exceed terminal growth ({inputs.growth_terminal}) "
            "for Gordon growth model to converge"
        )

    pv_explicit = 0.0
    fcf = inputs.fcf
    for year in range(1, inputs.years_high + 1):
        fcf *= 1 + inputs.growth_high
        pv_explicit += fcf / (1 + inputs.wacc) ** year

    terminal_fcf = fcf * (1 + inputs.growth_terminal)
    terminal_value = terminal_fcf / (inputs.wacc - inputs.growth_terminal)
    pv_terminal = terminal_value / (1 + inputs.wacc) ** inputs.years_high

    equity_value = pv_explicit + pv_terminal
    return equity_value / inputs.shares
