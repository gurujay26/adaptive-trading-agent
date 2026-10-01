from __future__ import annotations

from dataclasses import dataclass
from math import isnan

import numpy as np


@dataclass
class StrategySignal:
    """Represents a generated trading signal and its risk metadata."""

    setup: str
    direction: str
    entry_price: float | None = None
    stop_loss: float | None = None
    take_profit: float | None = None
    reason: str = ""
    strength: float = 0.0
    valid: bool = False


class SignalGenerator:
    """Signal generator for Setup A and Setup B rules."""

    def __init__(self, atr_guardrail_multiplier: float = 1.5) -> None:
        self.atr_guardrail_multiplier = atr_guardrail_multiplier

    def generate(
        self,
        *,
        price: float,
        macro_bias: str,
        session_distance: float,
        daily_atr: float,
        box_high: float,
        box_low: float,
        range_high: float,
        range_low: float,
        swing_high: float,
        swing_low: float,
        current_5m_close: float,
        prior_5m_low: float,
        prior_5m_high: float,
    ) -> StrategySignal:
        """Return the highest-probability active setup at the current bar close."""
        if any(val != val for val in [box_high, box_low, range_high, range_low]):
            return StrategySignal(setup="NONE", direction="FLAT", reason="Missing data", valid=False)

        guardrail_active = session_distance >= self.atr_guardrail_multiplier * daily_atr

        if macro_bias == "BEARISH" or guardrail_active:
            if not np.isnan(swing_high) and (range_high <= price <= swing_high) and current_5m_close < prior_5m_low:
                return StrategySignal(
                    setup="A",
                    direction="SHORT",
                    entry_price=price,
                    stop_loss=swing_high + 0.0001,
                    take_profit=box_high,
                    reason="Institutional reversal short in sell zone",
                    strength=1.0,
                    valid=True,
                )

        if macro_bias == "BULLISH" or guardrail_active:
            if not np.isnan(swing_low) and (swing_low <= price <= range_low) and current_5m_close > prior_5m_high:
                return StrategySignal(
                    setup="A",
                    direction="LONG",
                    entry_price=price,
                    stop_loss=swing_low - 0.0001,
                    take_profit=box_low,
                    reason="Institutional reversal long in buy zone",
                    strength=1.0,
                    valid=True,
                )

        if range_low <= price <= range_high and session_distance < self.atr_guardrail_multiplier * daily_atr:
            if macro_bias == "BULLISH" and current_5m_close > box_high:
                return StrategySignal(
                    setup="B",
                    direction="LONG",
                    entry_price=price,
                    stop_loss=box_low,
                    take_profit=range_high,
                    reason="Bullish opening range expansion",
                    strength=0.9,
                    valid=True,
                )
            if macro_bias == "BEARISH" and current_5m_close < box_low:
                return StrategySignal(
                    setup="B",
                    direction="SHORT",
                    entry_price=price,
                    stop_loss=box_high,
                    take_profit=range_low,
                    reason="Bearish opening range expansion",
                    strength=0.9,
                    valid=True,
                )

        return StrategySignal(setup="NONE", direction="FLAT", reason="No valid setup", valid=False)

