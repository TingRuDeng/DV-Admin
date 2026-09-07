"""Test-only query-shape and informational time/memory measurements."""

from __future__ import annotations

import json
import time
import tracemalloc


class QueryProbe:
    def __init__(self, label: str):
        self.label = label
        self.queries: list[tuple[str, int]] = []

    def record(self, sql, params):
        self.queries.append((sql, len(params or ())))

    def __enter__(self):
        tracemalloc.start()
        self.started = time.perf_counter()
        return self

    def __exit__(self, *_):
        elapsed = time.perf_counter() - self.started
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        self.metrics = {
            "label": self.label,
            "queries": len(self.queries),
            "max_parameters": max((size for _, size in self.queries), default=0),
            "total_parameters": sum(size for _, size in self.queries),
            "elapsed_ms": round(elapsed * 1000, 2),
            "peak_bytes": peak,
        }
        print(json.dumps(self.metrics, sort_keys=True))

    def django_execute(self, execute, sql, params, many, context):
        self.record(sql, params)
        return execute(sql, params, many, context)
