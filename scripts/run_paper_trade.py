"""
Check today's strategy signal and (optionally) place the matching paper order.

Defaults to --dry-run (prints what it would do, places nothing) even though
this only ever touches Alpaca's paper/fake-money account -- it's a good habit
for anything that places orders, and makes this safe to run repeatedly while
you're testing.

Usage:
    python scripts/run_paper_trade.py --ticker AAPL --qty 5
        (dry run: shows the decision, places no order)

    python scripts/run_paper_trade.py --ticker AAPL --qty 5 --live
        (places the paper order for real, in your fake-money Alpaca account)
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trading.alpaca_client import AlpacaPaperClient
from trading.data import get_history
from trading.strategy import SmaCrossoverStrategy

LOG_FILE = Path(__file__).resolve().parents[1] / "data" / "paper_trade_log.csv"


def log_decision(ticker: str, signal: int, action: str, detail: str) -> None:
    LOG_FILE.parent.mkdir(exist_ok=True)
    is_new = not LOG_FILE.exists()
    with open(LOG_FILE, "a") as f:
        if is_new:
            f.write("timestamp,ticker,signal,action,detail\n")
        f.write(f"{datetime.now(timezone.utc).isoformat()},{ticker},{signal},{action},{detail}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run today's strategy signal against Alpaca paper trading.")
    parser.add_argument("--ticker", default="AAPL")
    parser.add_argument("--qty", type=float, default=1, help="Shares to buy/sell when the signal flips")
    parser.add_argument("--short", type=int, default=20)
    parser.add_argument("--long", type=int, default=50)
    parser.add_argument("--live", action="store_true", help="Actually place the paper order (default: dry run only)")
    args = parser.parse_args()

    # Force a fresh download so today's signal reflects the latest bar, not a stale cache.
    prices = get_history(args.ticker, period="1y", use_cache=False)
    strategy = SmaCrossoverStrategy(short_window=args.short, long_window=args.long)
    signal = strategy.generate_signals(prices)
    today_signal = int(signal.iloc[-1])

    print(f"{args.ticker}: SMA({args.short}/{args.long}) signal today = "
          f"{'LONG' if today_signal == 1 else 'FLAT'}")

    client = AlpacaPaperClient()
    positions = {p["symbol"]: p for p in client.get_positions()}
    currently_holding = args.ticker in positions

    if today_signal == 1 and not currently_holding:
        action, detail = "buy", f"qty={args.qty}"
    elif today_signal == 0 and currently_holding:
        action, detail = "sell", f"qty={positions[args.ticker]['qty']}"
    else:
        action, detail = "hold", "no change needed"

    print(f"Decision: {action} ({detail})")

    if action == "hold":
        log_decision(args.ticker, today_signal, action, detail)
        return

    if not args.live:
        print("Dry run -- no order placed. Re-run with --live to actually place this paper order.")
        log_decision(args.ticker, today_signal, f"{action} (dry-run)", detail)
        return

    qty = args.qty if action == "buy" else positions[args.ticker]["qty"]
    result = client.place_market_order(args.ticker, qty=qty, side=action)
    print(f"Order placed: {result}")
    log_decision(args.ticker, today_signal, action, f"order_id={result.id} qty={qty}")


if __name__ == "__main__":
    main()
