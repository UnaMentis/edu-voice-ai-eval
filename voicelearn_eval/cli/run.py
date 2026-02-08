"""voicelearn-eval run: Execute evaluations."""

import click
from rich.console import Console

from ._helpers import get_orchestrator, run_sync

console = Console()


@click.command("run")
@click.option("--model", required=True, help="Model ID, slug, HF repo, or path")
@click.option("--suite", "suite_slug", help="Predefined suite slug")
@click.option("--benchmark", multiple=True, help="Specific benchmark IDs")
@click.option("--gpu", default="auto", help="GPU device (cuda:0, mps, cpu, auto)")
@click.option("--batch-size", default=8, type=int, help="Batch size")
@click.option("--output", type=click.Path(), help="Output directory")
@click.option("--format", "output_format", default="json", help="Output format (json, csv, vlef)")
@click.option("--ci", is_flag=True, help="CI mode: exit non-zero on failure")
@click.option("--timeout", default=3600, type=int, help="Timeout per benchmark (seconds)")
@click.option("--quiet", is_flag=True, help="Suppress progress output")
@click.option("--priority", default=5, type=int, help="Queue priority (0=low, 10=urgent)")
@click.pass_context
def run_cmd(ctx, model, suite_slug, benchmark, gpu, batch_size, output, output_format, ci, timeout, quiet, priority):
    """Run an evaluation on a model."""
    if not suite_slug and not benchmark:
        console.print("[red]Error: Specify --suite or --benchmark[/red]")
        raise SystemExit(3)

    async def _run():
        orchestrator, storage, config = await get_orchestrator(
            ctx.obj.get("config_path"), ctx.obj.get("db_path")
        )

        try:
            # Resolve model: try ID first, then slug
            model_data = await storage.get_model(model)
            if not model_data:
                model_data = await storage.get_model_by_slug(model)
            if not model_data:
                console.print(f"[red]Error: Model not found: {model}[/red]")
                raise SystemExit(4)

            # Resolve suite
            suite = None
            if suite_slug:
                suite = await storage.get_suite_by_slug(suite_slug)
                if not suite:
                    console.print(f"[red]Error: Suite not found: {suite_slug}[/red]")
                    raise SystemExit(3)

            if not suite:
                console.print("[red]Error: No suite specified[/red]")
                raise SystemExit(3)

            eval_config = {
                "gpu_device": gpu,
                "batch_size": batch_size,
                "timeout": timeout,
            }

            if not quiet:
                console.print("\n[bold]Running evaluation[/bold]")
                console.print(f"  Model: {model_data['name']}")
                console.print(f"  Suite: {suite['name']}")
                console.print(f"  GPU:   {gpu}")
                console.print()

            run_id = await orchestrator.start_evaluation(
                model_id=model_data["id"],
                suite_id=suite["id"],
                config=eval_config,
                priority=priority,
            )

            # Get results
            run_data = await storage.get_run(run_id)
            results = await storage.get_results_for_run(run_id)

            if not quiet:
                console.print("\n[green]Evaluation complete![/green]")
                console.print(f"  Run ID: {run_id}")
                console.print(f"  Score:  {run_data.get('overall_score', 'N/A')}")
                console.print(f"  Status: {run_data.get('status', 'unknown')}")

                if results:
                    console.print(f"\n  Tasks completed: {len(results)}")
                    for r in results:
                        score = r.get("score")
                        name = r.get("task_name", r.get("task_id", "?"))
                        status_icon = "[green]✓[/green]" if r.get("status") == "completed" else "[red]✗[/red]"
                        score_str = f"{score:.1f}" if score is not None else "N/A"
                        console.print(f"    {status_icon} {name}: {score_str}")

            # CI mode: check score
            if ci:
                score = run_data.get("overall_score", 0)
                if score < config.ci_min_score:
                    if not quiet:
                        console.print(f"\n[red]CI FAIL: Score {score:.1f} < threshold {config.ci_min_score}[/red]")
                    raise SystemExit(1)

        finally:
            await storage.close()

    run_sync(_run())
