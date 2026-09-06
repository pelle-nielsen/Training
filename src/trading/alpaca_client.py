"""
Alpaca paper-trading client.

SAFETY: this module is hardcoded to Alpaca's PAPER trading endpoint
(https://paper-api.alpaca.markets). Paper trading uses fake money in a
simulated account -- no real funds are ever at risk through this module.
There is deliberately no code path here that can reach Alpaca's live
trading endpoint. If a real-money version is ever wanted, that should be a
new, clearly-separate module you build and switch to on purpose -- not a
flag on this one.

Setup:
  1. Create a free account at https://alpaca.markets and generate paper
     trading API keys from the dashboard.
  2. Create a `.env` file in the project root (never committed -- it's in
     .gitignore) with:
         ALPACA_API_KEY=your_key_id
         ALPACA_SECRET_KEY=your_secret_key
  3. pip install alpaca-py
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

PAPER_BASE_URL = "https://paper-api.alpaca.markets"


@dataclass
class OrderResult:
    id: str
    symbol: str
    side: str
    qty: float
    status: str


class AlpacaPaperClient:
    """Thin wrapper around alpaca-py, restricted to the paper endpoint."""

    def __init__(self, api_key: str | None = None, secret_key: str | None = None):
        load_dotenv()
        api_key = api_key or os.getenv("ALPACA_API_KEY")
        secret_key = secret_key or os.getenv("ALPACA_SECRET_KEY")

        if not api_key or not secret_key:
            raise RuntimeError(
                "Missing Alpaca API credentials. Set ALPACA_API_KEY and "
                "ALPACA_SECRET_KEY in a .env file in the project root "
                "(see the docstring at the top of alpaca_client.py)."
            )

        try:
            from alpaca.trading.client import TradingClient
        except ImportError as e:
            raise RuntimeError(
                "alpaca-py isn't installed. Run: pip install alpaca-py"
            ) from e

        # paper=True is what pins this to Alpaca's simulated-money endpoint.
        self._client = TradingClient(api_key, secret_key, paper=True)

    def get_account(self) -> dict:
        account = self._client.get_account()
        return {
            "status": account.status,
            "cash": float(account.cash),
            "portfolio_value": float(account.portfolio_value),
            "buying_power": float(account.buying_power),
        }

    def get_positions(self) -> list[dict]:
        positions = self._client.get_all_positions()
        return [
            {
                "symbol": p.symbol,
                "qty": float(p.qty),
                "avg_entry_price": float(p.avg_entry_price),
                "current_price": float(p.current_price),
                "unrealized_pl": float(p.unrealized_pl),
            }
            for p in positions
        ]

    def place_market_order(self, symbol: str, qty: float, side: str) -> OrderResult:
        """Place a paper market order. side must be 'buy' or 'sell'."""
        from alpaca.trading.enums import OrderSide, TimeInForce
        from alpaca.trading.requests import MarketOrderRequest

        if side not in ("buy", "sell"):
            raise ValueError("side must be 'buy' or 'sell'")

        order_request = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.BUY if side == "buy" else OrderSide.SELL,
            time_in_force=TimeInForce.DAY,
        )
        order = self._client.submit_order(order_request)
        return OrderResult(
            id=str(order.id),
            symbol=order.symbol,
            side=side,
            qty=qty,
            status=str(order.status),
        )
