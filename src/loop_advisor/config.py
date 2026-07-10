"""Chargement de configuration pour loop-advisor.

Supporte un fichier `.loop-advisor.config.yaml` optionnel à la racine du repo
analysé, ainsi qu'un emplacement par défaut pour la base de loops.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

DEFAULT_LOOPS_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "loops.json"
CONFIG_FILENAME = ".loop-advisor.config.yaml"


@dataclass
class LoopAdvisorConfig:
    """Configuration résolue pour une exécution de loop-advisor."""

    loops_db_path: Path = field(default_factory=lambda: DEFAULT_LOOPS_DB_PATH)
    default_agent: str = "cli"
    max_recommendations: int = 5
    history_path: Path | None = None


def _read_yaml_config(config_path: Path) -> dict[str, Any]:
    if not config_path.exists():
        return {}
    with config_path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        return {}
    return data


def load_config(repo_path: str | Path) -> LoopAdvisorConfig:
    """Charge la configuration en cherchant `.loop-advisor.config.yaml` dans le repo.

    Les valeurs absentes retombent sur les défauts de `LoopAdvisorConfig`.
    """
    repo_path = Path(repo_path)
    config_path = repo_path / CONFIG_FILENAME
    raw = _read_yaml_config(config_path)

    loops_db_path = Path(raw["loops_db_path"]) if raw.get("loops_db_path") else DEFAULT_LOOPS_DB_PATH
    history_path = Path(raw["history_path"]) if raw.get("history_path") else None

    return LoopAdvisorConfig(
        loops_db_path=loops_db_path,
        default_agent=raw.get("default_agent", "cli"),
        max_recommendations=int(raw.get("max_recommendations", 5)),
        history_path=history_path,
    )
