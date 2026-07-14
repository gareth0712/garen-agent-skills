#!/usr/bin/env python3
"""Contained behavioral tests for the vendored runner-owned audit observer."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Callable


HERE = Path(__file__).resolve().parent
OBSERVER = HERE / "run_audit.py"
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))

from run_audit import classify_file  # noqa: E402


def run(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args),
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )


def wait_for(predicate: Callable[[], bool], description: str, timeout: float = 10.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.05)
    raise AssertionError(f"timed out waiting for {description}")


def append_jsonl(path: Path, item: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(item, sort_keys=True) + "\n")


def read_events(audit: Path) -> list[dict[str, Any]]:
    path = audit / "runner-audit.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def wait_for_event(audit: Path, event_type: str, **fields: Any) -> None:
    def found() -> bool:
        return any(
            event.get("event_type") == event_type
            and all(event.get(key) == value for key, value in fields.items())
            for event in read_events(audit)
        )

    wait_for(found, f"{event_type} {fields}")


def initialize_repo(repo: Path) -> None:
    run("git", "init", "--quiet", cwd=repo)
    run("git", "config", "user.email", "audit-smoke@example.invalid", cwd=repo)
    run("git", "config", "user.name", "Runner Audit Smoke Test", cwd=repo)
    (repo / "tracked.txt").write_text("baseline\n", encoding="utf-8")
    run("git", "add", "tracked.txt", cwd=repo)
    run("git", "commit", "--quiet", "-m", "test: baseline", cwd=repo)


def start_observer(repo: Path, output: Path, audit: Path) -> tuple[subprocess.Popen[str], Path, Path]:
    stop = audit / "STOP"
    control = audit / "runner-control.jsonl"
    output.mkdir(parents=True)
    process = subprocess.Popen(
        [
            sys.executable,
            str(OBSERVER),
            "--repo",
            str(repo),
            "--output-root",
            str(output),
            "--audit-dir",
            str(audit),
            "--stop-file",
            str(stop),
            "--control-file",
            str(control),
            "--poll-ms",
            "40",
        ],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    wait_for_event(audit, "runner_started")
    return process, stop, control


def finalize_observer(process: subprocess.Popen[str], audit: Path, stop: Path) -> dict[str, Any]:
    stop.touch()
    stdout, stderr = process.communicate(timeout=10)
    assert process.returncode == 0, f"observer failed\nstdout={stdout}\nstderr={stderr}"
    summary = json.loads((audit / "summary.json").read_text(encoding="utf-8"))
    events = read_events(audit)
    assert events[-1]["event_type"] == "runner_finalized"
    assert [item["event_seq"] for item in events] == list(range(1, len(events) + 1))
    assert all(item.get("timestamp") for item in events)
    return summary


def stop_observer_after_failure(process: subprocess.Popen[str], audit: Path, stop: Path) -> None:
    if process.poll() is not None:
        return
    audit.mkdir(parents=True, exist_ok=True)
    stop.touch()
    try:
        process.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        process.terminate()
        process.communicate(timeout=5)


def write_and_observe(audit: Path, path: Path, relative: str, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    wait_for_event(audit, "output_file_created", path=relative)


def write_lifecycle_outputs(output: Path, audit: Path) -> tuple[Path, Path]:
    write_and_observe(
        audit,
        output / "evidence" / "D-001" / "path-containment-preflight.md",
        "evidence/D-001/path-containment-preflight.md",
        "orchestrator containment preflight: PASS\n",
    )
    report = output / "reports" / "D-001-report.md"
    write_and_observe(audit, report, "reports/D-001-report.md", "# D-001 report\n\nPASS\n")
    evidence = output / "evidence" / "D-001" / "result.txt"
    write_and_observe(audit, evidence, "evidence/D-001/result.txt", "observed signal\n")
    write_and_observe(
        audit,
        output / "evidence" / "D-001" / "path-containment-postwrite.md",
        "evidence/D-001/path-containment-postwrite.md",
        "orchestrator post-write containment: PASS\n",
    )
    return report, evidence


def assert_invalid_location_rejected(repo: Path, output: Path) -> None:
    invalid_audit = output / "runner-audit-must-be-rejected"
    invalid = subprocess.run(
        [
            sys.executable,
            str(OBSERVER),
            "--repo",
            str(repo),
            "--output-root",
            str(output),
            "--audit-dir",
            str(invalid_audit),
            "--stop-file",
            str(invalid_audit / "STOP"),
        ],
        cwd=repo,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    assert invalid.returncode != 0
    assert "outside assigned output root" in invalid.stderr


def test_gate_roles_are_neutral() -> None:
    gate_types = (
        "preference",
        "product_decision",
        "authority",
        "uat",
        "security_legal",
        "external_evidence",
        "capability",
        "environment",
        "internal_recovery",
    )
    for index, gate_type in enumerate(gate_types, start=1):
        role = classify_file(f"gates/G-{index:03d}-{gate_type}.md")
        assert role == "canonical_gate", (gate_type, role)


def test_production_only_invalid_claims_cannot_pass() -> None:
    with tempfile.TemporaryDirectory(prefix="discovery-audit-production-only-") as raw:
        repo = Path(raw).resolve()
        initialize_repo(repo)
        output = repo / "eval" / "outputs"
        audit = repo / "eval" / "runner-audit"
        process, stop, _control = start_observer(repo, output, audit)
        try:
            report, evidence = write_lifecycle_outputs(output, audit)
            production = output / "EVENTS.jsonl"
            append_jsonl(
                production,
                {
                    "event_seq": 9,
                    "event_type": "artifact_sampled",
                    "packet_id": "D-001",
                    "references": [],
                },
            )
            append_jsonl(
                production,
                {
                    "event_seq": 1,
                    "timestamp": "2026-01-01T00:00:01Z",
                    "event_type": "packet_verified",
                    "packet_id": "D-001",
                    "references": [{"path": evidence.relative_to(output).as_posix()}],
                },
            )
            wait_for_event(audit, "production_event_observed", production_event_seq=1)
            summary = finalize_observer(process, audit, stop)
        finally:
            stop_observer_after_failure(process, audit, stop)

        lifecycle = summary["lifecycle"]["D-001"]
        assert lifecycle["sampling_event_seq"] is None
        assert lifecycle["verified_event_seq"] is None
        assert lifecycle["strictly_ordered"] is False
        stream = summary["production_cross_checks"]["files"]["EVENTS.jsonl"]
        assert stream["valid"] is False
        joined_errors = "\n".join(stream["errors"])
        assert "missing_or_invalid_timestamp" in joined_errors
        assert "required_references_empty" in joined_errors
        assert "non_monotonic_event_seq" in joined_errors
        assert "hash_or_revision_missing" in joined_errors
        assert report.is_file()


def test_valid_production_only_claims_cannot_pass() -> None:
    with tempfile.TemporaryDirectory(prefix="discovery-audit-valid-production-only-") as raw:
        repo = Path(raw).resolve()
        initialize_repo(repo)
        output = repo / "eval" / "outputs"
        audit = repo / "eval" / "runner-audit"
        process, stop, _control = start_observer(repo, output, audit)
        try:
            report, evidence = write_lifecycle_outputs(output, audit)
            production = output / "EVENTS.jsonl"
            append_jsonl(
                production,
                {
                    "event_seq": 1,
                    "timestamp": "2026-01-01T00:00:00Z",
                    "event_type": "artifact_sampled",
                    "packet_id": "D-001",
                    "references": [
                        {
                            "path": report.relative_to(output).as_posix(),
                            "sha256": hashlib.sha256(report.read_bytes()).hexdigest(),
                        }
                    ],
                },
            )
            append_jsonl(
                production,
                {
                    "event_seq": 2,
                    "timestamp": "2026-01-01T00:00:01Z",
                    "event_type": "packet_verified",
                    "packet_id": "D-001",
                    "references": [
                        {
                            "path": evidence.relative_to(output).as_posix(),
                            "sha256": hashlib.sha256(evidence.read_bytes()).hexdigest(),
                        }
                    ],
                },
            )
            wait_for_event(audit, "production_event_observed", production_event_seq=2)
            summary = finalize_observer(process, audit, stop)
        finally:
            stop_observer_after_failure(process, audit, stop)

        assert summary["production_cross_checks"]["files"]["EVENTS.jsonl"]["valid"] is True
        lifecycle = summary["lifecycle"]["D-001"]
        assert lifecycle["sampling_event_seq"] is None
        assert lifecycle["verified_event_seq"] is None
        assert lifecycle["strictly_ordered"] is False


def test_sample_without_verification_stays_false() -> None:
    with tempfile.TemporaryDirectory(prefix="discovery-audit-sample-only-") as raw:
        repo = Path(raw).resolve()
        initialize_repo(repo)
        output = repo / "eval" / "outputs"
        audit = repo / "eval" / "runner-audit"
        process, stop, control = start_observer(repo, output, audit)
        try:
            write_lifecycle_outputs(output, audit)
            append_jsonl(
                control,
                {
                    "request_id": "sample-D-001",
                    "action": "sample",
                    "packet_id": "D-001",
                    "paths": ["reports/D-001-report.md", "evidence/D-001/result.txt"],
                },
            )
            wait_for_event(audit, "runner_sample_completed", request_id="sample-D-001")
            summary = finalize_observer(process, audit, stop)
        finally:
            stop_observer_after_failure(process, audit, stop)
        lifecycle = summary["lifecycle"]["D-001"]
        assert lifecycle["sampling_event_seq"] is not None
        assert lifecycle["verified_event_seq"] is None
        assert lifecycle["strictly_ordered"] is False


def test_runner_control_produces_strict_order() -> None:
    with tempfile.TemporaryDirectory(prefix="discovery-audit-valid-control-") as raw:
        repo = Path(raw).resolve()
        initialize_repo(repo)
        output = repo / "eval" / "outputs"
        audit = repo / "eval" / "runner-audit"
        assert_invalid_location_rejected(repo, output)
        process, stop, control = start_observer(repo, output, audit)
        try:
            report, evidence = write_lifecycle_outputs(output, audit)
            production = output / "EVENTS.jsonl"
            append_jsonl(
                production,
                {
                    "event_seq": 1,
                    "timestamp": "2026-01-01T00:00:00Z",
                    "event_type": "artifact_sampled",
                    "packet_id": "D-001",
                    "references": [
                        {
                            "path": report.relative_to(output).as_posix(),
                            "sha256": hashlib.sha256(report.read_bytes()).hexdigest(),
                        }
                    ],
                },
            )
            append_jsonl(
                production,
                {
                    "event_seq": 2,
                    "timestamp": "2026-01-01T00:00:01Z",
                    "event_type": "packet_verified",
                    "packet_id": "D-001",
                    "references": [
                        {
                            "path": evidence.relative_to(output).as_posix(),
                            "sha256": hashlib.sha256(evidence.read_bytes()).hexdigest(),
                        }
                    ],
                },
            )
            wait_for_event(audit, "production_event_observed", production_event_seq=2)

            append_jsonl(
                control,
                {
                    "request_id": "verify-too-early",
                    "action": "verify",
                    "packet_id": "D-001",
                    "sample_request_id": "not-yet-sampled",
                },
            )
            wait_for_event(audit, "runner_control_rejected", request_id="verify-too-early")
            append_jsonl(
                control,
                {
                    "request_id": "sample-D-001",
                    "action": "sample",
                    "packet_id": "D-001",
                    "paths": ["reports/D-001-report.md", "evidence/D-001/result.txt"],
                },
            )
            wait_for_event(audit, "runner_sample_completed", request_id="sample-D-001")
            append_jsonl(
                control,
                {
                    "request_id": "verify-D-001",
                    "action": "verify",
                    "packet_id": "D-001",
                    "sample_request_id": "sample-D-001",
                },
            )
            wait_for_event(audit, "runner_verification_accepted", request_id="verify-D-001")
            summary = finalize_observer(process, audit, stop)
        finally:
            stop_observer_after_failure(process, audit, stop)

        assert summary["schema"] == "runner-audit-v1"
        assert summary["assigned_output_root"] == str(output)
        assert summary["runner_audit_root"] == str(audit)
        assert summary["tracked_head_unchanged"] is True
        assert summary["tracked_status_unchanged"] is True
        assert summary["new_nonignored_untracked_outside_output"] == []
        lifecycle = summary["lifecycle"]["D-001"]
        assert lifecycle["strictly_ordered"] is True
        assert lifecycle["containment_before_sampling"] is True
        assert summary["production_cross_checks"]["files"]["EVENTS.jsonl"]["valid"] is True
        assert summary["observation_scope"]["unaudited"]
        assert "Only observed scopes" in summary["observation_scope"]["clean_claim_boundary"]

        events = read_events(audit)
        report_event = next(item for item in events if item.get("path") == "reports/D-001-report.md")
        preflight_event = next(
            item for item in events if item.get("path", "").endswith("path-containment-preflight.md")
        )
        sample_event = next(
            item
            for item in events
            if item.get("event_type") == "runner_artifact_sampled"
            and item.get("path") == "reports/D-001-report.md"
        )
        assert preflight_event["role"] == "orchestrator_preflight_evidence"
        assert report_event["sha256"] == hashlib.sha256(report.read_bytes()).hexdigest()
        assert sample_event["sha256"] == report_event["sha256"]
        summary_path = audit / "summary.json"
        assert events[-1]["summary_sha256"] == hashlib.sha256(summary_path.read_bytes()).hexdigest()


def main() -> None:
    assert OBSERVER.is_file(), f"observer missing: {OBSERVER}"
    test_gate_roles_are_neutral()
    test_production_only_invalid_claims_cannot_pass()
    test_valid_production_only_claims_cannot_pass()
    test_sample_without_verification_stays_false()
    test_runner_control_produces_strict_order()
    print("runner audit smoke test: PASS")


if __name__ == "__main__":
    main()
