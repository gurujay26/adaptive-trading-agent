from __future__ import annotations

import pandas as pd


class DailyMacroEngine:
    """Higher-timeframe daily trend and volatility engine."""

    def __init__(self, sma_period: int = 50, atr_period: int = 14) -> None:
        self.sma_period = sma_period
        self.atr_period = atr_period

    def calculate_daily_metrics(self, daily_bars: pd.DataFrame) -> dict[str, float | str | bool]:
        if daily_bars.empty:
            return {
                "Daily_SMA50": float("nan"),
                "Daily_ATR": float("nan"),
                "Macro_Bias": "NEUTRAL",
                "Session_Distance": float("nan"),
                "ATR_Guardrail": False,
            }

        bars = daily_bars.copy()
        if "Close" not in bars.columns:
            raise ValueError("Daily bars must include a Close column.")

        close = pd.to_numeric(bars["Close"], errors="coerce")
        high = pd.to_numeric(bars.get("High", close), errors="coerce")
        low = pd.to_numeric(bars.get("Low", close), errors="coerce")
        open_ = pd.to_numeric(bars.get("Open", close), errors="coerce")

        sma50 = close.rolling(window=self.sma_period, min_periods=1).mean()
        prev_close = close.shift(1)
        true_range = pd.concat(
            [high - low, (high - prev_close).abs(), (low - prev_close).abs()],
            axis=1,
        ).max(axis=1)
        atr14 = true_range.rolling(window=self.atr_period, min_periods=1).mean()

        current_close = float(close.iloc[-1])
        daily_open = float(open_.iloc[-1])
        daily_sma = float(sma50.iloc[-1])
        daily_atr = float(atr14.iloc[-1])
        session_distance = abs(current_close - daily_open)

        if pd.isna(daily_sma) or pd.isna(daily_atr):
            macro_bias = "NEUTRAL"
        elif current_close > daily_sma:
            macro_bias = "BULLISH"
        elif current_close < daily_sma:
            macro_bias = "BEARISH"
        else:
            macro_bias = "NEUTRAL"

        return {
            "Daily_SMA50": daily_sma,
            "Daily_ATR": daily_atr,
            "Macro_Bias": macro_bias,
            "Session_Distance": session_distance,
            "ATR_Guardrail": session_distance >= 1.5 * daily_atr,
        }

    def market_regime(self, daily_bars: pd.DataFrame) -> str:
        return str(self.calculate_daily_metrics(daily_bars)["Macro_Bias"])
