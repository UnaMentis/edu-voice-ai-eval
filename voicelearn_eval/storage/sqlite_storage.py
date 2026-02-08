"""SQLite storage implementation."""

import json
import uuid
from datetime import datetime
from pathlib import Path

import aiosqlite

from .base import BaseStorage


def _generate_id() -> str:
    return str(uuid.uuid4())


def _now() -> str:
    return datetime.utcnow().isoformat()


def _json_dumps(obj) -> str | None:
    if obj is None:
        return None
    return json.dumps(obj)


def _json_loads(s) -> any | None:
    if s is None:
        return None
    if isinstance(s, (dict, list)):
        return s
    return json.loads(s)


def _row_to_dict(row: aiosqlite.Row) -> dict:
    return dict(row)


class SQLiteStorage(BaseStorage):
    """SQLite-based storage backend."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._db: aiosqlite.Connection | None = None

    async def initialize(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._db = await aiosqlite.connect(str(self.db_path))
        self._db.row_factory = aiosqlite.Row
        await self._db.execute("PRAGMA journal_mode=WAL")
        await self._db.execute("PRAGMA foreign_keys=ON")
        await self._run_migrations()

    async def _run_migrations(self) -> None:
        migration_path = Path(__file__).parent / "migrations" / "001_initial.sql"
        sql = migration_path.read_text()
        await self._db.executescript(sql)
        await self._db.commit()

    async def close(self) -> None:
        if self._db:
            await self._db.close()
            self._db = None

    # --- Models ---

    async def create_model(self, model: dict) -> str:
        model_id = model.get("id") or _generate_id()
        now = _now()
        await self._db.execute(
            """INSERT INTO eval_models (id, name, slug, model_type, model_family, model_version,
               source_type, source_uri, source_format, api_base_url, api_key_env,
               deployment_target, parameter_count_b, model_size_gb, quantization, context_window,
               education_tiers, subjects, languages, tags, notes, is_reference, is_active,
               created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                model_id,
                model["name"],
                model.get("slug", model["name"].lower().replace(" ", "-")),
                model["model_type"],
                model.get("model_family"),
                model.get("model_version"),
                model["source_type"],
                model.get("source_uri"),
                model.get("source_format"),
                model.get("api_base_url"),
                model.get("api_key_env"),
                model.get("deployment_target", "server"),
                model.get("parameter_count_b"),
                model.get("model_size_gb"),
                model.get("quantization"),
                model.get("context_window"),
                _json_dumps(model.get("education_tiers", [])),
                _json_dumps(model.get("subjects", [])),
                _json_dumps(model.get("languages", [])),
                _json_dumps(model.get("tags", [])),
                model.get("notes"),
                model.get("is_reference", False),
                True,
                now,
                now,
            ),
        )
        await self._db.commit()
        return model_id

    async def get_model(self, model_id: str) -> dict | None:
        cursor = await self._db.execute(
            "SELECT * FROM eval_models WHERE id = ? AND is_active = TRUE", (model_id,)
        )
        row = await cursor.fetchone()
        return _row_to_dict(row) if row else None

    async def get_model_by_slug(self, slug: str) -> dict | None:
        cursor = await self._db.execute(
            "SELECT * FROM eval_models WHERE slug = ? AND is_active = TRUE", (slug,)
        )
        row = await cursor.fetchone()
        return _row_to_dict(row) if row else None

    async def list_models(
        self, filters: dict | None = None, limit: int = 20, offset: int = 0
    ) -> list[dict]:
        query = "SELECT * FROM eval_models WHERE is_active = TRUE"
        params: list = []
        if filters:
            if "model_type" in filters:
                query += " AND model_type = ?"
                params.append(filters["model_type"])
            if "deployment_target" in filters:
                query += " AND deployment_target = ?"
                params.append(filters["deployment_target"])
            if "model_family" in filters:
                query += " AND model_family = ?"
                params.append(filters["model_family"])
            if "is_reference" in filters:
                query += " AND is_reference = ?"
                params.append(filters["is_reference"])
            if "search" in filters:
                query += " AND (name LIKE ? OR slug LIKE ?)"
                params.extend([f"%{filters['search']}%"] * 2)
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        cursor = await self._db.execute(query, params)
        rows = await cursor.fetchall()
        return [_row_to_dict(r) for r in rows]

    async def count_models(self, filters: dict | None = None) -> int:
        query = "SELECT COUNT(*) FROM eval_models WHERE is_active = TRUE"
        params: list = []
        if filters:
            if "model_type" in filters:
                query += " AND model_type = ?"
                params.append(filters["model_type"])
            if "search" in filters:
                query += " AND (name LIKE ? OR slug LIKE ?)"
                params.extend([f"%{filters['search']}%"] * 2)
        cursor = await self._db.execute(query, params)
        row = await cursor.fetchone()
        return row[0]

    async def update_model(self, model_id: str, updates: dict) -> None:
        updates["updated_at"] = _now()
        for key in ("education_tiers", "subjects", "languages", "tags"):
            if key in updates and isinstance(updates[key], list):
                updates[key] = _json_dumps(updates[key])
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [model_id]
        await self._db.execute(
            f"UPDATE eval_models SET {set_clause} WHERE id = ?", values
        )
        await self._db.commit()

    async def delete_model(self, model_id: str) -> None:
        await self._db.execute(
            "UPDATE eval_models SET is_active = FALSE, updated_at = ? WHERE id = ?",
            (_now(), model_id),
        )
        await self._db.commit()

    # --- Benchmark Suites ---

    async def create_suite(self, suite: dict) -> str:
        suite_id = suite.get("id") or _generate_id()
        now = _now()
        await self._db.execute(
            """INSERT INTO eval_benchmark_suites (id, name, slug, description, model_type,
               config, default_params, category, is_builtin, is_active, created_by,
               created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                suite_id,
                suite["name"],
                suite.get("slug", suite["name"].lower().replace(" ", "_")),
                suite.get("description"),
                suite["model_type"],
                _json_dumps(suite.get("config", {})),
                _json_dumps(suite.get("default_params")),
                suite.get("category"),
                suite.get("is_builtin", False),
                True,
                suite.get("created_by"),
                now,
                now,
            ),
        )
        await self._db.commit()
        return suite_id

    async def get_suite(self, suite_id: str) -> dict | None:
        cursor = await self._db.execute(
            "SELECT * FROM eval_benchmark_suites WHERE id = ? AND is_active = TRUE",
            (suite_id,),
        )
        row = await cursor.fetchone()
        if not row:
            return None
        suite = _row_to_dict(row)
        suite["tasks"] = await self.get_tasks_for_suite(suite_id)
        return suite

    async def get_suite_by_slug(self, slug: str) -> dict | None:
        cursor = await self._db.execute(
            "SELECT * FROM eval_benchmark_suites WHERE slug = ? AND is_active = TRUE",
            (slug,),
        )
        row = await cursor.fetchone()
        if not row:
            return None
        suite = _row_to_dict(row)
        suite["tasks"] = await self.get_tasks_for_suite(suite["id"])
        return suite

    async def list_suites(self, filters: dict | None = None) -> list[dict]:
        query = "SELECT * FROM eval_benchmark_suites WHERE is_active = TRUE"
        params: list = []
        if filters:
            if "model_type" in filters:
                query += " AND model_type = ?"
                params.append(filters["model_type"])
            if "category" in filters:
                query += " AND category = ?"
                params.append(filters["category"])
            if "is_builtin" in filters:
                query += " AND is_builtin = ?"
                params.append(filters["is_builtin"])
        query += " ORDER BY is_builtin DESC, name ASC"
        cursor = await self._db.execute(query, params)
        rows = await cursor.fetchall()
        suites = []
        for r in rows:
            s = _row_to_dict(r)
            # Get task count without loading all tasks
            cnt_cursor = await self._db.execute(
                "SELECT COUNT(*) FROM eval_benchmark_tasks WHERE suite_id = ?", (s["id"],)
            )
            cnt_row = await cnt_cursor.fetchone()
            s["task_count"] = cnt_row[0]
            suites.append(s)
        return suites

    async def update_suite(self, suite_id: str, updates: dict) -> None:
        updates["updated_at"] = _now()
        for key in ("config", "default_params"):
            if key in updates and isinstance(updates[key], dict):
                updates[key] = _json_dumps(updates[key])
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [suite_id]
        await self._db.execute(
            f"UPDATE eval_benchmark_suites SET {set_clause} WHERE id = ?", values
        )
        await self._db.commit()

    async def delete_suite(self, suite_id: str) -> None:
        await self._db.execute(
            "UPDATE eval_benchmark_suites SET is_active = FALSE, updated_at = ? WHERE id = ?",
            (_now(), suite_id),
        )
        await self._db.commit()

    # --- Benchmark Tasks ---

    async def create_task(self, task: dict) -> str:
        task_id = task.get("id") or _generate_id()
        await self._db.execute(
            """INSERT INTO eval_benchmark_tasks (id, suite_id, name, description, task_type,
               config, weight, education_tier, subject, order_index, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                task_id,
                task["suite_id"],
                task["name"],
                task.get("description"),
                task["task_type"],
                _json_dumps(task.get("config", {})),
                task.get("weight", 1.0),
                task.get("education_tier"),
                task.get("subject"),
                task.get("order_index", 0),
                _now(),
            ),
        )
        await self._db.commit()
        return task_id

    async def get_tasks_for_suite(self, suite_id: str) -> list[dict]:
        cursor = await self._db.execute(
            "SELECT * FROM eval_benchmark_tasks WHERE suite_id = ? ORDER BY order_index",
            (suite_id,),
        )
        rows = await cursor.fetchall()
        return [_row_to_dict(r) for r in rows]

    # --- Evaluation Runs ---

    async def create_run(self, run: dict) -> str:
        run_id = run.get("id") or _generate_id()
        now = _now()
        await self._db.execute(
            """INSERT INTO eval_runs (id, model_id, suite_id, run_config, run_params,
               status, progress_percent, tasks_total, triggered_by, run_version,
               created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                run_id,
                run["model_id"],
                run["suite_id"],
                _json_dumps(run.get("run_config")),
                _json_dumps(run.get("run_params")),
                run.get("status", "pending"),
                0,
                run.get("tasks_total", 0),
                run.get("triggered_by", "manual"),
                run.get("run_version", 1),
                now,
                now,
            ),
        )
        await self._db.commit()
        return run_id

    async def get_run(self, run_id: str) -> dict | None:
        cursor = await self._db.execute(
            "SELECT * FROM eval_runs WHERE id = ?", (run_id,)
        )
        row = await cursor.fetchone()
        return _row_to_dict(row) if row else None

    async def list_runs(
        self, filters: dict | None = None, limit: int = 20, offset: int = 0
    ) -> list[dict]:
        query = "SELECT * FROM eval_runs WHERE 1=1"
        params: list = []
        if filters:
            if "status" in filters:
                query += " AND status = ?"
                params.append(filters["status"])
            if "model_id" in filters:
                query += " AND model_id = ?"
                params.append(filters["model_id"])
            if "suite_id" in filters:
                query += " AND suite_id = ?"
                params.append(filters["suite_id"])
            if "triggered_by" in filters:
                query += " AND triggered_by = ?"
                params.append(filters["triggered_by"])
        sort = "created_at DESC"
        if filters and "sort" in filters:
            sort_map = {
                "newest": "created_at DESC",
                "oldest": "created_at ASC",
                "score_high": "overall_score DESC",
                "score_low": "overall_score ASC",
            }
            sort = sort_map.get(filters["sort"], sort)
        query += f" ORDER BY {sort} LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        cursor = await self._db.execute(query, params)
        rows = await cursor.fetchall()
        return [_row_to_dict(r) for r in rows]

    async def count_runs(self, filters: dict | None = None) -> int:
        query = "SELECT COUNT(*) FROM eval_runs WHERE 1=1"
        params: list = []
        if filters:
            if "status" in filters:
                query += " AND status = ?"
                params.append(filters["status"])
            if "model_id" in filters:
                query += " AND model_id = ?"
                params.append(filters["model_id"])
        cursor = await self._db.execute(query, params)
        row = await cursor.fetchone()
        return row[0]

    async def update_run(self, run_id: str, updates: dict) -> None:
        updates["updated_at"] = _now()
        for key in ("overall_metrics", "run_config", "run_params", "hardware_info", "software_info"):
            if key in updates and isinstance(updates[key], dict):
                updates[key] = _json_dumps(updates[key])
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [run_id]
        await self._db.execute(
            f"UPDATE eval_runs SET {set_clause} WHERE id = ?", values
        )
        await self._db.commit()

    async def delete_run(self, run_id: str) -> None:
        await self._db.execute("DELETE FROM eval_task_results WHERE run_id = ?", (run_id,))
        await self._db.execute("DELETE FROM eval_queue WHERE run_id = ?", (run_id,))
        await self._db.execute("DELETE FROM eval_runs WHERE id = ?", (run_id,))
        await self._db.commit()

    # --- Task Results ---

    async def create_task_result(self, result: dict) -> str:
        result_id = result.get("id") or _generate_id()
        await self._db.execute(
            """INSERT INTO eval_task_results (id, run_id, task_id, score, raw_score,
               raw_metric_name, metrics, latency_ms, throughput, memory_peak_mb,
               gpu_memory_peak_mb, sample_audio_path, sample_text, status, error_message,
               started_at, completed_at, duration_seconds, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                result_id,
                result["run_id"],
                result["task_id"],
                result.get("score"),
                result.get("raw_score"),
                result.get("raw_metric_name"),
                _json_dumps(result.get("metrics", {})),
                result.get("latency_ms"),
                result.get("throughput"),
                result.get("memory_peak_mb"),
                result.get("gpu_memory_peak_mb"),
                result.get("sample_audio_path"),
                result.get("sample_text"),
                result.get("status", "completed"),
                result.get("error_message"),
                result.get("started_at"),
                result.get("completed_at"),
                result.get("duration_seconds"),
                _now(),
            ),
        )
        await self._db.commit()
        return result_id

    async def get_results_for_run(self, run_id: str) -> list[dict]:
        cursor = await self._db.execute(
            """SELECT r.*, t.name as task_name, t.education_tier, t.subject, t.task_type
               FROM eval_task_results r
               JOIN eval_benchmark_tasks t ON r.task_id = t.id
               WHERE r.run_id = ?
               ORDER BY t.order_index""",
            (run_id,),
        )
        rows = await cursor.fetchall()
        return [_row_to_dict(r) for r in rows]

    # --- Baselines ---

    async def create_baseline(self, baseline: dict) -> str:
        baseline_id = baseline.get("id") or _generate_id()
        await self._db.execute(
            """INSERT INTO eval_baselines (id, name, description, model_id, run_id, suite_id,
               overall_score, task_scores, is_active, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                baseline_id,
                baseline["name"],
                baseline.get("description"),
                baseline["model_id"],
                baseline["run_id"],
                baseline["suite_id"],
                baseline["overall_score"],
                _json_dumps(baseline.get("task_scores", {})),
                True,
                _now(),
            ),
        )
        await self._db.commit()
        return baseline_id

    async def list_baselines(
        self, model_id: str | None = None, suite_id: str | None = None
    ) -> list[dict]:
        query = "SELECT * FROM eval_baselines WHERE is_active = TRUE"
        params: list = []
        if model_id:
            query += " AND model_id = ?"
            params.append(model_id)
        if suite_id:
            query += " AND suite_id = ?"
            params.append(suite_id)
        query += " ORDER BY created_at DESC"
        cursor = await self._db.execute(query, params)
        rows = await cursor.fetchall()
        return [_row_to_dict(r) for r in rows]

    async def get_baseline(self, baseline_id: str) -> dict | None:
        cursor = await self._db.execute(
            "SELECT * FROM eval_baselines WHERE id = ? AND is_active = TRUE",
            (baseline_id,),
        )
        row = await cursor.fetchone()
        return _row_to_dict(row) if row else None

    async def delete_baseline(self, baseline_id: str) -> None:
        await self._db.execute(
            "UPDATE eval_baselines SET is_active = FALSE WHERE id = ?", (baseline_id,)
        )
        await self._db.commit()

    # --- Queue ---

    async def enqueue(self, queue_item: dict) -> str:
        item_id = queue_item.get("id") or _generate_id()
        await self._db.execute(
            """INSERT INTO eval_queue (id, run_id, priority, status, queued_at,
               required_gpu_memory_gb, required_compute)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                item_id,
                queue_item["run_id"],
                queue_item.get("priority", 0),
                "waiting",
                _now(),
                queue_item.get("required_gpu_memory_gb"),
                queue_item.get("required_compute", "any"),
            ),
        )
        await self._db.commit()
        return item_id

    async def get_queue(self) -> list[dict]:
        cursor = await self._db.execute(
            """SELECT q.*, r.model_id, r.suite_id, m.name as model_name, s.name as suite_name
               FROM eval_queue q
               JOIN eval_runs r ON q.run_id = r.id
               JOIN eval_models m ON r.model_id = m.id
               JOIN eval_benchmark_suites s ON r.suite_id = s.id
               WHERE q.status IN ('waiting', 'active')
               ORDER BY q.priority DESC, q.queued_at ASC""",
        )
        rows = await cursor.fetchall()
        return [_row_to_dict(r) for r in rows]

    async def update_queue_item(self, item_id: str, updates: dict) -> None:
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [item_id]
        await self._db.execute(
            f"UPDATE eval_queue SET {set_clause} WHERE id = ?", values
        )
        await self._db.commit()

    # --- Schedules ---

    async def create_schedule(self, schedule: dict) -> str:
        schedule_id = schedule.get("id") or _generate_id()
        await self._db.execute(
            """INSERT INTO eval_schedules (id, name, description, model_id, model_type,
               suite_id, schedule_type, cron_expression, is_active, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                schedule_id,
                schedule["name"],
                schedule.get("description"),
                schedule.get("model_id"),
                schedule.get("model_type"),
                schedule["suite_id"],
                schedule["schedule_type"],
                schedule.get("cron_expression"),
                True,
                _now(),
            ),
        )
        await self._db.commit()
        return schedule_id

    async def list_schedules(self) -> list[dict]:
        cursor = await self._db.execute(
            "SELECT * FROM eval_schedules ORDER BY created_at DESC"
        )
        rows = await cursor.fetchall()
        return [_row_to_dict(r) for r in rows]

    async def update_schedule(self, schedule_id: str, updates: dict) -> None:
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [schedule_id]
        await self._db.execute(
            f"UPDATE eval_schedules SET {set_clause} WHERE id = ?", values
        )
        await self._db.commit()

    async def delete_schedule(self, schedule_id: str) -> None:
        await self._db.execute("DELETE FROM eval_schedules WHERE id = ?", (schedule_id,))
        await self._db.commit()

    # --- Custom Test Sets ---

    async def create_test_set(self, test_set: dict) -> str:
        test_set_id = test_set.get("id") or _generate_id()
        items = test_set.get("items", [])
        now = _now()
        await self._db.execute(
            """INSERT INTO eval_custom_test_sets (id, name, description, model_type,
               items, item_count, tags, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                test_set_id,
                test_set["name"],
                test_set.get("description"),
                test_set["model_type"],
                _json_dumps(items),
                len(items),
                _json_dumps(test_set.get("tags", [])),
                now,
                now,
            ),
        )
        await self._db.commit()
        return test_set_id

    async def list_test_sets(self, model_type: str | None = None) -> list[dict]:
        query = "SELECT * FROM eval_custom_test_sets"
        params: list = []
        if model_type:
            query += " WHERE model_type = ?"
            params.append(model_type)
        query += " ORDER BY created_at DESC"
        cursor = await self._db.execute(query, params)
        rows = await cursor.fetchall()
        return [_row_to_dict(r) for r in rows]

    async def get_test_set(self, test_set_id: str) -> dict | None:
        cursor = await self._db.execute(
            "SELECT * FROM eval_custom_test_sets WHERE id = ?", (test_set_id,)
        )
        row = await cursor.fetchone()
        return _row_to_dict(row) if row else None

    async def delete_test_set(self, test_set_id: str) -> None:
        await self._db.execute(
            "DELETE FROM eval_custom_test_sets WHERE id = ?", (test_set_id,)
        )
        await self._db.commit()

    # --- Shared Reports ---

    async def create_shared_report(self, report: dict) -> str:
        report_id = report.get("id") or _generate_id()
        token = report.get("share_token") or _generate_id()
        await self._db.execute(
            """INSERT INTO eval_shared_reports (id, share_token, report_type, report_config,
               is_active, expires_at, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                report_id,
                token,
                report["report_type"],
                _json_dumps(report["report_config"]),
                True,
                report.get("expires_at"),
                _now(),
            ),
        )
        await self._db.commit()
        return token

    async def get_shared_report(self, token: str) -> dict | None:
        cursor = await self._db.execute(
            "SELECT * FROM eval_shared_reports WHERE share_token = ? AND is_active = TRUE",
            (token,),
        )
        row = await cursor.fetchone()
        return _row_to_dict(row) if row else None

    async def increment_share_views(self, token: str) -> None:
        await self._db.execute(
            "UPDATE eval_shared_reports SET view_count = view_count + 1 WHERE share_token = ?",
            (token,),
        )
        await self._db.commit()

    async def list_shared_reports(self) -> list[dict]:
        cursor = await self._db.execute(
            "SELECT * FROM eval_shared_reports WHERE is_active = TRUE ORDER BY created_at DESC"
        )
        rows = await cursor.fetchall()
        return [_row_to_dict(r) for r in rows]

    async def delete_shared_report(self, report_id: str) -> None:
        await self._db.execute(
            "UPDATE eval_shared_reports SET is_active = FALSE WHERE id = ?", (report_id,)
        )
        await self._db.commit()
