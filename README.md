---
title: GOD Simulation
emoji: 🕉️
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
license: mit
---

## GOD — a reincarnation-based social simulation

This is a Python project to simulate a “world engine” where a **fixed pool of souls** cycles through **birth → life → death → rebirth**, accumulating **karma** and experiencing **scarce shared resources**, **social identity**, and **events**.

The goal is not to “simulate everything”, but to build a configurable sandbox where we can run repeatable experiments and visualize emergent outcomes over many generations.

### What this application is trying to answer
- **Bias experiments**: What happens to world stability when the population is biased toward “good nature” vs “bad nature”?
- **Scarcity vs abundance**: How do shared natural resources shape inequality, wellbeing, cooperation/conflict, and longevity?
- **Identity dynamics**: How do race/faith/beauty norms influence social networks and opportunity, and how do they compound over rebirth cycles?
- **Sustainability Equilibrium**: What is the ideal balance of population, resources, and moral bias to ensure world longevity?

### Core Features
- **Deterministic Simulation**: Tick-based engine where every run is reproducible via seed.
- **Sustainable Equilibrium Optimizer**: An auto-tuning tool that hunts for parameters that maximize world longevity (surviving collapse).
- **Run History & AI Comparison**: Automatically saves all runs and allows AI to generate comparative insights between two different worlds.
- **Local AI Insights**: Uses Gemma 2 2b (via `llama_cpp` or `Ollama`) to quantitatively interpret simulation results and causal links.

### High-level model
- **Soul**: immutable id; persists across lifetimes; carries karma forward.
- **Person**: a transient body with traits (moral bias, health, wellbeing).
- **Karma**: numeric score updated by actions; influences next-life initialization.
- **Resources**: global pool with replenishment; consumption influenced by moral bias (sharing vs hoarding).
- **World Collapse**: Simulation ends if resources hit 0, everyone dies, or karma reaches 0.

### Running the App
The app is optimized for Hugging Face Spaces using Docker, but can be run locally:

```bash
# Run the UI (Streamlit)
uv run streamlit run src/god_sim/app/streamlit_app.py
```

### Local LLM insights
1) Install Ollama and pull Gemma: `ollama pull gemma2:2b`
2) Run the app and click **Generate insights**.

### Hugging Face Deployment
The app uses `llama_cpp` with GGUF for fast, serverless insights:
- **Provider**: `llama_cpp`
- **Model Repo**: `bartowski/gemma-2-2b-it-GGUF`
- **Model File**: `gemma-2-2b-it-Q4_K_M.gguf`
- **Context Window**: 8192 tokens.
