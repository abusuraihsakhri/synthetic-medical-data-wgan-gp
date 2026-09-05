# Synthetic Medical Data WGAN-GP

> **Domain:** Privacy-Preserving Healthcare & Federated Computing
> **Reference Guidelines & Standards:** `HIPAA Safe Harbor §164.514 & Differential Privacy RDP`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## What It Does

**Synthetic Medical Data WGAN-GP** is a clinical table analysis platform implementing a multi-agent evaluation system with Wasserstein GAN with Gradient Penalty concepts for synthetic data generation. It provides privacy-preserving analysis with Zero-PHI outbound protection and tamper-evident HMAC-SHA256 audit trails.

---

## Key Capabilities & Algorithmic Modules

- **Multi-Agent Evaluation System**: Three specialized workers (InvariantQC, SafetyEscalation, ProtocolConformance) analyze task payloads
- **Zero-PHI Outbound Interceptor**: Active regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers
- **Tamper-Evident HMAC-SHA256 Audit Trail**: Chained, cryptographically signed logs for every evaluation
- **MedGAN Synthesizer**: Wasserstein GAN with Gradient Penalty clinical generator with distribution matching and membership inference defense
- **FastAPI REST API**: OpenAPI 3.1 endpoints with Prometheus telemetry (`/metrics`)
- **Enrichment Suite**: Feature analysis, data quality dashboard, terminology management, ETL monitoring, FHIR analytics, clinical decision support, interoperability, and data governance modules

---

## Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/synthetic-medical-data-wgan-gp.git
cd synthetic-medical-data-wgan-gp

# Install dependencies
pip install fastapi uvicorn pydantic pytest
```

---

## CLI Quickstart & Usage

### 1. Run Single Task Evaluation
```bash
python cli.py audit --task-id TASK-001 --target TARGET-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. Chat with Supervisor
```bash
python cli.py chat "What is the system status?"
```

### 3. Batch Process CSV Records
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch FastAPI REST Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### CLI Parameters

| Parameter | Description | Default |
|:----------|:------------|:--------|
| `--task-id` | Unique task identifier | `TASK-2026-001` |
| `--target` | Target identifier | `KEY-TARGET-01` |
| `--primary` | Primary metric (float) | `28.5` |
| `--secondary` | Secondary metric (float) | `14.2` |
| `--critical` | Critical flag (boolean) | `False` |
| `--status` | Status descriptor | `DISCORDANT` |

### Input Data Schema (CSV Batch)

| Field | Description | Requirement |
|:------|:------------|:------------|
| `task_id` | Task identifier | Required |
| `target_identifier` | Target identifier | Required |
| `primary_metric` | Primary measurement (float) | Required |
| `secondary_metric` | Secondary measurement (float) | Optional |
| `is_critical_flag` | Critical flag (boolean) | Optional |
| `status_descriptor` | Status descriptor | Optional |

---

## REST API Endpoints

| Method | Endpoint | Description |
|:-------|:---------|:------------|
| `GET` | `/health` | Health check |
| `GET` | `/metrics` | Prometheus operational metrics |
| `POST` | `/api/audit` | Submit task for evaluation |
| `POST` | `/api/chat` | Chat with supervisor |
| `GET` | `/api/audit/logs` | Retrieve audit trail |

---

## Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Audit Secret Key:** Configurable via `AUDIT_SECRET_KEY` environment variable. A random key is generated if not set (with a warning).
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## Container Deployment

```bash
docker build -t synthetic-medical-data-wgan-gp .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secret-key synthetic-medical-data-wgan-gp
```

Or using Docker Compose:

```bash
docker-compose up -d
```

---

## Project Structure

```
synthetic-medical-data-wgan-gp/
├── agents/                  # Core multi-agent evaluation system
│   ├── api.py              # FastAPI REST server
│   ├── base.py             # Security, PHI guard, audit trail
│   ├── models.py           # Pydantic data models
│   ├── supervisor.py       # Supervisor orchestrator
│   ├── workers.py          # Specialized worker agents
│   ├── llm_factory.py      # LLM provider factory
│   ├── learning.py         # Bayesian calibration engine
│   ├── metrics.py          # Prometheus metrics collector
│   └── streamer.py         # WebSocket telemetry broadcaster
├── medgan_synthesizer/      # WGAN-GP clinical generator
│   ├── agents.py           # MedGAN coordinator & sub-agents
│   ├── engine.py           # Core algorithmic engine
│   ├── models.py           # Data models
│   ├── cli.py              # MedGAN CLI
│   └── server.py           # MedGAN FastAPI server
├── tests/                   # Pytest test suite
├── web/                     # Operations console (HTML)
├── cli.py                   # Main CLI entry point
├── simulator.py             # High-throughput simulation
├── enrichment.py            # Enrichment feature modules
├── pyproject.toml           # Project configuration
├── Dockerfile               # Container build
└── docker-compose.yml       # Container orchestration
```
