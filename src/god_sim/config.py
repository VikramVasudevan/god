from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WorldConfig:
    seed: int = 42
    ticks: int = 200
    num_souls: int = 300

    # Resources
    resource_capacity: float = 10_000.0
    resource_start: float = 6_000.0
    resource_replenish_rate: float = 120.0

    # Needs / wellbeing / health
    baseline_consumption_need: float = 1.0
    starvation_health_penalty: float = 0.15
    wellbeing_from_surplus: float = 0.03

    # Events
    event_rate: float = 0.05
    event_health_impact: float = 0.25
    event_wellbeing_impact: float = 0.35

    # Moral bias initialization
    initial_moral_bias_mean: float = 0.0
    initial_moral_bias_std: float = 0.5

    # Rebirth / karma coupling
    rebirth_influence_strength: float = 0.25
    karma_decay_per_tick: float = 0.0

    # Lifespan
    min_max_age: int = 40
    max_max_age: int = 90

