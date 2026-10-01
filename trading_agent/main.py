from __future__ import annotations

from math import sqrt
from typing import Iterable


def compute_metrics(equity_curve: Iterable[float]) -> dict[str, float]:
    """Compute standard trading-performance metrics."""
    values = list(equity_curve)
    if len(values) < 2:
        return {"total_return": 0.0, "win_rate": 0.0, "profit_factor": 0.0, "max_drawdown": 0.0, "sharpe": 0.0}

    returns = []
    for idx in range(1, len(values)):
        if values[idx - 1] > 0:
            returns.append((values[idx] - values[idx - 1]) / values[idx - 1])

    total_return = (values[-1] / values[0]) - 1.0 if values[0] else 0.0
    if returns:
        positive = sum(1 for r in returns if r > 0)
        gross_profit = sum(r for r in returns if r > 0)
        gross_loss = sum(abs(r) for r in returns if r < 0)
        win_rate = positive / len(returns)
        profit_factor = gross_profit / gross_loss if gross_loss else float("inf")
        avg = sum(returns) / len(returns)
        std = sqrt(sum((r - avg) ** 2 for r in returns) / len(returns))
        sharpe = (avg / std) if std else 0.0
    else:
        win_rate, profit_factor, sharpe = 0.0, 0.0, 0.0

    running_peak = values[0]
    max_drawdown = 0.0
    for value in values:
        if value > running_peak:
            running_peak = value
        drawdown = (running_peak - value) / running_peak if running_peak else 0.0
        max_drawdown = max(max_drawdown, drawdown)

    return {
        "total_return": total_return,
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "max_drawdown": max_drawdown,
        "sharpe": sharpe,
    }

