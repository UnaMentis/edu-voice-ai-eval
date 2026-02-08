"""voicelearn-eval compare: Compare models."""

import click
from rich.console import Console

console = Console()


@click.command("compare")
@click.option("--models", required=True, help="Comma-separated model IDs (2-5)")
@click.option("--suite", help="Suite to compare on")
@click.option("--format", "fmt", default="table", help="Output format (table, json)")
@click.pass_context
def compare_cmd(ctx, models, suite, fmt):
    """Compare 2-5 models side by side."""

    from ._helpers import get_initialized_storage, run_sync

    model_ids = [m.strip() for m in models.split(",")]
    if len(model_ids) < 2 or len(model_ids) > 5:
        console.print("[red]Error: Provide 2-5 model IDs separated by commas[/red]")
        raise SystemExit(3)

    async def _compare():
        storage, _ = await get_initialized_storage(
            ctx.obj.get("config_path"), ctx.obj.get("db_path")
        )
        try:
            from rich.table import Table

            table = Table(title="Model Comparison")
            table.add_column("Metric", style="bold")

            resolved_models = []
            for mid in model_ids:
                m = await storage.get_model(mid) or await storage.get_model_by_slug(mid)
                if not m:
                    console.print(f"[red]Model not found: {mid}[/red]")
                    raise SystemExit(4)
                resolved_models.append(m)
                table.add_column(m["name"][:20])

            # Get latest runs for each model
            for m in resolved_models:
                runs = await storage.list_runs(
                    filters={"model_id": m["id"], "status": "completed"}, limit=1
                )
                m["_latest_run"] = runs[0] if runs else None

            # Score row
            scores = []
            for m in resolved_models:
                run = m.get("_latest_run")
                scores.append(f"{run['overall_score']:.1f}" if run and run.get("overall_score") else "N/A")
            table.add_row("Overall Score", *scores)

            # Type row
            table.add_row("Type", *[m["model_type"] for m in resolved_models])

            # Parameters row
            table.add_row(
                "Parameters",
                *[
                    f"{m.get('parameter_count_b', '?')}B" if m.get("parameter_count_b") else "-"
                    for m in resolved_models
                ],
            )

            console.print(table)

        finally:
            await storage.close()

    run_sync(_compare())
