"""
A small vectorized backtesting engine.

This is intentionally simple: it assumes we can always buy/sell at the
next bar's close after a signal changes, applies a flat per-trade cost,
and does not model slippage, partial fills, or intraday risk. Good enough
for comparing strategies; not good enough to trade real money on.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class BacktestResult:
    equity_curve: pd.Series
    returns: pd.Series
    trades: int
    total_return_pct: float
    max_drawdown_pct: float
    sharpe_ratio: float


def run_backtest(
    prices: pd.DataFrame,
    signal: pd.Series,
    initial_capital: float = 100_000.0,
    cost_per_trade_pct: float = 0.05,
) -> BacktestResult:
    """Run a vectorized backtest of `signal` against `prices`.

    Parameters
    ----------
    prices: DataFrame with a "Close" column, as returned by trading.data.get_history.
    signal: Series of 0/1 positions, same index as prices (see trading.strategy).
    initial_capital: Starting portfolio value.
    cost_per_trade_pct: Round-trip cost charged whenever the position changes,
        as a percentage of portfolio value (crude stand-in for spread + fees).
    """
    close = prices["Close"]
    position = signal.shift(1).fillna(0)  # trade on next bar, avoid lookahead bias

    daily_returns = close.pct_change().fillna(0)
    strategy_returns = position * daily_returns

    position_changes = position.diff().abs().fillna(0)
    trade_costs = position_changes * (cost_per_trade_pct / 100)
    strategy_returns = strategy_returns - trade_costs

    equity_curve = initial_capital * (1 + strategy_returns).cumprod()

    running_max = equity_curve.cummax()
    drawdown = (equity_curve - running_max) / running_max
    max_drawdown_pct = drawdown.min() * 100

    total_return_pct = (equity_curve.iloc[-1] / initial_capital - 1) * 100

    # Annualized Sharpe assuming daily bars, 252 trading days/year, 0% risk-free rate.
    std = strategy_returns.std()
    sharpe_ratio = (strategy_returns.mean() / std) * (252 ** 0.5) if std > 0 else 0.0

    trades = int(position_changes.sum())

    return BacktestResult(
        equity_curve=equity_curve,
        returns=strategy_returns,
        trades=trades,
        total_return_pct=total_return_pct,
        max_drawdown_pct=max_drawdown_pct,
        sharpe_ratio=sharpe_ratio,
    )
