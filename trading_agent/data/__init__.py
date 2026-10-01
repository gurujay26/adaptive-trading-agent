from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Optional

import pandas as pd


@dataclass
class MarketBar:
    """Single OHLCV bar."""

    timestamp: pd.Timestamp
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> "MarketBar":
        timestamp = row.get("timestamp")
        if timestamp is None:
            timestamp = row.get("Datetime")
        return cls(
            timestamp=pd.to_datetime(timestamp),
            open=float(row.get("Open", row.get("open", 0.0))),
            high=float(row.get("High", row.get("high", 0.0))),
            low=float(row.get("Low", row.get("low", 0.0))),
            close=float(row.get("Close", row.get("close", 0.0))),
            volume=float(row.get("Volume", row.get("volume", 0.0))),
        )


class DataFeed:
    """Resilient data source wrapper for yfinance-backed market data."""

    def __init__(self, symbol: str, interval: str = "5m", source: str = "yfinance", heartbeat_timeout_seconds: int = 60) -> None:
        self.symbol = symbol
        self.interval = interval
        self.source = source
        self.heartbeat_timeout_seconds = heartbeat_timeout_seconds
        self.last_update: Optional[pd.Timestamp] = None
        self.bars: list[MarketBar] = []

    def fetch_latest_bars(self, period: str = "1mo") -> pd.DataFrame:
        if self.source.lower() != "yfinance":
            raise ValueError(f"Unsupported data source: {self.source!r}")

        import yfinance as yf

        ticker = yf.Ticker(self.symbol)
        data = ticker.history(period=period, interval=self.interval, auto_adjust=False)
        if data.empty:
            return pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])

        data = data.rename(columns={"Open": "Open", "High": "High", "Low": "Low", "Close": "Close", "Volume": "Volume"})
        data.index = pd.to_datetime(data.index)
        data = data.sort_index()
        self.last_update = data.index[-1]
        self.bars = [MarketBar.from_row(row) for row in data.reset_index().to_dict(orient="records")]
        return data

    def heartbeat_ok(self, now: Optional[pd.Timestamp] = None) -> bool:
        if self.last_update is None:
            return False
        now = pd.Timestamp.utcnow() if now is None else now
        return (now - self.last_update).total_seconds() <= self.heartbeat_timeout_seconds

    def reconnect(self) -> None:
        self.last_update = None

    def __iter__(self) -> Iterable[MarketBar]:
        return iter(self.bars)

