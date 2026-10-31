import pandas as pd


def calculate_spreads(df: pd.DataFrame) -> pd.DataFrame:
    """Adds spread columns to df. Does not modify original columns.
    NaN inputs → NaN spread (no fill, no interpolation).
    """
    out = df.copy()

    out["SPREAD_US_DE"] = out.get("US10Y", pd.Series(dtype=float)) - out.get("DE10Y", pd.Series(dtype=float))
    out["SPREAD_US_JP"] = out.get("US10Y", pd.Series(dtype=float)) - out.get("JP10Y", pd.Series(dtype=float))

    out["CURVE_2_10"] = out.get("US10Y", pd.Series(dtype=float)) - out.get("US2Y", pd.Series(dtype=float))
    out["CURVE_2_5"]  = out.get("US5Y",  pd.Series(dtype=float)) - out.get("US2Y", pd.Series(dtype=float))
    out["CURVE_5_10"] = out.get("US10Y", pd.Series(dtype=float)) - out.get("US5Y", pd.Series(dtype=float))

    # Real yield: prefer FRED TIPS-based; fallback to nominal - breakeven
    if "REAL10Y" in out.columns and out["REAL10Y"].notna().any():
        out["REAL_YIELD"] = out["REAL10Y"]
    elif "US10Y" in out.columns and "BREAK10" in out.columns:
        out["REAL_YIELD"] = out["US10Y"] - out["BREAK10"]
    else:
        out["REAL_YIELD"] = float("nan")

    out["SPREAD_HY_IG"] = out.get("HY", pd.Series(dtype=float)) - out.get("IG", pd.Series(dtype=float))

    return out


SPREAD_COLS = [
    "SPREAD_US_DE", "SPREAD_US_JP",
    "CURVE_2_10", "CURVE_2_5", "CURVE_5_10",
    "REAL_YIELD", "SPREAD_HY_IG",
]


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from data.cache import load_all

    df = load_all()
    df = calculate_spreads(df)

    print("Spreads sample (last 5 rows):")
    print(df[SPREAD_COLS].tail(5))
    print("\nVerification — CURVE_2_10 negative in 2022-2023 (should be True):")
    mask = (df.index >= "2022-07-01") & (df.index <= "2023-06-30")
    inverted = (df.loc[mask, "CURVE_2_10"] < 0).mean()
    print(f"  {inverted*100:.0f}% of days inverted in that window")
