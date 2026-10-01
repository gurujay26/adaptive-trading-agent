from __future__ import annotations

from typing import Optional


class PositionSizer:
    """Risk-based sizing with Wall Street Raise scaling."""

    def __init__(self, risk_pct: float = 0.01, counter_trend_fraction: float = 0.5, growth_step_pct: float = 0.10) -> None:
        self.risk_pct = risk_pct
        self.counter_trend_fraction = counter_trend_fraction
        self.growth_step_pct = growth_step_pct

    def base_risk_amount(self, account_balance: float) -> float:
        return max(account_balance * self.risk_pct, 0.0)

    def calculate_shares(
        self,
        *,
        account_balance: float,
        entry_price: float,
        stop_loss: float,
        is_counter_trend: bool = False,
        growth_pct: float = 0.0,
        max_position_size: Optional[float] = None,
    ) -> float:
        if entry_price <= 0 or stop_loss <= 0:
            return 0.0

        risk_budget = self.base_risk_amount(account_balance)
        if is_counter_trend:
            risk_budget *= self.counter_trend_fraction

        growth_steps = int(growth_pct / self.growth_step_pct)
        risk_budget *= (1.0 + growth_steps * 0.10)

        stop_distance = abs(entry_price - stop_loss)
        if stop_distance <= 0:
            return 0.0

        shares = risk_budget / stop_distance
        if max_position_size is not None:
            shares = min(shares, max_position_size)
        return max(shares, 0.0)

