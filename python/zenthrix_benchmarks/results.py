"""Benchmark result loading, validation, and comparison."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .exceptions import BenchmarkValidationError

METRICS = ("ttft_ms", "tokens_per_second", "peak_memory_mb", "load_time_ms")


@dataclass(frozen=True, slots=True)
class BenchmarkResult:
    """One measured implementation on one hardware/model configuration."""

    implementation: str
    hardware: str
    model: str
    metrics: dict[str, float]

    @classmethod
    def from_mapping(cls, value: object) -> "BenchmarkResult":
        """Validate and construct a result from decoded JSON."""
        if not isinstance(value, dict):
            raise BenchmarkValidationError("Each result must be a JSON object")
        implementation = _required_text(value, "implementation")
        hardware = _required_text(value, "hardware")
        model = _required_text(value, "model")
        raw_metrics = value.get("metrics")
        if not isinstance(raw_metrics, dict) or not raw_metrics:
            raise BenchmarkValidationError("metrics must be a non-empty object")
        metrics: dict[str, float] = {}
        for name, raw_value in raw_metrics.items():
            if name not in METRICS:
                raise BenchmarkValidationError(f"Unsupported metric: {name}")
            if isinstance(raw_value, bool) or not isinstance(raw_value, (int, float)):
                raise BenchmarkValidationError(f"Metric {name} must be numeric")
            if raw_value <= 0:
                raise BenchmarkValidationError(f"Metric {name} must be positive")
            metrics[name] = float(raw_value)
        return cls(implementation, hardware, model, metrics)


def load_results(path: str | Path) -> list[BenchmarkResult]:
    """Load and validate a JSON array of benchmark results."""
    result_path = Path(path)
    try:
        payload = json.loads(result_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise BenchmarkValidationError(
            f"Unable to read benchmark results: {result_path}"
        ) from error
    if not isinstance(payload, list) or not payload:
        raise BenchmarkValidationError("Results file must contain a non-empty array")
    return [BenchmarkResult.from_mapping(item) for item in payload]


def render_summary(results: list[BenchmarkResult]) -> str:
    """Render a stable Markdown table from validated results."""
    lines = ["| Implementation | Hardware | Model | Metrics |", "|---|---|---|---|"]
    for result in results:
        metrics = ", ".join(
            f"{name}={value:g}" for name, value in sorted(result.metrics.items())
        )
        lines.append(
            f"| {result.implementation} | {result.hardware} | "
            f"{result.model} | {metrics} |"
        )
    return "\n".join(lines)


def _required_text(value: dict[str, Any], key: str) -> str:
    raw_value = value.get(key)
    if not isinstance(raw_value, str) or not raw_value.strip():
        raise BenchmarkValidationError(f"{key} must be a non-empty string")
    return raw_value.strip()

