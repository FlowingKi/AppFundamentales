"""
Cache layer: load from CSV if fresh, else fetch and save.
Also handles merging FRED + yfinance into one aligned DataFrame.
"""
import warnings
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (
    FRED_SERIES, YF_TICKERS,
    FRED_CACHE, YF_CACHE,
    CACHE_MAX_AGE_HOURS,
)
from data.fetcher_fred import fetch_fred_series
from data.fetcher_yfinance import fetch_yf_series


def _is_fresh(path: Path, max_age_hours: int) -> bool:
    if not path.exists():
        return False
    age = datetime.now() - datetime.fromtimestamp(path.stat().st_mtime)
    return age < timedelta(hours=max_age_hours)


def load_or_fetch_fred(start: str = "2018-01-01", max_age_hours: int = CACHE_MAX_AGE_HOURS) -> pd.DataFrame:
    if _is_fresh(FRED_CACHE, max_age_hours):
        df = pd.read_csv(FRED_CACHE, index_col=0, parse_dates=True)
        df.index = pd.to_datetime(df.index).normalize()
        return df

    df = fetch_fred_series(FRED_SERIES, start=start)
    FRED_CACHE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(FRED_CACHE)
    return df


def load_or_fetch_yf(start: str = "2018-01-01", max_age_hours: int = CACHE_MAX_AGE_HOURS) -> pd.DataFrame:
    if _is_fresh(YF_CACHE, max_age_hours):
        df = pd.read_csv(YF_CACHE, index_col=0, parse_dates=True)
        df.index = pd.to_datetime(df.index).normalize()
        return df

    df = fetch_yf_series(YF_TICKERS, start=start)
    YF_CACHE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(YF_CACHE)
    return df


def merge_all_sources(fred_df: pd.DataFrame, yf_df: pd.DataFrame) -> pd.DataFrame:
    """Inner join on date — drops days where either source has no data.
    This eliminates holiday mismatches between FRED and yfinance.
    """
    fred_df.index = pd.to_datetime(fred_df.index).normalize()
    yf_df.index   = pd.to_datetime(yf_df.index).normalize()

    df = pd.merge(fred_df, yf_df, left_index=True, right_index=True, how="inner")

    # Sanity: warn if merge dropped more than 5% of rows
    total = max(len(fred_df), len(yf_df))
    dropped_pct = (total - len(df)) / total * 100
    if dropped_pct > 5:
        warnings.warn(f"merge_all_sources: inner join dropped {dropped_pct:.1f}% of rows — check date alignment")

    return df


def load_all(start: str = "2018-01-01") -> pd.DataFrame:
    """Full pipeline: load/fetch both sources and merge."""
    fred = load_or_fetch_fred(start=start)
    yf   = load_or_fetch_yf(start=start)
    return merge_all_sources(fred, yf)


if __name__ == "__main__":
    df = load_all()
    print(df.tail(5))
    print(f"\nShape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"NaN totals:\n{df.isna().sum()}")
