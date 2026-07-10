"""Analyse d'un repo Git pour produire un ProjectProfile."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import git


@dataclass
class ProjectProfile:
    languages: list[str]
    frameworks: list[str]
    ci_cd: list[str]
    has_tests: bool
    test_frameworks: list[str]
    has_security_checks: bool
    security_tools: list[str]
    repo_path: str


def _detect_languages(files: list[str]) -> list[str]:
    """Détecte les langages via heuristiques simples (extensions + manifests)."""
    langs = set()

    ext_map = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".go": "golang",
        ".sh": "bash",
        ".bash": "bash",
        ".rs": "rust",
        ".java": "java",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "c",
        ".hpp": "cpp",
    }

    for f in files:
        ext = Path(f).suffix.lower()
        if ext in ext_map:
            langs.add(ext_map[ext])

    if any(Path(f).name == "requirements.txt" for f in files):
        langs.add("python")
    if any(Path(f).name == "pyproject.toml" for f in files):
        langs.add("python")
    if any(Path(f).name == "package.json" for f in files):
        langs.add("javascript")
        langs.add("typescript")
    if any(Path(f).name == "Cargo.toml" for f in files):
        langs.add("rust")
    if any(Path(f).name == "go.mod" for f in files):
        langs.add("golang")

    return sorted(langs)


def _detect_frameworks(files: list[str]) -> list[str]:
    """Détecte des frameworks/outils courants via fichiers manifestes."""
    frameworks = set()

    for f in files:
        name = Path(f).name
        if name == "requirements.txt" or name == "pyproject.toml":
            frameworks.add("pip")
        if name == "package.json":
            frameworks.add("node")
        if name == "Cargo.toml":
            frameworks.add("rust")
        if name == "go.mod":
            frameworks.add("golang")
        if name == "Makefile":
            frameworks.add("make")
        if name == "docker-compose.yml":
            frameworks.add("docker")
        if name == "Dockerfile":
            frameworks.add("docker")

    return sorted(frameworks)


def _detect_ci_cd(files: list[str]) -> list[str]:
    """Détecte les systèmes CI/CD présents dans le repo."""
    ci_cd = set()

    for f in files:
        p = Path(f)
        if p.name in (".gitlab-ci.yml", "gitlab-ci.yml"):
            ci_cd.add("gitlab-ci")
        if len(p.parts) >= 2 and p.parts[-3:-1] == (".github", "workflows"):
            ci_cd.add("github-actions")
        elif ".github/workflows" in f.replace("\\", "/"):
            ci_cd.add("github-actions")
        if p.name == ".drone.yml":
            ci_cd.add("drone")
        if p.name == "azure-pipelines.yml":
            ci_cd.add("azure-pipelines")

    return sorted(ci_cd)


def _detect_tests(files: list[str]) -> tuple[bool, list[str]]:
    """Déduit s'il y a des tests et quels frameworks sont probablement utilisés."""
    has_tests = False
    test_frameworks: set[str] = set()

    dirs = {Path(f).parts[0] for f in files if Path(f).parts}
    if dirs & {"tests", "test", "spec"}:
        has_tests = True
    for f in files:
        parts = Path(f).parts
        if any(part in ("tests", "test", "spec") for part in parts):
            has_tests = True

    for f in files:
        name = Path(f).name
        if name == "pytest.ini":
            has_tests = True
            test_frameworks.add("pytest")
        if name in ("setup.cfg", "tox.ini"):
            has_tests = True
            test_frameworks.add("pytest")
        if name == "pyproject.toml":
            # heuristique faible : présence de pyproject ne garantit rien,
            # mais on ne force pas has_tests ici.
            pass
        if name == "package.json":
            has_tests = True
            test_frameworks.add("jest")
        if name == "go.mod":
            has_tests = True
            test_frameworks.add("go-test")

    return has_tests, sorted(test_frameworks)


def _detect_security_checks(files: list[str]) -> tuple[bool, list[str]]:
    """Déduit la présence d'outils de sécurité configurés dans le repo."""
    has_security = False
    tools: set[str] = set()

    for f in files:
        name = Path(f).name
        if name in ("bandit.yml", ".bandit.yml", ".bandit"):
            has_security = True
            tools.add("bandit")
        if name in ("safety.yml", "safety.lock", ".safety-policy.yml"):
            has_security = True
            tools.add("safety")
        if name in (".gitleaks.toml", "gitleaks.toml"):
            has_security = True
            tools.add("gitleaks")
        if name in (".sourcery.yaml", "sourcery.yaml"):
            has_security = True
            tools.add("sourcery")

    return has_security, sorted(tools)


def analyze_repo(repo_path: str) -> ProjectProfile:
    """Analyse un repo Git à `repo_path` et retourne un ProjectProfile.

    Version minimale : heuristiques simples sur les fichiers versionnés (git ls-files).
    """
    repo = git.Repo(repo_path)
    files = repo.git.ls_files().splitlines()

    languages = _detect_languages(files)
    frameworks = _detect_frameworks(files)
    ci_cd = _detect_ci_cd(files)
    has_tests, test_frameworks = _detect_tests(files)
    has_security_checks, security_tools = _detect_security_checks(files)

    return ProjectProfile(
        languages=languages,
        frameworks=frameworks,
        ci_cd=ci_cd,
        has_tests=has_tests,
        test_frameworks=test_frameworks,
        has_security_checks=has_security_checks,
        security_tools=security_tools,
        repo_path=repo_path,
    )
