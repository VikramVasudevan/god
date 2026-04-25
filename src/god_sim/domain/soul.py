from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Soul:
    soul_id: int
    karma: float = 0.0

