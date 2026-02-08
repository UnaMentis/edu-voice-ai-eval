"""Subprocess plugin runner for GPU memory isolation."""

import asyncio
import json
import sys


class SubprocessPluginRunner:
    """Run a plugin evaluation in a subprocess for GPU memory isolation."""

    @staticmethod
    async def run_in_subprocess(
        plugin_module: str,
        plugin_class: str,
        model_spec: dict,
        benchmark_ids: list[str],
        config: dict,
    ) -> list[dict]:
        """Execute plugin evaluation in a subprocess.

        This isolates GPU memory so it can be fully released after evaluation.
        """
        script = f"""
import asyncio
import json
import sys

from {plugin_module} import {plugin_class}

async def main():
    plugin = {plugin_class}()
    model_spec = json.loads('{json.dumps(model_spec)}')
    benchmark_ids = json.loads('{json.dumps(benchmark_ids)}')
    config = json.loads('{json.dumps(config)}')

    results = await plugin.run_evaluation(model_spec, benchmark_ids, config)
    print(json.dumps(results))

asyncio.run(main())
"""
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            "-c",
            script,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_msg = stderr.decode() if stderr else "Unknown subprocess error"
            raise RuntimeError(f"Plugin subprocess failed: {error_msg}")

        return json.loads(stdout.decode())
