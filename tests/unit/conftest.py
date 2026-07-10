from __future__ import annotations

import json
from pathlib import Path

import pytest

from loop_advisor.analyzer import ProjectProfile


@pytest.fixture
def python_profile() -> ProjectProfile:
    """Un ProjectProfile Python typique, avec tests pytest et CI GitHub Actions."""
    return ProjectProfile(
        languages=["python"],
        frameworks=["pip"],
        ci_cd=["github-actions"],
        has_tests=True,
        test_frameworks=["pytest"],
        has_security_checks=False,
        security_tools=[],
        repo_path="/tmp/fake-python-repo",
    )


@pytest.fixture
def bare_profile() -> ProjectProfile:
    """Un ProjectProfile minimal, sans rien détecté."""
    return ProjectProfile(
        languages=[],
        frameworks=[],
        ci_cd=[],
        has_tests=False,
        test_frameworks=[],
        has_security_checks=False,
        security_tools=[],
        repo_path="/tmp/fake-empty-repo",
    )


@pytest.fixture
def loops_db_path(tmp_path: Path) -> Path:
    """Copie la base de loops réelle du package dans un fichier temporaire."""
    from loop_advisor.config import DEFAULT_LOOPS_DB_PATH

    data = json.loads(DEFAULT_LOOPS_DB_PATH.read_text(encoding="utf-8"))
    dest = tmp_path / "loops.json"
    dest.write_text(json.dumps(data), encoding="utf-8")
    return dest
