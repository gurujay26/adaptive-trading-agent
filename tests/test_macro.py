# Adaptive Multi-Timeframe Trading Agent

This repository contains a modular, production-oriented Python trading agent that combines:

- 3R Rule macro trend filtering based on the 50-day SMA and 14-day ATR
- Liquidity zone detection using previous-day ranges and pivot structure
- Opening Range Box breakout logic for intraday continuation trades
- Structural risk placement and OCO bracket order simulation
- Historical backtesting and paper trading modes

## Repository Structure

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

## Setup

1. Install Python 3.11+
2. Create a virtual environment
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Copy or edit `trading_agent/config/settings.yaml` with your asset, risk, and API settings.

## Backtest Mode

```bash
python main.py --mode backtest
```

## Paper Trading Mode

```bash
python main.py --mode paper
```

## Test Suite

```bash
pytest -q
```

## Notes

- The strategy uses structural stops based on liquidity pivots rather than arbitrary fixed-dollar exits.
- The code is intended to be extensible to broker APIs such as Alpaca, CCXT, or a live WebSocket feed.
- `settings.yaml` contains the default configuration template for easy deployment.
