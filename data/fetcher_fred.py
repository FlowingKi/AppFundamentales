import warnings
import pandas as pd
from datetime import date
from fredapi import Fred

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import FRED_API_KEY, FRED_SERIES


def fetch_fred_series(
    series_ids: dict[str, str],
    start: str,
    end: str | None = None,
) -> pd.DataFrame:
    """Fetches FRED series. Returns DataFrame with one column per series (friendly key).
    Missing or empty series → NaN column, no crash.
    """
    if not FRED_API_KEY:
        raise ValueError("FRED_API_KEY is empty — set it in config.py (gratis: fred.stlouisfed.org)")

    fred = Fred(api_key=FRED_API_KEY)
    end = end or str(date.today())
    frames = {}

    for key, code in series_ids.items():
        try:
            s = fred.get_series(code, observation_start=start, observation_end=end)
            if s is None or s.empty:
                warnings.warn(f"FRED: {code} ({key}) returned empty — column will be NaN")
                frames[key] = pd.Series(dtype=float, name=key)
            else:
                s.name = key
                frames[key] = s
        except Exception as e:
            warnings.warn(f"FRED: could not fetch {code} ({key}): {e}")
            frames[key] = pd.Series(dtype=float, name=key)

    df = pd.DataFrame(frames)
    df.index = pd.to_datetime(df.index).normalize()
    df.index.name = "date"
    return df


if __name__ == "__main__":
    df = fetch_fred_series(FRED_SERIES, start="2020-01-01")
    print(df.tail(5))
    print(f"\nShape: {df.shape}")
    print(f"NaN counts:\n{df.isna().sum()}")
