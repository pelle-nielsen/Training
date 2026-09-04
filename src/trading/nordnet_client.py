"""
Nordnet External API (NEXT) client -- NOT YET IMPLEMENTED.

This module is a placeholder for connecting to Nordnet's real API once you
have credentials (docs: https://www.nordnet.se/externalapi/docs). It is kept
separate from the backtesting code on purpose: nothing in `data.py`,
`strategy.py`, or `backtest.py` depends on this module, so research and
strategy development can happen safely with zero risk of accidentally
touching a real account.

When we're ready to build this out, next steps will be:
  1. Register for Nordnet API access and get a test-environment session.
  2. Implement authentication (session id via Basic auth per their docs).
  3. Implement read-only endpoints first: accounts, positions, instrument
     lookup -- so we can sanity check the connection with zero trading risk.
  4. Only after that: order placement, gated behind an explicit
     confirmation step and a hard-coded max order size / daily loss limit.

Nothing in this file should ever be called automatically -- any function
that places a real order must require an explicit, human-triggered call.
"""

from __future__ import annotations


class NordnetClient:
    def __init__(self, *_, **__):
        raise NotImplementedError(
            "Nordnet API integration hasn't been built yet. See the module "
            "docstring in nordnet_client.py for the planned next steps."
        )
