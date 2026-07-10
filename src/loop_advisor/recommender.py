"""Moteur de recommandation de loops basé sur un ProjectProfile."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from loop_advisor.analyzer import ProjectProfile
from loop_advisor.config import DEFAULT_LOOPS_DB_PATH


@dataclass
class LoopRecommendation:
    """Représente une loop recommandée pour un projet donné."""

    name: str
    url: str
    description: str
    category: str
    reason: str
    suggested_check_command: str
    score: float
    raw_loop: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "url": self.url,
            "description": self.description,
            "category": self.category,
            "reason": self.reason,
            "suggested_check_command": self.suggested_check_command,
            "score": round(self.score, 2),
        }


def load_loops_db(db_path: str | Path = DEFAULT_LOOPS_DB_PATH) -> list[dict[str, Any]]:
    """Charge la base de loops depuis un fichier JSON."""
    db_path = Path(db_path)
    if not db_path.exists():
        raise FileNotFoundError(f"Base de loops introuvable: {db_path}")
    with db_path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError(f"Format invalide pour la base de loops: {db_path}")
    return data


def suggest_check_command(loop: dict[str, Any], profile: ProjectProfile) -> str:
    """Déduit une commande de check plus précise si le profil le permet.

    Sinon, retombe sur `default_check_command` du loop.
    """
    default_cmd = loop.get("default_check_command", "")
    test_frameworks = set(profile.test_frameworks)

    if "pytest" in test_frameworks and "python" in profile.languages:
        return "pytest -q"
    if "go-test" in test_frameworks and "golang" in profile.languages:
        return "go test -v ./..."
    if "jest" in test_frameworks and (
        "javascript" in profile.languages or "typescript" in profile.languages
    ):
        return "npm test"

    return default_cmd


def _score_loop(loop: dict[str, Any], profile: ProjectProfile, agent: str) -> tuple[float, list[str]]:
    """Calcule un score de pertinence pour un loop donné et les raisons associées."""
    score = 0.0
    reasons: list[str] = []

    supported_langs = set(loop.get("supported_languages", []))
    lang_matches = supported_langs & set(profile.languages)
    if lang_matches:
        score += 2.0 * len(lang_matches)
        reasons.append(f"langage(s) compatible(s): {', '.join(sorted(lang_matches))}")

    supported_ci = set(loop.get("supported_ci_cd", []))
    ci_matches = supported_ci & set(profile.ci_cd)
    if ci_matches:
        score += 1.5 * len(ci_matches)
        reasons.append(f"CI/CD compatible: {', '.join(sorted(ci_matches))}")
    elif "none" in supported_ci and not profile.ci_cd:
        score += 0.5
        reasons.append("pas de CI/CD détectée, loop utilisable en local")

    category = loop.get("category", "")
    if category == "testing" and profile.has_tests:
        score += 1.5
        reasons.append("le projet a déjà des tests, ce loop renforce la fiabilité")
    if category == "security" and profile.has_security_checks:
        score += 1.0
        reasons.append("outils de sécurité déjà présents dans le projet")
    if category == "quality":
        score += 0.5
        reasons.append("amélioration générale de la qualité du code")

    supported_agents = set(loop.get("supported_agents", []))
    if agent in supported_agents:
        score += 1.0
        reasons.append(f"compatible avec l'agent '{agent}'")

    if not reasons:
        reasons.append("loop générique, faible correspondance avec le profil détecté")

    return score, reasons


def recommend_loops(
    profile: ProjectProfile,
    agent: str = "cli",
    db_path: str | Path = DEFAULT_LOOPS_DB_PATH,
    top_n: int = 5,
) -> list[LoopRecommendation]:
    """Recommande les `top_n` loops les plus adaptées à un ProjectProfile donné."""
    loops = load_loops_db(db_path)

    scored: list[LoopRecommendation] = []
    for loop in loops:
        score, reasons = _score_loop(loop, profile, agent)
        if score <= 0:
            continue
        scored.append(
            LoopRecommendation(
                name=loop.get("name", "unknown"),
                url=loop.get("url", ""),
                description=loop.get("description", ""),
                category=loop.get("category", ""),
                reason="; ".join(reasons),
                suggested_check_command=suggest_check_command(loop, profile),
                score=score,
                raw_loop=loop,
            )
        )

    scored.sort(key=lambda r: r.score, reverse=True)
    return scored[:top_n]
