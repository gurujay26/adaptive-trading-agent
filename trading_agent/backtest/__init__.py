from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TradeOrder:
    """Represents a simple bracket order."""

    symbol: str
    side: str
    quantity: float
    entry_price: float
    stop_loss: float
    take_profit: float
    order_type: str = "market"
    status: str = "submitted"


class OrderManager:
    """Broker abstraction for bracket orders."""

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
        entry = order.entry_price
        take_profit = order.take_profit
        if abs(take_profit - entry) <= 0:
            return order

        move = (current_price - entry) if order.side == "BUY" else (entry - current_price)
        if move >= 0.5 * abs(take_profit - entry):
            order.stop_loss = entry
        return order
