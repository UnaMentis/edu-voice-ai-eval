"""Top-level CLI group for voicelearn-eval."""

import click

from voicelearn_eval import __version__


@click.group()
@click.version_option(version=__version__)
@click.option("--config", type=click.Path(exists=True), help="YAML config file")
@click.option("--db", type=click.Path(), help="Database path override")
@click.pass_context
def cli(ctx, config, db):
    """UnaMentis Voice Learning AI Eval Suite.

    Evaluate AI models for educational voice interaction across
    LLM, STT, and TTS modalities with grade-level scoring.
    """
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config
    ctx.obj["db_path"] = db


# Import and register subcommands
from .compare import compare_cmd  # noqa: E402
from .export_import import export_cmd, import_cmd  # noqa: E402
from .grade import grade_cmd  # noqa: E402
from .list_cmd import list_cmd  # noqa: E402
from .model import model_cmd  # noqa: E402
from .plugin import plugin_cmd  # noqa: E402
from .run import run_cmd  # noqa: E402
from .schedule import schedule_cmd  # noqa: E402
from .serve import serve_cmd  # noqa: E402
from .suite import suite_cmd  # noqa: E402

cli.add_command(run_cmd, "run")
cli.add_command(list_cmd, "list")
cli.add_command(grade_cmd, "grade")
cli.add_command(compare_cmd, "compare")
cli.add_command(model_cmd, "model")
cli.add_command(suite_cmd, "suite")
cli.add_command(export_cmd, "export")
cli.add_command(import_cmd, "import")
cli.add_command(serve_cmd, "serve")
cli.add_command(plugin_cmd, "plugin")
cli.add_command(schedule_cmd, "schedule")
