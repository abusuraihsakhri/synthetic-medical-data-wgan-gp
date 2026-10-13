"""
Command-Line Interface for MedGAN-Synthesizer: Wasserstein GAN with Gradient Penalty Clinical Generator.
"""
import argparse
import csv
import json
import sys
from pathlib import Path
from .models import FrontierPayload
from .agents import MedGANCoordinator

coordinator = MedGANCoordinator()



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
    parser = argparse.ArgumentParser(prog="synthetic-medical-data-wgan-gp", description="MedGAN-Synthesizer: Wasserstein GAN with Gradient Penalty Clinical Generator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Audit
    p_audit = subparsers.add_parser("audit", help="Run single task evaluation")
    p_audit.add_argument("--task-id", default="TASK-2026-001")
    p_audit.add_argument("--target", default="TARGET-GEN-01")
    p_audit.add_argument("--primary", type=float, default=29.4)
    p_audit.add_argument("--secondary", type=float, default=15.1)
    p_audit.add_argument("--critical", action="store_true")
    p_audit.add_argument("--status", default="DISCORDANT")

    # Chat
    p_chat = subparsers.add_parser("chat", help="System configuration query")
    p_chat.add_argument("query", nargs="+")

    # Batch
    p_batch = subparsers.add_parser("batch", help="Batch process CSV records")
    p_batch.add_argument("-i", "--input", required=True)
    p_batch.add_argument("-o", "--output", default="results.csv")

    # Serve
    p_serve = subparsers.add_parser("serve", help="Launch FastAPI REST server")
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=8000)

    args = parser.parse_args(argv)

    if args.command == "audit":
        payload = FrontierPayload(
            task_id=args.task_id,
            target_identifier=args.target,
            primary_metric=args.primary,
            secondary_metric=args.secondary,
            status_descriptor=args.status,
            is_critical_flag=args.critical,
        )
        dossier = coordinator.process(payload)
        print("=" * 80)
        print(f"  MEDGAN-SYNTHESIZER: WASSERSTEIN GAN WITH GRADIENT PENALTY CLINICAL GENERATOR")
        print(f"  Domain: Privacy-Preserving Federated Healthcare & FHE | Standard: Synthetic Data Generation Best Practices")
        print(f"  Task: {dossier['task_id']} | Status: [{dossier['overall_status']}] | Total Alerts: {dossier['total_alerts']}")
        print("=" * 80)
        for a in dossier["alerts"]:
            print(f"\n  [{a['status']}] from {a['origin_agent']}:")
            print(f"  Summary: {a['summary']}")
            print(f"  Details: {a['technical_details']}")
            print(f"  Action:  {a['actionable_remediation']}")
        print("\n" + "=" * 80)
        return 0

    if args.command == "chat":
        ans = coordinator.query_supervisory_chat(" ".join(args.query))
        print(f"\n[MedGANCoordinator]:\n{ans}\n")
        return 0

    if args.command == "batch":
        try:
            with open(args.input, mode="r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                fieldnames = list(reader.fieldnames or [])
                rows = list(reader)
        except FileNotFoundError:
            print(f"Error: Input file '{args.input}' not found.", file=sys.stderr)
            return 1
        except PermissionError:
            print(f"Error: Permission denied reading '{args.input}'.", file=sys.stderr)
            return 1

        if not fieldnames:
            print("Error: CSV file has no header.", file=sys.stderr)
            return 1
        output_fields = ["overall_status","total_alerts","critical_count","consensus_summary"]
        if any(name in fieldnames for name in output_fields):
            print("Error: Input CSV already contains an output column.", file=sys.stderr)
            return 1
        if Path(args.input).resolve() == Path(args.output).resolve():
            print("Error: Input and output paths must differ.", file=sys.stderr)
            return 1

        out_fields = fieldnames + output_fields
        out_rows = []
        for line_number, r in enumerate(rows, start=2):
            try:
                if None in r or not (r.get("primary_metric") or "").strip():
                    raise ValueError("Malformed row or missing primary_metric")
                payload = FrontierPayload(
                    task_id=r.get("task_id") or "TASK-01",
                    target_identifier=r.get("target_identifier") or "TARGET-01",
                    primary_metric=float(r["primary_metric"]),
                    secondary_metric=float(r.get("secondary_metric") or 5.0),
                    status_descriptor=r.get("status_descriptor") or "NOMINAL",
                    is_critical_flag=parse_boolean(r.get("is_critical_flag")),
                )
                dossier = coordinator.process(payload)
                row_dict = dict(r)
                row_dict["overall_status"] = dossier["overall_status"]
                row_dict["total_alerts"] = dossier["total_alerts"]
                row_dict["critical_count"] = dossier["critical_count"]
                row_dict["consensus_summary"] = dossier["consensus_summary"]
                out_rows.append(row_dict)
            except (ValueError, TypeError, KeyError) as exc:
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
        try:
            import uvicorn
            from .server import create_app
            app = create_app()
            if app:
                print(f"Starting MedGAN-Synthesizer: Wasserstein GAN with Gradient Penalty Clinical Generator on http://{args.host}:{args.port}")
                uvicorn.run(app, host=args.host, port=args.port)
            else:
                print("FastAPI is not installed.", file=sys.stderr)
                return 1
        except ImportError:
            print("FastAPI / uvicorn not installed. Run 'pip install fastapi uvicorn'")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
