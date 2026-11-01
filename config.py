from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent
DB_DIR = ROOT / "db"
DB_PATH = DB_DIR / "log.db"
FRED_CACHE = DB_DIR / "fred_cache.csv"
YF_CACHE   = DB_DIR / "yf_cache.csv"
LATEST_JSON = DB_DIR / "latest_values.json"

# ── API Keys ─────────────────────────────────────────────────────────────────
import os
FRED_API_KEY = os.environ.get("FRED_API_KEY", "")

# ── Series FRED ──────────────────────────────────────────────────────────────
FRED_SERIES = {
    "US2Y":    "DGS2",
    "US5Y":    "DGS5",
    "US10Y":   "DGS10",
    "US30Y":   "DGS30",
    "REAL10Y": "DFII10",
    "BREAK10": "T10YIE",
    "DE10Y":   "IRLTLT01DEM156N",   # 1-month lag en Fase 1; reemplazar con tvdatafeed en Fase 8
    "JP10Y":   "IRLTLT01JPM156N",   # ídem
    "HY":      "BAMLH0A0HYM2",      # ICE BofA HY — solo disponible desde Oct 2023 en FRED (cambio de licencia)
    "BAA10Y":  "BAA10Y",             # Moody's Baa spread vs 10Y — historia desde 1986, proxy de crédito
    "IG":      "BAMLC0A0CM",
    "SOFR":    "SOFR",
    "CURVE":   "T10Y2Y",
}

# ── Tickers yfinance ──────────────────────────────────────────────────────────
YF_TICKERS = {
    "DXY":      "DX-Y.NYB",
    "GOLD":     "GC=F",
    "SPY":      "SPY",
    "QQQ":      "QQQ",
    "VIX":      "^VIX",
    "DE10Y_RT": "DE10YT=RR",   # Reuters daily — override FRED mensual cuando disponible
    "JP10Y_RT": "JP10YT=RR",
}

# ── Thresholds de régimen (calibrar en Fase 10) ───────────────────────────────
REGIME_THRESHOLDS = {
    # BAA10Y — Moody's Baa spread vs 10Y Treasury (en %, historia desde 1986)
    # COVID 2020 peak: ~4.5%, crisis 2008: ~6%, normal: 1.5-2.5%, tight: <1.5%
    "BAA10Y": [
        (1.50,  2.0),   # < 150bps  → euforia
        (2.00,  1.0),   # 150-200   → risk-on
        (2.80,  0.0),   # 200-280   → transición
        (4.00, -1.0),   # 280-400   → risk-off
        (99.0, -2.0),   # > 400     → pánico
    ],
    # HY spread (BAMLH0A0HYM2 — solo desde Oct 2023, usa % no bps)
    "HY": [
        (2.80,  2.0),
        (3.80,  1.0),
        (5.00,  0.0),
        (6.50, -1.0),
        (99.0, -2.0),
    ],
    # Curva 2Y-10Y (%) — FRED T10Y2Y en %
    "CURVE": [
        (-0.8, -2.0),   # < -80bps  → invertida severa
        (-0.2, -1.0),   # -80 a -20 → invertida leve
        ( 0.2,  0.0),   # -20 a +20 → plana
        ( 1.0,  1.0),   # +20 a +100→ normal
        ( 9.9,  2.0),   # > +100    → muy empinada
    ],
    # Real yield (%) — FRED DFII10
    "REAL10Y": [
        ( 0.0,  2.0),   # negativo  → muy favorable (2020 scenario)
        ( 1.0,  1.0),   # 0-1%      → favorable
        ( 1.8,  0.0),   # 1-1.8%    → neutral
        ( 2.5, -1.0),   # 1.8-2.5%  → restrictivo
        ( 9.9, -2.0),   # > 2.5%    → muy restrictivo
    ],
}

REGIME_WEIGHTS = {
    "HY":        0.25,
    "CURVE":     0.20,
    "REAL10Y":   0.15,
    "VIX":       0.20,   # agregado: detecta pánico por volatilidad (ej: carry unwind ago-2024)
    "DXY_TREND": 0.12,
    "HY_TREND":  0.08,
}

REGIME_VIX_THRESHOLDS = [
    (15.0,  2.0),   # < 15   → calma/euforia
    (20.0,  1.0),   # 15-20  → normal
    (30.0,  0.0),   # 20-30  → cautela
    (40.0, -1.0),   # 30-40  → miedo
    (99.0, -2.0),   # > 40   → pánico (COVID: 80, ago-2024: 65)
]

REGIME_LEVELS = [
    ( 1.0, "EUFORIA"),
    ( 0.25, "RISK_ON"),
    (-0.25, "TRANSICION"),
    (-0.60, "RISK_OFF"),
    (-9.9,  "PANICO"),
]

# ── Thresholds de imbalances ──────────────────────────────────────────────────
PERCENTILE_HIGH = 90
PERCENTILE_LOW  = 10
CORR_BREAKDOWN  = 0.4
ZSCORE_EXTREME  = 2.0

CORR_PAIRS = [
    ("SPREAD_US_JP", "DXY",  0.75),
    ("REAL10Y",      "GOLD", -0.70),
    ("HY",           "SPY",  -0.65),
    ("SPREAD_US_DE", "DXY",  0.70),
]

# ── Eventos históricos para gráficos ─────────────────────────────────────────
CHART_EVENTS = [
    ("2020-03-15", "COVID crash"),
    ("2022-03-16", "Fed 1er hike"),
    ("2022-12-20", "BOJ amplía YCC"),
    ("2023-07-26", "Fed último hike"),
    ("2024-08-05", "JPY carry unwind"),
]

# ── Refresh ───────────────────────────────────────────────────────────────────
REFRESH_INTERVAL_SEC = 900   # 15 min
CACHE_MAX_AGE_HOURS  = 23

# ── Alertas ───────────────────────────────────────────────────────────────────
ALERT_EMAIL        = ""
ALERT_COOLDOWN_H   = 4
