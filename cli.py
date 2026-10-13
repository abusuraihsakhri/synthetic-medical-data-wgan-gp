"""
Command Line Interface for Synthetic Medical Data Wgan Gp.
"""
import argparse
import csv
import json
import sys
from pathlib import Path
from agents.models import SystemTaskPayload
from agents.supervisor import SystemSupervisor
from agents.base import AuditLogger, SecurityException

supervisor = SystemSupervisor(model_provider="mock")



def parse_boolean(value):
    """Parse CSV boolean values without treating 'False' as True."""
    if isinstance(value, bool):
        return value
    normalized = str(value if value is not None else "").strip().lower()
    if normalized in ("true", "1", "yes", "y", "on"):
        return True
    if normalized in ("false", "0", "no", "n", "off", ""):
        return False
    raise ValueError(f"Invalid boolean value: {value!r}")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="synthetic-medical-data-wgan-gp", description="Synthetic Medical Data Wgan Gp")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Audit
    p_audit = subparsers.add_parser("audit", help="Run single task evaluation")
    p_audit.add_argument("--task-id", default="TASK-2026-001")
    p_audit.add_argument("--target", default="KEY-TARGET-01")
    p_audit.add_argument("--primary", type=float, default=28.5)
    p_audit.add_argument("--secondary", type=float, default=14.2)
    p_audit.add_argument("--critical", action="store_true")
    p_audit.add_argument("--status", default="DISCORDANT")

    # Chat
    p_chat = subparsers.add_parser("chat", help="System configuration query")
    p_chat.add_argument("query", nargs="+")

    # Batch
    p_batch = subparsers.add_parser("batch", help="Batch process CSV records")
    p_batch.add_argument("-i", "--input", required=True)
    p_batch.add_argument("-o", "--output", default="results.csv")

    # Verify Audit
    subparsers.add_parser("verify-audit", help="Verify HMAC audit trail integrity")

    # Serve
    p_serve = subparsers.add_parser("serve", help="Launch FastAPI REST server")
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=8000)

    args = parser.parse_args(argv)

    if args.command == "audit":
        payload = SystemTaskPayload(
            task_id=args.task_id,
            target_identifier=args.target,
            primary_metric=args.primary,
            secondary_metric=args.secondary,
            status_descriptor=args.status,
            is_critical_flag=args.critical,
        )
        dossier = supervisor.process_task(payload)
        print("=" * 80)
        print(f"  SYNTHETIC MEDICAL DATA WGAN GP")
        print(f"  Domain: Privacy-Preserving Federated Healthcare & FHE | Standard: HIPAA Safe Harbor §164.514 / Google SecAgg Standards")
        print(f"  Dossier ID: {dossier.dossier_id} | Urgency: [{dossier.overall_urgency.value}]")
        print("=" * 80)
        for a in dossier.alerts:
            print(f"\n  [{a.urgency.value}] from {a.origin_worker}:")
            print(f"  Summary: {a.summary}")
            print(f"  Details: {a.technical_details}")
            print(f"  Action:  {a.actionable_remediation}")
        print(f"\n  HMAC-SHA256 Audit Hash: {dossier.audit_hash}")
        print("=" * 80)
        return 0

    if args.command == "chat":
        ans = supervisor.query_supervisory_chat(" ".join(args.query))
        print(f"\n[Synthetic Medical Data Wgan Gp Supervisor]:\n{ans}\n")
        return 0

    if args.command == "verify-audit":
        trail = AuditLogger.get_trail()
        valid = AuditLogger.verify_integrity()
        print(f"Audit Trail Blocks: {len(trail)} | Cryptographic Integrity Verified: {valid}")
        return 0

    if args.command == "batch":
        try:
            with open(args.input, mode="r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                fieldnames = list(reader.fieldnames or [])
                rows = list(reader)
        except OSError as exc:
            print(f"Error: Cannot read input CSV: {exc}", file=sys.stderr)
            return 1

        if not fieldnames:
            print("Error: CSV file has no header.", file=sys.stderr)
            return 1
        output_fields = ["overall_urgency", "integrity_status", "total_alerts", "audit_hash"]
        if any(name in fieldnames for name in output_fields):
            print("Error: Input CSV already contains an output column.", file=sys.stderr)
            return 1
        if Path(args.input).resolve() == Path(args.output).resolve():
            print("Error: Input and output paths must differ.", file=sys.stderr)
            return 1

        out_fields = fieldnames + output_fields
        out_rows = []
        for line_number, row in enumerate(rows, start=2):
            try:
                if None in row or not (row.get("primary_metric") or "").strip():
                    raise ValueError("Malformed row or missing primary_metric")
                payload = SystemTaskPayload(
                    task_id=row.get("task_id") or "TASK-01",
                    target_identifier=row.get("target_identifier") or "TARGET-01",
                    primary_metric=float(row["primary_metric"]),
                    secondary_metric=float(row.get("secondary_metric") or 5.0),
                    status_descriptor=row.get("status_descriptor") or "NOMINAL",
                    is_critical_flag=parse_boolean(row.get("is_critical_flag")),
                )
                dossier = supervisor.process_task(payload)
                enriched = dict(row)
                enriched["overall_urgency"] = dossier.overall_urgency.value
                enriched["integrity_status"] = dossier.integrity_status.value
                enriched["total_alerts"] = dossier.total_alerts
                enriched["audit_hash"] = dossier.audit_hash
                out_rows.append(enriched)
            except (ValueError, TypeError, KeyError, SecurityException) as exc:
                print(f"Error: Invalid CSV row {line_number}: {exc}", file=sys.stderr)
                return 1

        try:
            with open(args.output, mode="w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=out_fields)
                writer.writeheader()
                writer.writerows(out_rows)
        except OSError as exc:
            print(f"Error: Cannot write output CSV: {exc}", file=sys.stderr)
            return 1
        print(f"Processed {len(out_rows)} records -> {args.output}")
        return 0

    if args.command == "serve":
        import uvicorn
        from agents.api import app
        print(f"Starting Synthetic Medical Data Wgan Gp API server on http://{args.host}:{args.port}")
        uvicorn.run(app, host=args.host, port=args.port)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
