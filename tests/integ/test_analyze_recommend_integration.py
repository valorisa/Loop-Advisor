from __future__ import annotations

from pathlib import Path

import git
import pytest

from loop_advisor.analyzer import analyze_repo
from loop_advisor.recommender import recommend_loops


@pytest.fixture
def minimal_python_repo(tmp_path: Path) -> Path:
    """Crée un mini repo Git réel avec des fichiers Python + tests + CI GitHub Actions."""
    repo_dir = tmp_path / "minimal-python-repo"
    repo_dir.mkdir()

    (repo_dir / "requirements.txt").write_text("requests\n", encoding="utf-8")
    (repo_dir / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")

    src_dir = repo_dir / "src"
    src_dir.mkdir()
    (src_dir / "main.py").write_text("def hello():\n    return 'hello'\n", encoding="utf-8")

    tests_dir = repo_dir / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_main.py").write_text(
        "from src.main import hello\n\ndef test_hello():\n    assert hello() == 'hello'\n",
        encoding="utf-8",
    )

    workflows_dir = repo_dir / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)
    (workflows_dir / "ci.yml").write_text("name: CI\non: [push]\n", encoding="utf-8")

    repo = git.Repo.init(repo_dir)
    repo.index.add(
        [
            "requirements.txt",
            "pytest.ini",
            "src/main.py",
            "tests/test_main.py",
            ".github/workflows/ci.yml",
        ]
    )
    repo.index.commit("initial commit")

    return repo_dir


def test_analyze_repo_on_minimal_python_repo(minimal_python_repo: Path):
    profile = analyze_repo(str(minimal_python_repo))

    assert "python" in profile.languages
    assert "github-actions" in profile.ci_cd
    assert profile.has_tests is True
    assert "pytest" in profile.test_frameworks
    assert profile.repo_path == str(minimal_python_repo)


def test_recommend_loops_end_to_end(minimal_python_repo: Path):
    profile = analyze_repo(str(minimal_python_repo))
    recommendations = recommend_loops(profile, agent="claude-code", top_n=5)

    assert isinstance(recommendations, list)
    assert len(recommendations) > 0

    for rec in recommendations:
        assert rec.name
        assert rec.url.startswith("https://")
        assert rec.suggested_check_command
        assert rec.reason

    names = [r.name for r in recommendations]
    assert "python-test-looper" in names
