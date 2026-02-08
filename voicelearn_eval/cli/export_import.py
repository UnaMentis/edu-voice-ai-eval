"""voicelearn-eval export/import: VLEF format operations."""

import json

import click
from rich.console import Console

from ._helpers import get_initialized_storage, run_sync

console = Console()


@click.command("export")
@click.option("--run", "run_id", help="Run ID to export")
@click.option("--all", "export_all", is_flag=True, help="Export all results")
@click.option("--model", "model_id", help="Export all results for a model")
@click.option("--format", "fmt", default="vlef", help="Format (vlef, json, csv)")
@click.option("--output", "-o", required=True, type=click.Path(), help="Output file")
@click.pass_context
def export_cmd(ctx, run_id, export_all, model_id, fmt, output):
    """Export evaluation results."""
    from voicelearn_eval.vlef.exporter import export_vlef

    async def _export():
        storage, _ = await get_initialized_storage(
            ctx.obj.get("config_path"), ctx.obj.get("db_path")
        )
        try:
            data = await export_vlef(
                storage,
                run_ids=[run_id] if run_id else None,
                model_id=model_id,
                export_all=export_all,
            )

            with open(output, "w") as f:
                json.dump(data, f, indent=2)

            console.print(f"[green]Exported to:[/green] {output}")

        finally:
            await storage.close()

    run_sync(_export())


@click.command("import")
@click.option("--file", "-f", "file_path", required=True, type=click.Path(exists=True), help="VLEF file to import")
@click.option("--merge", is_flag=True, help="Merge with existing data")
@click.pass_context
def import_cmd(ctx, file_path, merge):
    """Import evaluation results from VLEF format."""
    from voicelearn_eval.vlef.importer import import_vlef

    async def _import():
        storage, _ = await get_initialized_storage(
            ctx.obj.get("config_path"), ctx.obj.get("db_path")
        )
        try:
            with open(file_path) as f:
                data = json.load(f)

            summary = await import_vlef(storage, data, merge=merge)
            console.print(f"[green]Imported:[/green] {file_path}")
            console.print(f"  Models:  {summary.get('models_imported', 0)}")
            console.print(f"  Runs:    {summary.get('runs_imported', 0)}")
            console.print(f"  Skipped: {summary.get('skipped', 0)}")

        finally:
            await storage.close()

    run_sync(_import())
