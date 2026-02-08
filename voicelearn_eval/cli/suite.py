"""voicelearn-eval suite: Benchmark suite management."""

import click
from rich.console import Console

console = Console()


@click.group("suite")
@click.pass_context
def suite_cmd(ctx):
    """Manage benchmark suites."""
    pass


@suite_cmd.command("list")
@click.pass_context
def suite_list(ctx):
    """List benchmark suites (alias for 'voicelearn-eval list suites')."""
    from .list_cmd import list_suites
    ctx.invoke(list_suites)


@suite_cmd.command("info")
@click.argument("suite_slug")
@click.pass_context
def suite_info(ctx, suite_slug):
    """Show suite details and tasks."""
    from ._helpers import get_initialized_storage, run_sync

    async def _info():
        storage, _ = await get_initialized_storage(
            ctx.obj.get("config_path"), ctx.obj.get("db_path")
        )
        try:
            suite = await storage.get_suite_by_slug(suite_slug)
            if not suite:
                console.print(f"[red]Suite not found: {suite_slug}[/red]")
                raise SystemExit(1)

            console.print(f"\n[bold]{suite['name']}[/bold]")
            console.print(f"  Slug:     {suite.get('slug', '-')}")
            console.print(f"  Type:     {suite['model_type']}")
            console.print(f"  Category: {suite.get('category', '-')}")
            console.print(f"  Built-in: {'Yes' if suite.get('is_builtin') else 'No'}")
            console.print(f"  {suite.get('description', '')}\n")

            tasks = suite.get("tasks", [])
            if tasks:
                from rich.table import Table
                table = Table(title=f"Tasks ({len(tasks)})")
                table.add_column("#", justify="right")
                table.add_column("Name", style="bold")
                table.add_column("Type")
                table.add_column("Tier")
                table.add_column("Subject")

                for i, t in enumerate(tasks):
                    table.add_row(
                        str(i + 1),
                        t.get("name", "?"),
                        t.get("task_type", "?"),
                        t.get("education_tier", "-"),
                        t.get("subject", "-"),
                    )
                console.print(table)

        finally:
            await storage.close()

    run_sync(_info())
