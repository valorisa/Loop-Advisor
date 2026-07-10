# loop-advisor

Outil CLI pour analyser un projet Git et recommander des loops adaptés ([loops.elorm.xyz](https://loops.elorm.xyz)).

## Installation

```bash
pip install -e ".[dev]"
```

ou, avec `make` :

```bash
make install
```

## Usage

```bash
# Analyse du projet (sortie JSON par défaut)
loop-advisor analyze --repo ./mon-projet

# Analyse en texte lisible
loop-advisor analyze --repo ./mon-projet --text

# Recommandation de loops
loop-advisor recommend --repo ./mon-projet --agent cursor

# Recommandation avec kickoff généré pour chaque loop
loop-advisor recommend --repo ./mon-projet --agent claude-code --kickoff

# Générer uniquement le kickoff d'un loop précis
loop-advisor kickoff --repo ./mon-projet --loop python-test-looper
```

## Structure du projet

```text
loop-advisor/
├── data/
│   └── loops.json          # base de loops (version alpha)
├── src/
│   └── loop_advisor/
│       ├── __init__.py
│       ├── cli.py          # point d'entrée CLI (typer)
│       ├── analyzer.py     # analyse du repo -> ProjectProfile
│       ├── recommender.py  # moteur de recommandation
│       ├── formatter.py    # génération de kickoffs
│       └── config.py       # chargement de config (.loop-advisor.config.yaml)
├── tests/
│   ├── unit/
│   ├── integ/
│   └── e2e/
├── docs/
│   ├── usage.md
│   └── architecture.md
├── pyproject.toml
├── Makefile
└── README.md
```

## Fonctionnement

1. **`analyze`** :
   - Scanne le repo Git (fichiers versionnés via `git ls-files`),
   - Détecte langages, frameworks, CI/CD, tests, sécurité,
   - Retourne un `ProjectProfile`.

2. **`recommend`** :
   - Charge la base de loops (`data/loops.json` par défaut),
   - Matche avec le `ProjectProfile` (score = langage + CI/CD + catégorie + agent),
   - Retourne les 3–5 loops les mieux notées avec la raison du match.

3. **`kickoff`** :
   - Génère un kickoff personnalisé (commande de check adaptée, exit condition,
     max iterations) pour un loop donné.

## Configuration optionnelle

Un fichier `.loop-advisor.config.yaml` peut être placé à la racine du repo analysé :

```yaml
loops_db_path: /chemin/vers/loops.json
default_agent: claude-code
max_recommendations: 5
```

## Développement

```bash
make install
make test
make lint
```

## Contribuer

Voir `CONTRIBUTING.md`.

## Licence

Voir `LICENSE`.
