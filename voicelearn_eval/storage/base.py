"""Abstract storage interface for the evaluation system."""

from abc import ABC, abstractmethod


class BaseStorage(ABC):
    """Abstract base class for all storage backends."""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize storage (create tables, run migrations)."""

    @abstractmethod
    async def close(self) -> None:
        """Close storage connection."""

    # --- Models ---

    @abstractmethod
    async def create_model(self, model: dict) -> str:
        """Create a model record. Returns model ID."""

    @abstractmethod
    async def get_model(self, model_id: str) -> dict | None:
        """Get a model by ID."""

    @abstractmethod
    async def get_model_by_slug(self, slug: str) -> dict | None:
        """Get a model by slug."""

    @abstractmethod
    async def list_models(
        self, filters: dict | None = None, limit: int = 20, offset: int = 0
    ) -> list[dict]:
        """List models with optional filtering."""

    @abstractmethod
    async def count_models(self, filters: dict | None = None) -> int:
        """Count models matching filters."""

    @abstractmethod
    async def update_model(self, model_id: str, updates: dict) -> None:
        """Update model fields."""

    @abstractmethod
    async def delete_model(self, model_id: str) -> None:
        """Soft-delete a model."""

    # --- Benchmark Suites ---

    @abstractmethod
    async def create_suite(self, suite: dict) -> str:
        """Create a benchmark suite. Returns suite ID."""

    @abstractmethod
    async def get_suite(self, suite_id: str) -> dict | None:
        """Get a suite by ID, including its tasks."""

    @abstractmethod
    async def get_suite_by_slug(self, slug: str) -> dict | None:
        """Get a suite by slug."""

    @abstractmethod
    async def list_suites(self, filters: dict | None = None) -> list[dict]:
        """List benchmark suites."""

    @abstractmethod
    async def update_suite(self, suite_id: str, updates: dict) -> None:
        """Update suite fields."""

    @abstractmethod
    async def delete_suite(self, suite_id: str) -> None:
        """Delete a custom suite."""

    # --- Benchmark Tasks ---

    @abstractmethod
    async def create_task(self, task: dict) -> str:
        """Create a benchmark task. Returns task ID."""

    @abstractmethod
    async def get_tasks_for_suite(self, suite_id: str) -> list[dict]:
        """Get all tasks for a suite, ordered by order_index."""

    # --- Evaluation Runs ---

    @abstractmethod
    async def create_run(self, run: dict) -> str:
        """Create an evaluation run. Returns run ID."""

    @abstractmethod
    async def get_run(self, run_id: str) -> dict | None:
        """Get a run by ID."""

    @abstractmethod
    async def list_runs(
        self, filters: dict | None = None, limit: int = 20, offset: int = 0
    ) -> list[dict]:
        """List runs with optional filtering."""

    @abstractmethod
    async def count_runs(self, filters: dict | None = None) -> int:
        """Count runs matching filters."""

    @abstractmethod
    async def update_run(self, run_id: str, updates: dict) -> None:
        """Update run fields (status, progress, scores, etc)."""

    @abstractmethod
    async def delete_run(self, run_id: str) -> None:
        """Delete a run and its results."""

    # --- Task Results ---

    @abstractmethod
    async def create_task_result(self, result: dict) -> str:
        """Create a task result. Returns result ID."""

    @abstractmethod
    async def get_results_for_run(self, run_id: str) -> list[dict]:
        """Get all task results for a run."""

    # --- Baselines ---

    @abstractmethod
    async def create_baseline(self, baseline: dict) -> str:
        """Create a baseline. Returns baseline ID."""

    @abstractmethod
    async def list_baselines(
        self, model_id: str | None = None, suite_id: str | None = None
    ) -> list[dict]:
        """List baselines with optional filtering."""

    @abstractmethod
    async def get_baseline(self, baseline_id: str) -> dict | None:
        """Get a baseline by ID."""

    @abstractmethod
    async def delete_baseline(self, baseline_id: str) -> None:
        """Delete a baseline."""

    # --- Queue ---

    @abstractmethod
    async def enqueue(self, queue_item: dict) -> str:
        """Add item to evaluation queue. Returns queue item ID."""

    @abstractmethod
    async def get_queue(self) -> list[dict]:
        """Get current queue ordered by priority."""

    @abstractmethod
    async def update_queue_item(self, item_id: str, updates: dict) -> None:
        """Update queue item status."""

    # --- Schedules ---

    @abstractmethod
    async def create_schedule(self, schedule: dict) -> str:
        """Create a schedule. Returns schedule ID."""

    @abstractmethod
    async def list_schedules(self) -> list[dict]:
        """List all schedules."""

    @abstractmethod
    async def update_schedule(self, schedule_id: str, updates: dict) -> None:
        """Update schedule fields."""

    @abstractmethod
    async def delete_schedule(self, schedule_id: str) -> None:
        """Delete a schedule."""

    # --- Custom Test Sets ---

    @abstractmethod
    async def create_test_set(self, test_set: dict) -> str:
        """Create a custom test set. Returns test set ID."""

    @abstractmethod
    async def list_test_sets(self, model_type: str | None = None) -> list[dict]:
        """List custom test sets."""

    @abstractmethod
    async def get_test_set(self, test_set_id: str) -> dict | None:
        """Get a test set by ID."""

    @abstractmethod
    async def delete_test_set(self, test_set_id: str) -> None:
        """Delete a custom test set."""

    # --- Shared Reports ---

    @abstractmethod
    async def create_shared_report(self, report: dict) -> str:
        """Create a shared report. Returns report ID."""

    @abstractmethod
    async def get_shared_report(self, token: str) -> dict | None:
        """Get a shared report by token."""

    @abstractmethod
    async def increment_share_views(self, token: str) -> None:
        """Increment view count for a shared report."""

    @abstractmethod
    async def list_shared_reports(self) -> list[dict]:
        """List all shared reports."""

    @abstractmethod
    async def delete_shared_report(self, report_id: str) -> None:
        """Delete a shared report."""
