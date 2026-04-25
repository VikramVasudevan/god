from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ResourcePool:
    capacity: float
    amount: float
    replenish_rate: float

    def replenish(self) -> None:
        self.amount = min(self.capacity, self.amount + self.replenish_rate)

    def take(self, requested: float) -> float:
        taken = min(self.amount, max(0.0, requested))
        self.amount -= taken
        return taken

