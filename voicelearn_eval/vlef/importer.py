"""Import evaluation results from VLEF format."""

from voicelearn_eval.storage.base import BaseStorage


async def import_vlef(
    storage: BaseStorage,
    data: dict,
    merge: bool = False,
) -> dict:
    """Import VLEF data into storage.

    Args:
        storage: Storage backend
        data: Parsed VLEF JSON data
        merge: If True, merge with existing data; if False, skip duplicates

    Returns:
        Summary dict with import counts
    """
    summary = {
        "models_imported": 0,
        "runs_imported": 0,
        "results_imported": 0,
        "skipped": 0,
    }

    # Import models
    for model in data.get("models", []):
        existing = await storage.get_model(model.get("id", ""))
        if existing and not merge:
            summary["skipped"] += 1
            continue

        if not existing:
            await storage.create_model(model)
            summary["models_imported"] += 1

    # Import suites (skip built-ins, they should already exist)
    for suite in data.get("suites", []):
        if suite.get("is_builtin"):
            continue
        existing = await storage.get_suite(suite.get("id", ""))
        if existing:
            summary["skipped"] += 1
            continue
        tasks = suite.pop("tasks", [])
        suite_id = await storage.create_suite(suite)
        for task in tasks:
            task["suite_id"] = suite_id
            await storage.create_task(task)

    # Import runs and results
    for run in data.get("runs", []):
        existing = await storage.get_run(run.get("id", ""))
        if existing and not merge:
            summary["skipped"] += 1
            continue

        if not existing:
            results = run.pop("results", [])
            run_id = await storage.create_run(run)
            summary["runs_imported"] += 1

            for result in results:
                result["run_id"] = run_id
                await storage.create_task_result(result)
                summary["results_imported"] += 1

    return summary
