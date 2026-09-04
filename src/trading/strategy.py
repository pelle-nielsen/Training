"""
Trading strategies.

A strategy takes a price DataFrame (see `trading.data.get_history`) and
returns a "signal" series aligned to the same index:
    1  -> be long / hold the position
    0  -> be flat / no position

This keeps strategies simple and easy to test in isolation from the
backtesting engine and from any live order-placement code.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class SmaCrossoverStrategy:
    """Classic moving-average crossover.

    Go long when the short-window SMA is above the long-window SMA,
    flat otherwise. Simple, easy to reason about, and a good baseline
    to compare more sophisticated strategies against.
    """

    short_window: int = 20
    long_window: int = 50

    def generate_signals(self, prices: pd.DataFrame) -> pd.Series:
        if self.short_window >= self.long_window:
            raise ValueError("short_window must be smaller than long_window")

        close = prices["Close"]
        short_sma = close.rolling(self.short_window).mean()
        long_sma = close.rolling(self.long_window).mean()

        signal = (short_sma > long_sma).astype(int)
        signal.name = "signal"
        return signal
