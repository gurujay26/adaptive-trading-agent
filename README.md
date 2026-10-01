from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import yaml

from trading_agent.backtest.backtester import BacktestEngine
from trading_agent.data.feed import DataFeed
from trading_agent.utils.logger import StructuredLogger

logger = StructuredLogger("trading_agent")


def load_settings(path: str | None = None) -> dict:
    config_path = Path(path or Path(__file__).resolve().parent / "config" / "settings.yaml")
    with config_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def run_backtest(settings: dict) -> dict:
    config = settings.get("trading_agent", {})
    logger.log_event("backtest_start", ticker=config.get("ticker", "AAPL"))

    sample = pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=200, freq="5min"),
            "Open": [100 + i * 0.25 for i in range(200)],
            "High": [100.7 + i * 0.32 for i in range(200)],
            "Low": [99.5 + i * 0.20 for i in range(200)],
            "Close": [100.2 + i * 0.28 for i in range(200)],
            "Volume": [1000] * 200,
        }
    )

    engine = BacktestEngine(symbol=config.get("ticker", "AAPL"), initial_balance=float(config.get("backtest", {}).get("initial_balance", 100000.0)))
    result = engine.run(
        sample,
        config={
            "risk_pct": float(config.get("risk_pct", 0.01)),
            "counter_trend_fraction": float(config.get("counter_trend_fraction", 0.5)),
            "atr_guardrail_multiplier": float(config.get("atr_guardrail_multiplier", 1.5)),
        },
    )
    print(result.summary)
    return {"status": "ok", "trade_count": len(result.trades), "summary": result.summary}


def run_paper(settings: dict) -> dict:
    config = settings.get("trading_agent", {})
    logger.log_event("paper_start", ticker=config.get("ticker", "AAPL"))
    feed = DataFeed(symbol=config.get("ticker", "AAPL"), interval=config.get("default_interval", "5m"))
    data = feed.fetch_latest_bars(period="5d")
    logger.log_event("data_loaded", bars=len(data))
    return {"status": "paper mode active", "bars": len(data)}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Adaptive multi-timeframe trading agent")
    parser.add_argument("--mode", choices=["backtest", "paper"], default="backtest")
    parser.add_argument("--config", default=None)
    args = parser.parse_args(argv)

    settings = load_settings(args.config)
    if args.mode == "backtest":
        run_backtest(settings)
    else:
        run_paper(settings)


if __name__ == "__main__":
    main()

