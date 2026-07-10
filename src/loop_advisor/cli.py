"""Point d'entrée CLI de loop-advisor."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Optional

import typer

from loop_advisor.analyzer import analyze_repo
from loop_advisor.config import load_config
from loop_advisor.formatter import generate_kickoff
from loop_advisor.recommender import load_loops_db, recommend_loops

app = typer.Typer(
    name="loop-advisor",
    help="Analyse un repo Git et recommande des loops adaptées (loops.elorm.xyz).",
    no_args_is_help=True,
)


@app.command()
def analyze(
    repo: str = typer.Option(..., "--repo", help="Chemin vers le repo Git à analyser."),
    as_json: bool = typer.Option(True, "--json/--text", help="Afficher en JSON ou en texte lisible."),
) -> None:
    """Analyse un repo et affiche son ProjectProfile."""
    profile = analyze_repo(repo)
    if as_json:
        typer.echo(json.dumps(asdict(profile), indent=2, ensure_ascii=False))
        return

    typer.echo(f"Repo: {profile.repo_path}")
    typer.echo(f"Langages: {', '.join(profile.languages) or '(aucun détecté)'}")
    typer.echo(f"Frameworks: {', '.join(profile.frameworks) or '(aucun détecté)'}")
    typer.echo(f"CI/CD: {', '.join(profile.ci_cd) or '(aucune détectée)'}")
    typer.echo(f"Tests: {'oui' if profile.has_tests else 'non'} ({', '.join(profile.test_frameworks)})")
    typer.echo(
        f"Sécurité: {'oui' if profile.has_security_checks else 'non'} "
        f"({', '.join(profile.security_tools)})"
    )


@app.command()
def recommend(
    repo: str = typer.Option(..., "--repo", help="Chemin vers le repo Git à analyser."),
    agent: str = typer.Option("cli", "--agent", help="Agent cible: cursor, claude-code, cli..."),
    top: int = typer.Option(5, "--top", help="Nombre max de loops recommandées."),
    loops_db: Optional[str] = typer.Option(
        None, "--loops-db", help="Chemin custom vers loops.json (sinon config ou défaut)."
    ),
    show_kickoff: bool = typer.Option(
        False, "--kickoff/--no-kickoff", help="Afficher le kickoff généré pour chaque loop."
    ),
) -> None:
    """Recommande des loops adaptées au profil du repo analysé."""
    profile = analyze_repo(repo)
    config = load_config(repo)
    db_path = Path(loops_db) if loops_db else config.loops_db_path

    recommendations = recommend_loops(profile, agent=agent, db_path=db_path, top_n=top)

    if not recommendations:
        typer.echo("Aucune loop pertinente trouvée pour ce profil.")
        raise typer.Exit(code=0)

    for i, rec in enumerate(recommendations, start=1):
        typer.echo(f"\n{i}. {rec.name} (score: {rec.score:.2f})")
        typer.echo(f"   Catégorie: {rec.category}")
        typer.echo(f"   Raison: {rec.reason}")
        typer.echo(f"   URL: {rec.url}")
        typer.echo(f"   Commande de check suggérée: {rec.suggested_check_command}")
        if show_kickoff:
            kickoff = generate_kickoff(rec.raw_loop, profile)
            typer.echo("   --- Kickoff ---")
            for line in kickoff.splitlines():
                typer.echo(f"   {line}")


@app.command()
def kickoff(
    repo: str = typer.Option(..., "--repo", help="Chemin vers le repo Git à analyser."),
    loop_name: str = typer.Option(..., "--loop", help="Nom du loop (voir data/loops.json)."),
    loops_db: Optional[str] = typer.Option(
        None, "--loops-db", help="Chemin custom vers loops.json (sinon config ou défaut)."
    ),
) -> None:
    """Génère le kickoff personnalisé pour un loop précis."""
    profile = analyze_repo(repo)
    config = load_config(repo)
    db_path = Path(loops_db) if loops_db else config.loops_db_path

    loops = load_loops_db(db_path)
    matches = [loop for loop in loops if loop.get("name") == loop_name]
    if not matches:
        typer.echo(f"Loop '{loop_name}' introuvable dans {db_path}.", err=True)
        raise typer.Exit(code=1)

    typer.echo(generate_kickoff(matches[0], profile))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
