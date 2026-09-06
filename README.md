# Training

A research, backtesting, and paper-trading toolkit for building (and
proving out) stock trading strategies before any real money is involved.

## Status

**Backtesting + paper trading (fake money) only.** Nothing in this repo
places real orders or touches a real brokerage account.
- Strategy research uses historical data via Yahoo Finance (free, no
  account needed).
- "Live" testing uses Alpaca's paper trading account -- a real trading API,
  simulated money. You could run this every day for months and never risk
  a real dollar.
- `nordnet_client.py` is a placeholder for a possible future Nordnet
  integration and is not used anywhere else in the project.

## Why this order of operations

1. **Backtest** a strategy against history -- fast, free, zero risk.
2. **Optimize honestly**: sweep parameters with a train/test split, so we
   can tell a real edge from a lucky fit to one stretch of history.
3. **Paper trade** the strategy for a while against live (but fake-money)
   markets -- this catches problems backtesting can't, like how a strategy
   handles the *current*, unknown market rather than known history.
4. Only after a strategy holds up through all of that would real-money
   trading even be worth considering -- and that's a deliberate, separate
   decision to make later, not a default this project drifts toward.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

For paper trading, also:
1. Create a free account at [alpaca.markets](https://alpaca.markets) and
   generate **paper trading** API keys from the dashboard.
2. Copy `.env.example` to `.env` and fill in your keys. `.env` is
   git-ignored -- your keys never get committed.

## Usage

**Backtest a strategy** against history:

```bash
python scripts/run_backtest.py --ticker AAPL --short 20 --long 50
```

**Sweep parameters** with a train/test split, to find settings that
generalize rather than just fit the past:

```bash
python scripts/run_optimize.py --ticker AAPL --period 5y
```

**Check today's signal against your Alpaca paper account** (dry run by
default -- add `--live` to actually place the paper order):

```bash
python scripts/run_paper_trade.py --ticker AAPL --qty 5
python scripts/run_paper_trade.py --ticker AAPL --qty 5 --live
```

Run the tests:

```bash
pytest
```

## Project layout

```
src/trading/
  data.py             historical price data (via yfinance, cached to ./data)
  strategy.py         strategy definitions -- add new ones here
  backtest.py         vectorized backtesting engine
  optimize.py         parameter sweep with train/test split
  alpaca_client.py    paper-trading client (hardcoded to Alpaca's paper endpoint)
  nordnet_client.py   placeholder, not wired up anywhere yet
scripts/
  run_backtest.py     backtest one strategy, print stats, save a chart
  run_optimize.py     sweep SMA windows, compare train vs. test performance
  run_paper_trade.py  check today's signal, optionally place a paper order
tests/
  test_strategy.py    unit tests for strategy + backtest logic
```

## Roadmap

- [x] Historical data loading
- [x] Strategy interface + SMA crossover example
- [x] Vectorized backtester (return, drawdown, Sharpe)
- [x] Parameter sweep with train/test split
- [x] Alpaca paper trading connection
- [ ] More strategies to compare against SMA crossover (momentum, RSI, mean reversion)
- [ ] Scheduled/automated daily paper trading runs
- [ ] Track paper-trading performance over time, compare to backtest predictions
- [ ] (Much later, only if paper trading proves the strategy out) real-money trading, on a Nordnet or other real broker connection, with strict position/loss limits
