import streamlit as st
import plotly.graph_objects as go
import pandas as pd

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from data.fetcher_ohlc import fetch_ohlc


# ── Catálogo de activos ───────────────────────────────────────────────────────
# ("tipo", "ticker_o_col", "descripcion")
# tipo: "fred_line" → usa df ya cargado (yield diario, solo línea)
#       "yf_candle" → descarga OHLC en tiempo real

_ASSETS = {
    # ── Yields FRED (tasa, no precio) ─────────────────────────────────────────
    "📈 US2Y — Yield Treasury 2Y  [FRED, tasa diaria]":  ("fred_line", "US2Y",   "Tasa (%) — dato diario de FRED"),
    "📈 US5Y — Yield Treasury 5Y  [FRED, tasa diaria]":  ("fred_line", "US5Y",   "Tasa (%) — dato diario de FRED"),
    "📈 US10Y — Yield Treasury 10Y [FRED, tasa diaria]": ("fred_line", "US10Y",  "Tasa (%) — dato diario de FRED"),
    "📈 US30Y — Yield Treasury 30Y [FRED, tasa diaria]": ("fred_line", "US30Y",  "Tasa (%) — dato diario de FRED"),
    "📈 DE10Y — Yield Bund 10Y  [FRED, tasa diaria]":    ("fred_line", "DE10Y",  "Tasa (%) — dato diario de FRED"),
    "📈 JP10Y — Yield JGB 10Y  [FRED, tasa diaria]":     ("fred_line", "JP10Y",  "Tasa (%) — dato diario de FRED"),
    # ── Futuros de bonos (precio, intraday) ───────────────────────────────────
    "🕯️ ZT=F — Futuro T-Note 2Y  [precio, intraday]":   ("yf_candle", "ZT=F",   "Precio del futuro 2Y — inverso al yield"),
    "🕯️ ZF=F — Futuro T-Note 5Y  [precio, intraday]":   ("yf_candle", "ZF=F",   "Precio del futuro 5Y — inverso al yield"),
    "🕯️ ZN=F — Futuro T-Note 10Y [precio, intraday]":   ("yf_candle", "ZN=F",   "Precio del futuro 10Y — inverso al yield"),
    "🕯️ ZB=F — Futuro T-Bond 30Y [precio, intraday]":   ("yf_candle", "ZB=F",   "Precio del futuro 30Y — inverso al yield"),
    "🕯️ TLT — ETF bono largo EEUU [precio, intraday]":  ("yf_candle", "TLT",    "ETF que sigue bonos 20Y+"),
    # ── Macro intraday ─────────────────────────────────────────────────────────
    "🕯️ DXY — US Dollar Index [precio, intraday]":      ("yf_candle", "DX-Y.NYB", "Índice del dólar vs cesta de divisas"),
    "🕯️ GC=F — Oro futuro [precio, intraday]":          ("yf_candle", "GC=F",   "Futuro del oro en USD/oz"),
    "🕯️ SPY — S&P 500 ETF [precio, intraday]":          ("yf_candle", "SPY",    "ETF del S&P 500"),
    "🕯️ QQQ — Nasdaq 100 ETF [precio, intraday]":       ("yf_candle", "QQQ",    "ETF del Nasdaq 100"),
    "🕯️ ^VIX — Volatilidad implícita S&P [intraday]":   ("yf_candle", "^VIX",   "Índice de miedo del mercado"),
}

_TIMEFRAMES = {
    "1H":  "1h",
    "4H":  "4h",
    "Diario": "1d",
    "Semanal": "1w",
}

_FRED_RANGES = {"3M": 63, "6M": 126, "1Y": 252, "3Y": 756, "MAX": None}


def render(df: pd.DataFrame):
    st.subheader("Velas / Intraday")

    label = st.selectbox("Activo", list(_ASSETS.keys()), key="candle_asset")
    kind, ticker_or_col, descripcion = _ASSETS[label]

    # ── FRED yield → línea diaria ─────────────────────────────────────────────
    if kind == "fred_line":
        st.info(f"**{descripcion}** — Los yields de FRED son datos de cierre diario; no hay OHLC intraday disponible gratis.")

        range_key = st.radio("Rango", list(_FRED_RANGES.keys()), index=2, horizontal=True, key="candle_fred_range")
        n_days = _FRED_RANGES[range_key]

        if ticker_or_col not in df.columns:
            st.warning(f"Serie '{ticker_or_col}' no disponible.")
            return

        series = df[ticker_or_col].dropna()
        if n_days:
            series = series.iloc[-n_days:]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=series.index, y=series.values, name=ticker_or_col, line=dict(width=2, color="#4fc3f7")))
        fig.update_layout(
            height=450,
            margin=dict(l=0, r=0, t=10, b=0),
            hovermode="x unified",
            dragmode="pan",
            yaxis_title="Yield (%)",
            xaxis_rangeslider_visible=False,
        )
        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True})
        return

    # ── yfinance candle ───────────────────────────────────────────────────────
    st.caption(f"📌 {descripcion}")
    st.warning("⚠️ Este gráfico muestra el **precio** del instrumento, NO la tasa. Precio de bono y yield se mueven en direcciones opuestas.", icon=None)

    tf_label = st.radio("Timeframe", list(_TIMEFRAMES.keys()), index=2, horizontal=True, key="candle_tf")
    interval = _TIMEFRAMES[tf_label]

    with st.spinner("Cargando datos..."):
        ohlc = fetch_ohlc(ticker_or_col, interval)

    if ohlc.empty:
        st.error("No se pudieron cargar datos para este activo.")
        return

    fig = go.Figure(go.Candlestick(
        x=ohlc.index,
        open=ohlc["Open"],
        high=ohlc["High"],
        low=ohlc["Low"],
        close=ohlc["Close"],
        name=ticker_or_col,
        increasing_line_color="#26a69a",
        decreasing_line_color="#ef5350",
    ))

    fig.update_layout(
        height=500,
        margin=dict(l=0, r=0, t=10, b=0),
        hovermode="x unified",
        dragmode="pan",
        xaxis_rangeslider_visible=False,
    )
    st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True})

    c1, c2, c3, c4 = st.columns(4)
    last = ohlc.iloc[-1]
    prev = ohlc.iloc[-2] if len(ohlc) > 1 else last
    chg = last["Close"] - prev["Close"]
    pct = chg / prev["Close"] * 100 if prev["Close"] else 0
    c1.metric("Último", f"{last['Close']:.4f}")
    c2.metric("Cambio", f"{chg:+.4f}", f"{pct:+.2f}%")
    c3.metric("Máx sesión", f"{last['High']:.4f}")
    c4.metric("Mín sesión", f"{last['Low']:.4f}")
