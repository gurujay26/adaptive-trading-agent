from __future__ import annotations

import numpy as np
import pandas as pd


class Resampler:
    """Convert raw OHLCV into broader timeframes."""

    @staticmethod
    def resample_ohlcv(frame: pd.DataFrame, rule: str) -> pd.DataFrame:
        if frame.empty:
            return pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])

        work = frame.copy()
        if "timestamp" in work.columns:
            work["timestamp"] = pd.to_datetime(work["timestamp"], errors="coerce")
            work = work.set_index("timestamp")
        elif "Datetime" in work.columns:
            work["Datetime"] = pd.to_datetime(work["Datetime"], errors="coerce")
            work = work.set_index("Datetime")
        elif not isinstance(work.index, pd.DatetimeIndex):
            work.index = pd.to_datetime(work.index, errors="coerce")

        work = work.sort_index().dropna(how="any")
        if work.empty:
            return pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])

        agg = {"Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"}
        result = work.resample(rule).agg(agg)
        return result.replace([np.inf, -np.inf], np.nan).dropna(how="any")

    @staticmethod
    def build_timeframes(frame: pd.DataFrame) -> dict[str, pd.DataFrame]:
        if frame.empty:
            empty = pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])
            return {"1m": empty.copy(), "5m": empty.copy(), "15m": empty.copy(), "daily": empty.copy()}

        work = frame.copy()
        if "timestamp" in work.columns:
            work = work.set_index(pd.to_datetime(work["timestamp"], errors="coerce"))
        elif "Datetime" in work.columns:
            work = work.set_index(pd.to_datetime(work["Datetime"], errors="coerce"))
        elif not isinstance(work.index, pd.DatetimeIndex):
            work.index = pd.to_datetime(work.index, errors="coerce")

        work = work.sort_index().dropna(how="any")
        return {
            "1m": work,
            "5m": Resampler.resample_ohlcv(work, "5min"),
            "15m": Resampler.resample_ohlcv(work, "15min"),
            "daily": Resampler.resample_ohlcv(work, "1D"),
        }
