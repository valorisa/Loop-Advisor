from __future__ import annotations

from loop_advisor.analyzer import (
    _detect_ci_cd,
    _detect_frameworks,
    _detect_languages,
    _detect_security_checks,
    _detect_tests,
)


def test_detect_languages_from_extensions():
    files = ["src/main.py", "src/app.ts", "index.js", "README.md"]
    langs = _detect_languages(files)
    assert "python" in langs
    assert "typescript" in langs
    assert "javascript" in langs
    assert "markdown" not in langs  # .md n'est pas mappé, ignoré


def test_detect_languages_from_manifests():
    files = ["requirements.txt", "go.mod", "Cargo.toml"]
    langs = _detect_languages(files)
    assert set(langs) == {"python", "golang", "rust"}


def test_detect_frameworks():
    files = ["package.json", "Dockerfile", "Makefile"]
    frameworks = _detect_frameworks(files)
    assert "node" in frameworks
    assert "docker" in frameworks
    assert "make" in frameworks


def test_detect_ci_cd_github_actions():
    files = [".github/workflows/ci.yml", "src/main.py"]
    ci_cd = _detect_ci_cd(files)
    assert "github-actions" in ci_cd


def test_detect_ci_cd_gitlab():
    files = [".gitlab-ci.yml"]
    ci_cd = _detect_ci_cd(files)
    assert "gitlab-ci" in ci_cd


def test_detect_ci_cd_empty():
    files = ["src/main.py", "README.md"]
    assert _detect_ci_cd(files) == []


def test_detect_tests_from_directory():
    files = ["tests/test_foo.py", "src/foo.py"]
    has_tests, frameworks = _detect_tests(files)
    assert has_tests is True


def test_detect_tests_pytest_ini():
    files = ["pytest.ini", "src/foo.py"]
    has_tests, frameworks = _detect_tests(files)
    assert has_tests is True
    assert "pytest" in frameworks


def test_detect_tests_none():
    files = ["README.md", "LICENSE"]
    has_tests, frameworks = _detect_tests(files)
    assert has_tests is False
    assert frameworks == []


def test_detect_security_checks():
    files = [".gitleaks.toml", "src/main.py"]
    has_security, tools = _detect_security_checks(files)
    assert has_security is True
    assert "gitleaks" in tools


def test_detect_security_checks_none():
    files = ["src/main.py"]
    has_security, tools = _detect_security_checks(files)
    assert has_security is False
    assert tools == []
