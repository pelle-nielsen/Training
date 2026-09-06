"""
Sweep SMA window combinations for a ticker and show train vs. test performance
side by side, so you can see whether the "best" combo actually generalizes --
and whether it beats simply buying and holding.

Usage:
    python scripts/run_optimize.py --ticker AAPL
    python scripts/run_optimize.py --ticker MSFT --period 5y --top 10
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trading.data import get_history
from trading.optimize import sweep_sma_windows


def main() -> None:
    parser = argparse.ArgumentParser(description="Sweep SMA crossover parameters with a train/test split.")
    parser.add_argument("--ticker", default="AAPL", help="Yahoo Finance ticker, e.g. AAPL, MSFT, SPY")
    parser.add_argument("--period", default="5y", help="History window, e.g. 2y, 5y, max")
    parser.add_argument("--top", type=int, default=5, help="How many top results to show")
    args = parser.parse_args()

    print(f"Fetching {args.ticker} ({args.period})...")
    prices = get_history(args.ticker, period=args.period)

    short_windows = [5, 10, 20, 30, 50]
    long_windows = [30, 50, 100, 150, 200]

    results = sweep_sma_windows(prices, short_windows, long_windows, rank_by="train_sharpe")

    if not results:
        print("No valid window combinations for this amount of data -- try a longer --period.")
        return

    test_buy_hold = results[0].test_buy_hold_return_pct
    print(f"\nBuy-and-hold return over the test period alone: {test_buy_hold:+.2f}%")
    print(f"Top {min(args.top, len(results))} by train-period Sharpe ratio "
          f"(ranked WITHOUT looking at test data):\n")
    header = (f"{'short':>5} {'long':>5} | {'train ret%':>10} {'train shrp':>10} | "
              f"{'test ret%':>9} {'test shrp':>9} {'test dd%':>8} {'test trades':>11} {'vs b&h':>8}")
    print(header)
    print("-" * len(header))
    for r in results[: args.top]:
        vs_bh = r.test_return_pct - r.test_buy_hold_return_pct
        print(
            f"{r.short_window:>5} {r.long_window:>5} | "
            f"{r.train_return_pct:>10.2f} {r.train_sharpe:>10.2f} | "
            f"{r.test_return_pct:>9.2f} {r.test_sharpe:>9.2f} {r.test_max_drawdown_pct:>8.2f} "
            f"{r.test_trades:>11} {vs_bh:>+7.2f}%"
        )

    best = results[0]
    print(
        f"\nBest on train data: SMA({best.short_window}/{best.long_window}). "
        f"Its test-period Sharpe was {best.test_sharpe:.2f} vs train {best.train_sharpe:.2f}."
    )
    if best.test_sharpe < best.train_sharpe * 0.5:
        print(
            "That's a big drop from train to test -- a warning sign this combo may be "
            "overfit to the train period rather than reflecting a real, repeatable edge."
        )
    if best.test_return_pct < test_buy_hold:
        print(
            f"Note: it also underperformed plain buy-and-hold on the test period "
            f"({best.test_return_pct:+.2f}% vs {test_buy_hold:+.2f}%) -- the extra "
            f"complexity (and trading costs) may not be earning its keep here."
        )


if __name__ == "__main__":
    main()
