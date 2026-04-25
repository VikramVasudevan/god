from __future__ import annotations

import argparse
import json

from .config import WorldConfig
from .engine.sim import run_simulation


def main() -> None:
    parser = argparse.ArgumentParser(prog="god-sim")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--ticks", type=int, default=200)
    parser.add_argument("--num-souls", type=int, default=300)
    args = parser.parse_args()

    cfg = WorldConfig(seed=args.seed, ticks=args.ticks, num_souls=args.num_souls)
    out = run_simulation(cfg)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

