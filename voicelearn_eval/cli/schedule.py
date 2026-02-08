"""voicelearn-eval schedule: Recurring evaluations."""

import click
from rich.console import Console

console = Console()


@click.group("schedule")
@click.pass_context
def schedule_cmd(ctx):
    """Manage recurring evaluations."""
    pass


@schedule_cmd.command("list")
@click.pass_context
def schedule_list(ctx):
    """List all schedules."""
    from ._helpers import get_initialized_storage, run_sync

    async def _list():
        storage, _ = await get_initialized_storage(
            ctx.obj.get("config_path"), ctx.obj.get("db_path")
        )
        try:
            schedules = await storage.list_schedules()
            if not schedules:
                console.print("[dim]No schedules configured.[/dim]")
                return

            from rich.table import Table
            table = Table(title="Evaluation Schedules")
            table.add_column("ID", style="dim", max_width=8)
            table.add_column("Name", style="bold")
            table.add_column("Type")
            table.add_column("Cron")
            table.add_column("Active")

            for s in schedules:
                table.add_row(
                    s["id"][:8],
                    s["name"],
                    s.get("schedule_type", "?"),
                    s.get("cron_expression", "-"),
                    "✓" if s.get("is_active") else "",
                )
            console.print(table)

        finally:
            await storage.close()

    run_sync(_list())


@schedule_cmd.command("create")
@click.option("--name", required=True, help="Schedule name")
@click.option("--suite", required=True, help="Suite slug")
@click.option("--cron", required=True, help='Cron expression (e.g. "0 0 * * SUN")')
@click.option("--model", "model_id", help="Specific model ID (omit for all)")
@click.pass_context
def schedule_create(ctx, name, suite, cron, model_id):
    """Create a recurring evaluation schedule."""
    from ._helpers import get_initialized_storage, run_sync

    async def _create():
        storage, _ = await get_initialized_storage(
            ctx.obj.get("config_path"), ctx.obj.get("db_path")
        )
        try:
            suite_data = await storage.get_suite_by_slug(suite)
            if not suite_data:
                console.print(f"[red]Suite not found: {suite}[/red]")
                raise SystemExit(1)

            schedule_id = await storage.create_schedule({
                "name": name,
                "suite_id": suite_data["id"],
                "schedule_type": "cron",
                "cron_expression": cron,
                "model_id": model_id,
            })
            console.print(f"[green]Schedule created:[/green] {name} (ID: {schedule_id[:8]})")

        finally:
            await storage.close()

    run_sync(_create())
