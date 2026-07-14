#!/usr/bin/env python3
"""Runner-owned filesystem/Git observer for cold-start skill evaluations."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PACKET_RE = re.compile(r"(?:^|[^A-Z0-9])(D-\d{3})(?:[^A-Z0-9]|$)", re.I)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_git(repo: Path, *args: str) -> dict[str, Any]:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return {
        "command": ["git", *args],
        "exit_code": completed.returncode,
        "stdout_lines": completed.stdout.splitlines(),
        "stderr_excerpt": completed.stderr[:1000],
    }


def git_snapshot(repo: Path) -> dict[str, Any]:
    head = run_git(repo, "rev-parse", "HEAD")
    tracked = run_git(repo, "status", "--porcelain=v1", "--untracked-files=no")
    untracked = run_git(repo, "ls-files", "--others", "--exclude-standard")
    return {
        "captured_at": utc_now(),
        "head": head["stdout_lines"][0] if head["exit_code"] == 0 and head["stdout_lines"] else None,
        "tracked_status": tracked,
        "nonignored_untracked": untracked,
    }


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def snapshot_files(root: Path) -> dict[str, dict[str, Any]]:
    if not root.exists():
        return {}
    result: dict[str, dict[str, Any]] = {}
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        stat = path.stat()
        relative = path.relative_to(root).as_posix()
        result[relative] = {
            "absolute_path": str(path),
            "size": stat.st_size,
            "mtime_ns": stat.st_mtime_ns,
            "sha256": sha256(path),
        }
    return result


def packet_from(*values: str | None) -> str | None:
    for value in values:
        if not value:
            continue
        match = PACKET_RE.search(value)
        if match:
            return match.group(1).upper()
    return None


def classify_file(relative: str) -> str:
    lowered = relative.lower()
    name = Path(relative).name.lower()
    if "/reports/" in f"/{lowered}" or re.match(r"d-\d{3}-report\.md$", name):
        return "worker_report"
    if "/evidence/" in f"/{lowered}" and name in {"preflight.md", "path-containment-preflight.md"}:
        return "orchestrator_preflight_evidence"
    if "/evidence/" in f"/{lowered}" and name == "path-containment-postwrite.md":
        return "orchestrator_postwrite_containment"
    if "/evidence/" in f"/{lowered}":
        return "worker_evidence"
    if name == "events.jsonl":
        return "production_events"
    if name == "agent-state.md":
        return "control_state"
    if "/packets/" in f"/{lowered}":
        return "packet_contract"
    if "/gates/" in f"/{lowered}":
        return "human_gate"
    return "other_output"


class Audit:
    def __init__(self, repo: Path, output: Path, audit_dir: Path, stop_file: Path, poll_ms: int):
        self.repo = repo.resolve()
        self.output = output.resolve()
        self.audit_dir = audit_dir.resolve()
        self.stop_file = stop_file.resolve()
        self.poll_seconds = poll_ms / 1000
        self.events_path = self.audit_dir / "runner-audit.jsonl"
        self.summary_path = self.audit_dir / "summary.json"
        self.seq = 0
        self.events: list[dict[str, Any]] = []
        self.files: dict[str, dict[str, Any]] = {}
        self.production_lines_seen: dict[str, int] = {}
        self.initial_git = git_snapshot(self.repo)

    def emit(self, event_type: str, **fields: Any) -> None:
        self.seq += 1
        event = {
            "event_seq": self.seq,
            "timestamp": utc_now(),
            "event_type": event_type,
            **fields,
        }
        self.events.append(event)
        with self.events_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")

    def observe_files(self) -> None:
        current = snapshot_files(self.output)
        changed = [
            (relative, metadata)
            for relative, metadata in current.items()
            if relative not in self.files or self.files[relative]["sha256"] != metadata["sha256"]
        ]
        # Detection order is not creation order when several writes land inside one
        # polling interval. NTFS mtimes preserve the stronger runner-observed signal.
        for relative, metadata in sorted(changed, key=lambda item: (item[1]["mtime_ns"], item[0])):
            previous = self.files.get(relative)
            role = classify_file(relative)
            self.emit(
                "output_file_created" if previous is None else "output_file_modified",
                path=relative,
                absolute_path=metadata["absolute_path"],
                sha256=metadata["sha256"],
                size=metadata["size"],
                mtime_ns=metadata["mtime_ns"],
                role=role,
                packet_id=packet_from(relative),
            )
        for relative, metadata in self.files.items():
            if relative not in current:
                self.emit(
                    "output_file_deleted",
                    path=relative,
                    sha256=metadata["sha256"],
                    role=classify_file(relative),
                    packet_id=packet_from(relative),
                )
        self.files = current

    def observe_production_events(self) -> None:
        for path in sorted(self.output.rglob("EVENTS.jsonl")) if self.output.exists() else []:
            relative = path.relative_to(self.output).as_posix()
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            start = self.production_lines_seen.get(relative, 0)
            for line_number, raw in enumerate(lines[start:], start=start + 1):
                try:
                    item = json.loads(raw)
                except json.JSONDecodeError as error:
                    self.emit(
                        "production_event_parse_error",
                        path=relative,
                        line_number=line_number,
                        error=str(error),
                    )
                    continue
                source_type = str(item.get("event_type", "unknown"))
                packet_id = item.get("packet_id") or packet_from(json.dumps(item, ensure_ascii=False))
                self.emit(
                    "production_event_observed",
                    path=relative,
                    line_number=line_number,
                    line_sha256=hashlib.sha256(raw.encode("utf-8")).hexdigest(),
                    production_event_type=source_type,
                    production_event_seq=item.get("event_seq"),
                    production_timestamp=item.get("timestamp"),
                    packet_id=packet_id,
                    referenced_paths=item.get("references", []),
                )
                if source_type == "artifact_sampled":
                    self.emit(
                        "orchestrator_sampling_event_observed",
                        source="production_EVENTS_cross_check",
                        packet_id=packet_id,
                        production_event_seq=item.get("event_seq"),
                        referenced_paths=item.get("references", []),
                    )
                if source_type == "packet_verified" or (
                    source_type == "packet_status_transition" and item.get("to_status") == "verified"
                ):
                    self.emit(
                        "verified_transition_observed",
                        source="production_EVENTS_cross_check",
                        packet_id=packet_id,
                        production_event_seq=item.get("event_seq"),
                        referenced_paths=item.get("references", []),
                    )
            self.production_lines_seen[relative] = len(lines)

    def lifecycle_summary(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        packet_ids = sorted({event.get("packet_id") for event in self.events if event.get("packet_id")})
        for packet_id in packet_ids:
            report = next((e for e in self.events if e.get("packet_id") == packet_id and e.get("role") == "worker_report" and e["event_type"] == "output_file_created"), None)
            evidence = next((e for e in self.events if e.get("packet_id") == packet_id and e.get("role") == "worker_evidence" and e["event_type"] == "output_file_created"), None)
            sampled = next((e for e in self.events if e.get("packet_id") == packet_id and e["event_type"] == "orchestrator_sampling_event_observed"), None)
            verified = next((e for e in self.events if e.get("packet_id") == packet_id and e["event_type"] == "verified_transition_observed"), None)
            containment = next((e for e in self.events if e.get("packet_id") == packet_id and e.get("role") == "orchestrator_postwrite_containment" and e["event_type"] == "output_file_created"), None)
            ordered = bool(report and evidence and sampled and verified and report["event_seq"] < evidence["event_seq"] < sampled["event_seq"] < verified["event_seq"])
            result[packet_id] = {
                "report_write_event_seq": report["event_seq"] if report else None,
                "evidence_write_event_seq": evidence["event_seq"] if evidence else None,
                "postwrite_containment_event_seq": containment["event_seq"] if containment else None,
                "containment_before_sampling": bool(containment and sampled and containment["event_seq"] < sampled["event_seq"]),
                "sampling_event_seq": sampled["event_seq"] if sampled else None,
                "verified_event_seq": verified["event_seq"] if verified else None,
                "strictly_ordered": ordered,
                "note": "Sampling/verified observations are runner-recorded cross-checks of production EVENTS claims; filesystem report/evidence writes are independently hashed.",
            }
        return result

    def finalize(self) -> None:
        self.observe_files()
        self.observe_production_events()
        final_git = git_snapshot(self.repo)
        initial_untracked = set(self.initial_git["nonignored_untracked"]["stdout_lines"])
        final_untracked = set(final_git["nonignored_untracked"]["stdout_lines"])

        def runner_owned(relative: str) -> bool:
            absolute = (self.repo / relative).resolve()
            return is_relative_to(absolute, self.audit_dir) or absolute == self.stop_file

        new_untracked = sorted(final_untracked - initial_untracked)
        new_untracked_outside_output = [
            value
            for value in new_untracked
            if not is_relative_to((self.repo / value).resolve(), self.output) and not runner_owned(value)
        ]
        code_suffixes = {".c", ".cpp", ".go", ".java", ".js", ".jsx", ".py", ".rb", ".rs", ".swift", ".ts", ".tsx"}
        production_code_candidates = sorted(
            relative
            for relative in self.files
            if Path(relative).suffix.lower() in code_suffixes and "/evidence/" not in f"/{relative.lower()}" and "/prototypes/" not in f"/{relative.lower()}"
        )
        summary = {
            "schema": "runner-audit-v1",
            "created_at": utc_now(),
            "repo_root": str(self.repo),
            "assigned_output_root": str(self.output),
            "runner_audit_root": str(self.audit_dir),
            "initial_git": self.initial_git,
            "final_git": final_git,
            "tracked_head_unchanged": self.initial_git["head"] == final_git["head"],
            "tracked_status_unchanged": self.initial_git["tracked_status"]["stdout_lines"] == final_git["tracked_status"]["stdout_lines"],
            "created_or_final_output_files": sorted(self.files),
            "new_nonignored_untracked_outside_output": new_untracked_outside_output,
            "production_code_candidates_under_output": production_code_candidates,
            "lifecycle": self.lifecycle_summary(),
            "observation_scope": {
                "observed": [
                    "assigned output-root file creation/modification/deletion with SHA-256 and mtime",
                    "repository tracked HEAD and tracked status at runner start/end",
                    "repository nonignored untracked path set at runner start/end",
                    "production EVENTS.jsonl append lines as cross-check claims",
                ],
                "unaudited": [
                    "network and remote service side effects",
                    "filesystem writes outside the repository/worktree",
                    "ignored paths outside the assigned output and runner-audit roots",
                    "credential stores, messages, publishing, purchases, deployments, and external process state",
                    "host-private tool transcripts and read syscalls; sampling is cross-checked from production EVENTS, not claimed as OS-level read tracing",
                ],
                "clean_claim_boundary": "Only observed scopes above are eligible for clean/no-change claims. Every listed external channel remains unaudited.",
            },
        }
        self.summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        self.emit("runner_finalized", summary_path=str(self.summary_path), summary_sha256=sha256(self.summary_path))

    def run(self) -> None:
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        self.events_path.write_text("", encoding="utf-8")
        self.emit(
            "runner_started",
            repo_root=str(self.repo),
            assigned_output_root=str(self.output),
            initial_git_head=self.initial_git["head"],
            initial_tracked_status=self.initial_git["tracked_status"]["stdout_lines"],
        )
        while not self.stop_file.exists():
            self.observe_files()
            self.observe_production_events()
            time.sleep(self.poll_seconds)
        self.emit("runner_stop_requested", stop_file=str(self.stop_file))
        self.finalize()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--audit-dir", type=Path, required=True)
    parser.add_argument("--stop-file", type=Path, required=True)
    parser.add_argument("--poll-ms", type=int, default=100)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo = args.repo.resolve()
    output = args.output_root.resolve()
    audit_dir = args.audit_dir.resolve()
    stop_file = args.stop_file.resolve()
    if not is_relative_to(output, repo):
        raise SystemExit("output root must be inside repository/worktree")
    if not is_relative_to(audit_dir, repo) or is_relative_to(audit_dir, output):
        raise SystemExit("audit dir must be inside repository/worktree but outside assigned output root")
    if stop_file.parent != audit_dir:
        raise SystemExit("stop file must be directly inside audit dir")
    if args.poll_ms < 20:
        raise SystemExit("poll interval must be at least 20 ms")
    Audit(repo, output, audit_dir, stop_file, args.poll_ms).run()


if __name__ == "__main__":
    main()
