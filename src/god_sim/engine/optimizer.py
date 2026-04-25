from __future__ import annotations
from typing import Any
import numpy as np
from ..config import WorldConfig
from .sim import run_simulation

def evaluate_fitness(out: dict[str, Any]) -> float:
    series = out.get("series", [])
    ticks_survived = len(series)
    
    if ticks_survived == 0:
        return 0.0

    last_tick = series[-1]
    
    # Check for collapse conditions
    has_resources = last_tick["resource"] > 0.1
    has_people = last_tick["alive"] > 0
    has_karma = abs(last_tick["mean_karma"]) > 0.001
    
    # If the world collapsed, fitness is just the ticks survived
    if not (has_resources and has_people and has_karma):
        return float(ticks_survived)
    
    # If it survived to the end, it's a high fitness
    return float(ticks_survived * 10)

def run_optimization_step(fixed_resource_capacity: float, iterations: int = 10) -> dict[str, Any]:
    best_fitness = -1.0
    best_cfg = None
    results = []

    rng = np.random.default_rng()

    for _ in range(iterations):
        # Generate random parameters to test
        test_cfg = WorldConfig(
            seed=int(rng.integers(0, 100000)),
            ticks=1000, # Max goal
            num_souls=int(rng.integers(50, 500)),
            resource_capacity=fixed_resource_capacity,
            resource_start=fixed_resource_capacity * 0.8,
            resource_replenish_rate=float(rng.uniform(10, 200)),
            initial_moral_bias_mean=float(rng.uniform(-0.5, 0.8)),
            initial_moral_bias_std=float(rng.uniform(0.1, 0.6)),
            rebirth_influence_strength=float(rng.uniform(0.1, 0.9)),
            event_rate=float(rng.uniform(0.01, 0.15))
        )

        out = run_simulation(test_cfg)
        fitness = evaluate_fitness(out)
        
        result = {
            "config": test_cfg,
            "fitness": fitness,
            "ticks": len(out["series"])
        }
        results.append(result)

        if fitness > best_fitness:
            best_fitness = fitness
            best_cfg = test_cfg

    return {
        "best_config": best_cfg,
        "best_fitness": best_fitness,
        "all_trials": results
    }
