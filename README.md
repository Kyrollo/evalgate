# EvalGate

> **Automated CI/CD Quality Gate & Faithfulness Lab**

[![CI Quality Gate](https://github.com/Kyrollo/evalgate/actions/workflows/ci.yml/badge.svg)](https://github.com/Kyrollo/evalgate/actions)
[![Release](https://img.shields.io/badge/Release-v1.0.0-blue.svg)](https://github.com/Kyrollo/evalgate/releases/tag/v1.0.0)
[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/downloads/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-blue.svg)](https://www.typescriptlang.org/)
[![Category: LLMOps & Security](https://img.shields.io/badge/Category-LLMOps%20&%20Security-indigo.svg)](https://kyrollo.github.io/projects/evalgate)
[![Tier: Flagship](https://img.shields.io/badge/Tier-Flagship-purple.svg)](https://kyrollo.github.io/projects/evalgate)

CI/CD quality gate platform for LLMs featuring LLM-as-a-judge faithfulness scoring, regression radar charts, assertion labs, and automated pass/fail thresholds.

---

## 🎬 Interactive Live Demonstration & Video Player

> **▶️ In-Browser Playback (Zero Download Required)**:  
> Watch the full 1080p high-definition interactive demonstration directly inside your browser without downloading any files:  
> - 🌐 **[Launch In-Browser Video Player](https://kyrollo.github.io/projects/evalgate)** *(Hardware-accelerated web player with scrub bar, speed control & architecture breakdown)*  
> - 🎥 **[Direct 1080p Video Stream](https://kyrollo.github.io/media/evalgate/demo.mp4)** *(Instant browser playback via GitHub Pages)*  
> - 📦 **[Download HD Release Asset (v1.0.0)](https://github.com/Kyrollo/evalgate/releases/download/v1.0.0/demo.mp4)** *(Official master recording)*  

[![Watch 1080p Interactive Video Demo](docs/assets/screenshots/01_hero_dashboard.png)](https://kyrollo.github.io/projects/evalgate)

---

### 📸 Visual Feature Gallery

| 1. System Overview & Dashboard | 2. Studio / Interactive Workbench |
|:---:|:---:|
| ![EvalGate Dashboard](docs/assets/screenshots/01_hero_dashboard.png) | ![EvalGate Workbench](docs/assets/screenshots/02_workbench_studio.png) |
| **3. Analysis Results & Diagnostics** | **4. Telemetry, Metrics & Health** |
| ![EvalGate Results](docs/assets/screenshots/03_analysis_results.png) | ![EvalGate Telemetry](docs/assets/screenshots/04_telemetry_metrics.png) |

---

## 📖 Executive Summary & Engineering Challenge

### The Problem
Shipping LLM features into production without automated CI regression testing causes silent regressions, hallucinations, and format breaking changes that slip past human spot checks.

### The Solution Architecture
EvalGate introduces deterministic automated quality gates into GitHub Actions and CI pipelines. It executes golden assertion test suites, runs dual-judge consensus scoring (Llama 3.3 70B + Qwen 2.5 72B), visualizes multidimensional regression radar charts, and blocks PRs that fall below strict faithfulness and answer relevancy thresholds.

---

## 🏗️ System Architecture & Workflow Pipeline

```mermaid
flowchart TD
    N0["CI Pipeline Webhook / Test Suite Trigger"] --> N1["EvalGate Orchestrator & Assertion Engine (FastAPI)"]
    N1["EvalGate Orchestrator & Assertion Engine (FastAPI)"] --> N2["Dual LLM Judge Consensus (Llama 3.3 70B & Qwen 2.5 72B)"]
    N2["Dual LLM Judge Consensus (Llama 3.3 70B & Qwen 2.5 72B)"] --> N3["Regression Radar & CI Pass/Fail Threshold Verifier"]
```


### Pipeline Execution Stages

| Stage | Operation Detail |
|:---|:---|
| **Stage 01: Test Ingestion** | Loads benchmark test datasets (Q&A pairs, context documents, expected facts) from JSONL. |
| **Stage 02: Multi-Judge Eval** | Scores candidate answers for faithfulness, answer relevance, context recall, and tone. |
| **Stage 03: Statistical Consensus** | Computes inter-judge agreement and statistical confidence intervals across eval runs. |
| **Stage 04: CI Gate Enforcement** | Emits pass/fail status to CI/CD pipelines with actionable regression diffs. |


---

## 🚀 Key Features & Innovations

- **Dual-Judge Consensus Engine**: Cross-evaluates candidate outputs using independent LLM judges to eliminate scoring bias.
- **Multi-Axis Regression Radar**: Visualizes performance shifts across faithfulness, relevancy, harmfulness, and latency.
- **Automated CI Quality Gate**: GitHub Actions integration blocking PRs that fail pre-defined statistical quality thresholds.
- **Assertion Lab & Fuzzer**: Interactive testbed for creating deterministic regex, schema, and semantic assertion suites.
- **Statistical Agreement Matrix**: Calculates Cohen's kappa and inter-judge confidence intervals across evaluation batches.


---

## 📊 Empirical Benchmarks & Performance Metrics

| Metric | Target Benchmark | Achieved Production Result |
|:---|:---:|:---:|
| **Gate Pass Rate** | Enterprise Tier SLA | `100.0%` |
| **Faithfulness Score** | Enterprise Tier SLA | `98.2%` |
| **Consensus Agreement** | Enterprise Tier SLA | `96.5%` |
| **Eval Latency** | Enterprise Tier SLA | `1.2 ms/item` |


---

## 🛠️ Technology Stack & Dependencies

| Layer | Technologies Used |
|:---|:---|
| **Frontend** | `React 19`, `Tailwind CSS`, `Chart.js / Recharts`, `Lucide Icons` |
| **Backend** | `FastAPI`, `Python 3.12`, `Pydantic`, `Celery Workers` |
| **AI / ML** | `Ragas`, `G-Eval`, `Groq API`, `Llama 3.3 70B`, `Qwen 2.5 72B` |
| **Data Storage** | `PostgreSQL 16`, `Redis (Batch Queue)` |
| **DevOps & Infra** | `GitHub Actions CI`, `Docker Compose`, `Pytest Integration` |


---

## 🔌 API Reference & Core Endpoints

| Method | Endpoint Route | Description |
|:---:|:---|:---|
| `POST` | `/api/v1/eval/batch` | Trigger parallel multi-judge evaluation across benchmark dataset |
| `GET` | `/api/v1/eval/reports` | Retrieve regression radar reports and score distributions |
| `POST` | `/api/v1/assertions/verify` | Verify regex, semantic, and schema assertions against output |
| `GET` | `/api/v1/ci/status` | Query latest CI commit quality gate pass/fail status |
| `GET` | `/metrics` | Prometheus telemetry for judge latency and agreement stats |


---

## ⚡ Getting Started & Local Launch

### 1-Click Standalone Windows Launch
Run the automated launcher script to spin up services and launch the browser immediately:
```bat
.\run.bat
```

### Docker Compose Multi-Container Stack
```bash
# 1. Clone repository
git clone https://github.com/Kyrollo/evalgate.git
cd evalgate

# 2. Configure environment credentials
cp .env.example .env

# 3. Boot full stack (Frontend, Backend API, Databases, Workers)
docker compose -f deploy/compose.dev.yml up --build
```

### Local Service Ports Table

| Service Component | Port / Local URL | Swagger / Health Documentation |
|:---|:---:|:---|
| **Web Console UI** | [http://localhost:3002](http://localhost:3002) | Single Page Application (React 19 / Vite) |
| **Backend REST API** | [http://localhost:8002](http://localhost:8002) | OpenAPI Documentation: [http://localhost:8002/docs](http://localhost:8002/docs) |
| **Health Check** | [http://localhost:8002/healthz](http://localhost:8002/healthz) | Health probe endpoint |
| **Prometheus Metrics** | [http://localhost:8002/metrics](http://localhost:8002/metrics) | Real-time telemetry export |

---

## 🧪 CI Quality Gate & Automated Verification

Each commit is validated via automated GitHub Actions CI quality gates:

```bash
# 1. Run backend unit & integration tests with coverage
pytest --cov=backend/src --cov-report=term-missing backend/tests/

# 2. Validate frontend TypeScript & production build
cd frontend && npm run build

# 3. Enforce production policy guard (strict verification of real logic)
python scripts/check_no_simulation.py
```

---

## 📁 Repository Directory Structure

```text
evalgate/
├── backend/            # FastAPI async backend service, domain engines, and APIs
│   ├── src/            # Core architecture implementation & pipelines
│   ├── tests/          # Unit, integration, and e2e test suites
│   └── pyproject.toml  # Python dependencies and build config
├── frontend/           # React 19 + TypeScript + Vite frontend application
│   ├── src/            # UI components, state stores, and API clients
│   └── package.json    # Frontend dependencies and build scripts
├── docs/               # Technical documentation, architecture, and assets
│   └── assets/         # 1080p demo video, high-resolution screenshots
├── deploy/             # Docker Compose configurations (dev, prod, gpu)
├── scripts/            # CI quality checks, smoke tests, and dev utilities
└── run.bat             # Standalone 1-click Windows launcher
```

---

## 👤 Author & Architecture Lead

**Kerollos Mansour**  
AI Platform Architect & Senior Software Engineer  
- 🌐 **Portfolio & Interactive Demos**: [https://kyrollo.github.io](https://kyrollo.github.io)  
- 💼 **GitHub Profile**: [@Kyrollo](https://github.com/Kyrollo)  
- 📧 **Contact**: kirolsmansour@gmail.com  

---

## 📄 License
This project is open-source under the [MIT License](LICENSE).
