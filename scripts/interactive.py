#!/usr/bin/env python3
"""Shared interactive input helpers for scripts."""
from __future__ import annotations


def ask_str(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{prompt}{suffix}: ").strip()
    return value if value else default


def ask_int(prompt: str, default: int | None = None) -> int | None:
    suffix = f" [{default}]" if default is not None else ""
    raw = input(f"{prompt}{suffix}: ").strip()
    if not raw:
        return default
    return int(raw)


def ask_float(prompt: str, default: float | None = None) -> float | None:
    suffix = f" [{default}]" if default is not None else ""
    raw = input(f"{prompt}{suffix}: ").strip()
    if not raw:
        return default
    return float(raw)


def ask_bool(prompt: str, default: bool = False) -> bool:
    hint = "Y/n" if default else "y/N"
    raw = input(f"{prompt} ({hint}): ").strip().lower()
    if not raw:
        return default
    return raw in ("y", "yes", "true", "1")


def ask_choice(prompt: str, choices: list[str], default: str | None = None) -> str:
    print(f"{prompt}")
    for i, choice in enumerate(choices, 1):
        marker = " (default)" if choice == default else ""
        print(f"  {i}. {choice}{marker}")
    suffix = f" [1-{len(choices)}]"
    raw = input(f"选择{suffix}: ").strip()
    if not raw and default is not None:
        return default
    if not raw:
        return choices[0]
    idx = int(raw) - 1
    return choices[idx]


def ask_multi_choice(prompt: str, choices: list[str], default: list[str] | None = None) -> list[str]:
    default = default or choices[:]
    print(f"{prompt} (逗号分隔，直接回车使用默认)")
    for i, choice in enumerate(choices, 1):
        marker = " *" if choice in default else ""
        print(f"  {i}. {choice}{marker}")
    raw = input(f"选择 [1-{len(choices)}]: ").strip()
    if not raw:
        return default
    indices = [int(x.strip()) - 1 for x in raw.split(",")]
    return [choices[i] for i in indices if 0 <= i < len(choices)]


def ask_paths(prompt: str, default: list[str] | None = None) -> list[str]:
    default_str = ",".join(default) if default else ""
    raw = ask_str(prompt, default_str)
    return [p.strip() for p in raw.split(",") if p.strip()]
