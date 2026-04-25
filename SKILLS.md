# GOD Simulation Skills & Knowledge

This document serves as a guide for working on the GOD reincarnation-based social simulation. It outlines the core mental models, technical patterns, and workflows used in this project.

## 核心理念 (Core Philosophy)
The project is a "world engine" simulating a fixed pool of souls cycling through birth, life, death, and rebirth.
- **Fixed Soul Pool:** Souls are persistent; only their physical manifestations (Persons) cycle.
- **Karma-Driven Rebirth:** Actions in one life influence the starting conditions of the next.
- **Resource Scarcity:** A central driver for behavior (cooperation vs. hoarding).
- **Extensible Worldviews:** (Planned) Pluggable rulesets for different philosophical lenses (Advaita, Buddhist, etc.).

## Domain Models (`src/god_sim/domain/`)
- **`Soul`**: Immutable ID + persistent `karma`. Carries history across lifetimes.
- **`Person`**: The transient physical entity. Has `age`, `health`, `wellbeing`, `moral_bias`, and `consumption_need`.
- **`World`**: Container for the `ResourcePool`, `Person` list, and `Soul` dictionary.
- **`ResourcePool`**: Manages finite resources with a replenishment rate.

## Simulation Engine (`src/god_sim/engine/sim.py`)
- **Tick-Based:** The simulation progresses in discrete time steps (ticks).
- **Step Logic:**
    1. **Replenish Resources:** Global pool grows by `replenish_rate`.
    2. **Consumption & Interaction:**
        - High `moral_bias` (good) -> Sharing part of resources.
        - Low `moral_bias` (bad) -> Hoarding (requesting more than need).
        - Shortfalls hurt health/wellbeing; surplus helps.
    3. **Karma Updates:** Updated based on `moral_bias` and life events.
    4. **Events:** Stochastic shocks (positive/negative) impacting health/wellbeing.
    5. **Aging & Death:** Health drops with age; death triggers rebirth.
    6. **Rebirth:** A new `Person` is created for the `Soul`. Karma influences the new `moral_bias`.

## Analytics & Metrics (`src/god_sim/analytics/`)
- Every tick produces a metric snapshot: `alive`, `resource`, `mean_karma`, `mean_wellbeing`, `mean_health`, `events`.
- **Persistence:** Runs are saved to `data/run_history.json` for comparison.

## AI Insights (`src/god_sim/insights/`)
The system uses LLMs to interpret simulation results.
- **Providers:** Supports `ollama` (local dev), `openai_compatible`, and `llama_cpp` (recommended for Hugging Face).
- **Format Note:** `llama_cpp` requires **GGUF** files. Old `.bin` files will not work.
- **Recommended for HF Spaces:**
    - `GOD_LLM_PROVIDER`: `llama_cpp`
    - `GOD_LLM_HF_REPO`: `bartowski/gemma-2-2b-it-GGUF`
    - `GOD_LLM_HF_FILE`: `gemma-2-2b-it-Q4_K_M.gguf`
- **Workflow:**
    1. `build_run_summary` extracts deltas and trends from the simulation output.
    2. LLM analyzes JSON summary to provide bulleted insights and suggested experiments.

## Development Workflows

### Running the CLI
```bash
uv run god-sim --ticks 200 --num-souls 300
```

### Running the Dashboard
```bash
uv run streamlit run src/god_sim/app/streamlit_app.py
```

### Key Configurations (`src/god_sim/config.py`)
Modify `WorldConfig` to tune the simulation:
- `initial_moral_bias_mean/std`: Sets the world's starting "nature".
- `resource_replenish_rate`: Controls scarcity.
- `rebirth_influence_strength`: Controls how much karma matters for the next life.

## Adding New Features
- **New Metrics:** Update `step_world` return dict and `analytics/metrics.py`.
- **New Rules:** Add logic to `step_world` or create a new module in `rules/`.
- **New Worldviews:** Implement hooks in `engine/sim.py` that change `moral_bias` interpretation or karma calculation.
