"""
Example: fetch data, run the SMA crossover strategy, print & plot results.

Usage:
    python scripts/run_backtest.py
    python scripts/run_backtest.py --ticker DNB.OL --short 10 --long 30
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import matplotlib.pyplot as plt

from trading.backtest import run_backtest
from trading.data import get_history
from trading.strategy import SmaCrossoverStrategy


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a simple SMA crossover backtest.")
    parser.add_argument("--ticker", default="EQNR.OL", help="Yahoo Finance ticker (Oslo Bors uses .OL suffix)")
    parser.add_argument("--period", default="2y", help="History window, e.g. 6mo, 1y, 2y, 5y")
    parser.add_argument("--short", type=int, default=20, help="Short SMA window")
    parser.add_argument("--long", type=int, default=50, help="Long SMA window")
    parser.add_argument("--capital", type=float, default=100_000.0, help="Starting capital")
    parser.add_argument("--no-plot", action="store_true", help="Skip the matplotlib chart")
    args = parser.parse_args()

    print(f"Fetching {args.ticker} ({args.period})...")
    prices = get_history(args.ticker, period=args.period)

    strategy = SmaCrossoverStrategy(short_window=args.short, long_window=args.long)
    signal = strategy.generate_signals(prices)

    result = run_backtest(prices, signal, initial_capital=args.capital)

    print(f"\n--- {args.ticker}: SMA({args.short}/{args.long}) crossover ---")
    print(f"Total return:    {result.total_return_pct:+.2f}%")
    print(f"Max drawdown:    {result.max_drawdown_pct:.2f}%")
    print(f"Sharpe ratio:    {result.sharpe_ratio:.2f}")
    print(f"Number of trades:{result.trades:>5}")

    buy_hold = args.capital * (prices["Close"] / prices["Close"].iloc[0])
    print(f"Buy & hold return: {(buy_hold.iloc[-1] / args.capital - 1) * 100:+.2f}%")

    if not args.no_plot:
        fig, ax = plt.subplots(figsize=(10, 5))
        result.equity_curve.plot(ax=ax, label="Strategy")
        buy_hold.plot(ax=ax, label="Buy & hold")
        ax.set_title(f"{args.ticker}: SMA({args.short}/{args.long}) vs buy & hold")
        ax.set_ylabel("Portfolio value")
        ax.legend()
        out_path = Path(__file__).resolve().parents[1] / "data" / f"{args.ticker.replace('.', '_')}_equity.png"
        fig.savefig(out_path, dpi=120, bbox_inches="tight")
        print(f"\nChart saved to {out_path}")


if __name__ == "__main__":
    main()
