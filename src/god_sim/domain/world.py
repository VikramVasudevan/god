from __future__ import annotations

from dataclasses import dataclass

from .person import Person
from .resources import ResourcePool
from .soul import Soul


@dataclass(slots=True)
class World:
    time: int
    resource_pool: ResourcePool
    people: list[Person]
    souls: dict[int, Soul]

