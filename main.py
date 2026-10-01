# Adaptive Multi-Timeframe Trading Agent

This repository contains a modular Python trading agent implementation built around a multi-timeframe intraday strategy. It combines macro trend filtering, liquidity zone detection, and opening-range breakout logic into a clean testable package.

## What it includes

- Daily macro trend engine using a 50-day SMA and ATR guardrail
- Institutional liquidity detection based on prior-day levels and pivots
- Opening-range box logic for breakout and reversal setups
- Risk-based position sizing with counter-trend scaling
- Bracket-order simulation layer
- Backtesting engine and performance metrics
- CLI entry points for backtest and paper-trading modes

## Project structure

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

1. Create a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Edit `trading_agent/config/settings.yaml` for your asset and trading settings.

## Run a backtest

```bash
python main.py --mode backtest
```

## Run paper-trading mode

```bash
python main.py --mode paper
```

## Run tests

```bash
pytest -q
```

## Notes

- This is a modular starting implementation intended for testing and iteration.
- Live execution should be gated behind account credentials and proper broker integration.
- Use a dedicated paper environment before trading real capital.
