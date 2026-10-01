from __future__ import annotations

import numpy as np
import pandas as pd


class Resampler:
    """Resample intraday OHLCV data to broader timeframes."""

    @staticmethod
    def resample_ohlcv(frame: pd.DataFrame, rule: str) -> pd.DataFrame:
        """Aggregate raw OHLCV into target frequency using a robust, edge-safe method."""
        if frame.empty:
            return pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])

        work = frame.copy()
        if isinstance(work.index, pd.MultiIndex):
            work = work.reset_index(drop=True)
        if not isinstance(work.index, pd.DatetimeIndex):
            if "timestamp" in work.columns:
                work["timestamp"] = pd.to_datetime(work["timestamp"], errors="coerce")
                work = work.set_index("timestamp")
            elif "Datetime" in work.columns:
                work["Datetime"] = pd.to_datetime(work["Datetime"], errors="coerce")
                work = work.set_index("Datetime")
            else:
                work.index = pd.to_datetime(work.index, errors="coerce")

        work = work.sort_index()
        work = work[~work.index.isna()]
        if work.empty:
            return pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])

        agg_map = {
            "Open": "first",
            "High": "max",
            "Low": "min",
            "Close": "last",
            "Volume": "sum",
        }
        result = work.resample(rule).agg(agg_map)
        result = result.replace([np.inf, -np.inf], np.nan).dropna(how="any")
        return result

    @staticmethod
    def build_timeframes(frame: pd.DataFrame) -> dict[str, pd.DataFrame]:
        """Produce 1m -> 5m, 15m, and daily OHLCV timelines."""
        if frame.empty:
            empty = pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])
            return {"1m": empty.copy(), "5m": empty.copy(), "15m": empty.copy(), "daily": empty.copy()}

        work = frame.copy()
        if "timestamp" in work.columns:
            work["timestamp"] = pd.to_datetime(work["timestamp"], errors="coerce")
            work = work.set_index("timestamp")
        elif "Datetime" in work.columns:
            work["Datetime"] = pd.to_datetime(work["Datetime"], errors="coerce")
            work = work.set_index("Datetime")
        else:
            work.index = pd.to_datetime(work.index, errors="coerce")

        work = work.sort_index()
        return {
            "1m": work,
            "5m": Resampler.resample_ohlcv(work, "5min"),
            "15m": Resampler.resample_ohlcv(work, "15min"),
            "daily": Resampler.resample_ohlcv(work, "1D"),
        }
