"""
Parameter sweep for rule-based strategies, with an honest train/test split.

The trap with "just try lots of parameter combos and keep the best one" is
that the best-performing combo on a given stretch of history is often just
the one that got luckiest, not the one that reflects a real edge. To guard
against that (a little -- this is still a simple tool, not a research lab):

  1. Split history into an in-sample ("train") period and a later
     out-of-sample ("test") period.
  2. Sweep parameters on the train period only, rank by a chosen metric.
  3. Report how the top candidates *actually* performed on the test period,
     which they never got to see while being chosen.

If a strategy's test-period performance looks a lot worse than its
train-period performance, that's a real signal it was overfit -- pay
attention to that gap, not just the train-period number.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from trading.backtest import run_backtest
from trading.strategy import SmaCrossoverStrategy


@dataclass
class SweepResult:
    short_window: int
    long_window: int
    train_return_pct: float
    train_sharpe: float
    test_return_pct: float
    test_sharpe: float
    test_max_drawdown_pct: float
    test_trades: int


def train_test_split(prices: pd.DataFrame, train_fraction: float = 0.7) -> tuple[pd.DataFrame, pd.DataFrame]:
    split_idx = int(len(prices) * train_fraction)
    return prices.iloc[:split_idx], prices.iloc[split_idx:]


def sweep_sma_windows(
    prices: pd.DataFrame,
    short_windows: list[int],
    long_windows: list[int],
    train_fraction: float = 0.7,
    rank_by: str = "train_sharpe",
) -> list[SweepResult]:
    """Try every valid (short, long) window pair and return results sorted best-first.

    `rank_by` must be one of the SweepResult field names, e.g. "train_sharpe"
    or "train_return_pct". Ranking must use a train_* field -- ranking by
    test performance would defeat the point of the split.
    """
    if not rank_by.startswith("train_"):
        raise ValueError("rank_by must be a train_* metric -- never select using test data")

    train, test = train_test_split(prices, train_fraction)
    # Both halves need enough bars for the longest moving average to be meaningful.
    min_bars = max(long_windows) + 5

    results: list[SweepResult] = []
    for short in short_windows:
        for long in long_windows:
            if short >= long:
                continue
            if len(train) < min_bars or len(test) < min_bars:
                continue

            strategy = SmaCrossoverStrategy(short_window=short, long_window=long)

            train_signal = strategy.generate_signals(train)
            train_result = run_backtest(train, train_signal)

            test_signal = strategy.generate_signals(test)
            test_result = run_backtest(test, test_signal)

            results.append(
                SweepResult(
                    short_window=short,
                    long_window=long,
                    train_return_pct=train_result.total_return_pct,
                    train_sharpe=train_result.sharpe_ratio,
                    test_return_pct=test_result.total_return_pct,
                    test_sharpe=test_result.sharpe_ratio,
                    test_max_drawdown_pct=test_result.max_drawdown_pct,
                    test_trades=test_result.trades,
                )
            )

    results.sort(key=lambda r: getattr(r, rank_by), reverse=True)
    return results
