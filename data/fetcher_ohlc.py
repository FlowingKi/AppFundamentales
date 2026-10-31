import pandas as pd
import yfinance as yf


def fetch_ohlc(ticker: str, interval: str) -> pd.DataFrame:
    """Fetch OHLC from yfinance. interval: '1h', '4h', '1d', '1w'."""
    if interval in ("1h", "4h"):
        raw = yf.download(ticker, period="60d", interval="1h", progress=False, auto_adjust=True)
        if interval == "4h":
            raw = _resample(raw, "4h")
    elif interval == "1d":
        raw = yf.download(ticker, period="2y", interval="1d", progress=False, auto_adjust=True)
    else:  # 1w
        raw = yf.download(ticker, period="5y", interval="1d", progress=False, auto_adjust=True)
        raw = _resample(raw, "W")

    if raw.empty:
        return pd.DataFrame()

    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)

    raw.index = pd.to_datetime(raw.index).tz_localize(None)
    return raw[["Open", "High", "Low", "Close"]].dropna()


def _resample(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df.resample(rule).agg({
        "Open":  "first",
        "High":  "max",
        "Low":   "min",
        "Close": "last",
    }).dropna()
