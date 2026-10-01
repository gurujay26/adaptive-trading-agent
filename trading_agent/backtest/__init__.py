from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class TradeOrder:
    """Represents a bracket order payload."""

    symbol: str
    side: str
    quantity: float
    entry_price: float
    stop_loss: float
    take_profit: float
    order_type: str = "market"
    status: str = "submitted"


class PositionSizer:
    """Risk-based sizing with Wall Street Raise scaling."""

    def __init__(self, risk_pct: float = 0.01, counter_trend_fraction: float = 0.5, growth_step_pct: float = 0.10) -> None:
        self.risk_pct = risk_pct
        self.counter_trend_fraction = counter_trend_fraction
        self.growth_step_pct = growth_step_pct

    def base_risk_amount(self, account_balance: float) -> float:
        """Compute the account risk budget in dollars."""
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
        """Calculate number of shares to buy/sell based on risk and growth scaling."""
        if entry_price <= 0 or stop_loss <= 0:
            return 0.0

        raw_risk = self.base_risk_amount(account_balance)
        growth_multiplier = 1.0 + (growth_pct // self.growth_step_pct) * 0.10
        if is_counter_trend:
            raw_risk *= self.counter_trend_fraction
        risk_budget = raw_risk * growth_multiplier
        stop_distance = abs(entry_price - stop_loss)
        if stop_distance <= 0:
            return 0.0
        shares = risk_budget / stop_distance
        if max_position_size is not None:
            shares = min(shares, max_position_size)
        return max(shares, 0.0)


class OrderManager:
    """Broker abstraction for bracket orders and risk-adjusted execution."""

    def __init__(self, paper_trading: bool = True) -> None:
        self.paper_trading = paper_trading
        self.orders: list[TradeOrder] = []

    def submit_bracket_order(
        self,
        *,
        symbol: str,
        side: str,
        quantity: float,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        order_type: str = "market",
    ) -> TradeOrder:
        """Submit an atomic bracket order with entry, stop, and target."""
        side = side.upper()
        if side not in {"BUY", "SELL"}:
            raise ValueError("side must be BUY or SELL")

        order = TradeOrder(
            symbol=symbol,
            side=side,
            quantity=quantity,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            order_type=order_type,
        )
        self.orders.append(order)
        return order

    def move_stop_to_breakeven(self, order: TradeOrder, current_price: float) -> TradeOrder:
        """Adjust the stop to breakeven after price has moved halfway toward take-profit."""
        entry = order.entry_price
        tp = order.take_profit
        if abs(tp - entry) == 0:
            return order
        if (current_price - entry) * (1 if order.side == "BUY" else -1) >= 0.5 * abs(tp - entry):
            order.stop_loss = entry
        return order
