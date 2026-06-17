#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"

# Keys that should fall back to OS environment variables in CI
_CI_ENV_KEYS = ("DEEPSEEK_API_KEY", "IMG_TANO_API_KEY")


def _parse_env_line(line: str) -> tuple[str, str] | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None
    if stripped.startswith("export "):
        stripped = stripped[7:].lstrip()
    if "=" not in stripped:
        return None
    key, value = stripped.split("=", 1)
    key = key.strip()
    value = value.strip()
    if not key:
        return None
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        value = value[1:-1]
    return key, value


def load_repo_env(path: Path | None = None) -> dict[str, str]:
    env_path = path or ENV_PATH
    loaded: dict[str, str] = {}
    if env_path.exists():
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            parsed = _parse_env_line(raw_line)
            if parsed is None:
                continue
            key, value = parsed
            loaded[key] = value
    # Fall back to OS environment variables (for CI / GitHub Actions)
    for key in _CI_ENV_KEYS:
        if key not in loaded:
            val = os.environ.get(key, "").strip()
            if val:
                loaded[key] = val
    return loaded
