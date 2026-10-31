import streamlit as st
import plotly.graph_objects as go
import pandas as pd

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from signals.correlations import rolling_percentile
from signals.context import get_signal_context, get_corr_context


_SEVERITY_COLOR = {
    "percentile_high":      "#ff9800",
    "percentile_low":       "#ff9800",
    "correlation_breakdown":"#9c27b0",
    "zscore_extreme":       "#f44336",
}

_TYPE_LABEL = {
    "percentile_high":      "📈 Extremo alto",
    "percentile_low":       "📉 Extremo bajo",
    "correlation_breakdown":"🔗 Corr rota",
    "zscore_extreme":       "⚡ Z-score",
}


def render(df: pd.DataFrame, imbalances: list[dict]):
    st.subheader("Imbalances activos")

    if not imbalances:
        st.success("Sin desbalances detectados en este momento.")
        return

    st.caption(f"{len(imbalances)} imbalance(s) activo(s)")

    for item in imbalances:
        asset  = item["asset"]
        itype  = item["type"]
        color  = _SEVERITY_COLOR.get(itype, "#888")
        badge  = _TYPE_LABEL.get(itype, itype)

        with st.expander(f"{badge} — **{asset}** — {item['description'][:80]}"):

            # ── Contexto ─────────────────────────────────────────────────────
            related = item.get("related_asset")
            ctx = (get_corr_context(asset, related) if itype == "correlation_breakdown" and related
                   else get_signal_context(asset))

            if ctx:
                with st.container():
                    st.markdown("---")
                    c_left, c_right = st.columns([1, 1])
                    with c_left:
                        st.markdown(f"**¿Qué es?** {ctx.get('que_es', '')}")
                        if "tesis" in ctx:
                            st.markdown(f"**Tesis:** {ctx['tesis']}")
                    with c_right:
                        if "direccion" in ctx:
                            st.info(f"**Dirección:** {ctx['direccion']}")
                        if "implicancia" in ctx:
                            st.info(f"**Implicancia:** {ctx['implicancia']}")
                        if "que_vigilar" in ctx:
                            st.warning(f"**Qué vigilar:** {ctx['que_vigilar']}")
                    st.markdown("---")

            # ── Main series chart with percentile bands ───────────────────────
            if asset in df.columns:
                series = df[asset].dropna().iloc[-252:]
                p10 = series.quantile(0.10)
                p90 = series.quantile(0.90)

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=list(series.index) + list(series.index[::-1]),
                    y=[p90]*len(series) + [p10]*len(series),
                    fill="toself",
                    fillcolor=f"rgba(255,152,0,0.15)",
                    line=dict(color="rgba(0,0,0,0)"),
                    name="Banda p10-p90",
                    hoverinfo="skip",
                ))
                fig.add_trace(go.Scatter(x=series.index, y=series.values, name=asset, line=dict(width=2)))
                # Mark current value
                fig.add_trace(go.Scatter(
                    x=[series.index[-1]],
                    y=[series.iloc[-1]],
                    mode="markers",
                    marker=dict(color=color, size=10),
                    name="Valor actual",
                ))

                # If related asset, overlay with secondary Y
                related = item.get("related_asset")
                if related and related in df.columns:
                    s2 = df[related].dropna().iloc[-252:]
                    fig.add_trace(go.Scatter(
                        x=s2.index, y=s2.values,
                        name=related, yaxis="y2",
                        line=dict(width=1.5, dash="dash", color="#90caf9"),
                    ))
                    fig.update_layout(yaxis2=dict(overlaying="y", side="right", showgrid=False))

                    # Rolling correlation
                    aligned = pd.concat([series, s2], axis=1).dropna()
                    if len(aligned) >= 60:
                        corr = aligned.iloc[:, 0].rolling(60).corr(aligned.iloc[:, 1])
                        c1, c2 = st.columns(2)
                        with c1:
                            st.metric("Correlación rolling 60d", f"{corr.iloc[-1]:.2f}")
                        with c2:
                            exp = item.get("expected_corr")
                            if exp:
                                st.metric("Correlación esperada", f"{exp:.2f}")

                fig.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0), hovermode="x unified")
                st.plotly_chart(fig, use_container_width=True)

            # Detail row
            dc1, dc2, dc3 = st.columns(3)
            with dc1:
                st.markdown(f"**Tipo:** `{itype}`")
            with dc2:
                if item.get("percentile") is not None:
                    st.markdown(f"**Percentil:** `{item['percentile']:.0f}%`")
                if item.get("zscore") is not None:
                    st.markdown(f"**Z-score:** `{item['zscore']:.2f}`")
            with dc3:
                st.markdown(f"**Valor:** `{item['current_value']:.2f}`")
