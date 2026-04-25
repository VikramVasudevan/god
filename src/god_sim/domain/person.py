from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Person:
    soul_id: int
    age: int
    max_age: int

    health: float
    wellbeing: float

    moral_bias: float
    consumption_need: float

    alive: bool = True

