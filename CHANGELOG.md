# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [Unreleased]

## [0.1.0] - 2026-07-10

### Ajouté

- Structure initiale du projet (`pyproject.toml`, `src/loop_advisor/`, `tests/`, `docs/`).
- `analyzer.py` : analyse d'un repo Git (langages, frameworks, CI/CD, tests, sécurité).
- `recommender.py` : moteur de recommandation de loops avec scoring.
- `formatter.py` : génération de kickoffs personnalisés.
- `cli.py` : commandes `analyze`, `recommend`, `kickoff` (typer).
- `data/loops.json` : base initiale de 12 loops.
- Tests unitaires et d'intégration.
- Documentation (`README.md`, `docs/usage.md`, `docs/architecture.md`).
