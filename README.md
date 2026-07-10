# loop-advisor

**loop-advisor** est un petit outil en ligne de commande (CLI) qui regarde le contenu d'un
projet Git et te suggère des **"loops"** adaptées à ce projet — des routines de travail
automatisées, disponibles sur [loops.elorm.xyz](https://loops.elorm.xyz), que tu peux ensuite
donner à un assistant IA (comme Claude Code, Cursor, ou un simple script) pour qu'il corrige des
tests, du lint, de la sécurité, etc. jusqu'à ce qu'un critère de succès soit atteint.

Ce README est volontairement détaillé : il s'adresse à quelqu'un qui découvre le projet, la
ligne de commande, ou même Git. Si tu es déjà à l'aise avec tout ça, tu peux aller directement à
la section [Usage rapide](#usage-rapide).

---

## Table des matières

- [C'est quoi, une "loop" ?](#cest-quoi-une-loop-)
- [Que fait concrètement loop-advisor ?](#que-fait-concrètement-loop-advisor-)
- [Prérequis](#prérequis)
- [Installation, étape par étape](#installation-étape-par-étape)
- [Usage rapide](#usage-rapide)
- [Tutoriel complet, avec des exemples de sortie](#tutoriel-complet-avec-des-exemples-de-sortie)
- [Comprendre les 3 commandes](#comprendre-les-3-commandes)
- [Structure du projet](#structure-du-projet)
- [Comment fonctionne la recommandation ? (le détail)](#comment-fonctionne-la-recommandation--le-détail)
- [Configuration optionnelle](#configuration-optionnelle)
- [Développement et tests](#développement-et-tests)
- [Questions fréquentes (FAQ)](#questions-fréquentes-faq)
- [Dépannage](#dépannage)
- [Contribuer](#contribuer)
- [Licence](#licence)

---

## C'est quoi, une "loop" ?

Une **loop** (boucle, en anglais) est une petite recette de travail répétitive destinée à un
agent IA. L'idée : au lieu de dire vaguement "corrige mon code", on donne à l'IA :

- un **objectif clair** (ex. "tous les tests doivent passer"),
- une **commande de vérification** à relancer entre chaque tentative (ex. `pytest -q`),
- une **condition de sortie** (ex. "quand la commande ne renvoie plus d'erreur"),
- un **nombre maximum d'itérations**, pour éviter que l'IA tourne en boucle indéfiniment.

Ce texte structuré s'appelle un **kickoff**. Une fois qu'on le donne à un agent IA, celui-ci
répète le cycle *corriger → vérifier → recommencer* jusqu'à réussite ou jusqu'à la limite
d'itérations. C'est une manière de rendre le travail d'un agent IA plus fiable et plus mesurable
qu'un simple "fais-le bien".

Le site [loops.elorm.xyz](https://loops.elorm.xyz) référence plusieurs loops génériques : tests
Python, lint TypeScript, vérification de déploiement, audit de sécurité, etc.

## Que fait concrètement loop-advisor ?

Le problème que résout cet outil : parmi toutes les loops disponibles, laquelle est pertinente
*pour ton projet précis* ? `loop-advisor` répond à cette question en 3 étapes automatisées :

1. Il **regarde ton dépôt Git** (les fichiers qu'il contient, pas leur contenu détaillé) pour
   deviner : quel(s) langage(s) tu utilises, si tu as déjà des tests, si tu as une pipeline
   CI/CD (GitHub Actions, GitLab CI...), si des outils de sécurité sont configurés.
2. Il **compare ce profil** à une base de loops connues (`data/loops.json`) et calcule un score
   de pertinence pour chacune.
3. Il **génère le texte de kickoff** prêt à copier-coller vers ton agent IA préféré, avec la
   bonne commande de test adaptée à ton projet.

Aucune donnée n'est envoyée sur Internet : tout se passe en local, sur les fichiers de ton
dépôt Git.

## Prérequis

Avant de commencer, tu as besoin de :

- **Python 3.11 ou plus récent** installé sur ta machine.
  Vérifie avec :

  ```bash
  python3 --version
  ```

- **Git** installé (l'outil analyse un dépôt Git, donc ton projet doit déjà être initialisé
  avec `git init` et contenir au moins un commit).
  Vérifie avec :

  ```bash
  git --version
  ```

- **pip**, le gestionnaire de paquets Python (il est fourni avec Python dans la grande
  majorité des cas).

Aucune connaissance avancée de Python n'est nécessaire pour *utiliser* l'outil — seulement
pour le modifier si tu le souhaites (voir [Contribuer](#contribuer)).

## Installation, étape par étape

1. **Récupère le projet** (si ce n'est pas déjà fait) :

   ```bash
   git clone git@github.com:valorisa/Loop-Advisor.git
   cd Loop-Advisor
   ```

2. **Installe le paquet en mode "éditable"**. Le mode éditable veut dire que si tu modifies le
   code source plus tard, tu n'as pas besoin de réinstaller : les changements sont pris en
   compte directement.

   ```bash
   pip install -e ".[dev]"
   ```

   Le suffixe `[dev]` installe en plus les outils nécessaires pour lancer les tests et le lint
   (`pytest`, `ruff`). Si tu veux seulement *utiliser* l'outil sans contribuer au code, tu peux
   te contenter de :

   ```bash
   pip install -e .
   ```

3. **Ou, plus simple : utilise `make`** (un raccourci vers la commande ci-dessus) :

   ```bash
   make install
   ```

4. **Vérifie que l'installation a fonctionné** :

   ```bash
   loop-advisor --help
   ```

   Si tu vois une liste de commandes disponibles (`analyze`, `recommend`, `kickoff`), tout est
   en ordre.

   > 💡 Si tu obtiens une erreur du type `command not found: loop-advisor`, c'est probablement
   > que le dossier d'installation de pip (`~/.local/bin` sur Linux/Termux, par exemple) n'est
   > pas dans ton `PATH`. Vois la section [Dépannage](#dépannage).

## Usage rapide

Pour les personnes pressées, voici les 3 commandes essentielles :

```bash
# 1. Comprendre ce que loop-advisor détecte dans ton projet
loop-advisor analyze --repo ./mon-projet --text

# 2. Obtenir des recommandations de loops adaptées
loop-advisor recommend --repo ./mon-projet --agent claude-code

# 3. Générer le texte prêt à donner à ton agent IA pour une loop précise
loop-advisor kickoff --repo ./mon-projet --loop python-test-looper
```

Remplace `./mon-projet` par le chemin vers le dépôt Git que tu veux analyser (`.` si tu es déjà
dedans).

## Tutoriel complet, avec des exemples de sortie

Imaginons que tu as un petit projet Python nommé `mon-app`, avec des tests et une pipeline
GitHub Actions. Voici ce qui se passe, commande par commande.

### Étape 1 — Analyser le projet

```bash
loop-advisor analyze --repo ./mon-app --text
```

Sortie attendue (les valeurs varient selon ton projet) :

```text
Repo: ./mon-app
Langages: python
Frameworks: pip
CI/CD: github-actions
Tests: oui (pytest)
Sécurité: non ()
```

Ce que ça veut dire :

- `loop-advisor` a trouvé des fichiers `.py` et un `requirements.txt` → il en déduit que le
  projet est en Python.
- Il a trouvé un dossier `.github/workflows/` → il en déduit une pipeline GitHub Actions.
- Il a trouvé un dossier `tests/` et/ou un fichier `pytest.ini` → il en déduit que le projet a
  des tests, avec `pytest` comme framework probable.
- Aucun outil de sécurité connu (`bandit`, `gitleaks`...) n'a été détecté.

Si tu préfères une sortie machine-readable (par exemple pour la brancher dans un script), utilise
le format JSON, qui est celui par défaut :

```bash
loop-advisor analyze --repo ./mon-app
```

```json
{
  "languages": ["python"],
  "frameworks": ["pip"],
  "ci_cd": ["github-actions"],
  "has_tests": true,
  "test_frameworks": ["pytest"],
  "has_security_checks": false,
  "security_tools": [],
  "repo_path": "./mon-app"
}
```

### Étape 2 — Obtenir des recommandations

```bash
loop-advisor recommend --repo ./mon-app --agent claude-code --top 3
```

Sortie attendue :

```text
1. python-test-looper (score: 4.50)
   Catégorie: testing
   Raison: langage(s) compatible(s): python; CI/CD compatible: github-actions; le projet a
   déjà des tests, ce loop renforce la fiabilité; compatible avec l'agent 'claude-code'
   URL: https://loops.elorm.xyz/loops/python-test-looper
   Commande de check suggérée: pytest -q

2. guardrails-learning-loop (score: 3.50)
   ...

3. security-guardloop (score: 1.00)
   ...
```

Chaque ligne "Raison" t'explique *pourquoi* cette loop a été proposée — c'est le score détaillé
en langage naturel, pas une boîte noire.

L'option `--agent` te permet de préciser à quel outil la loop sera destinée
(`claude-code`, `cursor`, `cli`...), car certaines loops ne sont pas compatibles avec tous les
agents. L'option `--top` limite le nombre de résultats (5 par défaut).

### Étape 3 — Générer le kickoff

Une fois que tu as choisi une loop dans la liste ci-dessus (par exemple
`python-test-looper`), génère son texte de lancement :

```bash
loop-advisor kickoff --repo ./mon-app --loop python-test-looper
```

Sortie attendue :

```text
Goal: all Python tests must pass.
Max iterations: 10
Between iterations, run: pytest -q
Exit when: all tests pass.
```

Ce texte est **directement copiable** dans une conversation avec ton agent IA (Claude Code,
Cursor, etc.). L'agent saura précisément quoi faire, comment vérifier son travail, et quand
s'arrêter.

> 💡 Astuce : tu peux obtenir ce texte directement dans les résultats de `recommend`, sans passer
> par une commande séparée, en ajoutant l'option `--kickoff` :
>
> ```bash
> loop-advisor recommend --repo ./mon-app --agent claude-code --kickoff
> ```

## Comprendre les 3 commandes

| Commande    | Ce qu'elle fait                                        | Entrée principale        | Sortie                            |
| ----------- | ------------------------------------------------------- | ------------------------- | ---------------------------------- |
| `analyze`   | Inspecte le dépôt et déduit son profil technique         | `--repo <chemin>`         | Un `ProjectProfile` (JSON/texte)   |
| `recommend` | Compare le profil à la base de loops et trie par score   | `--repo`, `--agent`       | Une liste de loops classées        |
| `kickoff`   | Génère le texte de lancement pour une loop précise        | `--repo`, `--loop <nom>`  | Un bloc de texte prêt à l'emploi   |

Ces trois commandes forment un pipeline logique :

```text
analyze  →  recommend  →  kickoff
(profil)    (choix)        (texte prêt)
```

## Structure du projet

Si tu veux explorer ou modifier le code, voici à quoi sert chaque dossier :

```text
loop-advisor/
├── data/
│   └── loops.json          # la "base de données" des loops connues (fichier JSON simple)
├── src/
│   └── loop_advisor/
│       ├── __init__.py
│       ├── cli.py          # point d'entrée : définit les commandes analyze/recommend/kickoff
│       ├── analyzer.py     # scanne un dépôt Git -> produit un ProjectProfile
│       ├── recommender.py  # compare un ProjectProfile aux loops et calcule un score
│       ├── formatter.py    # transforme une loop + un profil en texte de kickoff
│       └── config.py       # lecture d'un fichier de config optionnel
├── tests/
│   ├── unit/                # tests rapides, sur des fonctions isolées
│   ├── integ/                # tests qui utilisent un vrai mini-dépôt Git temporaire
│   └── e2e/
├── docs/
│   ├── usage.md              # exemples de commandes (extrait de ce README)
│   └── architecture.md       # schéma détaillé des modules
├── .github/workflows/         # intégration continue (tests + lint automatiques)
├── pyproject.toml            # définit le paquet Python et ses dépendances
├── Makefile                   # raccourcis de commandes (make install, make test...)
└── README.md                  # ce fichier
```

Si tu ne comprends pas un de ces termes (paquet Python, dépendances, intégration continue...),
n'hésite pas à demander — le but de ce projet est justement d'être accessible.

## Comment fonctionne la recommandation ? (le détail)

Cette section est pour les curieux qui veulent comprendre le calcul derrière les scores.

Pour chaque loop de la base `data/loops.json`, `loop-advisor` calcule un score en additionnant
des points selon les règles suivantes :

- **+2 points par langage en commun** entre la loop et ton projet.
  *Exemple : ta loop supporte Python et JavaScript, ton projet est en Python → +2.*
- **+1.5 point par système CI/CD en commun** (GitHub Actions, GitLab CI...).
- **+1.5 point** si la loop est de catégorie `testing` **et** que ton projet a déjà des tests
  détectés (ça veut dire que la loop a de quoi vérifier son propre travail).
- **+1 point** si la loop est de catégorie `security` **et** que ton projet a déjà des outils
  de sécurité configurés.
- **+0.5 point** si la loop est de catégorie `quality` (bonus générique, car la qualité de code
  profite toujours à un projet).
- **+1 point** si l'agent que tu as précisé (`--agent`) est explicitement supporté par la loop.

Les loops sont ensuite triées du score le plus haut au plus bas, et seules les `--top N`
premières te sont montrées (5 par défaut). Une loop avec un score de 0 (aucune correspondance)
n'est jamais proposée.

Ce calcul est volontairement simple et transparent — pas de "boîte noire" à base
d'intelligence artificielle pour cette étape : uniquement des règles claires que tu peux lire
directement dans `src/loop_advisor/recommender.py`.

## Configuration optionnelle

Si tu veux personnaliser le comportement de `loop-advisor` pour un projet donné (par exemple,
utiliser ta propre base de loops au lieu de celle fournie), crée un fichier
`.loop-advisor.config.yaml` **à la racine du dépôt que tu analyses** :

```yaml
# .loop-advisor.config.yaml
loops_db_path: /chemin/vers/ma-base-de-loops.json
default_agent: claude-code
max_recommendations: 5
```

Ce fichier est entièrement optionnel : sans lui, `loop-advisor` utilise ses réglages par
défaut (la base `data/loops.json` fournie avec le paquet, l'agent `cli`, 5 recommandations
maximum).

## Développement et tests

Si tu veux contribuer au code ou juste vérifier que tout fonctionne correctement sur ta
machine :

```bash
make install   # installe le projet + les outils de développement
make test      # lance la suite de tests (pytest)
make lint      # vérifie le style du code (ruff)
make format    # reformate automatiquement le code (ruff)
```

Le projet contient actuellement une vingtaine de tests automatisés, répartis en deux catégories :

- **Tests unitaires** (`tests/unit/`) : testent chaque fonction individuellement, avec des
  données fabriquées à la main. Rapides (quelques millisecondes).
- **Tests d'intégration** (`tests/integ/`) : créent un vrai mini-dépôt Git temporaire, y lancent
  `loop-advisor`, et vérifient que le résultat est cohérent de bout en bout.

Chaque `push` ou `pull request` déclenche automatiquement ces vérifications via GitHub Actions
(voir le badge et le dossier `.github/workflows/`).

## Questions fréquentes (FAQ)

**Est-ce que `loop-advisor` modifie mon code ?**
Non. Il ne fait que *lire* les fichiers de ton dépôt (via `git ls-files`, qui liste les fichiers
suivis par Git) pour deviner ton profil technique. Il n'écrit, ne modifie, ni ne supprime rien
dans ton projet.

**Est-ce que mes données sont envoyées quelque part ?**
Non, aucune connexion réseau n'est faite par `loop-advisor` lui-même. Tout le calcul est local.

**Pourquoi mon projet n'a "aucun langage détecté" ?**
Vérifie que tes fichiers sont bien suivis par Git (`git status`), car `analyze` se base sur
`git ls-files`, qui ne liste que les fichiers déjà ajoutés avec `git add` puis committés (ou au
moins indexés). Un fichier non suivi par Git n'est pas vu par l'outil.

**Puis-je ajouter mes propres loops ?**
Oui, soit en modifiant `data/loops.json` directement, soit en pointant vers ta propre base via
le fichier de config (voir [Configuration optionnelle](#configuration-optionnelle)). Le format
attendu pour chaque loop est documenté dans `CONTRIBUTING.md`.

**C'est quoi la différence entre `recommend` et `kickoff` ?**
`recommend` te donne une liste de plusieurs loops possibles avec leur score et la raison du
choix. `kickoff` prend UNE loop précise (dont tu connais déjà le nom) et génère uniquement son
texte de lancement, prêt à copier-coller.

## Dépannage

**`command not found: loop-advisor` après installation**
Le script `loop-advisor` a été installé dans un dossier qui n'est pas dans ton `PATH`. Cherche
son emplacement avec :

```bash
python3 -m site --user-base
```

puis ajoute `<résultat>/bin` à ton `PATH` (dans `~/.bashrc` ou `~/.zshrc` selon ton shell), et
recharge ton terminal.

**`git.exc.InvalidGitRepositoryError` en lançant `analyze`**
Le chemin donné à `--repo` n'est pas un dépôt Git valide. Vérifie que le dossier contient bien
un sous-dossier `.git/` (créé par `git init`), et qu'au moins un commit existe.

**La commande `recommend` ne renvoie aucun résultat**
Cela arrive si ton profil ne correspond à aucun langage/CI/CD connu de la base de loops (par
exemple, un projet sans aucun fichier reconnaissable). Vérifie d'abord la sortie de `analyze`
pour voir ce qui a été détecté.

## Contribuer

Les contributions sont bienvenues ! Voir `CONTRIBUTING.md` pour :

- le workflow de branches (`main` / `dev` / branches de fonctionnalité),
- le format attendu pour ajouter une nouvelle loop à `data/loops.json`,
- les conventions de commit (Conventional Commits).

## Licence

Ce projet est distribué sous licence MIT. Voir le fichier `LICENSE` pour le texte complet.
