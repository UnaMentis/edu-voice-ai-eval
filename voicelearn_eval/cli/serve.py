"""voicelearn-eval serve: Start API + web dashboard."""

import click
from rich.console import Console

console = Console()


@click.command("serve")
@click.option("--port", default=3201, type=int, help="API server port")
@click.option("--web-port", default=3200, type=int, help="Web dashboard port")
@click.option("--host", default="127.0.0.1", help="Bind host")
@click.option("--no-web", is_flag=True, help="API server only, no web dashboard")
@click.option("--reload", "dev_reload", is_flag=True, help="Auto-reload for development")
@click.option("--db", type=click.Path(), help="Database path")
@click.pass_context
def serve_cmd(ctx, port, web_port, host, no_web, dev_reload, db):
    """Start the API server and web dashboard."""
    import os
    import subprocess
    from pathlib import Path

    console.print("\n[bold]VoiceLearn Eval Server[/bold]")
    console.print(f"  API:       http://{host}:{port}")
    console.print(f"  API Docs:  http://{host}:{port}/docs")

    web_process = None
    if not no_web:
        web_dir = Path(__file__).parent.parent.parent / "web"
        if web_dir.exists() and (web_dir / "package.json").exists():
            console.print(f"  Dashboard: http://{host}:{web_port}")
            web_process = subprocess.Popen(
                ["npx", "next", "dev", "--port", str(web_port)],
                cwd=str(web_dir),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            console.print("  [dim]Dashboard not available (web/ directory not found)[/dim]")

    console.print()

    try:
        import uvicorn

        # Set DB path via environment if provided
        if db:
            os.environ["VOICELEARN_EVAL_DB_PATH"] = db

        uvicorn.run(
            "voicelearn_eval.api.app:create_app",
            host=host,
            port=port,
            reload=dev_reload,
            factory=True,
        )
    except ImportError:
        console.print("[red]uvicorn not installed. Run: pip install uvicorn[/red]")
        raise SystemExit(1)
    finally:
        if web_process:
            web_process.terminate()
