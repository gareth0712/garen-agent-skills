#!/usr/bin/env python3
"""Contained smoke test for the vendored runner-owned audit observer."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
OBSERVER = HERE / "run_audit.py"


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


def wait_for(predicate, description: str, timeout: float = 10.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.05)
    raise AssertionError(f"timed out waiting for {description}")


def append_event(path: Path, event: dict[str, object]) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")


def exercise_observer(process: subprocess.Popen[str], output: Path, audit: Path, stop: Path) -> None:
    events_path = audit / "runner-audit.jsonl"
    wait_for(
        lambda: events_path.exists() and "runner_started" in events_path.read_text(encoding="utf-8"),
        "runner_started",
    )

    preflight = output / "evidence" / "D-001" / "path-containment-preflight.md"
    preflight.parent.mkdir(parents=True)
    preflight.write_text("orchestrator containment preflight: PASS\n", encoding="utf-8")
    time.sleep(0.15)

    report = output / "reports" / "D-001-report.md"
    report.parent.mkdir(parents=True)
    report.write_text("# D-001 report\n\nPASS\n", encoding="utf-8")
    time.sleep(0.15)

    evidence = output / "evidence" / "D-001" / "result.txt"
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text("observed signal\n", encoding="utf-8")
    time.sleep(0.15)

    postwrite = output / "evidence" / "D-001" / "path-containment-postwrite.md"
    postwrite.write_text("orchestrator post-write containment: PASS\n", encoding="utf-8")
    time.sleep(0.15)

    production_events = output / "EVENTS.jsonl"
    append_event(
        production_events,
        {
            "event_seq": 1,
            "timestamp": "2026-01-01T00:00:00Z",
            "event_type": "artifact_sampled",
            "stage": "DISCOVERY",
            "packet_id": "D-001",
            "references": [{"path": "reports/D-001-report.md"}],
        },
    )
    time.sleep(0.15)
    append_event(
        production_events,
        {
            "event_seq": 2,
            "timestamp": "2026-01-01T00:00:01Z",
            "event_type": "packet_verified",
            "stage": "DISCOVERY",
            "packet_id": "D-001",
            "references": [{"path": "evidence/D-001/result.txt"}],
        },
    )
    time.sleep(0.15)

    stop.touch()
    stdout, stderr = process.communicate(timeout=10)
    assert process.returncode == 0, f"observer failed\nstdout={stdout}\nstderr={stderr}"

    summary_path = audit / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    events = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines()]

    assert summary["schema"] == "runner-audit-v1"
    assert summary["assigned_output_root"] == str(output)
    assert summary["runner_audit_root"] == str(audit)
    assert summary["tracked_head_unchanged"] is True
    assert summary["tracked_status_unchanged"] is True
    assert summary["new_nonignored_untracked_outside_output"] == []
    assert summary["lifecycle"]["D-001"]["strictly_ordered"] is True
    assert summary["lifecycle"]["D-001"]["containment_before_sampling"] is True
    assert summary["observation_scope"]["unaudited"]
    assert "Only observed scopes" in summary["observation_scope"]["clean_claim_boundary"]
    assert events[-1]["event_type"] == "runner_finalized"
    assert [item["event_seq"] for item in events] == list(range(1, len(events) + 1))
    assert all(item.get("timestamp") for item in events)

    report_event = next(item for item in events if item.get("path") == "reports/D-001-report.md")
    preflight_event = next(item for item in events if item.get("path", "").endswith("path-containment-preflight.md"))
    assert preflight_event["role"] == "orchestrator_preflight_evidence"
    expected_hash = hashlib.sha256(report.read_bytes()).hexdigest()
    assert report_event["sha256"] == expected_hash
    expected_summary_hash = hashlib.sha256(summary_path.read_bytes()).hexdigest()
    assert events[-1]["summary_sha256"] == expected_summary_hash


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


def main() -> None:
    assert OBSERVER.is_file(), f"observer missing: {OBSERVER}"
    with tempfile.TemporaryDirectory(prefix="discovery-runner-audit-") as raw:
        repo = Path(raw).resolve()
        output = repo / "eval" / "with_skill" / "outputs"
        audit = repo / "eval" / "with_skill" / "runner-audit"
        stop = audit / "STOP"
        output.mkdir(parents=True)

        run("git", "init", "--quiet", cwd=repo)
        run("git", "config", "user.email", "audit-smoke@example.invalid", cwd=repo)
        run("git", "config", "user.name", "Runner Audit Smoke Test", cwd=repo)
        (repo / "tracked.txt").write_text("baseline\n", encoding="utf-8")
        run("git", "add", "tracked.txt", cwd=repo)
        run("git", "commit", "--quiet", "-m", "test: baseline", cwd=repo)

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

        try:
            exercise_observer(process, output, audit, stop)
        finally:
            stop_observer_after_failure(process, audit, stop)

    print("runner audit smoke test: PASS")


if __name__ == "__main__":
    main()
