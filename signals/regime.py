import pandas as pd

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import REGIME_THRESHOLDS, REGIME_WEIGHTS, REGIME_LEVELS, REGIME_VIX_THRESHOLDS


def score_variable(value: float, thresholds: list[tuple]) -> float:
    """Maps a value to a score using ordered (limit, score) pairs.
    Returns the score of the first threshold whose limit >= value.
    """
    if pd.isna(value):
        return 0.0
    for limit, score in thresholds:
        if value <= limit:
            return score
    return thresholds[-1][1]


def _dxy_trend(df: pd.DataFrame, idx: int, window: int = 20) -> float:
    """Score DXY 20-day trend: rising = negative for risk assets."""
    if "DXY" not in df.columns or idx < window:
        return 0.0
    start = df["DXY"].iloc[idx - window]
    end   = df["DXY"].iloc[idx]
    if pd.isna(start) or pd.isna(end) or start == 0:
        return 0.0
    pct = (end - start) / start * 100
    if   pct > 2:  return -2.0
    elif pct > 0:  return -1.0
    elif pct > -2: return  1.0
    else:           return  2.0


def _hy_trend_col(df: pd.DataFrame, idx: int, col: str, window: int = 10) -> float:
    """Score credit spread 10-day trend: widening = negative."""
    if col not in df.columns or idx < window:
        return 0.0
    start = df[col].iloc[idx - window]
    end   = df[col].iloc[idx]
    if pd.isna(start) or pd.isna(end):
        return 0.0
    delta = end - start
    # ponytail: thresholds in % units (BAA10Y and HY are both in %)
    if   delta >  0.50: return -2.0
    elif delta >  0.15: return -1.0
    elif delta > -0.15: return  0.0
    elif delta > -0.50: return  1.0
    else:                return  2.0


def calculate_regime_score(df: pd.DataFrame, idx: int) -> float:
    """Weighted score for one row (by integer index position)."""
    row = df.iloc[idx]

    # Credit spread: prefer BAMLH0A0HYM2 (HY, since Oct 2023) else BAA10Y (history since 1986)
    hy_val  = row.get("HY", float("nan"))
    baa_val = row.get("BAA10Y", float("nan"))
    if not pd.isna(hy_val):
        credit_score = score_variable(hy_val, REGIME_THRESHOLDS["HY"])
        credit_trend = _hy_trend_col(df, idx, "HY")
    elif not pd.isna(baa_val):
        credit_score = score_variable(baa_val, REGIME_THRESHOLDS["BAA10Y"])
        credit_trend = _hy_trend_col(df, idx, "BAA10Y")
    else:
        credit_score = 0.0
        credit_trend = 0.0

    scores = {
        "HY":        credit_score,
        "CURVE":     score_variable(row.get("CURVE_2_10", float("nan")), REGIME_THRESHOLDS["CURVE"]),
        "REAL10Y":   score_variable(row.get("REAL_YIELD", float("nan")), REGIME_THRESHOLDS["REAL10Y"]),
        "VIX":       score_variable(row.get("VIX", float("nan")), REGIME_VIX_THRESHOLDS),
        "DXY_TREND": _dxy_trend(df, idx),
        "HY_TREND":  credit_trend,
    }

    return sum(scores[k] * REGIME_WEIGHTS[k] for k in scores)


def assign_regime(score: float) -> str:
    for threshold, name in REGIME_LEVELS:
        if score >= threshold:
            return name
    return "PANICO"


def get_regime_series(df: pd.DataFrame) -> pd.Series:
    """Returns a Series of regime strings indexed by date."""
    scores = pd.Series(
        [calculate_regime_score(df, i) for i in range(len(df))],
        index=df.index,
    )
    return scores.map(assign_regime)


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from data.cache import load_all
    from signals.spreads import calculate_spreads

    df = load_all()
    df = calculate_spreads(df)
    regimes = get_regime_series(df)

    test_cases = [
        ("2020-03-20", ["PANICO", "RISK_OFF"]),   # COVID — curva positiva compensa parcialmente
        ("2021-11-01", ["EUFORIA", "RISK_ON"]),
        ("2022-09-01", ["RISK_OFF", "PANICO"]),
        ("2023-04-01", ["RISK_ON", "TRANSICION"]),
        ("2024-08-05", ["PANICO", "RISK_OFF", "TRANSICION"]),  # JPY carry unwind — VIX-driven, sin VIX en modelo
    ]

    print("=== Checkpoint 2: régimen en fechas clave ===")
    for date_str, expected in test_cases:
        closest = regimes.index[regimes.index.searchsorted(date_str)]
        result = regimes.loc[closest]
        ok = "OK" if result in expected else "FAIL"
        print(f"[{ok}] {date_str}: {result}  (esperado: {expected})")
