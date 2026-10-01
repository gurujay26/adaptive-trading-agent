from __future__ import annotations

from dataclasses import dataclass


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

