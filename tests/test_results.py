import json
from pathlib import Path

import pytest
from zenthrix_benchmarks.exceptions import BenchmarkValidationError
from zenthrix_benchmarks.results import load_results, render_summary


def _write_results(path: Path) -> None:
    path.write_text(
        json.dumps(
            [
                {
                    "implementation": "zenthrix",
                    "hardware": "Apple M3 Max",
                    "model": "Llama-3.2-1B-Instruct",
                    "metrics": {"ttft_ms": 18.7, "tokens_per_second": 94.6},
                }
            ]
        ),
        encoding="utf-8",
    )


def test_load_results_and_render_summary(tmp_path: Path) -> None:
    results_path = tmp_path / "results.json"
    _write_results(results_path)

    results = load_results(results_path)

    assert len(results) == 1
    summary = render_summary(results)
    assert "| Implementation | Hardware | Model | TTFT (ms) | Tokens/s |" in summary
    assert "**18.7**" in summary


def test_render_summary_marks_metric_winners() -> None:
    from zenthrix_benchmarks.results import BenchmarkResult

    results = [
        BenchmarkResult(
            "baseline",
            "hardware",
            "model",
            {"ttft_ms": 20, "tokens_per_second": 80},
        ),
        BenchmarkResult(
            "zenthrix",
            "hardware",
            "model",
            {"ttft_ms": 10, "tokens_per_second": 90},
        ),
    ]

    summary = render_summary(results)

    assert "| baseline | hardware | model | 20 | 80 |" in summary
    assert "| zenthrix | hardware | model | **10** | **90** |" in summary


def test_load_results_rejects_unknown_metric(tmp_path: Path) -> None:
    results_path = tmp_path / "results.json"
    _write_results(results_path)
    payload = json.loads(results_path.read_text(encoding="utf-8"))
    payload[0]["metrics"]["latency"] = 1
    results_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(BenchmarkValidationError, match="Unsupported metric"):
        load_results(results_path)


def test_load_results_rejects_non_finite_metric(tmp_path: Path) -> None:
    results_path = tmp_path / "results.json"
    _write_results(results_path)
    payload = json.loads(results_path.read_text(encoding="utf-8"))
    payload[0]["metrics"]["ttft_ms"] = float("nan")
    results_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(BenchmarkValidationError, match="must be positive"):
        load_results(results_path)
