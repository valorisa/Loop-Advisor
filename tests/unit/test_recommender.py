from __future__ import annotations

from pathlib import Path

from loop_advisor.analyzer import ProjectProfile
from loop_advisor.recommender import (
    LoopRecommendation,
    load_loops_db,
    recommend_loops,
    suggest_check_command,
)


def test_load_loops_db(loops_db_path: Path):
    loops = load_loops_db(loops_db_path)
    assert isinstance(loops, list)
    assert len(loops) >= 10
    assert all("name" in loop for loop in loops)


def test_recommend_loops_python_profile(python_profile: ProjectProfile, loops_db_path: Path):
    recommendations = recommend_loops(
        python_profile, agent="claude-code", db_path=loops_db_path, top_n=5
    )
    assert len(recommendations) > 0
    assert all(isinstance(r, LoopRecommendation) for r in recommendations)
    # Les recommandations doivent être triées par score décroissant
    scores = [r.score for r in recommendations]
    assert scores == sorted(scores, reverse=True)
    # Un loop Python (ex: python-test-looper) doit apparaître dans le top
    names = [r.name for r in recommendations]
    assert "python-test-looper" in names


def test_recommend_loops_empty_profile_returns_few_or_none(
    bare_profile: ProjectProfile, loops_db_path: Path
):
    recommendations = recommend_loops(bare_profile, agent="cli", db_path=loops_db_path, top_n=5)
    # Un profil vide ne devrait matcher aucun langage/CI, donc peu ou pas de résultats
    assert isinstance(recommendations, list)


def test_suggest_check_command_pytest(python_profile: ProjectProfile):
    loop = {
        "default_check_command": "npm test",
        "supported_languages": ["python"],
    }
    cmd = suggest_check_command(loop, python_profile)
    assert cmd == "pytest -q"


def test_suggest_check_command_fallback_to_default(bare_profile: ProjectProfile):
    loop = {"default_check_command": "echo noop", "supported_languages": []}
    cmd = suggest_check_command(loop, bare_profile)
    assert cmd == "echo noop"


def test_recommendation_to_dict(python_profile: ProjectProfile, loops_db_path: Path):
    recommendations = recommend_loops(python_profile, db_path=loops_db_path, top_n=1)
    assert len(recommendations) == 1
    d = recommendations[0].to_dict()
    assert set(d.keys()) == {
        "name",
        "url",
        "description",
        "category",
        "reason",
        "suggested_check_command",
        "score",
    }
