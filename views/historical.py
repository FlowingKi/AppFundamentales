import streamlit as st
import plotly.graph_objects as go
import pandas as pd

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import CHART_EVENTS
from signals.context import get_signal_context
from signals.spreads import SPREAD_COLS


_SERIES_OPTIONS = {
    "US2Y — Treasury 2Y": "US2Y",
    "US5Y — Treasury 5Y": "US5Y",
    "US10Y — Treasury 10Y": "US10Y",
    "US30Y — Treasury 30Y": "US30Y",
    "DE10Y — Bund 10Y": "DE10Y",
    "JP10Y — JGB 10Y": "JP10Y",
    "HY — High Yield spread": "HY",
    "IG — Investment Grade spread": "IG",
    "SOFR": "SOFR",
    "DXY": "DXY",
    "GOLD": "GOLD",
    "VIX": "VIX",
    "SPY": "SPY",
    "Spread US-DE": "SPREAD_US_DE",
    "Spread US-JP": "SPREAD_US_JP",
    "Curva 2Y-10Y": "CURVE_2_10",
    "Curva 2Y-5Y": "CURVE_2_5",
    "Curva 5Y-10Y": "CURVE_5_10",
    "Real Yield": "REAL_YIELD",
    "Spread HY-IG": "SPREAD_HY_IG",
}

_RANGES = {"3M": 63, "6M": 126, "1Y": 252, "3Y": 756, "MAX": None}

_REGIME_COLORS = {
    "EUFORIA":    "#00c853",
    "RISK_ON":    "#69f0ae",
    "TRANSICION": "#ffeb3b",
    "RISK_OFF":   "#ff9800",
    "PANICO":     "#f44336",
}


def render(df: pd.DataFrame, regime_series: pd.Series):
    st.subheader("Histórico")

    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        label = st.selectbox("Serie", list(_SERIES_OPTIONS.keys()), key="hist_series")
    with col2:
        range_key = st.radio("Rango", list(_RANGES.keys()), index=2, horizontal=True, key="hist_range")
    with col3:
        compare_label = st.selectbox("Comparar con", ["—"] + list(_SERIES_OPTIONS.keys()), key="hist_compare")

    col = _SERIES_OPTIONS[label]
    n_days = _RANGES[range_key]

    if col not in df.columns:
        st.warning(f"Serie '{col}' no disponible en los datos cargados.")
        return

    series = df[col].dropna()
    if n_days:
        series = series.iloc[-n_days:]

    if series.empty:
        st.info("Sin datos para el rango seleccionado.")
        return

    # Percentile bands
    p10 = series.quantile(0.10)
    p50 = series.quantile(0.50)
    p90 = series.quantile(0.90)

    fig = go.Figure()

    # Shaded band p10-p90
    fig.add_trace(go.Scatter(
        x=list(series.index) + list(series.index[::-1]),
        y=[p90]*len(series) + [p10]*len(series),
        fill="toself",
        fillcolor="rgba(100,100,200,0.12)",
        line=dict(color="rgba(0,0,0,0)"),
        name="Banda p10-p90",
        hoverinfo="skip",
    ))

    # p50 dashed line
    fig.add_hline(y=p50, line_dash="dot", line_color="gray", annotation_text="p50")

    # Main line
    fig.add_trace(go.Scatter(x=series.index, y=series.values, name=col, line=dict(width=2)))

    # Optional comparison series (dual Y)
    if compare_label != "—":
        compare_col = _SERIES_OPTIONS[compare_label]
        if compare_col in df.columns:
            s2 = df[compare_col].dropna()
            if n_days:
                s2 = s2.iloc[-n_days:]
            fig.add_trace(go.Scatter(
                x=s2.index, y=s2.values,
                name=compare_col,
                yaxis="y2",
                line=dict(width=1.5, dash="dash"),
            ))
            fig.update_layout(yaxis2=dict(overlaying="y", side="right", showgrid=False))

    # Event lines
    for event_date, event_name in CHART_EVENTS:
        if pd.Timestamp(event_date) in series.index or (
            pd.Timestamp(event_date) >= series.index[0] and pd.Timestamp(event_date) <= series.index[-1]
        ):
            fig.add_vline(
                x=event_date,
                line_dash="dot",
                line_color="rgba(255,100,0,0.5)",
                annotation_text=event_name,
                annotation_position="top left",
                annotation_font_size=10,
            )

    fig.update_layout(
        height=400,
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", y=-0.1),
        hovermode="x unified",
        dragmode="pan",
    )
    st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True})

    # Regime bar
    if regime_series is not None and not regime_series.empty:
        reg = regime_series.reindex(series.index, method="ffill").dropna()
        if not reg.empty:
            colors = [_REGIME_COLORS.get(r, "#888") for r in reg.values]
            fig_reg = go.Figure(go.Bar(
                x=reg.index,
                y=[1]*len(reg),
                marker_color=colors,
                hovertext=reg.values,
                hoverinfo="text+x",
                showlegend=False,
            ))
            fig_reg.update_layout(
                height=40,
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis=dict(visible=False),
                yaxis=dict(visible=False, range=[0, 1]),
                bargap=0,
            )
            st.plotly_chart(fig_reg, use_container_width=True)

    # ── Contexto de la señal seleccionada ────────────────────────────────────
    ctx = get_signal_context(col)
    if ctx:
        with st.expander(f"📖 ¿Qué es {col}? — Contexto y tesis"):
            c1, c2 = st.columns([1, 1])
            with c1:
                st.markdown(f"**¿Qué es?**\n\n{ctx.get('que_es', '')}")
                st.markdown(f"**Tesis económica:**\n\n{ctx.get('tesis', '')}")
            with c2:
                if "direccion" in ctx:
                    st.info(f"**Cómo leerlo:**\n\n{ctx['direccion']}")
                if "que_vigilar" in ctx:
                    st.warning(f"**Qué vigilar:**\n\n{ctx['que_vigilar']}")
