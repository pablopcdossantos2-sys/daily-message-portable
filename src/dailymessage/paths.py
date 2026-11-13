from __future__ import annotations

import sys
from pathlib import Path


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def app_base_dir() -> Path:
    """Pasta do executável (frozen) ou raiz do repositório (dev)."""
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def resource_path(*parts: str) -> Path:
    """Caminho de recursos empacotados (assets)."""
    if is_frozen():
        base = Path(getattr(sys, "_MEIPASS", app_base_dir()))
    else:
        base = Path(__file__).resolve().parents[2]
    return base.joinpath(*parts)
