# GOD Simulation Skills & Knowledge

This document serves as a guide for working on the GOD reincarnation-based social simulation.

## 核心理念 (Core Philosophy)
The project is a "world engine" simulating a fixed pool of souls cycling through birth, life, death, and rebirth.
- **Fixed Soul Pool:** Souls are persistent; only their physical manifestations (Persons) cycle.
- **Sustainability Equilibrium:** The goal is to find parameters where the world does not collapse.
- **Collapse Conditions:** Resources = 0, Population = 0, or Karma = 0.

## Simulation Engine (`src/god_sim/engine/`)

### Core Simulator (`sim.py`)
- **Step Logic:** Replenish -> Consume/Interact -> Update Karma -> Events -> Age/Death -> Rebirth.
- **Collapsed Flag:** Every tick checks if the world has met any exit conditions.

### Sustainable Equilibrium Optimizer (`optimizer.py`)
- **Evaluation**: Uses a fitness function based on "Longevity" (ticks survived).
- **Random Search**: Iterates through parameter combinations to find the highest fitness world configuration for a fixed resource capacity.

## AI Insights & Comparisons (`src/god_sim/insights/`)
The system uses LLMs (Gemma 2 2b) to interpret results.
- **Single Run (`generate_insights`)**: Quantitative analysis of deltas and trends.
- **Comparative (`generate_comparative_insights`)**: Analyzing two runs to find causal links between parameter changes and outcomes.
- **Local Deployment**: Uses `llama_cpp` with GGUF files and an 8192 context window.

## Analytics & Persistence (`src/god_sim/analytics/`)
- **JSON Serialization**: Uses a custom `SimulationEncoder` in `history.py` to handle `numpy` types and booleans.
- **Run History**: Saved to `data/run_history.json`.

## Development Workflows
- **Hugging Face**: Deployed via Docker. Environment variables `GOD_LLM_PROVIDER`, `GOD_LLM_HF_REPO`, and `GOD_LLM_HF_FILE` control the AI engine.
- **Streamlit**: Main entry point is `src/god_sim/app/streamlit_app.py`.
