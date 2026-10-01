from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import pandas as pd

from trading_agent.engine.liquidity import LiquidityDetector
from trading_agent.engine.macro import DailyMacroEngine
from trading_agent.engine.strategy import SignalGenerator
from trading_agent.execution.order_manager import OrderManager
from trading_agent.execution.position_sizer import PositionSizer
from trading_agent.utils.metrics import compute_metrics


@dataclass
class BacktestTrade:
    symbol: str
    side: str
    entry_price: float
    exit_price: float
    quantity: float
    pnl: float
    setup: str


@dataclass
class BacktestMetrics:
    equity_curve: list[float]
    trades: list[BacktestTrade]
    summary: dict[str, float]


class BacktestEngine:
    """Simple backtesting loop over OHLCV bars."""

    def __init__(self, symbol: str = "AAPL", initial_balance: float = 100000.0) -> None:
        self.symbol = symbol
        self.initial_balance = initial_balance
        self.cash = initial_balance
        self.equity = initial_balance
        self.trades: list[BacktestTrade] = []
        self.equity_curve: list[float] = [initial_balance]

    def run(self, bars: pd.DataFrame, config: Optional[dict[str, Any]] = None) -> BacktestMetrics:
        if bars.empty:
            return BacktestMetrics(equity_curve=[self.initial_balance], trades=[], summary={"total_return": 0.0, "win_rate": 0.0, "profit_factor": 0.0, "max_drawdown": 0.0, "sharpe": 0.0})

        config = config or {}
        macro_engine = DailyMacroEngine()
        liquidity = LiquidityDetector()
        signal_generator = SignalGenerator(atr_guardrail_multiplier=config.get("atr_guardrail_multiplier", 1.5))
        position_sizer = PositionSizer(
            risk_pct=config.get("risk_pct", 0.01),
            counter_trend_fraction=config.get("counter_trend_fraction", 0.5),
            growth_step_pct=config.get("growth_step_pct", 0.10),
        )
        order_manager = OrderManager(paper_trading=True)

        for idx in range(1, len(bars)):
            row = bars.iloc[idx]
            price = float(row["Close"])

            daily_slice = bars.iloc[max(0, idx - 100): idx + 1]
            macro = macro_engine.calculate_daily_metrics(daily_slice)
            zones = liquidity.build_zones(daily_slice, daily_slice)

            signal = signal_generator.generate(
                price=price,
                macro_bias=str(macro["Macro_Bias"]),
                session_distance=float(macro["Session_Distance"]),
                daily_atr=float(macro["Daily_ATR"]),
                box_high=float(zones.get("Box_High", float("nan"))),
                box_low=float(zones.get("Box_Low", float("nan"))),
                range_high=float(zones.get("Range_High", float("nan"))),
                range_low=float(zones.get("Range_Low", float("nan"))),
                swing_high=float(zones.get("Swing_High", float("nan"))),
                swing_low=float(zones.get("Swing_Low", float("nan"))),
                current_5m_close=float(row["Close"]),
                prior_5m_low=float(row["Low"]),
                prior_5m_high=float(row["High"]),
            )

            if not signal.valid:
                continue

            shares = position_sizer.calculate_shares(
                account_balance=self.equity,
                entry_price=signal.entry_price or price,
                stop_loss=signal.stop_loss or price,
                is_counter_trend=signal.setup == "A",
            )
            if shares <= 0:
                continue

            order = order_manager.submit_bracket_order(
                symbol=self.symbol,
                side=signal.direction,
                quantity=shares,
                entry_price=signal.entry_price or price,
                stop_loss=signal.stop_loss or price,
                take_profit=signal.take_profit or price,
            )

            pnl = (price - order.entry_price) * order.quantity if order.side == "BUY" else (order.entry_price - price) * order.quantity
            self.cash += pnl
            self.equity = self.cash
            self.equity_curve.append(self.equity)
            self.trades.append(
                BacktestTrade(
                    symbol=self.symbol,
                    side=order.side,
                    entry_price=order.entry_price,
                    exit_price=price,
                    quantity=order.quantity,
                    pnl=pnl,
                    setup=signal.setup,
                )
            )

        summary = compute_metrics(self.equity_curve)
        return BacktestMetrics(equity_curve=self.equity_curve, trades=self.trades, summary=summary)

