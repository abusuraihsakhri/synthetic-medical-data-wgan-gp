# Synthetic Medical Data WGAN-GP

A Python repository containing **deterministic threshold-evaluation utilities** and a browser-based audit demonstration. Despite the historical repository name, the checked-in source **does not implement WGAN-GP training, gradient penalties, synthetic EHR sampling, federated learning, formal differential privacy, or membership-inference measurements**. It must not be represented as a validated medical-data synthesizer.

## What works

- A three-worker audit pipeline for primary metrics, secondary metrics and descriptor flags, with routine/elevated/critical classifications.
- A FastAPI service exposing health, metrics, audit, chat-stub and audit-log endpoints.
- A SHA-256/HMAC-chained, **in-memory** audit trail; integrity verification recomputes signatures and validates link continuity.
- CSV batch processing through the Python CLI and JSON results through the API.
- A standalone [local browser demonstration](web/index.html) with JSON download. It executes the corresponding threshold rules entirely in the browser and does **not** sign its results.
- A separate legacy `medgan_synthesizer` CLI/API with a similar threshold evaluator (different thresholds).
- Eight general-purpose enrichment modules that reuse threshold checks; they do not implement full FHIR analytics, terminology systems or data-quality pipelines.

The thresholds (`primary_metric > 25` and `secondary_metric > 12`, plus descriptor keywords and the critical flag) are **illustrative software rules**, not clinically derived or validated reference limits.

## Requirements and installation

CI is configured to test Python 3.10–3.12. From the repository root:

```bash
python -m pip install -e ".[api,dev]"
python -m pytest -q
```

The `pydantic` runtime dependency is declared in `pyproject.toml`; the `api` extra installs FastAPI and Uvicorn. The installed `synthetic-medical-data-wgan-gp` command currently invokes the **legacy** `medgan_synthesizer` CLI. For the main three-worker service, run `python cli.py` explicitly.

## Main command-line workflows

```bash
python cli.py audit --task-id DEMO-001 --target SAMPLE-A --primary 29.4 --secondary 14.8 --critical --status DISCORDANT
python cli.py chat "What can this supervisor do?"
python cli.py batch -i sample.csv -o results.csv
python cli.py verify-audit
python cli.py serve --host 127.0.0.1 --port 8000
```

Batch input CSV columns: `task_id`, `target_identifier`, `primary_metric`, `secondary_metric`, `is_critical_flag`, `status_descriptor`. The primary metric is required; missing optional metrics use the CLI's default. Critical flag values accept `true/false`, `yes/no` or `1/0` (case-insensitive); ambiguous values are rejected. The output is a separate CSV file.

For the legacy CLI, run `python medgan_synthesizer_app.py --help` or the installed `synthetic-medical-data-wgan-gp --help`.

## Local API

Start the server with `python cli.py serve` and visit `http://127.0.0.1:8000/docs` for the live OpenAPI schema.

| Method | Path | Output |
| --- | --- | --- |
| GET | `/health` | Service status |
| GET | `/metrics` | JSON counters (not Prometheus exposition format) |
| POST | `/api/audit` | Evaluated task dossier |
| POST | `/api/chat` | Deterministic mock response; **not an LLM** |
| GET | `/api/audit/logs` | In-memory audit entries and signature verification |

Example:

```bash
curl -X POST http://127.0.0.1:8000/api/audit \
  -H 'Content-Type: application/json' \
  -d '{"task_id":"DEMO-001","target_identifier":"SAMPLE-A","primary_metric":18,"secondary_metric":2}'
```

There is no built-in user authentication or persistence. **Do not expose this service directly to the public Internet or send actual clinical records.** A deployment handling real data requires application security and a formal privacy review beyond this repository.

## Browser application / GitHub Pages

Open `web/index.html` in a modern desktop or mobile browser for offline, client-side demonstration of the audit logic. All input evaluation stays on the local page; no storage or server calls are used for evaluation. The optional linked GitHub repository is an external site, and no claim is made that arbitrary patient identifiers are safe.

`.github/workflows/pages.yml` is configured to deploy the `web/` directory from `master`. Publishing requires GitHub Pages to be configured for **GitHub Actions** in repository settings. A live Pages URL should be advertised only after successful deployment and direct verification.

This site does not run Python or Pyodide: the deterministic audit rules are implemented in JavaScript, while the Python API remains a separate backend. Real model training would require a substantial new implementation and appropriate compute/runtime support.

## Container

The Compose configuration requires a private audit key from the environment. For local testing:

```bash
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
docker compose up --build
```

Set and persist a strong secret through your deployment's secret manager in production. Do not reuse the previously committed sample key; treat it as publicly exposed. The audit ledger is stored only in memory and is lost on process restart; an ephemeral key is generated for non-Compose use if `AUDIT_SECRET_KEY` is unset, with a warning.

## Security and limitations

The identifier guard detects a **limited set of regex patterns** (e.g. MRNs, SSNs, some telephone numbers, names and email addresses). It is **not** comprehensive de-identification and does not establish HIPAA Safe Harbor compliance, privacy guarantees, or absence of protected health information. The audit chain detects tampering in its current in-memory records when the signing key is trusted, but has no durable independent storage or key management. The static demo has no cryptographic signatures.

Results are not clinical recommendations. There is no demonstrated distribution matching or re-identification-risk evaluation.

## Development and verification

```bash
python -m pytest -q
python -m compileall -q agents medgan_synthesizer cli.py enrichment.py simulator.py
python simulator.py 100
```

GitHub Actions checks Python 3.10, 3.11 and 3.12, CLI batch behavior, Python syntax, and JavaScript syntax. No lockfile is currently maintained. The static UI has no external JavaScript dependencies and is responsive to narrow screens.

**License:** [MIT](LICENSE).
