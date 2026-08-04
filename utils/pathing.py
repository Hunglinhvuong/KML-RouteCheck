from pathlib import Path
import os
import sys


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def get_project_root() -> Path:
    return PROJECT_ROOT


def get_data_dir() -> Path:
    return DATA_DIR


def resolve_path(*parts: str) -> str:
    return str(PROJECT_ROOT.joinpath(*parts))


def resolve_data_path(filename: str) -> str:
    return str(get_data_dir() / filename)


def resolve_config_path() -> str:
    candidates = [
        PROJECT_ROOT / "config.env",
        PROJECT_ROOT / "bot" / "config.env",
    ]

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    return str(PROJECT_ROOT / "config.env")


def resolve_runtime_path(relative_path: str) -> str:
    if getattr(sys, "frozen", False):
        return str(Path(sys.executable).resolve().parent / relative_path)

    path = Path(relative_path)
    if path.is_absolute():
        return str(path)

    return str(PROJECT_ROOT / path)
