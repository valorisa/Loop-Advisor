# Architecture

## Schéma textuel

```text
                     │   CLI (typer)    │
                     │    cli.py        │
                     └───────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
 ┌─────────────┐    ┌─────────────────┐   ┌─────────────────┐
 │ analyzer.py │    │ recommender.py  │   │  formatter.py   │
 │             │    │                 │   │                 │
 │ analyze_repo│───▶│ recommend_loops │──▶│ generate_kickoff│
 │ ProjectProfile   │ LoopRecommendation │  │                 │
 └─────────────┘    └─────────────────┘   └─────────────────┘
        │                    │
        │                    ▼
        │           ┌─────────────────┐
        │           │ data/loops.json │
        │           └─────────────────┘
        ▼
 ┌─────────────┐
 │  git repo    │
 │ (gitpython)  │
 └─────────────┘

                ┌─────────────┐
                │  config.py  │
                │ load_config │  (.loop-advisor.config.yaml)
                └─────────────┘
```

## Description des modules

### `analyzer.py`

- Point d'entrée : `analyze_repo(repo_path: str) -> ProjectProfile`.
- Utilise `gitpython` pour lister les fichiers versionnés (`git ls-files`).
- Applique des heuristiques simples (extensions de fichiers, fichiers
  manifestes comme `package.json`, `requirements.txt`, `go.mod`, etc.) pour
  déduire :
  - les langages utilisés,
  - les frameworks/outils,
  - les systèmes CI/CD présents,
  - la présence de tests et leurs frameworks probables,
  - la présence d'outils de sécurité configurés.
- Ne fait aucun appel réseau ; tout est déduit localement du contenu du repo.

### `recommender.py`

- Charge la base de loops via `load_loops_db(db_path)`.
- `recommend_loops(profile, agent, db_path, top_n)` calcule un score par loop :
  - **+2 par langage** en commun entre le loop et le profil,
  - **+1.5 par système CI/CD** en commun,
  - **+1.5** si la catégorie est `testing` et que le profil a des tests,
  - **+1** si la catégorie est `security` et que le profil a des checks sécurité,
  - **+0.5** si la catégorie est `quality`,
  - **+1** si l'agent cible est supporté par le loop.
- Retourne les `top_n` loops avec le score le plus élevé, sous forme de
  `LoopRecommendation` (incluant la raison textuelle du score).
- `suggest_check_command(loop, profile)` affine la commande de check par
  défaut du loop en fonction des frameworks de test détectés dans le profil.

### `formatter.py`

- `generate_kickoff(loop, profile)` charge le template `base_kickoff` du loop
  (ou un template générique de secours) et remplace les placeholders
  `{max_iterations}`, `{check_command}` et `{exit_condition}` par les valeurs
  du loop et la commande de check adaptée au profil.

### `cli.py`

- Construit une application `typer` avec trois commandes :
  - `analyze --repo <path> [--json|--text]`
  - `recommend --repo <path> --agent <agent> [--top N] [--kickoff]`
  - `kickoff --repo <path> --loop <name>`
- Orchestre `analyzer`, `recommender`, `formatter` et `config`.

### `config.py`

- Charge un fichier optionnel `.loop-advisor.config.yaml` à la racine du repo
  analysé, permettant de surcharger :
  - `loops_db_path` : chemin vers une base de loops custom,
  - `default_agent` : agent par défaut,
  - `max_recommendations` : nombre de recommandations par défaut,
  - `history_path` : chemin vers un futur historique d'utilisation (Phase 2).
