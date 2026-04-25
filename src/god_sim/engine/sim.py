from __future__ import annotations

from dataclasses import asdict

import numpy as np

from ..config import WorldConfig
from ..domain.person import Person
from ..domain.resources import ResourcePool
from ..domain.soul import Soul
from ..domain.world import World


def _clamp(x: float, lo: float, hi: float) -> float:
    return lo if x < lo else hi if x > hi else x


def _make_initial_world(cfg: WorldConfig) -> World:
    rng = np.random.default_rng(cfg.seed)

    souls = {i: Soul(soul_id=i, karma=0.0) for i in range(cfg.num_souls)}
    pool = ResourcePool(
        capacity=float(cfg.resource_capacity),
        amount=float(cfg.resource_start),
        replenish_rate=float(cfg.resource_replenish_rate),
    )

    moral_bias = rng.normal(cfg.initial_moral_bias_mean, cfg.initial_moral_bias_std, size=cfg.num_souls)
    moral_bias = np.clip(moral_bias, -1.0, 1.0)
    max_ages = rng.integers(cfg.min_max_age, cfg.max_max_age + 1, size=cfg.num_souls)

    people: list[Person] = []
    for i in range(cfg.num_souls):
        people.append(
            Person(
                soul_id=i,
                age=int(rng.integers(0, 18)),
                max_age=int(max_ages[i]),
                health=float(rng.uniform(0.7, 1.0)),
                wellbeing=float(rng.uniform(0.4, 0.9)),
                moral_bias=float(moral_bias[i]),
                consumption_need=float(cfg.baseline_consumption_need),
                alive=True,
            )
        )

    return World(time=0, resource_pool=pool, people=people, souls=souls)


def _rebirth_person(cfg: WorldConfig, rng: np.random.Generator, soul: Soul) -> Person:
    # Karma nudges next-life moral bias (simple, V1).
    bias_shift = _clamp(cfg.rebirth_influence_strength * np.tanh(soul.karma / 10.0), -0.5, 0.5)
    moral_bias = float(np.clip(rng.normal(cfg.initial_moral_bias_mean + bias_shift, cfg.initial_moral_bias_std), -1.0, 1.0))

    max_age = int(rng.integers(cfg.min_max_age, cfg.max_max_age + 1))
    return Person(
        soul_id=soul.soul_id,
        age=0,
        max_age=max_age,
        health=float(rng.uniform(0.7, 1.0)),
        wellbeing=float(rng.uniform(0.4, 0.9)),
        moral_bias=moral_bias,
        consumption_need=float(cfg.baseline_consumption_need),
        alive=True,
    )


def step_world(world: World, cfg: WorldConfig, rng: np.random.Generator) -> dict[str, float]:
    world.resource_pool.replenish()

    alive_people = [p for p in world.people if p.alive]
    n_alive = len(alive_people)

    # If everyone died (shouldn’t happen with fixed souls, but keep it robust):
    if n_alive == 0:
        return {
            "time": float(world.time),
            "alive": 0.0,
            "resource": float(world.resource_pool.amount),
            "mean_karma": float(np.mean([s.karma for s in world.souls.values()])),
            "mean_wellbeing": 0.0,
            "mean_health": 0.0,
            "events": 0.0,
        }

    # “Good” people share a bit; “bad” people hoard a bit (very simple V1).
    # This indirectly affects average consumption outcomes under scarcity.
    share_pool = 0.0
    events_count = 0

    # First pass: take resources for baseline needs (plus hoarding).
    for p in alive_people:
        hoard_factor = max(0.0, -p.moral_bias) * 0.5  # bad bias → hoard
        requested = p.consumption_need * (1.0 + hoard_factor)
        taken = world.resource_pool.take(requested)

        # Surplus slightly increases wellbeing.
        surplus = max(0.0, taken - p.consumption_need)
        p.wellbeing = _clamp(p.wellbeing + cfg.wellbeing_from_surplus * surplus, 0.0, 1.0)

        # Shortfall hurts health and wellbeing.
        shortfall = max(0.0, p.consumption_need - taken)
        if shortfall > 0:
            p.health = _clamp(p.health - cfg.starvation_health_penalty * shortfall, 0.0, 1.0)
            p.wellbeing = _clamp(p.wellbeing - 0.05 * shortfall, 0.0, 1.0)

        # Good bias contributes a bit to a share pool.
        share_contrib = max(0.0, p.moral_bias) * 0.1 * taken
        share_pool += share_contrib

        # Karma update: good actions add karma, harmful/hoarding tendencies reduce.
        world.souls[p.soul_id].karma += 0.02 * p.moral_bias

        # Random life event.
        if rng.random() < cfg.event_rate:
            events_count += 1
            # Events can be good or bad; moral bias slightly changes expected impact.
            sign = 1.0 if rng.random() < (0.5 + 0.15 * p.moral_bias) else -1.0
            p.health = _clamp(p.health + sign * cfg.event_health_impact * rng.random(), 0.0, 1.0)
            p.wellbeing = _clamp(p.wellbeing + sign * cfg.event_wellbeing_impact * rng.random(), 0.0, 1.0)
            world.souls[p.soul_id].karma += 0.05 * sign * (0.5 + 0.5 * p.moral_bias)

    # Second pass: redistribute share_pool evenly (very simple V1 “social safety net”).
    if share_pool > 0 and n_alive > 0:
        per = share_pool / n_alive
        for p in alive_people:
            # Add wellbeing from shared support; keep it modest.
            p.wellbeing = _clamp(p.wellbeing + 0.01 * per, 0.0, 1.0)

    # Aging and death, then rebirth.
    for p in alive_people:
        p.age += 1
        # natural aging
        p.health = _clamp(p.health - 0.005, 0.0, 1.0)
        if p.age >= p.max_age or p.health <= 0.0:
            p.alive = False

    # Rebirth: replace dead persons with newborns for the same souls.
    # Keep population size constant.
    new_people: list[Person] = []
    for p in world.people:
        if p.alive:
            new_people.append(p)
        else:
            soul = world.souls[p.soul_id]
            if cfg.karma_decay_per_tick > 0:
                soul.karma *= (1.0 - cfg.karma_decay_per_tick)
            new_people.append(_rebirth_person(cfg, rng, soul))
    world.people = new_people

    world.time += 1

    karma = np.array([s.karma for s in world.souls.values()], dtype=float)
    wellbeing = np.array([p.wellbeing for p in world.people], dtype=float)
    health = np.array([p.health for p in world.people], dtype=float)

    return {
        "time": float(world.time),
        "alive": float(len([p for p in world.people if p.alive])),
        "resource": float(world.resource_pool.amount),
        "mean_karma": float(np.mean(karma)),
        "mean_wellbeing": float(np.mean(wellbeing)),
        "mean_health": float(np.mean(health)),
        "events": float(events_count),
        "collapsed": len(alive_people) == 0 or world.resource_pool.amount <= 0 or abs(np.mean(karma)) < 1e-6
    }


def run_simulation(cfg: WorldConfig) -> dict[str, object]:
    rng = np.random.default_rng(cfg.seed)
    world = _make_initial_world(cfg)
    series: list[dict[str, float]] = []

    for _ in range(int(cfg.ticks)):
        step_data = step_world(world, cfg, rng)
        series.append(step_data)
        if step_data.get("collapsed"):
            break

    return {
        "config": asdict(cfg),
        "series": series,
    }

