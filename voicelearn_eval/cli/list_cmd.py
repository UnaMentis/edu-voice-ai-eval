"""voicelearn-eval list: List resources."""

import json

import click
from rich.console import Console
from rich.table import Table

from ._helpers import get_initialized_storage, get_plugin_registry, run_sync

console = Console()


@click.group("list")
@click.pass_context
def list_cmd(ctx):
    """List models, benchmarks, runs, suites, or plugins."""
    pass


@list_cmd.command("models")
@click.option("--type", "model_type", help="Filter by type (llm, stt, tts)")
@click.option("--format", "fmt", default="table", help="Output format (table, json)")
@click.option("--limit", default=20, type=int, help="Max results")
@click.pass_context
def list_models(ctx, model_type, fmt, limit):
    """List registered models."""

    async def _list():
        storage, _ = await get_initialized_storage(
            ctx.obj.get("config_path"), ctx.obj.get("db_path")
        )
        try:
            filters = {}
            if model_type:
                filters["model_type"] = model_type
            models = await storage.list_models(filters=filters, limit=limit)

            if fmt == "json":
                console.print(json.dumps(models, indent=2))
                return

            table = Table(title="Registered Models")
            table.add_column("ID", style="dim", max_width=8)
            table.add_column("Name", style="bold")
            table.add_column("Type", style="cyan")
            table.add_column("Source")
            table.add_column("Target")
            table.add_column("Params", justify="right")
            table.add_column("Size", justify="right")

            for m in models:
                params = f"{m.get('parameter_count_b', '?')}B" if m.get("parameter_count_b") else "-"
                size = f"{m.get('model_size_gb', '?')}GB" if m.get("model_size_gb") else "-"
                table.add_row(
                    m["id"][:8],
                    m["name"],
                    m["model_type"],
                    m["source_type"],
                    m.get("deployment_target", "-"),
                    params,
                    size,
                )

            if not models:
                console.print("[dim]No models registered. Use 'voicelearn-eval model add' to register one.[/dim]")
            else:
                console.print(table)
        finally:
            await storage.close()

    run_sync(_list())


@list_cmd.command("suites")
@click.option("--type", "model_type", help="Filter by model type")
@click.option("--format", "fmt", default="table", help="Output format (table, json)")
@click.pass_context
def list_suites(ctx, model_type, fmt):
    """List benchmark suites."""

    async def _list():
        storage, _ = await get_initialized_storage(
            ctx.obj.get("config_path"), ctx.obj.get("db_path")
        )
        try:
            filters = {}
            if model_type:
                filters["model_type"] = model_type
            suites = await storage.list_suites(filters=filters)

            if fmt == "json":
                console.print(json.dumps(suites, indent=2))
                return

            table = Table(title="Benchmark Suites")
            table.add_column("Slug", style="bold")
            table.add_column("Name")
            table.add_column("Type", style="cyan")
            table.add_column("Category")
            table.add_column("Tasks", justify="right")
            table.add_column("Built-in")

            for s in suites:
                table.add_row(
                    s.get("slug", "?"),
                    s["name"],
                    s["model_type"],
                    s.get("category", "-"),
                    str(s.get("task_count", 0)),
                    "✓" if s.get("is_builtin") else "",
                )

            console.print(table)
        finally:
            await storage.close()

    run_sync(_list())


@list_cmd.command("runs")
@click.option("--status", help="Filter by status")
@click.option("--model", "model_id", help="Filter by model ID")
@click.option("--limit", default=20, type=int, help="Max results")
@click.option("--format", "fmt", default="table", help="Output format (table, json)")
@click.pass_context
def list_runs(ctx, status, model_id, limit, fmt):
    """List evaluation runs."""

    async def _list():
        storage, _ = await get_initialized_storage(
            ctx.obj.get("config_path"), ctx.obj.get("db_path")
        )
        try:
            filters = {}
            if status:
                filters["status"] = status
            if model_id:
                filters["model_id"] = model_id
            runs = await storage.list_runs(filters=filters, limit=limit)

            if fmt == "json":
                console.print(json.dumps(runs, indent=2))
                return

            table = Table(title="Evaluation Runs")
            table.add_column("ID", style="dim", max_width=8)
            table.add_column("Model", max_width=20)
            table.add_column("Suite")
            table.add_column("Status")
            table.add_column("Score", justify="right")
            table.add_column("Created")

            for r in runs:
                status_style = {
                    "completed": "[green]completed[/green]",
                    "running": "[blue]running[/blue]",
                    "failed": "[red]failed[/red]",
                    "pending": "[dim]pending[/dim]",
                    "cancelled": "[yellow]cancelled[/yellow]",
                }.get(r.get("status", ""), r.get("status", ""))

                score = f"{r['overall_score']:.1f}" if r.get("overall_score") is not None else "-"
                created = r.get("created_at", "")[:19]

                table.add_row(
                    r["id"][:8],
                    r.get("model_id", "?")[:20],
                    r.get("suite_id", "?")[:15],
                    status_style,
                    score,
                    created,
                )

            if not runs:
                console.print("[dim]No runs found. Use 'voicelearn-eval run' to start one.[/dim]")
            else:
                console.print(table)
        finally:
            await storage.close()

    run_sync(_list())


@list_cmd.command("benchmarks")
@click.option("--format", "fmt", default="table", help="Output format (table, json)")
@click.pass_context
def list_benchmarks(ctx, fmt):
    """List all available benchmarks from all plugins."""
    registry = get_plugin_registry()
    benchmarks = registry.get_all_benchmarks()

    if fmt == "json":
        console.print(json.dumps(benchmarks, indent=2))
        return

    table = Table(title="Available Benchmarks")
    table.add_column("ID", style="bold")
    table.add_column("Name")
    table.add_column("Plugin")
    table.add_column("Subject")

    for b in benchmarks:
        table.add_row(
            b.get("id", "?"),
            b.get("name", "?"),
            b.get("plugin_id", "?"),
            b.get("subject", "-"),
        )

    console.print(table)


@list_cmd.command("plugins")
@click.pass_context
def list_plugins(ctx):
    """List installed evaluation plugins."""
    registry = get_plugin_registry()
    plugins = registry.get_all_plugins()

    table = Table(title="Installed Plugins")
    table.add_column("ID", style="bold")
    table.add_column("Name")
    table.add_column("Type", style="cyan")
    table.add_column("Version")
    table.add_column("Benchmarks", justify="right")
    table.add_column("GPU")

    for plugin_id, plugin in plugins.items():
        info = plugin.get_plugin_info()
        table.add_row(
            info.plugin_id,
            info.name,
            info.plugin_type.value,
            info.version,
            str(len(info.supported_benchmarks)),
            "✓" if info.requires_gpu else "",
        )

    console.print(table)
