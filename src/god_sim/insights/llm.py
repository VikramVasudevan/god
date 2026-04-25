from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import requests

from .download import DEFAULT_FILENAME, DEFAULT_REPO, download_model

Provider = Literal["ollama", "openai_compatible", "llama_cpp"]


@dataclass(frozen=True, slots=True)
class InsightConfig:
    provider: Provider = "ollama"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gemma2:2b"

    # OpenAI-compatible local server (LM Studio / llama.cpp server / vLLM etc.)
    openai_base_url: str = "http://localhost:1234/v1"
    openai_model: str = "gemma"
    openai_api_key: str | None = None

    # llama.cpp (fully local, no server)
    model_path: str = "models/gemma-2b-it-cpu-int4.bin"
    auto_download_model: bool = True
    hf_repo_id: str = DEFAULT_REPO
    hf_filename: str = DEFAULT_FILENAME
    n_ctx: int = 4096
    n_threads: int = 0  # 0 = let llama.cpp decide

    # Generation defaults
    temperature: float = 0.2
    max_tokens: int = 600


def insight_config_from_env() -> InsightConfig:
    provider = os.getenv("GOD_LLM_PROVIDER", "ollama").strip().lower()
    if provider not in ("ollama", "openai_compatible", "llama_cpp"):
        provider = "ollama"

    api_key = os.getenv("OPENAI_API_KEY")
    return InsightConfig(
        provider=provider,  # type: ignore[arg-type]
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        ollama_model=os.getenv("OLLAMA_MODEL", "gemma2:2b"),
        openai_base_url=os.getenv("OPENAI_BASE_URL", "http://localhost:1234/v1"),
        openai_model=os.getenv("OPENAI_MODEL", "gemma"),
        openai_api_key=api_key if api_key else None,
        model_path=os.getenv("GOD_LLM_MODEL_PATH", "models/gemma-2b-it-cpu-int4.bin"),
        auto_download_model=os.getenv("GOD_LLM_AUTO_DOWNLOAD", "1").strip().lower() in ("1", "true", "yes", "on"),
        hf_repo_id=os.getenv("GOD_LLM_HF_REPO", DEFAULT_REPO),
        hf_filename=os.getenv("GOD_LLM_HF_FILE", DEFAULT_FILENAME),
        n_ctx=int(os.getenv("GOD_LLM_N_CTX", "4096")),
        n_threads=int(os.getenv("GOD_LLM_N_THREADS", "0")),
        temperature=float(os.getenv("GOD_LLM_TEMPERATURE", "0.2")),
        max_tokens=int(os.getenv("GOD_LLM_MAX_TOKENS", "600")),
    )


def _system_prompt() -> str:
    return (
        "You are an analyst helping interpret a world simulation run. "
        "Be concrete and quantitative. Avoid mysticism. "
        "Provide 5-10 bullet insights, then 3 follow-up experiments to run. "
        "If something is ambiguous, state what additional metric would resolve it."
    )


def build_run_summary(sim_output: dict[str, Any], df_tail_rows: int = 25) -> dict[str, Any]:
    series = sim_output.get("series", [])
    cfg = sim_output.get("config", {})

    if not series:
        return {"config": cfg, "note": "No series data."}

    # Compute simple trend deltas over run.
    first = series[0]
    last = series[-1]

    def _get(k: str, default: float = 0.0) -> float:
        try:
            return float(last.get(k, default))
        except Exception:
            return default

    def _get_first(k: str, default: float = 0.0) -> float:
        try:
            return float(first.get(k, default))
        except Exception:
            return default

    keys = ["alive", "resource", "mean_karma", "mean_wellbeing", "mean_health", "events"]
    deltas = {k: _get(k) - _get_first(k) for k in keys}

    tail = series[-min(df_tail_rows, len(series)) :]

    return {
        "config": cfg,
        "final": {k: _get(k) for k in keys},
        "delta_from_start": deltas,
        "tail_series": tail,
        "notes": {
            "interpretation": "alive is expected ~constant due to rebirth; resource shows scarcity/abundance regime; events are per-tick counts."
        },
    }


def check_ollama_health(base_url: str, model: str, timeout_s: int = 5) -> dict[str, Any]:
    """Return reachability and model availability for an Ollama host."""
    url = base_url.rstrip("/") + "/api/tags"
    try:
        r = requests.get(url, timeout=timeout_s)
        r.raise_for_status()
        data = r.json()
        models = data.get("models", [])
        names = {m.get("name", "") for m in models if isinstance(m, dict)}
        return {
            "ok": True,
            "reachable": True,
            "model_present": model in names,
            "models": sorted([n for n in names if n]),
            "error": None,
        }
    except Exception as e:
        return {
            "ok": False,
            "reachable": False,
            "model_present": False,
            "models": [],
            "error": str(e),
        }


def generate_insights(sim_output: dict[str, Any], cfg: InsightConfig | None = None, timeout_s: int = 120) -> str:
    cfg = cfg or insight_config_from_env()
    summary = build_run_summary(sim_output)

    user_prompt = (
        "Analyze this simulation run summary.\n\n"
        f"RUN_SUMMARY_JSON:\n{json.dumps(summary, indent=2)}\n\n"
        "Return:\n"
        "1) 5-10 bullet insights tied to numbers/trends\n"
        "2) 3 concrete next experiments (parameter changes)\n"
        "3) 3 metrics to add next (if needed)\n"
    )

    if cfg.provider == "ollama":
        url = cfg.ollama_base_url.rstrip("/") + "/api/generate"
        payload = {
            "model": cfg.ollama_model,
            "prompt": user_prompt,
            "system": _system_prompt(),
            "stream": False,
            "options": {"temperature": cfg.temperature},
        }
        r = requests.post(url, json=payload, timeout=timeout_s)
        r.raise_for_status()
        data = r.json()
        return str(data.get("response", "")).strip()

    if cfg.provider == "llama_cpp":
        try:
            from llama_cpp import Llama
        except ImportError as e:
            raise RuntimeError(
                "llama-cpp-python is not installed or could not be loaded. "
                "Ensure it is in requirements.txt and properly installed in the environment."
            ) from e

        model_path = Path(cfg.model_path)
        if not model_path.exists():
            if not cfg.auto_download_model:
                raise RuntimeError(
                    f"Model path does not exist: {cfg.model_path}. "
                    "Set GOD_LLM_AUTO_DOWNLOAD=1 or download model manually."
                )
            downloaded = download_model(
                repo_id=cfg.hf_repo_id,
                filename=cfg.hf_filename,
                out_dir=model_path.parent if str(model_path.parent) not in ("", ".") else Path("models"),
            )
            model_path = downloaded

        if model_path.suffix.lower() != ".gguf":
            raise RuntimeError(
                "llama_cpp requires a GGUF model file. "
                f"Current file is '{model_path.name}'. "
                "Use a .gguf model path for provider=llama_cpp, or switch provider to 'ollama' "
                "and use an Ollama model name."
            )

        try:
            llm = Llama(
                model_path=str(model_path),
                n_ctx=cfg.n_ctx,
                n_threads=None if cfg.n_threads <= 0 else cfg.n_threads,
                verbose=False,
            )
        except Exception as e:
            raise RuntimeError(
                "Failed to load model with llama_cpp. "
                "Ensure the file is a valid GGUF model compatible with llama.cpp."
            ) from e

        prompt = f"{_system_prompt()}\n\n{user_prompt}"
        out = llm(
            prompt,
            max_tokens=cfg.max_tokens,
            temperature=cfg.temperature,
            stop=["</s>"],
        )
        return str(out["choices"][0]["text"]).strip()

    # OpenAI-compatible Chat Completions
    url = cfg.openai_base_url.rstrip("/") + "/chat/completions"
    headers = {"Content-Type": "application/json"}
    if cfg.openai_api_key:
        headers["Authorization"] = f"Bearer {cfg.openai_api_key}"
    payload = {
        "model": cfg.openai_model,
        "temperature": cfg.temperature,
        "max_tokens": cfg.max_tokens,
        "messages": [
            {"role": "system", "content": _system_prompt()},
            {"role": "user", "content": user_prompt},
        ],
    }
    r = requests.post(url, headers=headers, json=payload, timeout=timeout_s)
    r.raise_for_status()
    data = r.json()
    return str(data["choices"][0]["message"]["content"]).strip()

