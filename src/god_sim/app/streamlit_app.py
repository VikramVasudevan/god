from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from god_sim.config import WorldConfig
from god_sim.engine.sim import run_simulation


st.set_page_config(page_title="GOD Simulator", layout="wide")

st.title("GOD — Simulation Sandbox (V1)")
st.caption("Tune parameters, run the world, inspect emergent metrics.")

with st.sidebar:
    st.header("Scenario")
    seed = st.number_input("Seed", min_value=0, max_value=1_000_000_000, value=42, step=1)
    ticks = st.slider("Ticks", min_value=10, max_value=2000, value=200, step=10)
    num_souls = st.slider("Number of souls", min_value=50, max_value=5000, value=300, step=50)

    st.header("Resources")
    resource_capacity = st.number_input("Resource capacity", min_value=100.0, value=10_000.0, step=100.0)
    resource_start = st.number_input("Resource start", min_value=0.0, value=6_000.0, step=100.0)
    resource_replenish_rate = st.number_input("Replenish / tick", min_value=0.0, value=120.0, step=10.0)

    st.header("Nature / bias")
    initial_moral_bias_mean = st.slider("Mean moral bias (good ↔ bad)", min_value=-1.0, max_value=1.0, value=0.0, step=0.05)
    initial_moral_bias_std = st.slider("Moral bias std", min_value=0.0, max_value=1.0, value=0.5, step=0.05)
    rebirth_influence_strength = st.slider("Karma → rebirth influence", min_value=0.0, max_value=1.0, value=0.25, step=0.05)

    st.header("Events")
    event_rate = st.slider("Event rate", min_value=0.0, max_value=0.5, value=0.05, step=0.01)

    run = st.button("Run simulation", type="primary")

if run:
    cfg = WorldConfig(
        seed=int(seed),
        ticks=int(ticks),
        num_souls=int(num_souls),
        resource_capacity=float(resource_capacity),
        resource_start=float(resource_start),
        resource_replenish_rate=float(resource_replenish_rate),
        initial_moral_bias_mean=float(initial_moral_bias_mean),
        initial_moral_bias_std=float(initial_moral_bias_std),
        rebirth_influence_strength=float(rebirth_influence_strength),
        event_rate=float(event_rate),
    )

    with st.spinner("Running..."):
        out = run_simulation(cfg)

    df = pd.DataFrame(out["series"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Final mean karma", f"{df['mean_karma'].iloc[-1]:.3f}")
    c2.metric("Final mean wellbeing", f"{df['mean_wellbeing'].iloc[-1]:.3f}")
    c3.metric("Final mean health", f"{df['mean_health'].iloc[-1]:.3f}")
    c4.metric("Final resources", f"{df['resource'].iloc[-1]:.1f}")

    st.subheader("Time series")
    left, right = st.columns(2)
    with left:
        st.plotly_chart(px.line(df, x="time", y=["mean_wellbeing", "mean_health"], title="Wellbeing & Health"), use_container_width=True)
        st.plotly_chart(px.line(df, x="time", y=["mean_karma"], title="Mean karma"), use_container_width=True)
    with right:
        st.plotly_chart(px.line(df, x="time", y=["resource"], title="Resources"), use_container_width=True)
        st.plotly_chart(px.bar(df, x="time", y="events", title="Events per tick"), use_container_width=True)

    with st.expander("Raw output"):
        st.json(out["config"])
        st.dataframe(df, use_container_width=True)

