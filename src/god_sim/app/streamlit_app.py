from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from god_sim.config import WorldConfig
from god_sim.analytics.history import append_run_history, load_run_history
from god_sim.engine.sim import run_simulation
from god_sim.insights.llm import check_ollama_health, generate_insights, insight_config_from_env


st.set_page_config(page_title="GOD Simulator", layout="wide")

st.title("GOD — Simulation Sandbox (V1)")
st.caption("Tune parameters, run the world, inspect emergent metrics.")


def info_box(title: str, body: str) -> None:
    with st.expander(f"ℹ️ {title}", expanded=False):
        st.write(body)

with st.sidebar:
    st.header("Scenario")
    seed = st.number_input("Seed", min_value=0, max_value=1_000_000_000, value=42, step=1)
    ticks = st.slider(
        "Ticks (simulation duration)",
        min_value=10,
        max_value=2000,
        value=200,
        step=10,
        help="How long to run the simulation (number of time steps/turns). More ticks = longer world evolution.",
    )
    num_souls = st.slider(
        "Number of souls (population size)",
        min_value=50,
        max_value=5000,
        value=300,
        step=50,
        help="How many souls/entities exist in the world. More souls = higher population and resource pressure per tick.",
    )
    st.caption("Ticks = for how long. Number of souls = for how many entities.")

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

    st.session_state["last_run_out"] = out
    saved = append_run_history(out)
    st.success(f"Saved run to history as `{saved['run_id']}`.")
    df = pd.DataFrame(out["series"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Final mean karma", f"{df['mean_karma'].iloc[-1]:.3f}")
    c2.metric("Final mean wellbeing", f"{df['mean_wellbeing'].iloc[-1]:.3f}")
    c3.metric("Final mean health", f"{df['mean_health'].iloc[-1]:.3f}")
    c4.metric("Final resources", f"{df['resource'].iloc[-1]:.1f}")
    info_box(
        "What these top metrics mean",
        (
            "- Final mean karma: average karma score at the end of the run.\n"
            "- Final mean wellbeing: average quality-of-life proxy (0 to 1).\n"
            "- Final mean health: average physical health proxy (0 to 1).\n"
            "- Final resources: units left in the global shared resource pool."
        ),
    )

    st.subheader("Time series")
    left, right = st.columns(2)
    with left:
        st.plotly_chart(px.line(df, x="time", y=["mean_wellbeing", "mean_health"], title="Wellbeing & Health"), use_container_width=True)
        info_box(
            "Wellbeing & Health graph",
            (
                "Tracks average wellbeing and health over time. Rising lines usually indicate favorable "
                "resource/event conditions; falling lines suggest sustained stress, scarcity, or frequent negative events."
            ),
        )
        st.plotly_chart(px.line(df, x="time", y=["mean_karma"], title="Mean karma"), use_container_width=True)
        info_box(
            "Mean karma graph",
            (
                "Shows average accumulated karma across souls. Upward trend means, on balance, actions/events are "
                "adding positive karma; flat/declining means neutral or negative net behavior."
            ),
        )
    with right:
        st.plotly_chart(px.line(df, x="time", y=["resource"], title="Resources"), use_container_width=True)
        info_box(
            "Resources graph",
            (
                "Shows the level of the shared global resource pool. Persistent decline indicates structural scarcity; "
                "stable or rising values indicate replenishment is keeping up with demand."
            ),
        )
        st.plotly_chart(px.bar(df, x="time", y="events", title="Events per tick"), use_container_width=True)
        info_box(
            "Events per tick graph",
            (
                "Counts random events that occurred each tick. Spikes represent volatile periods that can drive abrupt "
                "changes in health, wellbeing, and karma."
            ),
        )

    with st.expander("Raw output"):
        st.json(out["config"])
        st.dataframe(df, use_container_width=True)

st.divider()
st.subheader("Run History")
history = load_run_history()
if history:
    st.caption(f"Stored runs: {len(history)} (saved in `data/run_history.json`).")
    rows: list[dict[str, object]] = []
    for r in reversed(history[-20:]):
        final = r.get("final", {}) if isinstance(r.get("final"), dict) else {}
        cfg_hist = r.get("config", {}) if isinstance(r.get("config"), dict) else {}
        rows.append(
            {
                "run_id": r.get("run_id", ""),
                "created_at_utc": r.get("created_at_utc", ""),
                "ticks": cfg_hist.get("ticks", ""),
                "num_souls": cfg_hist.get("num_souls", ""),
                "resource_replenish_rate": cfg_hist.get("resource_replenish_rate", ""),
                "event_rate": cfg_hist.get("event_rate", ""),
                "final_mean_karma": final.get("mean_karma", ""),
                "final_mean_wellbeing": final.get("mean_wellbeing", ""),
                "final_mean_health": final.get("mean_health", ""),
                "final_resource": final.get("resource", ""),
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True)
else:
    st.caption("No runs stored yet. Run a simulation to create history.")

st.divider()
st.subheader("Insights (local Gemma)")
st.caption("Uses a local model. Choose Ollama (server) or llama.cpp (fully offline). Configure via env vars in README.")
st.info("For provider `llama_cpp`, use a local `.gguf` model file path. `.bin` files are not supported by llama.cpp.")

insight_cols = st.columns([1, 1, 2])
with insight_cols[0]:
    provider = st.selectbox("Provider", options=["ollama", "llama_cpp", "openai_compatible"], index=0)
with insight_cols[1]:
    model = st.text_input(
        "Model",
        value="gemma2:2b" if provider == "ollama" else ("models/gemma-2b-it-cpu-int4.bin" if provider == "llama_cpp" else "gemma"),
        help="For llama.cpp, set this to a local model file path.",
    )

if provider == "ollama":
    hc_cols = st.columns([1, 4])
    with hc_cols[0]:
        run_health_check = st.button("Check Ollama health")
    with hc_cols[1]:
        st.caption("Checks server reachability and whether the selected model exists locally.")

    if run_health_check:
        cfg0 = insight_config_from_env()
        health = check_ollama_health(base_url=cfg0.ollama_base_url, model=model)
        if not health["reachable"]:
            st.error(
                "Ollama server is not reachable. Start it first (example: `ollama serve`) "
                f"and ensure base URL is `{cfg0.ollama_base_url}`.\n\nDetails: {health['error']}"
            )
        elif not health["model_present"]:
            st.warning(
                f"Ollama is running, but model `{model}` is not available locally. "
                f"Run `ollama pull {model}` first."
            )
            if health["models"]:
                st.caption("Available local models: " + ", ".join(health["models"]))
        else:
            st.success(f"Ollama is healthy and model `{model}` is available.")

gen = st.button("Generate insights from last run")

if gen:
    out = st.session_state.get("last_run_out")
    if not out:
        st.warning("Run a simulation first.")
    else:
        cfg = insight_config_from_env()
        # Override UI-selected provider/model
        if provider == "ollama":
            cfg = type(cfg)(
                provider="ollama",
                ollama_base_url=cfg.ollama_base_url,
                ollama_model=model,
                openai_base_url=cfg.openai_base_url,
                openai_model=cfg.openai_model,
                openai_api_key=cfg.openai_api_key,
                model_path=cfg.model_path,
                n_ctx=cfg.n_ctx,
                n_threads=cfg.n_threads,
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
            )
        elif provider == "llama_cpp":
            cfg = type(cfg)(
                provider="llama_cpp",
                ollama_base_url=cfg.ollama_base_url,
                ollama_model=cfg.ollama_model,
                openai_base_url=cfg.openai_base_url,
                openai_model=cfg.openai_model,
                openai_api_key=cfg.openai_api_key,
                model_path=model,
                n_ctx=cfg.n_ctx,
                n_threads=cfg.n_threads,
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
            )
        else:
            cfg = type(cfg)(
                provider="openai_compatible",
                ollama_base_url=cfg.ollama_base_url,
                ollama_model=cfg.ollama_model,
                openai_base_url=cfg.openai_base_url,
                openai_model=model,
                openai_api_key=cfg.openai_api_key,
                model_path=cfg.model_path,
                n_ctx=cfg.n_ctx,
                n_threads=cfg.n_threads,
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
            )

        try:
            with st.spinner("Calling local model..."):
                text = generate_insights(out, cfg=cfg)
            st.markdown(text if text else "_(empty response)_")
        except Exception as e:
            st.error(f"Insight generation failed: {e}")
