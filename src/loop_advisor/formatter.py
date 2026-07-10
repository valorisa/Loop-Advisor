"""Génération de kickoffs personnalisés à partir d'un loop et d'un ProjectProfile."""

from __future__ import annotations

from typing import Any

from loop_advisor.analyzer import ProjectProfile
from loop_advisor.recommender import suggest_check_command


def generate_kickoff(loop: dict[str, Any], profile: ProjectProfile) -> str:
    """Génère un texte de kickoff personnalisé pour un loop donné.

    Remplace {max_iterations}, {check_command} et {exit_condition} dans le
    template `base_kickoff` du loop, en adaptant la commande de check au
    profil du projet quand c'est possible.
    """
    base_kickoff = loop.get("base_kickoff")
    if not base_kickoff:
        base_kickoff = (
            "Goal: {exit_condition}\n"
            "Max iterations: {max_iterations}\n"
            "Between iterations, run: {check_command}\n"
            "Exit when: {exit_condition}."
        )

    check_command = suggest_check_command(loop, profile)
    max_iterations = loop.get("max_iterations", 10)
    exit_condition = loop.get("exit_condition", "success criteria met")

    return base_kickoff.format(
        max_iterations=max_iterations,
        check_command=check_command,
        exit_condition=exit_condition,
    )
