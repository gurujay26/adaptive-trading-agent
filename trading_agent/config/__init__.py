# Adaptive Multi-Timeframe Trading Agent

This project implements a modular Python trading agent that blends:

- 50-day SMA macro trend filtering
- 14-day ATR volatility guardrails
- prior-day liquidity zones and swing pivots
- 15-minute opening range box breakout logic
- structural stop placement and bracket orders
- historical backtesting and paper trading execution

## Repository structure

```text
trading_agent/
├── __init__.py
├── config/
│   ├── __init__.py
│   └── settings.yaml
├── data/
│   ├── __init__.py
│   ├── feed.py
│   └── resampler.py
├── engine/
│   ├── __init__.py
│   ├── macro.py
│   ├── liquidity.py
│   └── strategy.py
├── execution/
│   ├── __init__.py
│   ├── position_sizer.py
│   └── order_manager.py
├── backtest/
│   ├── __init__.py
│   └── backtester.py
├── utils/
│   ├── __init__.py
│   ├── logger.py
│   └── metrics.py
├── main.py
└── __init__.py
```

## Quick start

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Edit `trading_agent/config/settings.yaml` and provide your API credentials if you plan to use paper or live trading.

## Run backtest

```bash
python main.py --mode backtest
```

## Run paper trading

```bash
python main.py --mode paper
```

## Tests

```bash
pytest -q
```

## Notes

- This codebase is intentionally modular and designed to be extended for Alpaca, yfinance, or CCXT data providers.
- The backtest path validates the trading logic against synthetic OHLCV data and can be replaced with real price history.
- For production live execution, add broker authentication and real-time WebSocket reconnection logic before trading capital.

