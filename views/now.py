import streamlit as st
import plotly.graph_objects as go
import pandas as pd

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

_REGIME_EMOJI = {
    "EUFORIA":    "💚 EUFORIA",
    "RISK_ON":    "🟢 RISK-ON",
    "TRANSICION": "🟡 TRANSICIÓN",
    "RISK_OFF":   "🟠 RISK-OFF",
    "PANICO":     "🔴 PÁNICO",
}

_REGIME_COLOR = {
    "EUFORIA":    "#00c853",
    "RISK_ON":    "#69f0ae",
    "TRANSICION": "#ffeb3b",
    "RISK_OFF":   "#ff9800",
    "PANICO":     "#f44336",
}


def _sparkline(series: pd.Series, color: str = "#4fc3f7") -> go.Figure:
    fig = go.Figure(go.Scatter(
        y=series.tail(30).values,
        mode="lines",
        line=dict(color=color, width=1.2),
    ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=30, width=100,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def _delta_arrow(delta: float) -> str:
    if pd.isna(delta):
        return "—"
    return f"▲ {delta:+.2f}" if delta > 0 else f"▼ {delta:+.2f}"


def render(df: pd.DataFrame, regime: str, last_refresh: str):
    # Header: régimen + timestamp
    color = _REGIME_COLOR.get(regime, "#888")
    label = _REGIME_EMOJI.get(regime, regime)
    st.markdown(
        f"<div style='background:{color};padding:12px 20px;border-radius:8px;"
        f"font-size:1.4em;font-weight:bold;color:#000;margin-bottom:12px'>"
        f"{label}</div>",
        unsafe_allow_html=True,
    )
    st.caption(f"Último refresh: {last_refresh}")

    if df is None or df.empty:
        st.warning("Sin datos disponibles.")
        return

    last = df.iloc[-1]
    prev = df.iloc[-2] if len(df) >= 2 else last

    # ── Yields grid ──────────────────────────────────────────────────────────
    st.markdown("##### Yields")
    yield_cols = [
        ("US2Y",  "US 2Y"),
        ("US5Y",  "US 5Y"),
        ("US10Y", "US 10Y"),
        ("US30Y", "US 30Y"),
        ("DE10Y", "DE 10Y"),
        ("JP10Y", "JP 10Y"),
    ]
    cols = st.columns(len(yield_cols))
    for (key, label_), col in zip(yield_cols, cols):
        val  = last.get(key, float("nan"))
        delt = val - prev.get(key, float("nan")) if key in df.columns else float("nan")
        with col:
            st.metric(label_, f"{val:.2f}%" if not pd.isna(val) else "—", _delta_arrow(delt))

    # ── Market assets grid ────────────────────────────────────────────────────
    st.markdown("##### Activos")
    asset_cols = [("DXY","DXY"), ("GOLD","Gold"), ("SPY","SPY"), ("QQQ","QQQ"), ("VIX","VIX")]
    cols = st.columns(len(asset_cols))
    for (key, label_), col in zip(asset_cols, cols):
        val  = last.get(key, float("nan"))
        delt = val - prev.get(key, float("nan")) if key in df.columns else float("nan")
        with col:
            fmt = f"{val:.0f}" if key == "GOLD" else f"{val:.2f}"
            st.metric(label_, fmt if not pd.isna(val) else "—", _delta_arrow(delt))

    # ── Spreads grid with sparklines ─────────────────────────────────────────
    st.markdown("##### Spreads")
    spread_defs = [
        ("SPREAD_US_DE", "US-DE"),
        ("SPREAD_US_JP", "US-JP"),
        ("CURVE_2_10",   "Curva 2-10"),
        ("REAL_YIELD",   "Real Yield"),
        ("HY",           "HY spread"),
        ("SPREAD_HY_IG", "HY-IG"),
    ]

    for key, label_ in spread_defs:
        if key not in df.columns:
            continue
        series = df[key].dropna()
        if series.empty:
            continue
        val  = series.iloc[-1]
        delt = val - series.iloc[-2] if len(series) >= 2 else float("nan")

        c1, c2, c3 = st.columns([1.5, 1, 2])
        with c1:
            st.markdown(f"**{label_}**")
        with c2:
            direction = "▲" if not pd.isna(delt) and delt > 0 else "▼"
            color_str  = "#f44336" if not pd.isna(delt) and delt > 0 else "#00c853"
            st.markdown(
                f"<span style='font-size:1.1em'>{val:.2f}</span> "
                f"<span style='color:{color_str}'>{direction} {abs(delt):.2f}</span>"
                if not pd.isna(val) else "—",
                unsafe_allow_html=True,
            )
        with c3:
            sparkline_color = "#4fc3f7" if not pd.isna(delt) or delt >= 0 else "#f44336"
            st.plotly_chart(_sparkline(series, sparkline_color), use_container_width=False)
