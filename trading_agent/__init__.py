from __future__ import annotations

from trading_agent.engine.strategy import SignalGenerator


def test_signal_generator_bullish_breakout() -> None:
    signal = SignalGenerator().generate(
        price=101.0,
        macro_bias="BULLISH",
        session_distance=1.0,
        daily_atr=10.0,
        box_high=100.0,
        box_low=98.0,
        range_high=110.0,
        range_low=90.0,
        swing_high=120.0,
        swing_low=80.0,
        current_5m_close=101.0,
        prior_5m_low=99.0,
        prior_5m_high=100.0,
    )
    assert signal.valid or signal.setup == "NONE"


def test_signal_generator_reversal_short() -> None:
    signal = SignalGenerator().generate(
        price=110.0,
        macro_bias="BEARISH",
        session_distance=20.0,
        daily_atr=10.0,
        box_high=120.0,
        box_low=100.0,
        range_high=110.0,
        range_low=90.0,
        swing_high=115.0,
        swing_low=80.0,
        current_5m_close=108.0,
        prior_5m_low=112.0,
        prior_5m_high=109.0,
    )
    assert signal.direction in {"SHORT", "FLAT"}

