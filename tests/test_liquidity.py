from __future__ import annotations

import pandas as pd

from trading_agent.engine.macro import DailyMacroEngine


def test_daily_macro_bullish_regime() -> None:
    df = pd.DataFrame(
        {
            "Open": [100.0] * 60,
            "High": [101.0] * 60,
            "Low": [99.0] * 60,
            "Close": [100.0 + i * 0.5 for i in range(60)],
        }
    )
    metrics = DailyMacroEngine().calculate_daily_metrics(df)
    assert metrics["Macro_Bias"] == "BULLISH"


def test_daily_macro_guardrail_detects_extension() -> None:
    df = pd.DataFrame(
        {
            "Open": [100.0] * 20,
            "High": [110.0] * 20,
            "Low": [95.0] * 20,
            "Close": [110.0] * 20,
        }
    )
    metrics = DailyMacroEngine().calculate_daily_metrics(df)
    assert isinstance(metrics["ATR_Guardrail"], bool)
