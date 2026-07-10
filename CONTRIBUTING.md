# Contribuer à loop-advisor

Merci de votre intérêt pour `loop-advisor` !

## Mise en place de l'environnement

```bash
git clone <url-du-repo>
cd loop-advisor
make install
```

## Workflow recommandé

1. Créez une branche dédiée : `git checkout -b feature/ma-fonctionnalite`.
2. Développez et ajoutez des tests dans `tests/unit/` ou `tests/integ/`.
3. Vérifiez la qualité du code :

   ```bash
   make lint
   make test
   ```

4. Committez avec des messages suivant [Conventional Commits](https://www.conventionalcommits.org/fr/)
   (ex: `feat: ajoute la commande kickoff`, `fix: corrige la détection CI/CD`).
5. Ouvrez une Pull Request et attendez la revue.

## Ajouter un nouveau loop

Pour ajouter un loop à la base `data/loops.json`, respectez le schéma existant :

```json
{
  "name": "mon-nouveau-loop",
  "category": "testing|quality|security|deployment|docs|ci-cd",
  "supported_agents": ["cursor", "claude-code", "cli"],
  "supported_languages": ["python", "javascript", "..."],
  "supported_ci_cd": ["github-actions", "gitlab-ci", "none"],
  "trigger_types": ["manual", "pre-commit"],
  "default_check_command": "...",
  "exit_condition": "...",
  "max_iterations": 10,
  "url": "https://loops.elorm.xyz/loops/mon-nouveau-loop",
  "description": "...",
  "base_kickoff": "Goal: ...\nMax iterations: {max_iterations}\nBetween iterations, run: {check_command}\nExit when: {exit_condition}."
}
```

Ajoutez un test associé dans `tests/unit/test_recommender.py` si le loop introduit
une nouvelle logique de matching.

## Style de code

- Python 3.11+, typage explicite (dataclasses).
- Formatage et lint via `ruff` (voir `make lint` / `make format`).
- Tests via `pytest` (voir `make test`).
