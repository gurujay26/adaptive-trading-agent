from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd


class LiquidityDetector:
    """Institutional liquidity zone detector from prior-day and 15m intraday structure."""

    def __init__(self, pivot_window: int = 2) -> None:
        self.pivot_window = pivot_window

    def detect_pivots(self, series: pd.Series) -> pd.Series:
        """Mark local pivot highs and lows using a rolling window."""
        if series.empty:
            return pd.Series(dtype=float)

        values = pd.to_numeric(series, errors="coerce")
        pivots = pd.Series(np.nan, index=values.index)
        left = self.pivot_window
        right = self.pivot_window

        for idx in range(left, len(values) - right):
            window = values.iloc[idx - left : idx + right + 1]
            if values.iloc[idx] == window.max() and values.iloc[idx] > values.iloc[idx - 1] and values.iloc[idx] >= values.iloc[idx + 1]:
                pivots.iloc[idx] = values.iloc[idx]
            if values.iloc[idx] == window.min() and values.iloc[idx] < values.iloc[idx - 1] and values.iloc[idx] <= values.iloc[idx + 1]:
                pivots.iloc[idx] = values.iloc[idx]
        return pivots

    def previous_day_levels(self, daily_bars: pd.DataFrame) -> Dict[str, float]:
        """Return prior day high and low for the current session."""
        if daily_bars.empty:
            return {"Range_High": float("nan"), "Range_Low": float("nan")}

        bars = daily_bars.copy()
        if len(bars) < 2:
            return {"Range_High": float(bars["High"].iloc[-1]), "Range_Low": float(bars["Low"].iloc[-1])}

        prev = bars.iloc[-2]
        return {"Range_High": float(prev["High"]), "Range_Low": float(prev["Low"])}

    def find_institutional_zones(self, fifteen_minute_bars: pd.DataFrame, range_high: float, range_low: float) -> Dict[str, float]:
        """Find swing high/low pivots above and below range boundaries."""
        if fifteen_minute_bars.empty:
            return {"Swing_High": float("nan"), "Swing_Low": float("nan")}

        high_series = pd.to_numeric(fifteen_minute_bars["High"], errors="coerce")
        low_series = pd.to_numeric(fifteen_minute_bars["Low"], errors="coerce")
        high_pivots = self.detect_pivots(high_series)
        low_pivots = self.detect_pivots(low_series)

        candidates_high = high_pivots[high_pivots > range_high].dropna()
        candidates_low = low_pivots[low_pivots < range_low].dropna()

        swing_high = float(candidates_high.max()) if not candidates_high.empty else float("nan")
        swing_low = float(candidates_low.min()) if not candidates_low.empty else float("nan")

        return {"Swing_High": swing_high, "Swing_Low": swing_low}

    def opening_range_box(self, first_15m_bar: pd.Series) -> Dict[str, float]:
        """Create the opening range box from the first 15-minute candle of the session."""
        if first_15m_bar.empty:
            return {"Box_High": float("nan"), "Box_Low": float("nan")}

        return {
            "Box_High": float(first_15m_bar["High"]),
            "Box_Low": float(first_15m_bar["Low"]),
        }

    def build_zones(self, daily_bars: pd.DataFrame, fifteen_minute_bars: pd.DataFrame) -> Dict[str, float]:
        """Return all key liquidity zone values consistent with the trading strategy."""
        previous = self.previous_day_levels(daily_bars)
        high = previous["Range_High"]
        low = previous["Range_Low"]
        swings = self.find_institutional_zones(fifteen_minute_bars, high, low)

        result = {
            "Range_High": high,
            "Range_Low": low,
            "Swing_High": swings["Swing_High"],
            "Swing_Low": swings["Swing_Low"],
        }

        if not fifteen_minute_bars.empty:
            first_bar = fifteen_minute_bars.iloc[0]
            box = self.opening_range_box(first_bar)
            result.update({"Box_High": box["Box_High"], "Box_Low": box["Box_Low"]})
        else:
            result.update({"Box_High": float("nan"), "Box_Low": float("nan")})
        return result

