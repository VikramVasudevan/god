from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def gini(x: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    if x.size == 0:
        return 0.0
    if np.allclose(x, 0):
        return 0.0
    x = np.sort(np.clip(x, 0.0, None))
    n = x.size
    cum = np.cumsum(x)
    return float((n + 1 - 2 * np.sum(cum) / cum[-1]) / n)


@dataclass(frozen=True, slots=True)
class Summary:
    mean_karma: float
    mean_wellbeing: float
    mean_health: float
    gini_wellbeing: float
    gini_health: float

