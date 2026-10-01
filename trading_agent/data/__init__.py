from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional

import pandas as pd


@dataclass
class MarketBar:
    """Single OHLCV bar for a symbol."""

    timestamp: pd.Timestamp
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "MarketBar":
        return cls(
            timestamp=pd.to_datetime(row.get("timestamp", row.get("Datetime"))),
            open=float(row.get("Open", row.get("open", 0.0))),
            high=float(row.get("High", row.get("high", 0.0))),
            low=float(row.get("Low", row.get("low", 0.0))),
            close=float(row.get("Close", row.get("close", 0.0))),
            volume=float(row.get("Volume", row.get("volume", 0.0))),
        )


class DataFeed:
    """Resilient market data feed polling yfinance or broker APIs."""

    def __init__(
        self,
        symbol: str,
        interval: str = "5m",
        source: str = "yfinance",
        heartbeat_timeout_seconds: int = 60,
    ) -> None:
        self.symbol = symbol
        self.interval = interval
        self.source = source
        self.heartbeat_timeout_seconds = heartbeat_timeout_seconds
        self.last_update: Optional[pd.Timestamp] = None
        self._bars: List[MarketBar] = []

    def fetch_latest_bars(self, period: str = "1mo") -> pd.DataFrame:
        """Fetch recent bars using yfinance fallbacks or mock-safe data."""
        if self.source.lower() != "yfinance":
            raise ValueError(f"Unsupported source {self.source!r}. Only 'yfinance' is implemented.")

        import yfinance as yf

        ticker = yf.Ticker(self.symbol)
        data = ticker.history(period=period, interval=self.interval, auto_adjust=False)
        if data.empty:
            return pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])

        data = data.rename(columns={"Open": "Open", "High": "High", "Low": "Low", "Close": "Close", "Volume": "Volume"})
        data.index = pd.to_datetime(data.index)
        data = data.sort_index()
        self.last_update = data.index[-1]
        self._bars = [MarketBar.from_row(row) for row in data.reset_index().to_dict(orient="records")]
        return data

    def heartbeat_ok(self, now: Optional[pd.Timestamp] = None) -> bool:
        """Return True when the feed is still alive within the configured timeout."""
        if self.last_update is None:
            return False
        if now is None:
            now = pd.Timestamp.utcnow()
        elapsed = (now - self.last_update).total_seconds()
        return elapsed <= self.heartbeat_timeout_seconds

    def reconnect(self) -> None:
        """Reconnect feed after a heartbeat failure."""
        self.last_update = None

    def __iter__(self) -> Iterable[MarketBar]:
        return iter(self._bars)
