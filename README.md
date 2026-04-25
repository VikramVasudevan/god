## GOD — a reincarnation-based social simulation

This is a Python project to simulate a “world engine” where a **fixed pool of souls** cycles through **birth → life → death → rebirth**, accumulating **karma** and experiencing **scarce shared resources**, **social identity**, and **events**.

The goal is not to “simulate everything”, but to build a configurable sandbox where we can run repeatable experiments and visualize emergent outcomes over many generations.

### What this application is trying to answer
- **Bias experiments**: What happens to world stability when the population is biased toward “good nature” vs “bad nature”?
- **Scarcity vs abundance**: How do shared natural resources shape inequality, wellbeing, cooperation/conflict, and longevity?
- **Identity dynamics**: How do race/faith/beauty norms influence social networks and opportunity, and how do they compound over rebirth cycles?
- **Randomness vs “engineering”**: Are outcomes explainable from explicit rules and parameters, or do they appear chaotic until you measure them?
- **Philosophical lenses**: If we encode different schools of thought (e.g., Advaita, Vishishtadvaita, Buddhist frameworks) as rule sets, how do they change emergent behavior and “liberation” outcomes?

### High-level model (simple, measurable, extensible)
To keep the simulation testable, each philosophical concept is mapped to something measurable.

- **Soul**: immutable id; persists across lifetimes; carries karma forward.
- **Person (a body/life)**: a soul embodied for one lifetime with traits, identity markers, wellbeing, and relationships.
- **Karma**: a numeric score (or vector later) updated by actions and outcomes; influences rebirth initialization.
- **Nature (good/bad bias)**: a trait like `moral_bias ∈ [-1, 1]` affecting decisions (cooperate, hoard, harm, help).
- **Resources**: global pool with replenishment; agents compete/coordinate to consume/produce.
- **Society**: group labels (race/faith) and norms (beauty) influencing trust, mate choice, cooperation, and conflict.
- **Events**: stochastic shocks (disease, drought, opportunity, tragedy) parameterized and observable in logs.
- **Philosophical school / worldview**: a configurable “lens” that changes how agents interpret self/other, attachment, ethics, and the karma→rebirth→liberation mechanics (implemented as a pluggable ruleset, not hard-coded into the engine).

### Bringing in philosophical schools of thought (planned)
At some point this simulation should support multiple **worldviews** as first-class configuration, such as:
- **Advaita (Adhvaitha)**: non-dual framing; emphasis on ignorance/knowledge; reduced self/other separation.
- **Vishishtadvaita (Vishistadvaitha)**: qualified non-dual framing; enduring individuality in relation to the whole.
- **Buddhist lenses**: no fixed self, dependent origination; attachment/craving as drivers of suffering; liberation as reduction of craving/ignorance.

Implementation-wise, these won’t be treated as “religion labels” like `faith`. Instead, they act as **simulation rule modules** that can change:
- **Decision policy**: cooperation vs hoarding vs harm vs help; attachment, compassion, renunciation as parameters.
- **Suffering/wellbeing model**: how craving/aversion affects wellbeing beyond material resources.
- **Karma semantics**: how actions update karma and which actions matter.
- **Rebirth mapping**: how karma affects next-life traits and circumstances.
- **Liberation / exit conditions** (optional): when a soul stops rebirthing (e.g., thresholds, convergent criteria, or explicit “moksha/nirvana” state in the model).

The key constraint: we’ll keep the **core engine neutral** and make worldviews pluggable so we can run the same initial world under different lenses and compare outcomes.

### Why a phases approach
This idea contains many interacting systems. If we build UI/visuals first, we’ll optimize for looks before we know the world model creates interesting behavior.

So we build **engine-first**, prove the simulation produces meaningful metrics and repeatable experiments, then layer visualization and richer social dynamics.

## Phased roadmap
Each phase should end with something runnable and measurable.

### Phase 0 — Foundations (scaffolding + repeatability)
- Basic repo structure and packaging
- Single config object (or YAML/JSON) that fully defines a run
- Deterministic seeding for reproducible scenarios
- Logging/tracing of key events

### Phase 1 — Core life-cycle engine (V1 target)
- A world with a **fixed soul pool**
- Birth/life/death loop with a tick-based simulation (e.g., one tick = one year)
- Shared resource pool with scarcity/abundance knobs
- Karma accumulation and rebirth mapping
- Metrics + simple charts

### Phase 2 — Social interactions
- Friendship/partnering rules
- Cooperation/conflict mechanics
- Network effects (who influences whom)
- New metrics: cohesion, inequality, conflict rate, cluster formation

### Phase 3 — Identity + norms
- Race/faith labels and trust matrices
- “Beauty” norms as socially defined advantage/disadvantage
- Bias and discrimination parameters

### Phase 4 — Rich events + scenario comparison UX
- Expanded event catalogue and world shocks
- Side-by-side scenario runner (good-biased vs bad-biased, scarcity vs abundance)
- Saved runs, replay, and comparative dashboards

### Phase 5 — Philosophical schools as pluggable worldviews
- Define a `Worldview` interface (policy + karma + rebirth + liberation hooks)
- Implement first set of worldview modules (Advaita, Vishishtadvaita, Buddhist lens)
- Add scenario comparison: same seed/config, different worldview → compare metrics and liberation rates
- Add new metrics relevant to worldviews (e.g., attachment/craving proxy, compassion proxy, “liberation” events)

## V1 technical plan (build the minimum interesting world)
V1 is the smallest version that can answer: **does “good vs bad bias” + “scarcity vs abundance” meaningfully change world-level outcomes over generations?**

### Deliverable (what “done” looks like for V1)
- A single command starts an interactive app where you can:
  - set parameters (seed, population size, resource abundance, bias toward good/bad nature)
  - run for `N` ticks / generations
  - view metrics and charts
- Runs are reproducible via seed + config snapshot.

### Running (Windows / PowerShell)
From `c:\Workspace\agentic-ai\projects\god`:

- Run the CLI (prints JSON):

```bash
uv sync
uv run god-sim --ticks 200 --num-souls 300
```

- Run the UI (Streamlit):

```bash
uv sync
uv run streamlit run .\src\god_sim\app\streamlit_app.py
```

### Local LLM insights (Gemma via Ollama)
The UI can optionally ask a **local** model to summarize and interpret a run (no cloud required).

1) Install and start Ollama, then pull a small Gemma model (example):

```bash
ollama pull gemma2:2b
ollama serve
```

2) Run the app and click **Generate insights from last run**.

3) Optional environment variables:
- `GOD_LLM_PROVIDER`: `ollama` (default) or `openai_compatible`
- `OLLAMA_BASE_URL`: default `http://localhost:11434`
- `OLLAMA_MODEL`: default `gemma2:2b`
- `OPENAI_BASE_URL`: default `http://localhost:1234/v1` (for local OpenAI-compatible servers)
- `OPENAI_MODEL`: default `gemma`
- `OPENAI_API_KEY`: only if your local server requires it

### Fully offline LLM insights (no server) using your HF `.bin`
Your Hugging Face repo contains a local file `gemma-2b-it-cpu-int4.bin` (uploaded here: [`vikramvasudevan/gemma-for-panchangam`](https://huggingface.co/vikramvasudevan/gemma-for-panchangam)).

This project supports loading that file **directly in-process** using `llama-cpp-python` (no Ollama, no server).

1) Download the model file into `.\models\`:

```bash
uv sync
uv run god-sim-download-model --repo vikramvasudevan/gemma-for-panchangam --file gemma-2b-it-cpu-int4.bin --out models
```

2) Run the UI and choose provider `llama_cpp` in the Insights section, or set env vars:
- `GOD_LLM_PROVIDER=llama_cpp`
- `GOD_LLM_MODEL_PATH=models/gemma-2b-it-cpu-int4.bin`
- (optional) `GOD_LLM_N_CTX=4096`, `GOD_LLM_N_THREADS=0`

### Recommended stack
- **Python**: `dataclasses` + type hints
- **Numerics**: `numpy` (optionally `pandas` if it helps)
- **Visualization/UI**: **Streamlit** (fastest to iterate on “play God” sliders + charts)
- **Plots**: `plotly` (or `matplotlib`)

### Suggested code organization
```
god/
  README.md
  pyproject.toml
  main.py                    # CLI or entrypoint (later can launch Streamlit)
  src/god_sim/
    __init__.py
    config.py                # WorldConfig, scenario presets
    domain/
      soul.py                 # Soul (id, karma)
      person.py               # Person (traits, identity, wellbeing, relationships)
      world.py                # World state (population, resources, time)
      resources.py            # ResourcePool (replenish, consume)
      events.py               # Event types and effects
    engine/
      sim.py                  # run_simulation(), step_world()
      rebirth.py              # Rebirth rules (karma → next-life initialization)
      karma.py                # Karma updates from actions/outcomes
    rules/
      decisions.py            # cooperate/hoard/help/harm policy driven by moral_bias
      social.py               # (minimal in V1) optional basic interaction
    analytics/
      metrics.py              # collectors + aggregations
      report.py               # plot helpers
    app/
      streamlit_app.py        # sliders → run → charts
```

### Core data model (V1)
Start numeric and simple; keep everything observable.

- `Soul`
  - `soul_id: int`
  - `karma: float`

- `Person`
  - `soul_id: int`
  - `age: int`
  - `max_age: int` (sampled)
  - `health: float`
  - `wellbeing: float`
  - `moral_bias: float` (good↔bad)
  - `consumption_need: float`
  - (optional in V1) `race`, `faith`, `beauty_score` (can exist but not heavily used yet)

- `World`
  - `time: int`
  - `resource_pool: ResourcePool`
  - `people: list[Person]`
  - `souls: dict[int, Soul]`

### Simulation loop (tick-based)
For each tick:
- Replenish global resources
- For each person:
  - consume resources (if insufficient, wellbeing/health drop)
  - decide actions influenced by `moral_bias` (e.g., share vs hoard)
  - sample an event (configurable probabilities)
  - update wellbeing/health/karma
- Age everyone, apply deaths
- For each death:
  - update soul karma summary if needed
  - rebirth: create a new `Person` for the same `Soul`, with traits drawn from distributions shifted by karma
- Collect metrics for this tick

### Metrics to track in V1 (minimum set)
- Population alive over time (should remain stable-ish given constant soul pool, but death/birth timing matters)
- Mean/median karma and distribution (histogram)
- Mean/median wellbeing and distribution
- Resource pool level over time
- Inequality proxy (simple: Gini of wellbeing or resources consumed; can be added later)
- Event counts by type

### Scenario knobs (V1 controls)
- `seed`
- `num_souls`
- `ticks`
- `resource_replenish_rate`
- `resource_capacity`
- `baseline_consumption_need`
- `event_rate` and event mix
- `initial_moral_bias_mean` and `initial_moral_bias_std`
- `rebirth_influence_strength` (how strongly karma affects next-life traits)

### Testing/validation (pragmatic)
- Same config + seed produces the same metrics time series
- Extreme scenarios behave sensibly:
  - very low replenish rate → widespread suffering / collapse-like signals
  - high replenish rate + good bias → higher wellbeing and lower conflict proxies (even if conflict is minimal in V1)

---

### Notes
- The original project statement is preserved as `README.backup.md` in this folder.
