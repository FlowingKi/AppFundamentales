import streamlit as st
import pandas as pd

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from alerts.log import get_events, init_db


_EVENT_TYPES = ["regime_change", "imbalance_new", "imbalance_resolved", "threshold", "divergence", "test"]


def render():
    st.subheader("Log de eventos")
    init_db()

    col1, col2 = st.columns(2)
    with col1:
        type_filter = st.multiselect("Tipo de evento", _EVENT_TYPES, key="log_type_filter")
    with col2:
        asset_filter_raw = st.text_input("Activo (ej: HY, CURVE_2_10)", key="log_asset_filter")

    asset_filter = [a.strip() for a in asset_filter_raw.split(",") if a.strip()] if asset_filter_raw else None

    events = get_events(
        limit=100,
        type_filter=type_filter or None,
        asset_filter=asset_filter,
    )

    if not events:
        st.info("No hay eventos registrados aún.")
        return

    df = pd.DataFrame(events)
    df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.strftime("%Y-%m-%d %H:%M")
    df = df[["timestamp", "type", "asset", "description"]].rename(columns={
        "timestamp": "Timestamp",
        "type": "Tipo",
        "asset": "Activo",
        "description": "Descripción",
    })
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption(f"{len(events)} evento(s) mostrado(s)")
