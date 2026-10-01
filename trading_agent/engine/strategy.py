from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


class LiquidityDetector:
    """Maps prior-day liquidity and opening-range structure."""

    def __init__(self, pivot_window: int = 2) -> None:
        self.pivot_window = pivot_window

    def detect_pivots(self, series: pd.Series) -> pd.Series:
        if series.empty:
            return pd.Series(dtype=float)

        values = pd.to_numeric(series, errors="coerce")
        pivots = pd.Series(np.nan, index=values.index)
        for idx in range(self.pivot_window, len(values) - self.pivot_window):
            window = values.iloc[idx - self.pivot_window : idx + self.pivot_window + 1]
            if values.iloc[idx] == window.max() and values.iloc[idx] >= values.iloc[idx - 1] and values.iloc[idx] >= values.iloc[idx + 1]:
                pivots.iloc[idx] = values.iloc[idx]
            if values.iloc[idx] == window.min() and values.iloc[idx] <= values.iloc[idx - 1] and values.iloc[idx] <= values.iloc[idx + 1]:
                pivots.iloc[idx] = values.iloc[idx]
        return pivots

    def previous_day_levels(self, daily_bars: pd.DataFrame) -> dict[str, float]:
        if daily_bars.empty:
            return {"Range_High": float("nan"), "Range_Low": float("nan")}

        bars = daily_bars.copy()
        if len(bars) < 2:
            return {"Range_High": float(bars["High"].iloc[-1]), "Range_Low": float(bars["Low"].iloc[-1])}

        prev = bars.iloc[-2]
        return {"Range_High": float(prev["High"]), "Range_Low": float(prev["Low"])}

    def find_institutional_zones(self, fifteen_minute_bars: pd.DataFrame, range_high: float, range_low: float) -> dict[str, float]:
        if fifteen_minute_bars.empty:
            return {"Swing_High": float("nan"), "Swing_Low": float("nan")}

        high_pivots = self.detect_pivots(pd.to_numeric(fifteen_minute_bars["High"], errors="coerce"))
        low_pivots = self.detect_pivots(pd.to_numeric(fifteen_minute_bars["Low"], errors="coerce"))

        swing_high = float(high_pivots[high_pivots > range_high].dropna().max()) if not high_pivots[high_pivots > range_high].dropna().empty else float("nan")
        swing_low = float(low_pivots[low_pivots < range_low].dropna().min()) if not low_pivots[low_pivots < range_low].dropna().empty else float("nan")
        return {"Swing_High": swing_high, "Swing_Low": swing_low}

    def opening_range_box(self, first_15m_bar: pd.Series) -> dict[str, float]:
        if first_15m_bar.empty:
            return {"Box_High": float("nan"), "Box_Low": float("nan")}
        return {"Box_High": float(first_15m_bar["High"]), "Box_Low": float(first_15m_bar["Low"])}

    def build_zones(self, daily_bars: pd.DataFrame, fifteen_minute_bars: pd.DataFrame) -> dict[str, float]:
        previous = self.previous_day_levels(daily_bars)
        high = previous["Range_High"]
        low = previous["Range_Low"]
        swings = self.find_institutional_zones(fifteen_minute_bars, high, low)

        result: dict[str, float] = {
            "Range_High": high,
            "Range_Low": low,
            "Swing_High": swings["Swing_High"],
            "Swing_Low": swings["Swing_Low"],
        }
        if fifteen_minute_bars.empty:
            result["Box_High"] = float("nan")
            result["Box_Low"] = float("nan")
        else:
            box = self.opening_range_box(fifteen_minute_bars.iloc[0])
            result["Box_High"] = box["Box_High"]
            result["Box_Low"] = box["Box_Low"]
        return result

