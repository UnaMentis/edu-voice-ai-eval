"""voicelearn-eval model: Model registry management."""

import re

import click
from rich.console import Console

from ._helpers import get_initialized_storage, run_sync

console = Console()


def _slugify(name: str) -> str:
    """Convert name to a URL-friendly slug."""
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


@click.group("model")
@click.pass_context
def model_cmd(ctx):
    """Manage model registry."""
    pass


@model_cmd.command("add")
@click.option("--name", required=True, help="Model display name")
@click.option("--type", "model_type", required=True, type=click.Choice(["llm", "stt", "tts", "vad", "embeddings"]))
@click.option("--source", "source_type", required=True, type=click.Choice(["huggingface", "local", "api", "ollama"]))
@click.option("--uri", help="Source URI (HF repo, path, or API endpoint)")
@click.option(
    "--target", "deployment_target", default="server",
    type=click.Choice(["on-device", "server", "cloud-api"]),
)
@click.option("--family", help="Model family (e.g. qwen, whisper)")
@click.option("--version", "model_version", help="Model version")
@click.option("--params", "parameter_count_b", type=float, help="Parameters (billions)")
@click.option("--size", "model_size_gb", type=float, help="Size (GB)")
@click.option("--quantization", help="Quantization (e.g. Q4_K_M, INT8)")
@click.option("--context", "context_window", type=int, help="Context window size")
@click.option("--reference", is_flag=True, help="Mark as reference model")
@click.pass_context
def add_model(ctx, name, model_type, source_type, uri, deployment_target, family,
              model_version, parameter_count_b, model_size_gb, quantization,
              context_window, reference):
    """Register a new model for evaluation."""

    async def _add():
        storage, _ = await get_initialized_storage(
            ctx.obj.get("config_path"), ctx.obj.get("db_path")
        )
        try:
            slug = _slugify(name)

            # Check for duplicate
            existing = await storage.get_model_by_slug(slug)
            if existing:
                console.print(f"[red]Error: Model with slug '{slug}' already exists[/red]")
                raise SystemExit(1)

            model_data = {
                "name": name,
                "slug": slug,
                "model_type": model_type,
                "source_type": source_type,
                "source_uri": uri,
                "deployment_target": deployment_target,
                "model_family": family,
                "model_version": model_version,
                "parameter_count_b": parameter_count_b,
                "model_size_gb": model_size_gb,
                "quantization": quantization,
                "context_window": context_window,
                "is_reference": reference,
            }

            model_id = await storage.create_model(model_data)
            console.print(f"[green]Model registered:[/green] {name}")
            console.print(f"  ID:   {model_id}")
            console.print(f"  Slug: {slug}")

        finally:
            await storage.close()

    run_sync(_add())


@model_cmd.command("import-hf")
@click.argument("repo_id")
@click.option("--type", "model_type", required=True, type=click.Choice(["llm", "stt", "tts"]))
@click.option(
    "--target", "deployment_target", default="server",
    type=click.Choice(["on-device", "server", "cloud-api"]),
)
@click.pass_context
def import_hf(ctx, repo_id, model_type, deployment_target):
    """Import a model from HuggingFace Hub."""

    async def _import():
        storage, _ = await get_initialized_storage(
            ctx.obj.get("config_path"), ctx.obj.get("db_path")
        )
        try:
            try:
                from huggingface_hub import HfApi

                api = HfApi()
                model_info = api.model_info(repo_id)

                name = model_info.modelId.split("/")[-1]
                slug = _slugify(name)

                model_data = {
                    "name": name,
                    "slug": slug,
                    "model_type": model_type,
                    "source_type": "huggingface",
                    "source_uri": repo_id,
                    "deployment_target": deployment_target,
                    "model_family": repo_id.split("/")[0] if "/" in repo_id else None,
                    "tags": list(model_info.tags) if model_info.tags else [],
                    "languages": (
                        list(model_info.languages)
                        if hasattr(model_info, "languages") and model_info.languages
                        else []
                    ),
                }

                # Try to extract parameter count
                if hasattr(model_info, "safetensors") and model_info.safetensors:
                    params = model_info.safetensors.get("total", 0)
                    if params:
                        model_data["parameter_count_b"] = round(params / 1e9, 2)

                model_id = await storage.create_model(model_data)
                console.print(f"[green]Imported from HuggingFace:[/green] {repo_id}")
                console.print(f"  ID:   {model_id}")
                console.print(f"  Name: {name}")

            except ImportError:
                console.print("[red]huggingface-hub not installed. Run: pip install huggingface-hub[/red]")
                raise SystemExit(1)

        finally:
            await storage.close()

    run_sync(_import())


@model_cmd.command("remove")
@click.argument("model_id")
@click.option("--force", is_flag=True, help="Skip confirmation")
@click.pass_context
def remove_model(ctx, model_id, force):
    """Remove a model from the registry (soft delete)."""

    async def _remove():
        storage, _ = await get_initialized_storage(
            ctx.obj.get("config_path"), ctx.obj.get("db_path")
        )
        try:
            model = await storage.get_model(model_id)
            if not model:
                model = await storage.get_model_by_slug(model_id)
            if not model:
                console.print(f"[red]Model not found: {model_id}[/red]")
                raise SystemExit(4)

            if not force:
                if not click.confirm(f"Remove model '{model['name']}'?"):
                    return

            await storage.delete_model(model["id"])
            console.print(f"[green]Removed:[/green] {model['name']}")

        finally:
            await storage.close()

    run_sync(_remove())


@model_cmd.command("info")
@click.argument("model_id")
@click.pass_context
def model_info(ctx, model_id):
    """Show detailed model information."""

    async def _info():
        storage, _ = await get_initialized_storage(
            ctx.obj.get("config_path"), ctx.obj.get("db_path")
        )
        try:
            model = await storage.get_model(model_id)
            if not model:
                model = await storage.get_model_by_slug(model_id)
            if not model:
                console.print(f"[red]Model not found: {model_id}[/red]")
                raise SystemExit(4)

            console.print(f"\n[bold]{model['name']}[/bold]")
            console.print(f"  ID:         {model['id']}")
            console.print(f"  Slug:       {model['slug']}")
            console.print(f"  Type:       {model['model_type']}")
            console.print(f"  Source:     {model['source_type']}")
            console.print(f"  URI:        {model.get('source_uri', '-')}")
            console.print(f"  Target:     {model.get('deployment_target', '-')}")
            console.print(f"  Family:     {model.get('model_family', '-')}")
            console.print(f"  Parameters: {model.get('parameter_count_b', '-')}B")
            console.print(f"  Size:       {model.get('model_size_gb', '-')}GB")
            console.print(f"  Quant:      {model.get('quantization', '-')}")
            console.print(f"  Context:    {model.get('context_window', '-')}")
            console.print(f"  Reference:  {'Yes' if model.get('is_reference') else 'No'}")
            console.print(f"  Created:    {model.get('created_at', '-')}")

        finally:
            await storage.close()

    run_sync(_info())
