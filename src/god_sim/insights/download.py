from __future__ import annotations

import argparse
from pathlib import Path

from huggingface_hub import hf_hub_download


DEFAULT_REPO = "vikramvasudevan/gemma-for-panchangam"
DEFAULT_FILENAME = "gemma-2b-it-cpu-int4.bin"


def download_model(repo_id: str, filename: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = hf_hub_download(repo_id=repo_id, filename=filename, local_dir=str(out_dir))
    return Path(path)


def main() -> None:
    p = argparse.ArgumentParser(prog="god-sim-download-model")
    p.add_argument("--repo", default=DEFAULT_REPO)
    p.add_argument("--file", default=DEFAULT_FILENAME)
    p.add_argument("--out", default="models")
    args = p.parse_args()

    dest = download_model(args.repo, args.file, Path(args.out))
    print(str(dest))


if __name__ == "__main__":
    main()

