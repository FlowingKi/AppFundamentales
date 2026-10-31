import pandas as pd


def rolling_corr(series_a: pd.Series, series_b: pd.Series, window: int = 60) -> pd.Series:
    """60-day rolling correlation. First 59 rows will be NaN — expected."""
    return series_a.rolling(window).corr(series_b)


def rolling_percentile(series: pd.Series, window: int = 252) -> pd.Series:
    """Position of current value within its rolling window (0–100).
    First (window-1) rows will be NaN.
    """
    return series.rolling(window).apply(
        lambda x: pd.Series(x).rank(pct=True).iloc[-1] * 100,
        raw=False,
    )


def zscore(series: pd.Series, window: int = 90) -> pd.Series:
    """Z-score of current value vs rolling mean/std.
    Protected against std=0 (constant window → returns 0.0).
    """
    mean = series.rolling(window).mean()
    std  = series.rolling(window).std()
    # ponytail: where() is faster than apply for this — stays vectorized
    return (series - mean).where(std > 0, 0.0) / std.where(std > 0, 1.0)
