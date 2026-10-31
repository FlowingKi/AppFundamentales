import pandas as pd

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (
    PERCENTILE_HIGH, PERCENTILE_LOW,
    CORR_BREAKDOWN, ZSCORE_EXTREME,
    CORR_PAIRS,
)
from signals.correlations import rolling_percentile, rolling_corr, zscore
from signals.spreads import SPREAD_COLS


_WATCH_COLS = SPREAD_COLS + ["HY", "REAL_YIELD", "DXY"]


def detect_imbalances(df: pd.DataFrame) -> list[dict]:
    """Returns list of active imbalances based on last available row.
    Three methods: percentile, correlation breakdown, z-score.
    """
    if df.empty:
        return []

    results = []
    last_idx = df.index[-1]

    # ── Method 1: Percentile extremes ────────────────────────────────────────
    for col in _WATCH_COLS:
        if col not in df.columns:
            continue
        series = df[col].dropna()
        if len(series) < 60:
            continue

        pct_series = rolling_percentile(series)
        if pct_series.empty or pd.isna(pct_series.iloc[-1]):
            continue

        pct = pct_series.iloc[-1]
        val = series.iloc[-1]

        if pct >= PERCENTILE_HIGH:
            results.append({
                "type": "percentile_high",
                "asset": col,
                "description": f"{col} en percentil {pct:.0f}% (máximo 12 meses) — valor: {val:.2f}",
                "percentile": pct,
                "current_value": val,
                "related_asset": None,
            })
        elif pct <= PERCENTILE_LOW:
            results.append({
                "type": "percentile_low",
                "asset": col,
                "description": f"{col} en percentil {pct:.0f}% (mínimo 12 meses) — valor: {val:.2f}",
                "percentile": pct,
                "current_value": val,
                "related_asset": None,
            })

    # ── Method 2: Correlation breakdown ──────────────────────────────────────
    for col_a, col_b, expected_corr in CORR_PAIRS:
        if col_a not in df.columns or col_b not in df.columns:
            continue
        a = df[col_a].dropna()
        b = df[col_b].dropna()
        aligned = pd.concat([a, b], axis=1).dropna()
        if len(aligned) < 60:
            continue

        corr_series = rolling_corr(aligned.iloc[:, 0], aligned.iloc[:, 1])
        if corr_series.empty or pd.isna(corr_series.iloc[-1]):
            continue

        current_corr = corr_series.iloc[-1]
        # Breakdown when rolling corr diverges from expected direction
        if abs(expected_corr) >= 0.5 and abs(current_corr) < CORR_BREAKDOWN:
            results.append({
                "type": "correlation_breakdown",
                "asset": col_a,
                "description": (
                    f"Correlación {col_a}↔{col_b} cayó a {current_corr:.2f} "
                    f"(normal: {expected_corr:.2f}) — posible desconexión"
                ),
                "percentile": None,
                "current_value": current_corr,
                "related_asset": col_b,
                "expected_corr": expected_corr,
            })

    # ── Method 3: Z-score extremes ────────────────────────────────────────────
    for col in _WATCH_COLS:
        if col not in df.columns:
            continue
        series = df[col].dropna()
        if len(series) < 90:
            continue

        z_series = zscore(series)
        if z_series.empty or pd.isna(z_series.iloc[-1]):
            continue

        z = z_series.iloc[-1]
        val = series.iloc[-1]

        if abs(z) >= ZSCORE_EXTREME:
            direction = "alto" if z > 0 else "bajo"
            results.append({
                "type": "zscore_extreme",
                "asset": col,
                "description": f"{col} z-score {z:.1f} ({direction} vs media 90d) — valor: {val:.2f}",
                "percentile": None,
                "current_value": val,
                "zscore": z,
                "related_asset": None,
            })

    return results
