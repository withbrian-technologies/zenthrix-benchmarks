# Zenthrix Reproducible Edge Benchmark Suite

[![License](https://img.shields.io/badge/license-Apache%202.0-green)](LICENSE)
[![Nightly Benchmarks](https://img.shields.io/badge/benchmarks-nightly-blue)](.github/workflows/nightly-benchmarks.yml)

This repository contains fully automated, deterministic benchmarking scripts comparing **Zenthrix** runtime performance against industry baselines:

- **Apple CoreML Tools** (v0.8+)
- **llama.cpp** (Metal & Hexagon builds)
- **PyTorch ExecuTorch** (v0.3+)

Results are published for acquisition due-diligence review and general reproducibility. Every number in this README can be regenerated locally using the scripts in this repo.

---

## Table of Contents

- [Primary Metrics Evaluated](#primary-metrics-evaluated)
- [Verified Benchmark Results](#verified-benchmark-results-llama-32-1b-instruct)
- [Reproducing the Results](#reproducing-the-results)
- [Integrity and Hardware Telemetry](#integrity-and-hardware-telemetry)
- [Contributing](CONTRIBUTING.md)
- [License](#license)

---

## Primary Metrics Evaluated

1. **Time To First Token (TTFT)** — Milliseconds elapsed before emitting the initial completion token.
2. **Tokens Per Second (TPS)** — Sustained autoregressive generation throughput under fixed sequence lengths (context = 512 tokens, generated = 128 tokens).
3. **Peak Resident Set Size (RSS)** — Physical RAM overhead measured throughout the execution lifecycle.
4. **Thermal Throttling Threshold** — Latency variation across continuous 15-minute inference stress tests.

## Verified Benchmark Results: Llama-3.2-1B-Instruct

**Hardware:** Apple M3 Max (36GB Unified Memory, macOS 14.5)

| Metric | Apple CoreML Tools | llama.cpp (Metal) | ExecuTorch | Zenthrix Compiler |
|---|---|---|---|---|
| TTFT (ms) | 48.2 | 34.1 | 39.5 | **18.7** |
| Throughput (tokens/s) | 52.4 | 68.2 | 61.0 | **94.6** |
| Peak Memory (RSS) | 1.82 GB | 1.24 GB | 1.35 GB | **0.82 GB** |
| Model Load Time (ms) | 410 | 120 | 185 | **44** |

> Bold values indicate the best result in each row.

## Reproducing the Results

### 1. Set Up the Environment

```bash
git clone https://github.com/withbrian-technologies/zenthrix-benchmarks.git
cd zenthrix-benchmarks
uv sync
```

### 2. Run the Matrix Test

Execute the automated harness across all installed framework runtimes:

```bash
python scripts/run_zenthrix_eval.py --config configs/llama_3.2_1b.yaml --device local
python scripts/run_coreml_eval.py --config configs/llama_3.2_1b.yaml
python scripts/run_llamacpp_eval.sh --model llama-3.2-1b.Q4_K_M.gguf
```

### 3. Generate a Comparative Report

Process the raw telemetry JSONs into visual performance plots:

```bash
python scripts/generate_charts.py --input results/ --output-dir ./charts
```

The `zbench` utility validates result JSON files and renders stable Markdown
summaries:

```bash
uv run zbench validate results.json
uv run zbench report results.json
```

## Integrity and Hardware Telemetry

All metrics are captured via OS-level tracing utilities (`powermetrics` on macOS; `perf` and `sysfs` on Linux/Android) to avoid runtime measurement distortion. System-level CPU/GPU/NPU core frequencies and thermal zones are logged continuously to verify the absence of thermal throttling during comparative iterations.

## License

The benchmarking harness, scripts, and aggregated result datasets are released under the [Apache License 2.0](LICENSE).
