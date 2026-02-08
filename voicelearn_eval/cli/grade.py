"""voicelearn-eval grade: Grade-level assessment."""

import json

import click
from rich.console import Console
from rich.table import Table

from voicelearn_eval.grade_levels.scorer import compute_grade_level_rating
from voicelearn_eval.grade_levels.tiers import TIER_LABELS, TIER_ORDER

from ._helpers import get_initialized_storage, run_sync

console = Console()


@click.command("grade")
@click.option("--model", required=True, help="Model ID or slug")
@click.option("--threshold", default=70.0, type=float, help="Pass threshold (0-100)")
@click.option("--run", "run_id", help="Specific run ID (default: latest)")
@click.option("--format", "fmt", default="table", help="Output format (table, json)")
@click.pass_context
def grade_cmd(ctx, model, threshold, run_id, fmt):
    """Show grade-level assessment for a model."""

    async def _grade():
        storage, _ = await get_initialized_storage(
            ctx.obj.get("config_path"), ctx.obj.get("db_path")
        )
        try:
            # Resolve model
            model_data = await storage.get_model(model)
            if not model_data:
                model_data = await storage.get_model_by_slug(model)
            if not model_data:
                console.print(f"[red]Error: Model not found: {model}[/red]")
                raise SystemExit(4)

            # Get run
            if run_id:
                run = await storage.get_run(run_id)
            else:
                # Get latest completed run for this model
                runs = await storage.list_runs(
                    filters={"model_id": model_data["id"], "status": "completed"},
                    limit=1,
                )
                run = runs[0] if runs else None

            if not run:
                console.print(f"[red]Error: No completed runs found for {model_data['name']}[/red]")
                console.print("[dim]Run an evaluation first: voicelearn-eval run --model ... --suite ...[/dim]")
                raise SystemExit(1)

            # Get task results
            results = await storage.get_results_for_run(run["id"])
            if not results:
                console.print(f"[red]Error: No results found for run {run['id']}[/red]")
                raise SystemExit(1)

            # Compute rating
            rating = compute_grade_level_rating(
                model_id=model_data["id"],
                run_id=run["id"],
                task_results=results,
                threshold=threshold,
            )

            if fmt == "json":
                console.print(json.dumps(rating.to_dict(), indent=2))
                return

            # Display table
            console.print(f"\n[bold]Grade-Level Assessment: {model_data['name']}[/bold]")
            console.print(f"  Run: {run['id'][:8]}  |  Threshold: {threshold}%\n")

            table = Table()
            table.add_column("Tier", style="bold")
            table.add_column("Score", justify="right")
            table.add_column("Status")
            table.add_column("Tasks", justify="right")

            for tier in TIER_ORDER:
                tier_key = tier.value
                score = rating.tier_scores.get(tier_key)
                if score is None:
                    continue

                passed = score >= threshold
                status = "[green]PASS[/green]" if passed else "[red]FAIL[/red]"
                tasks = rating.tier_details.get(tier_key, [])

                table.add_row(
                    TIER_LABELS.get(tier, tier_key),
                    f"{score:.1f}%",
                    status,
                    str(len(tasks)),
                )

            console.print(table)

            # Summary
            max_tier = rating.max_passing_tier
            if max_tier:
                tier_label = TIER_LABELS.get(
                    next((t for t in TIER_ORDER if t.value == max_tier), None),
                    max_tier,
                )
                console.print(f"\n  [bold green]Maximum Passing Tier: {tier_label}[/bold green]")
            else:
                console.print(f"\n  [bold red]No tiers passed at {threshold}% threshold[/bold red]")

            if rating.overall_education_score is not None:
                console.print(f"  Overall Education Score: {rating.overall_education_score:.1f}%")

        finally:
            await storage.close()

    run_sync(_grade())
