"""
Historical price data loading.

For now we pull data from Yahoo Finance via `yfinance` so strategies can be
researched and backtested without needing live Nordnet API credentials.
Oslo Bors tickers on Yahoo Finance use a ".OL" suffix, e.g. "EQNR.OL" for
Equinor, "DNB.OL" for DNB Bank, "NHY.OL" for Norsk Hydro.

Once Nordnet API access is set up, `nordnet_client.py` can provide a
matching `get_history()` so strategies can switch data sources without
changing their own code.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yfinance as yf

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def get_history(
    ticker: str,
    period: str = "2y",
    interval: str = "1d",
    use_cache: bool = True,
) -> pd.DataFrame:
    """Fetch historical OHLCV data for `ticker`.

    Parameters
    ----------
    ticker: Yahoo Finance ticker symbol, e.g. "EQNR.OL" (Oslo Bors) or "AAPL".
    period: How far back to fetch, e.g. "6mo", "1y", "2y", "5y", "max".
    interval: Bar size, e.g. "1d", "1h", "15m".
    use_cache: If True, reuse a cached CSV in ./data when available instead
        of hitting the network again.

    Returns
    -------
    DataFrame indexed by date with columns: Open, High, Low, Close, Volume.
    """
    DATA_DIR.mkdir(exist_ok=True)
    cache_file = DATA_DIR / f"{ticker.replace('.', '_')}_{period}_{interval}.csv"

    if use_cache and cache_file.exists():
        df = pd.read_csv(cache_file, index_col=0, parse_dates=True)
        return df

    df = yf.download(ticker, period=period, interval=interval, progress=False)
    if df.empty:
        raise ValueError(
            f"No data returned for ticker '{ticker}'. Check the symbol "
            f"(Oslo Bors tickers need a '.OL' suffix, e.g. 'EQNR.OL')."
        )

    # yfinance sometimes returns MultiIndex columns for a single ticker; flatten them.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df.to_csv(cache_file)
    return df


if __name__ == "__main__":
    # Quick manual check: python -m trading.data
    sample = get_history("EQNR.OL", period="6mo")
    print(sample.tail())
