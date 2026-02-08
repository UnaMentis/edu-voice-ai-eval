"""Tests for SQLite storage backend."""

import pytest


@pytest.mark.asyncio
class TestModelCRUD:
    async def test_create_and_get_model(self, storage, sample_model):
        model_id = await storage.create_model(sample_model)
        assert model_id

        model = await storage.get_model(model_id)
        assert model is not None
        assert model["name"] == "Test Model"
        assert model["model_type"] == "llm"
        assert model["slug"] == "test-model"

    async def test_list_models(self, storage, sample_model):
        await storage.create_model(sample_model)
        models = await storage.list_models()
        assert len(models) >= 1

    async def test_count_models(self, storage, sample_model):
        await storage.create_model(sample_model)
        count = await storage.count_models()
        assert count >= 1

    async def test_update_model(self, storage, sample_model):
        model_id = await storage.create_model(sample_model)
        await storage.update_model(model_id, {"name": "Updated Name"})
        model = await storage.get_model(model_id)
        assert model["name"] == "Updated Name"

    async def test_delete_model(self, storage, sample_model):
        model_id = await storage.create_model(sample_model)
        await storage.delete_model(model_id)
        model = await storage.get_model(model_id)
        assert model is None

    async def test_get_model_by_slug(self, storage, sample_model):
        await storage.create_model(sample_model)
        model = await storage.get_model_by_slug("test-model")
        assert model is not None
        assert model["name"] == "Test Model"

    async def test_filter_by_type(self, storage, sample_model):
        await storage.create_model(sample_model)
        stt_model = dict(sample_model)
        stt_model["name"] = "STT Model"
        stt_model["model_type"] = "stt"
        await storage.create_model(stt_model)

        llm_models = await storage.list_models(filters={"model_type": "llm"})
        assert all(m["model_type"] == "llm" for m in llm_models)


@pytest.mark.asyncio
class TestSuiteCRUD:
    async def test_seeded_suites(self, seeded_storage):
        suites = await seeded_storage.list_suites()
        assert len(suites) >= 7  # 7 built-in suites

    async def test_get_suite_by_slug(self, seeded_storage):
        suite = await seeded_storage.get_suite_by_slug("quick_scan")
        assert suite is not None
        assert suite["name"] == "Quick Scan"
        assert suite["is_builtin"] == 1

    async def test_get_suite_with_tasks(self, seeded_storage):
        suite = await seeded_storage.get_suite_by_slug("quick_scan")
        assert "tasks" in suite
        assert len(suite["tasks"]) > 0


@pytest.mark.asyncio
class TestRunCRUD:
    async def test_create_and_get_run(self, seeded_storage, sample_model):
        model_id = await seeded_storage.create_model(sample_model)
        suites = await seeded_storage.list_suites()
        suite_id = suites[0]["id"]

        run_id = await seeded_storage.create_run({
            "model_id": model_id,
            "suite_id": suite_id,
            "tasks_total": 5,
        })
        assert run_id

        run = await seeded_storage.get_run(run_id)
        assert run is not None
        assert run["model_id"] == model_id
        assert run["status"] == "pending"

    async def test_update_run_status(self, seeded_storage, sample_model):
        model_id = await seeded_storage.create_model(sample_model)
        suites = await seeded_storage.list_suites()
        suite_id = suites[0]["id"]

        run_id = await seeded_storage.create_run({
            "model_id": model_id,
            "suite_id": suite_id,
        })
        await seeded_storage.update_run(run_id, {"status": "running"})
        run = await seeded_storage.get_run(run_id)
        assert run["status"] == "running"

    async def test_list_runs_with_filter(self, seeded_storage, sample_model):
        model_id = await seeded_storage.create_model(sample_model)
        suites = await seeded_storage.list_suites()
        suite_id = suites[0]["id"]

        await seeded_storage.create_run({"model_id": model_id, "suite_id": suite_id})
        runs = await seeded_storage.list_runs(filters={"model_id": model_id})
        assert len(runs) >= 1
        assert all(r["model_id"] == model_id for r in runs)


@pytest.mark.asyncio
class TestTaskResults:
    async def test_create_and_get_results(self, seeded_storage, sample_model):
        model_id = await seeded_storage.create_model(sample_model)
        suites = await seeded_storage.list_suites()
        suite_id = suites[0]["id"]

        run_id = await seeded_storage.create_run({
            "model_id": model_id,
            "suite_id": suite_id,
        })

        tasks = await seeded_storage.get_tasks_for_suite(suite_id)
        result_id = await seeded_storage.create_task_result({
            "run_id": run_id,
            "task_id": tasks[0]["id"],
            "score": 85.0,
            "raw_score": 0.85,
            "raw_metric_name": "accuracy",
            "status": "completed",
        })
        assert result_id

        results = await seeded_storage.get_results_for_run(run_id)
        assert len(results) == 1
        assert results[0]["score"] == 85.0
