from __future__ import annotations

import pandas as pd

from trading_agent.engine.liquidity import LiquidityDetector


def test_liquidity_zones_detected() -> None:
    daily = pd.DataFrame({
        "Open": [100.0, 102.0],
        "High": [110.0, 112.0],
        "Low": [90.0, 92.0],
        "Close": [108.0, 109.0],
    })
    fifteen = pd.DataFrame({
        "High": [101.0, 105.0, 103.0, 107.0],
        "Low": [98.0, 99.0, 96.0, 94.0],
    })
    detector = LiquidityDetector()
    zones = detector.build_zones(daily, fifteen)
    assert "Range_High" in zones
    assert "Box_High" in zones
