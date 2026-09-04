# Training

A research and backtesting toolkit, building toward an automated stock
trading system for Nordnet.

## Status

**Backtesting / strategy research only.** Nothing in this repo places real
orders or touches a real brokerage account. `src/trading/nordnet_client.py`
is a placeholder for that future work, kept deliberately disconnected from
everything else.

## Why start here

Before risking real money (or even a paper-trading account), we want to be
able to:
1. Pull historical price data for the instruments we care about.
2. Express a trading strategy as code.
3. Backtest it against history and see real numbers: return, drawdown,
   Sharpe ratio, vs. just buying and holding.
4. Iterate quickly, without any live-trading risk.

Live Nordnet integration (via their [External API](https://www.nordnet.se/externalapi/docs))
is a later phase, once a strategy has been validated here.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

Run the example SMA crossover strategy against Equinor (Oslo Bors):

```bash
python scripts/run_backtest.py --ticker EQNR.OL --short 20 --long 50
```

Oslo Bors tickers need a `.OL` suffix on Yahoo Finance (data source for now),
e.g. `DNB.OL`, `NHY.OL`, `MOWI.OL`. US tickers work as-is, e.g. `AAPL`.

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
  nordnet_client.py   placeholder for live Nordnet API integration (later)
scripts/
  run_backtest.py     CLI entry point: fetch data, run a strategy, report results
tests/
  test_strategy.py    unit tests for strategy + backtest logic
```

## Roadmap

- [x] Historical data loading
- [x] Strategy interface + SMA crossover example
- [x] Vectorized backtester (return, drawdown, Sharpe)
- [ ] More strategies (momentum, mean reversion, RSI, etc.)
- [ ] Parameter optimization / walk-forward testing
- [ ] Nordnet API: read-only account/position/market-data connection
- [ ] Nordnet API: order placement, with strict safety limits and manual confirmation
