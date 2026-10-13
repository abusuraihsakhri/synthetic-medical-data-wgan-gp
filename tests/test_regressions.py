"""Regression tests for audit integrity, identifier handling, and CSV input."""
import csv

import pytest

from agents.base import AuditTrail, SecurityException
from agents.models import SystemTaskPayload
from agents.supervisor import SystemSupervisor
from cli import main as enterprise_main
from medgan_synthesizer.cli import main as legacy_main


def test_hmac_detects_tampering():
    trail = AuditTrail(secret_key="test-key")
    trail.log("test", "tester", "CREATED", {"status": "SUCCESS"})
    trail.log("test", "tester", "UPDATED", {"status": "SUCCESS"})
    assert trail.verify_integrity()
    trail.logs[0]["event_type"] = "DELETED"
    assert not trail.verify_integrity()


def test_hmac_detects_modified_signature():
    trail = AuditTrail(secret_key="test-key")
    trail.log("test", "tester", "CREATED", {"status": "SUCCESS"})
    trail.logs[0]["current_hash"] = "0" * 64
    assert not trail.verify_integrity()


def test_audit_trail_snapshot_cannot_mutate_internal_log():
    trail = AuditTrail(secret_key="test-key")
    trail.log("test", "tester", "CREATED", {"status": "SUCCESS"})
    snapshot = trail.get_trail()
    snapshot[0]["actor"] = "changed"
    snapshot.clear()
    assert len(trail.get_trail()) == 1
    assert trail.verify_integrity()


def test_identifiers_in_attributes_are_screened():
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="TEST-01", target_identifier="SPECIMEN-01",
        primary_metric=5, attributes={"note": "Patient MRN-12345678"}
    )
    with pytest.raises(SecurityException):
        supervisor.process_task(payload)


@pytest.mark.parametrize("entry", ["False", "false", "0", "no", "off", ""])
def test_csv_false_flags_are_not_truthy(tmp_path, entry):
    source = tmp_path / "input.csv"
    target = tmp_path / "output.csv"
    with source.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=[
            "task_id", "target_identifier", "primary_metric",
            "secondary_metric", "is_critical_flag", "status_descriptor"
        ])
        writer.writeheader()
        writer.writerow({
            "task_id": "T1", "target_identifier": "SPECIMEN-01",
            "primary_metric": 4, "secondary_metric": 2,
            "is_critical_flag": entry, "status_descriptor": "NOMINAL"
        })
    assert enterprise_main(["batch", "-i", str(source), "-o", str(target)]) == 0
    with target.open(newline="") as fh:
        row = next(csv.DictReader(fh))
    assert row["overall_urgency"] == "ROUTINE"

    legacy_target = tmp_path / "legacy.csv"
    assert legacy_main(["batch", "-i", str(source), "-o", str(legacy_target)]) == 0
    with legacy_target.open(newline="") as fh:
        row = next(csv.DictReader(fh))
    assert row["overall_status"] == "NOMINAL_OPTIMAL"


@pytest.mark.parametrize("entry", ["maybe", "trueish", "2"])
def test_invalid_csv_booleans_fail_cleanly(tmp_path, entry, capsys):
    source = tmp_path / "input.csv"
    target = tmp_path / "output.csv"
    source.write_text(
        "task_id,target_identifier,primary_metric,is_critical_flag\n"
        "T1,SAMPLE-A,10," + entry + "\n", encoding="utf-8"
    )
    assert enterprise_main(["batch", "-i", str(source), "-o", str(target)]) == 1
    assert not target.exists()
    assert "Invalid CSV row" in capsys.readouterr().err


def test_batch_rejects_overwriting_source(tmp_path):
    source = tmp_path / "input.csv"
    source.write_text("task_id,primary_metric\nT1,12\n", encoding="utf-8")
    assert enterprise_main(["batch", "-i", str(source), "-o", str(source)]) == 1
    assert "T1,12" in source.read_text()
