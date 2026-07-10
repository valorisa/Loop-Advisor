from __future__ import annotations

from loop_advisor.analyzer import ProjectProfile
from loop_advisor.formatter import generate_kickoff


def test_generate_kickoff_basic(python_profile: ProjectProfile):
    loop = {
        "default_check_command": "npm test",
        "supported_languages": ["python"],
        "max_iterations": 10,
        "exit_condition": "all tests pass",
        "base_kickoff": (
            "Goal: {exit_condition}\n"
            "Max iterations: {max_iterations}\n"
            "Between iterations, run: {check_command}\n"
            "Exit when: {exit_condition}."
        ),
    }
    kickoff = generate_kickoff(loop, python_profile)
    assert "all tests pass" in kickoff
    assert "Max iterations: 10" in kickoff
    # La commande doit être adaptée (pytest, pas npm test) car le profil est Python/pytest
    assert "pytest -q" in kickoff


def test_generate_kickoff_fallback_template(bare_profile: ProjectProfile):
    loop = {
        "default_check_command": "make test",
        "supported_languages": [],
        "max_iterations": 5,
        "exit_condition": "build succeeds",
        # pas de base_kickoff -> doit utiliser le template générique
    }
    kickoff = generate_kickoff(loop, bare_profile)
    assert "build succeeds" in kickoff
    assert "Max iterations: 5" in kickoff
    assert "make test" in kickoff
