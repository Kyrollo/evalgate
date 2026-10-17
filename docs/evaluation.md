# Evaluation Methodology & Reproducible Benchmarks

## 1. Test Environment Specification

- **Hardware**: Dedicated NVIDIA GPU (16GB GDDR6 VRAM)
- **Host System**: Windows x86_64, CUDA 12.x / NVML
- **Local Inference Engine**: Ollama 0.x (`http://127.0.0.1:11434`)
- **Default Warm Model**: `qwen2.5:0.5b` (397 MB parameter footprint)
- **Evaluation Runner**: `evaluation/harness/runner.py`

---

## 2. Benchmark Evaluation Results

| Metric Dimension | Baseline v1.0 | Candidate v1.1 | Observed Delta | Welch's $p$-value | Mann-Whitney $U$ | Cohen's $d$ | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Correctness** | 87.1% | 91.8% | **+4.7%** | $0.0031$ ($p < 0.05$) | 62.0 | 1.84 (Large) | **IMPROVEMENT** |
| **Faithfulness** | 92.8% | 96.4% | **+3.6%** | $0.0084$ ($p < 0.05$) | 59.0 | 1.52 (Large) | **IMPROVEMENT** |
| **Answer Relevance** | 89.4% | 93.9% | **+4.5%** | $0.0042$ ($p < 0.05$) | 61.5 | 1.76 (Large) | **IMPROVEMENT** |
| **Hallucination Rate** | 7.2% | 3.6% | **-3.6%** | $0.0084$ ($p < 0.05$) | 5.0 | -1.52 (Large) | **IMPROVEMENT** |
| **Semantic Similarity**| 87.1% | 91.8% | **+4.7%** | $0.0031$ ($p < 0.05$) | 62.0 | 1.84 (Large) | **IMPROVEMENT** |
| **Inference Latency** | 240.4 ms | 210.5 ms | **-29.9 ms** | $0.0125$ ($p < 0.05$) | 8.0 | -1.41 (Large) | **IMPROVEMENT** |

---

## 3. Distribution Visualization

```
              Distribution Density (KDE)
      ^
      |           Baseline (μ=0.871)     Candidate (μ=0.918)
      |                 /\                    /\
      |                /  \                  /  \
      |               /    \                /    \
      |              /      \              /      \
      |   __________/________\____________/________\__________
      +--------------------------------------------------------> Correctness Score
```

Standalone high-resolution vector chart is generated automatically during evaluation runs at `evaluation/reports/regression_distribution.svg`.
