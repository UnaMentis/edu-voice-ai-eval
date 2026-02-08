"""Evaluation pipeline orchestrator."""

import logging
import platform
import sys
import traceback
from collections.abc import Callable
from datetime import datetime

from voicelearn_eval.grade_levels.scorer import compute_grade_level_rating
from voicelearn_eval.plugins.base import PluginRegistry, ProgressUpdate
from voicelearn_eval.storage.base import BaseStorage

logger = logging.getLogger(__name__)


def _now() -> str:
    return datetime.utcnow().isoformat()


def _get_hardware_info() -> dict:
    """Collect hardware information for reproducibility."""
    import os

    info = {
        "platform": platform.platform(),
        "python_version": sys.version,
        "cpu_count": os.cpu_count(),
    }

    try:
        import torch

        if torch.cuda.is_available():
            info["gpu"] = torch.cuda.get_device_name(0)
            info["gpu_memory_gb"] = round(
                torch.cuda.get_device_properties(0).total_mem / 1e9, 1
            )
            info["cuda_version"] = torch.version.cuda
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            info["gpu"] = "Apple Silicon (MPS)"
        else:
            info["gpu"] = "None (CPU only)"
    except ImportError:
        info["gpu"] = "Unknown (torch not installed)"

    return info


class EvalOrchestrator:
    """Central coordinator for evaluation runs."""

    def __init__(self, storage: BaseStorage, plugin_registry: PluginRegistry):
        self.storage = storage
        self.registry = plugin_registry
        self._progress_listeners: list[Callable] = []

    async def start_evaluation(
        self,
        model_id: str,
        suite_id: str,
        config: dict | None = None,
        priority: int = 5,
        triggered_by: str = "manual",
    ) -> str:
        """Create and execute an evaluation run. Returns run_id."""
        config = config or {}

        # Validate model exists
        model = await self.storage.get_model(model_id)
        if not model:
            raise ValueError(f"Model not found: {model_id}")

        # Validate suite exists
        suite = await self.storage.get_suite(suite_id)
        if not suite:
            raise ValueError(f"Suite not found: {suite_id}")

        # Find plugin for model type
        plugin = self.registry.find_plugin_for_model_type(model["model_type"])
        if not plugin:
            raise ValueError(
                f"No plugin found for model type: {model['model_type']}"
            )

        # Validate model with plugin
        is_valid, msg = plugin.validate_model(model)
        if not is_valid:
            raise ValueError(f"Model validation failed: {msg}")

        # Get tasks
        tasks = await self.storage.get_tasks_for_suite(suite_id)
        if not tasks:
            raise ValueError(f"Suite has no tasks: {suite_id}")

        # Create run record
        run_id = await self.storage.create_run(
            {
                "model_id": model_id,
                "suite_id": suite_id,
                "run_config": config,
                "tasks_total": len(tasks),
                "triggered_by": triggered_by,
                "hardware_info": _get_hardware_info(),
            }
        )

        # Execute the run
        try:
            await self._execute_run(run_id, model, suite, tasks, plugin, config)
        except Exception as e:
            logger.error(f"Run {run_id} failed: {e}")
            await self.storage.update_run(
                run_id,
                {
                    "status": "failed",
                    "error_message": str(e),
                    "error_traceback": traceback.format_exc(),
                    "completed_at": _now(),
                },
            )

        return run_id

    async def _execute_run(
        self,
        run_id: str,
        model: dict,
        suite: dict,
        tasks: list[dict],
        plugin,
        config: dict,
    ) -> None:
        """Execute a single evaluation run."""
        # Update status to running
        await self.storage.update_run(
            run_id,
            {
                "status": "running",
                "started_at": _now(),
            },
        )

        # Prepare benchmark IDs from tasks
        import json

        all_task_results = []

        for i, task in enumerate(tasks):
            task_config = task.get("config", {})
            if isinstance(task_config, str):
                task_config = json.loads(task_config) if task_config else {}

            # Get lm-eval task names from config
            lm_eval_tasks = task_config.get("lm_eval_tasks", [])
            benchmark_ids = lm_eval_tasks if lm_eval_tasks else [task["name"]]

            # Build per-task config
            eval_config = dict(config)
            eval_config["education_tier"] = task.get("education_tier", "")

            # Progress callback
            async def on_progress(task_name, idx, total, message):
                percent = ((i + idx / max(total, 1)) / len(tasks)) * 100
                update = ProgressUpdate(
                    run_id=run_id,
                    task_name=task_name,
                    task_index=i,
                    total_tasks=len(tasks),
                    percent_complete=percent,
                    message=message,
                )
                await self._notify_progress(run_id, update)
                await self.storage.update_run(
                    run_id,
                    {
                        "progress_percent": percent,
                        "current_task": task.get("name", task_name),
                        "tasks_completed": i,
                    },
                )

            # Run evaluation for this task
            try:
                results = await plugin.run_evaluation(
                    model_spec=model,
                    benchmark_ids=benchmark_ids,
                    config=eval_config,
                    progress_callback=on_progress,
                )

                # Save results
                for result in results:
                    result["run_id"] = run_id
                    result["task_id"] = task["id"]
                    # Add task metadata for grade-level scoring
                    result["education_tier"] = task.get("education_tier")
                    result["weight"] = task.get("weight", 1.0)
                    result["task_name"] = task.get("name", "")

                    await self.storage.create_task_result(result)
                    all_task_results.append(result)

            except Exception as e:
                logger.error(f"Task {task['name']} failed: {e}")
                error_result = {
                    "run_id": run_id,
                    "task_id": task["id"],
                    "score": None,
                    "status": "failed",
                    "error_message": str(e),
                    "education_tier": task.get("education_tier"),
                    "weight": task.get("weight", 1.0),
                    "task_name": task.get("name", ""),
                }
                await self.storage.create_task_result(error_result)
                all_task_results.append(error_result)

        # Compute grade-level rating
        model_id = model["id"]
        rating = compute_grade_level_rating(
            model_id=model_id,
            run_id=run_id,
            task_results=all_task_results,
        )

        # Calculate overall score
        completed_results = [r for r in all_task_results if r.get("score") is not None]
        overall_score = (
            sum(r["score"] for r in completed_results) / len(completed_results)
            if completed_results
            else 0
        )

        # Update run as completed
        await self.storage.update_run(
            run_id,
            {
                "status": "completed",
                "overall_score": round(overall_score, 1),
                "overall_metrics": {
                    "grade_level": rating.to_dict(),
                    "tasks_completed": len(completed_results),
                    "tasks_failed": len(all_task_results) - len(completed_results),
                },
                "progress_percent": 100,
                "tasks_completed": len(tasks),
                "completed_at": _now(),
            },
        )

        # Notify completion
        await self._notify_progress(
            run_id,
            ProgressUpdate(
                run_id=run_id,
                task_name="Complete",
                task_index=len(tasks),
                total_tasks=len(tasks),
                percent_complete=100,
                message=f"Evaluation complete. Overall score: {overall_score:.1f}",
            ),
        )

    async def cancel_run(self, run_id: str) -> None:
        """Cancel a running evaluation."""
        run = await self.storage.get_run(run_id)
        if run and run["status"] in ("pending", "queued", "running"):
            await self.storage.update_run(
                run_id,
                {
                    "status": "cancelled",
                    "completed_at": _now(),
                },
            )

    def add_progress_listener(self, callback: Callable) -> None:
        """Register a callback for progress updates (used by WebSocket)."""
        self._progress_listeners.append(callback)

    def remove_progress_listener(self, callback: Callable) -> None:
        """Remove a progress listener."""
        self._progress_listeners = [
            cb for cb in self._progress_listeners if cb != callback
        ]

    async def _notify_progress(self, run_id: str, update: ProgressUpdate) -> None:
        """Broadcast progress to all listeners."""
        for listener in self._progress_listeners:
            try:
                await listener(run_id, update)
            except Exception as e:
                logger.warning(f"Progress listener error: {e}")
