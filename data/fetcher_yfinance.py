import warnings
import pandas as pd
import yfinance as yf
from datetime import date

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import YF_TICKERS


def fetch_yf_series(
    tickers: dict[str, str],
    start: str,
    end: str | None = None,
    interval: str = "1d",
) -> pd.DataFrame:
    """Fetches yfinance Close prices. Returns DataFrame with friendly-key columns.
    Handles MultiIndex, timezone issues, and missing tickers gracefully.
    """
    end = end or str(date.today())
    raw_tickers = list(tickers.values())

    try:
        raw = yf.download(
            raw_tickers,
            start=start,
            end=end,
            interval=interval,
            auto_adjust=True,
            progress=False,
            threads=True,
        )
    except Exception as e:
        warnings.warn(f"yfinance download failed: {e}")
        return pd.DataFrame()

    # Flatten MultiIndex columns (Price, Ticker) → just Close prices
    if isinstance(raw.columns, pd.MultiIndex):
        try:
            closes = raw["Close"]
        except KeyError:
            warnings.warn("yfinance: no 'Close' level found in MultiIndex")
            return pd.DataFrame()
    else:
        closes = raw[["Close"]] if "Close" in raw.columns else raw

    # Strip timezone
    if hasattr(closes.index, "tz") and closes.index.tz is not None:
        closes.index = closes.index.tz_localize(None)
    closes.index = pd.to_datetime(closes.index).normalize()
    closes.index.name = "date"

    # Rename ticker → friendly key
    rev = {v: k for k, v in tickers.items()}
    closes = closes.rename(columns=rev)

    # Warn about missing tickers
    for key in tickers:
        if key not in closes.columns:
            warnings.warn(f"yfinance: {key} ({tickers[key]}) not in result — column will be NaN")
            closes[key] = float("nan")

    return closes[list(tickers.keys())]


def fetch_yf_latest(tickers: dict[str, str]) -> dict:
    """Returns the most recent available value for each ticker (for NOW view)."""
    raw = yf.download(
        list(tickers.values()),
        period="5d",
        interval="1d",
        auto_adjust=True,
        progress=False,
    )

    if isinstance(raw.columns, pd.MultiIndex):
        closes = raw["Close"]
    else:
        closes = raw

    if hasattr(closes.index, "tz") and closes.index.tz is not None:
        closes.index = closes.index.tz_localize(None)

    rev = {v: k for k, v in tickers.items()}
    closes = closes.rename(columns=rev)

    result = {}
    for key in tickers:
        col = closes.get(key)
        if col is not None:
            last = col.dropna()
            result[key] = float(last.iloc[-1]) if not last.empty else None
        else:
            result[key] = None
    return result


if __name__ == "__main__":
    df = fetch_yf_series(YF_TICKERS, start="2020-01-01")
    print(df.tail(5))
    print(f"\nShape: {df.shape}")
    print(f"NaN counts:\n{df.isna().sum()}")
