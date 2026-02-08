"""Export evaluation results to VLEF (Voice Learning Eval Format)."""

import json
from datetime import datetime

from voicelearn_eval.core.models import VLEFExport
from voicelearn_eval.storage.base import BaseStorage


async def export_vlef(
    storage: BaseStorage,
    run_ids: list[str] | None = None,
    model_id: str | None = None,
    export_all: bool = False,
) -> dict:
    """Export evaluation results to VLEF format.

    Args:
        storage: Storage backend
        run_ids: Specific run IDs to export
        model_id: Export all runs for a model
        export_all: Export everything

    Returns:
        VLEF dict ready for JSON serialization
    """
    runs = []
    models_seen = set()
    suites_seen = set()

    # Gather runs
    if run_ids:
        for rid in run_ids:
            run = await storage.get_run(rid)
            if run:
                runs.append(run)
    elif model_id:
        runs = await storage.list_runs(filters={"model_id": model_id}, limit=1000)
    elif export_all:
        runs = await storage.list_runs(limit=1000)
    else:
        runs = await storage.list_runs(limit=100)

    # Gather related models and suites
    model_dicts = []
    suite_dicts = []

    for run in runs:
        mid = run.get("model_id")
        sid = run.get("suite_id")

        if mid and mid not in models_seen:
            m = await storage.get_model(mid)
            if m:
                model_dicts.append(m)
                models_seen.add(mid)

        if sid and sid not in suites_seen:
            s = await storage.get_suite(sid)
            if s:
                suite_dicts.append(s)
                suites_seen.add(sid)

    # Get results for each run
    run_dicts = []
    for run in runs:
        results = await storage.get_results_for_run(run["id"])
        run_dict = dict(run)
        run_dict["results"] = results
        # Parse JSON fields
        for key in ("overall_metrics", "run_config", "run_params", "hardware_info", "software_info"):
            if key in run_dict and isinstance(run_dict[key], str):
                try:
                    run_dict[key] = json.loads(run_dict[key])
                except (json.JSONDecodeError, TypeError):
                    pass
        run_dicts.append(run_dict)

    export = VLEFExport(
        format_version="1.0",
        exported_at=datetime.utcnow().isoformat(),
        runs=run_dicts,
        models=model_dicts,
        suites=suite_dicts,
        environment={
            "tool": "voicelearn-eval",
            "version": "0.1.0",
        },
        attribution={
            "project": "UnaMentis Voice Learning AI Eval Suite",
            "url": "https://github.com/UnaMentis/edu-voice-ai-eval",
        },
    )

    return export.to_dict()
