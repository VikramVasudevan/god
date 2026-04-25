from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4
import numpy as np

class SimulationEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
            return int(obj)
        if isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
            return float(obj)
        if isinstance(obj, (np.ndarray, np.generic)):
            if isinstance(obj, np.bool_):
                return bool(obj)
            if hasattr(obj, "tolist"):
                return obj.tolist()
            return str(obj)
        if isinstance(obj, (datetime, Path)):
            return str(obj)
        try:
            return super().default(obj)
        except TypeError:
            try:
                return str(obj)
            except Exception:
                raise

DEFAULT_HISTORY_PATH = Path("data/run_history.json")


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _safe_load_json_array(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    return [x for x in data if isinstance(x, dict)]


def build_run_record(sim_output: dict[str, Any]) -> dict[str, Any]:
    series = sim_output.get("series", [])
    config = sim_output.get("config", {})
    final = series[-1] if series else {}
    return {
        "run_id": str(uuid4()),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": config,
        "final": final,
        "ticks_recorded": len(series),
        "series": series,
    }


def append_run_history(sim_output: dict[str, Any], path: Path = DEFAULT_HISTORY_PATH) -> dict[str, Any]:
    _ensure_parent(path)
    runs = _safe_load_json_array(path)
    record = build_run_record(sim_output)
    runs.append(record)
    path.write_text(json.dumps(runs, indent=2, cls=SimulationEncoder), encoding="utf-8")
    return record


def load_run_history(path: Path = DEFAULT_HISTORY_PATH) -> list[dict[str, Any]]:
    return _safe_load_json_array(path)

