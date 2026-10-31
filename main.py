"""
Screener Intermarket — main.py
Run: streamlit run main.py
"""
import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Screener Intermarket",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Imports after page config ─────────────────────────────────────────────────
from streamlit_autorefresh import st_autorefresh  # type: ignore

from data.cache import load_all
from signals.spreads import calculate_spreads
from signals.regime import get_regime_series, assign_regime, calculate_regime_score
from signals.imbalances import detect_imbalances
from views import historical, now, imbalances_view, log_view, candles_view
from config import REFRESH_INTERVAL_SEC


# ── Auto-refresh ──────────────────────────────────────────────────────────────
st_autorefresh(interval=REFRESH_INTERVAL_SEC * 1000, key="autorefresh")


# ── Data loading (cached 15 min) ──────────────────────────────────────────────
@st.cache_data(ttl=REFRESH_INTERVAL_SEC)
def get_data():
    df = load_all()
    df = calculate_spreads(df)
    return df


@st.cache_data(ttl=REFRESH_INTERVAL_SEC)
def get_regime(df_hash: int):  # ponytail: hash arg forces cache invalidation when df changes
    df = get_data()
    return get_regime_series(df)


# ── Render ────────────────────────────────────────────────────────────────────
st.title("📊 Screener Intermarket")

# Load data — show spinner only on first load
with st.spinner("Cargando datos..."):
    try:
        df = get_data()
        data_ok = True
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        data_ok = False

if data_ok:
    regime_series = get_regime(hash(str(df.index[-1])))
    current_regime = regime_series.iloc[-1] if not regime_series.empty else "TRANSICION"
    imbalances = detect_imbalances(df)
    last_refresh = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    tab_hist, tab_candles, tab_now, tab_imb, tab_log = st.tabs([
        "📈 HISTÓRICO",
        "🕯️ VELAS",
        "⚡ NOW",
        f"🔍 IMBALANCES ({len(imbalances)})",
        "📋 LOG",
    ])

    with tab_hist:
        historical.render(df, regime_series)

    with tab_candles:
        candles_view.render(df)

    with tab_now:
        now.render(df, current_regime, last_refresh)

    with tab_imb:
        imbalances_view.render(df, imbalances)

    with tab_log:
        log_view.render()
