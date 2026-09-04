import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trading.backtest import run_backtest
from trading.strategy import SmaCrossoverStrategy


def _fake_prices(n=100, seed=0):
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2024-01-01", periods=n, freq="D")
    # Random walk that trends up, so crossover strategies have signal to find.
    returns = rng.normal(0.001, 0.01, n)
    close = 100 * (1 + pd.Series(returns)).cumprod()
    close.index = dates
    return pd.DataFrame({"Close": close.values}, index=dates)


def test_signal_is_binary():
    prices = _fake_prices()
    strategy = SmaCrossoverStrategy(short_window=5, long_window=20)
    signal = strategy.generate_signals(prices)
    assert set(signal.dropna().unique()).issubset({0, 1})


def test_short_window_must_be_smaller_than_long_window():
    strategy = SmaCrossoverStrategy(short_window=20, long_window=5)
    prices = _fake_prices()
    try:
        strategy.generate_signals(prices)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_backtest_runs_and_returns_sane_shapes():
    prices = _fake_prices()
    strategy = SmaCrossoverStrategy(short_window=5, long_window=20)
    signal = strategy.generate_signals(prices)
    result = run_backtest(prices, signal, initial_capital=10_000)

    assert len(result.equity_curve) == len(prices)
    assert result.equity_curve.iloc[0] > 0
    assert isinstance(result.total_return_pct, float)
    assert isinstance(result.trades, int)
