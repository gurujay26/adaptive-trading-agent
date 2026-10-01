from __future__ import annotations

from trading_agent.execution.position_sizer import PositionSizer


def test_position_sizer_risk_calculation() -> None:
    sizer = PositionSizer(risk_pct=0.01)
    shares = sizer.calculate_shares(account_balance=10000, entry_price=100.0, stop_loss=99.0)
    assert shares > 0


def test_position_sizer_counter_trend_scaling() -> None:
    sizer = PositionSizer(risk_pct=0.01, counter_trend_fraction=0.5)
    shares = sizer.calculate_shares(account_balance=10000, entry_price=100.0, stop_loss=99.0, is_counter_trend=True)
    assert shares > 0
    assert shares < sizer.calculate_shares(account_balance=10000, entry_price=100.0, stop_loss=99.0)
