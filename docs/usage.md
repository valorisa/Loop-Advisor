# Guide d'utilisation

## Flux général

```text
analyze  →  recommend  →  kickoff
```

1. `analyze` inspecte le repo Git et produit un `ProjectProfile`
   (langages, frameworks, CI/CD, tests, sécurité).
2. `recommend` compare ce profil à la base de loops (`data/loops.json`)
   et retourne les loops les mieux notées.
3. `kickoff` génère le texte de lancement (goal, commande de check,
   condition de sortie, nombre max d'itérations) pour un loop précis.

## Exemples de commandes

### Analyser un projet

```bash
loop-advisor analyze --repo ./mon-projet
```

Sortie (JSON) :

```json
{
  "languages": ["python"],
  "frameworks": ["pip"],
  "ci_cd": ["github-actions"],
  "has_tests": true,
  "test_frameworks": ["pytest"],
  "has_security_checks": false,
  "security_tools": [],
  "repo_path": "./mon-projet"
}
```

Version texte lisible :

```bash
loop-advisor analyze --repo ./mon-projet --text
```

### Obtenir des recommandations

```bash
loop-advisor recommend --repo ./mon-projet --agent claude-code
```

Avec génération du kickoff pour chaque loop recommandé :

```bash
loop-advisor recommend --repo ./mon-projet --agent claude-code --kickoff
```

Limiter le nombre de résultats :

```bash
loop-advisor recommend --repo ./mon-projet --top 3
```

### Générer le kickoff d'un loop précis

```bash
loop-advisor kickoff --repo ./mon-projet --loop python-test-looper
```

## Base de loops custom

Par défaut, `loop-advisor` utilise `data/loops.json` du package. Pour utiliser
une base personnalisée :

```bash
loop-advisor recommend --repo ./mon-projet --loops-db ./ma-base-loops.json
```

Ou via un fichier `.loop-advisor.config.yaml` à la racine du repo analysé
(voir `README.md`, section Configuration optionnelle).
