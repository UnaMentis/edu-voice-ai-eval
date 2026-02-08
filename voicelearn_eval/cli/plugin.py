"""voicelearn-eval plugin: Plugin management."""

import click
from rich.console import Console

console = Console()


@click.group("plugin")
@click.pass_context
def plugin_cmd(ctx):
    """Manage evaluation plugins."""
    pass


@plugin_cmd.command("list")
@click.pass_context
def plugin_list(ctx):
    """List installed plugins (alias for 'voicelearn-eval list plugins')."""
    from .list_cmd import list_plugins
    ctx.invoke(list_plugins)


@plugin_cmd.command("info")
@click.argument("plugin_id")
@click.pass_context
def plugin_info(ctx, plugin_id):
    """Show detailed plugin information."""
    from ._helpers import get_plugin_registry

    registry = get_plugin_registry()
    plugin = registry.get_plugin(plugin_id)

    if not plugin:
        console.print(f"[red]Plugin not found: {plugin_id}[/red]")
        raise SystemExit(1)

    info = plugin.get_plugin_info()
    console.print(f"\n[bold]{info.name}[/bold]")
    console.print(f"  ID:       {info.plugin_id}")
    console.print(f"  Version:  {info.version}")
    console.print(f"  Type:     {info.plugin_type.value}")
    console.print(f"  GPU:      {'Required' if info.requires_gpu else 'Optional'}")
    console.print(f"  Upstream: {info.upstream_project}")
    console.print(f"  URL:      {info.upstream_url}")
    console.print(f"  License:  {info.upstream_license}")
    console.print(f"\n  {info.description}")
    console.print(f"\n  Supported benchmarks: {len(info.supported_benchmarks)}")
