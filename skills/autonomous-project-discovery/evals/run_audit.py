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
PACKET_ID_RE = re.compile(r"D-\d{3}", re.I)


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
        return "canonical_gate"
    return "other_output"


def parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


class Audit:
    def __init__(
        self,
        repo: Path,
        output: Path,
        audit_dir: Path,
        stop_file: Path,
        control_file: Path,
        poll_ms: int,
    ):
        self.repo = repo.resolve()
        self.output = output.resolve()
        self.audit_dir = audit_dir.resolve()
        self.stop_file = stop_file.resolve()
        self.control_file = control_file.resolve()
        self.poll_seconds = poll_ms / 1000
        self.events_path = self.audit_dir / "runner-audit.jsonl"
        self.summary_path = self.audit_dir / "summary.json"
        self.seq = 0
        self.events: list[dict[str, Any]] = []
        self.files: dict[str, dict[str, Any]] = {}
        self.production_lines_seen: dict[str, int] = {}
        self.production_streams: dict[str, dict[str, Any]] = {}
        self.production_claims: list[dict[str, Any]] = []
        self.control_lines_seen = 0
        self.control_request_ids: set[str] = set()
        self.samples: dict[str, dict[str, Any]] = {}
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
            raw_text = path.read_text(encoding="utf-8", errors="replace")
            lines = raw_text.splitlines()
            if raw_text and not raw_text.endswith(("\n", "\r")):
                lines = lines[:-1]
            start = self.production_lines_seen.get(relative, 0)
            stream = self.production_streams.setdefault(
                relative,
                {
                    "observed_line_count": 0,
                    "parse_valid": True,
                    "append_only_valid": True,
                    "source_sequence_valid": True,
                    "source_timestamps_valid": True,
                    "references_valid": True,
                    "last_source_seq": None,
                    "last_source_timestamp": None,
                    "line_hashes": [],
                    "errors": [],
                },
            )
            current_hashes = [hashlib.sha256(line.encode("utf-8")).hexdigest() for line in lines]
            previous_hashes = stream["line_hashes"]
            prefix_length = min(start, len(lines))
            prefix_changed = current_hashes[:prefix_length] != previous_hashes[:prefix_length]
            truncated = len(lines) < start
            if prefix_changed or truncated:
                stream["append_only_valid"] = False
                mutation = "truncated" if truncated else "rewritten"
                stream["errors"].append(f"stream_{mutation}_after_observation")
                self.emit(
                    "production_stream_mutation_observed",
                    path=relative,
                    mutation=mutation,
                    previously_observed_lines=start,
                    current_complete_lines=len(lines),
                )
                # Do not reinterpret rewritten history as fresh append evidence.
                start = len(lines)
            for line_number, raw in enumerate(lines[start:], start=start + 1):
                try:
                    item = json.loads(raw)
                except json.JSONDecodeError as error:
                    stream["parse_valid"] = False
                    stream["errors"].append(f"line {line_number}: invalid JSON")
                    self.emit(
                        "production_event_parse_error",
                        path=relative,
                        line_number=line_number,
                        error=str(error),
                    )
                    continue
                source_type = str(item.get("event_type", "unknown"))
                packet_id = item.get("packet_id") or packet_from(json.dumps(item, ensure_ascii=False))
                errors: list[str] = []
                source_seq = item.get("event_seq")
                if not isinstance(source_seq, int) or isinstance(source_seq, bool) or source_seq < 1:
                    errors.append("invalid_event_seq")
                    stream["source_sequence_valid"] = False
                else:
                    previous_seq = stream["last_source_seq"]
                    if previous_seq is not None and source_seq <= previous_seq:
                        errors.append("non_monotonic_event_seq")
                        stream["source_sequence_valid"] = False
                    stream["last_source_seq"] = source_seq

                source_timestamp = parse_timestamp(item.get("timestamp"))
                if source_timestamp is None:
                    errors.append("missing_or_invalid_timestamp")
                    stream["source_timestamps_valid"] = False
                else:
                    previous_timestamp = stream["last_source_timestamp"]
                    if previous_timestamp is not None and source_timestamp <= previous_timestamp:
                        errors.append("non_monotonic_timestamp")
                        stream["source_timestamps_valid"] = False
                    stream["last_source_timestamp"] = source_timestamp

                references = item.get("references", [])
                requires_references = source_type in {"artifact_sampled", "packet_verified"} or (
                    source_type == "packet_status_transition" and item.get("to_status") == "verified"
                )
                resolved_references, reference_errors = self.validate_production_references(references)
                if requires_references and not references:
                    reference_errors.append("required_references_empty")
                if reference_errors:
                    errors.extend(reference_errors)
                    stream["references_valid"] = False

                for error_name in errors:
                    stream["errors"].append(f"line {line_number}: {error_name}")
                stream["observed_line_count"] += 1
                self.emit(
                    "production_event_observed",
                    path=relative,
                    line_number=line_number,
                    line_sha256=hashlib.sha256(raw.encode("utf-8")).hexdigest(),
                    production_event_type=source_type,
                    production_event_seq=source_seq,
                    production_timestamp=item.get("timestamp"),
                    packet_id=packet_id,
                    referenced_paths=references,
                    resolved_references=resolved_references,
                    cross_check_valid=not errors,
                    validation_errors=errors,
                )
                if source_type == "artifact_sampled" or source_type == "packet_verified" or (
                    source_type == "packet_status_transition" and item.get("to_status") == "verified"
                ):
                    self.production_claims.append(
                        {
                            "packet_id": packet_id,
                            "claim_kind": "sampling" if source_type == "artifact_sampled" else "verification",
                            "source_path": relative,
                            "source_line": line_number,
                            "cross_check_valid": not errors,
                            "validation_errors": errors,
                            "resolved_references": resolved_references,
                        }
                    )
            stream["line_hashes"] = current_hashes
            self.production_lines_seen[relative] = len(lines)

    def validate_production_references(self, references: Any) -> tuple[list[dict[str, Any]], list[str]]:
        if not isinstance(references, list):
            return [], ["references_not_array"]
        resolved: list[dict[str, Any]] = []
        errors: list[str] = []
        for index, reference in enumerate(references):
            prefix = f"reference_{index}"
            if not isinstance(reference, dict):
                errors.append(f"{prefix}_not_object")
                continue
            raw_path = reference.get("path")
            if not isinstance(raw_path, str) or not raw_path.strip():
                errors.append(f"{prefix}_path_missing")
                continue
            candidate_input = Path(raw_path)
            if candidate_input.is_absolute():
                errors.append(f"{prefix}_path_not_relative")
                continue
            try:
                candidate = (self.output / candidate_input).resolve(strict=True)
            except (OSError, RuntimeError):
                errors.append(f"{prefix}_path_missing")
                continue
            if not is_relative_to(candidate, self.output) or not candidate.is_file():
                errors.append(f"{prefix}_path_outside_or_not_file")
                continue
            observed_hash = sha256(candidate)
            declared_hash = reference.get("sha256")
            declared_revision = reference.get("revision")
            validation_kind: str | None = None
            if isinstance(declared_hash, str) and re.fullmatch(r"[0-9a-fA-F]{64}", declared_hash):
                if declared_hash.lower() != observed_hash:
                    errors.append(f"{prefix}_sha256_mismatch")
                    continue
                validation_kind = "sha256"
            elif isinstance(declared_revision, str) and declared_revision.strip():
                revision_check = self.validate_git_revision(candidate, declared_revision.strip(), observed_hash)
                if not revision_check["valid"]:
                    errors.append(f"{prefix}_{revision_check['error']}")
                    continue
                validation_kind = "git_revision"
            else:
                errors.append(f"{prefix}_hash_or_revision_missing")
                continue
            resolved.append(
                {
                    "path": candidate.relative_to(self.output).as_posix(),
                    "sha256": observed_hash,
                    "validation_kind": validation_kind,
                    "declared_revision": declared_revision if validation_kind == "git_revision" else None,
                }
            )
        return resolved, errors

    def validate_git_revision(self, candidate: Path, revision: str, observed_hash: str) -> dict[str, Any]:
        try:
            repo_relative = candidate.relative_to(self.repo).as_posix()
        except ValueError:
            return {"valid": False, "error": "revision_path_outside_repo"}
        revision_result = subprocess.run(
            ["git", "-C", str(self.repo), "rev-parse", "--verify", f"{revision}^{{commit}}"],
            capture_output=True,
            check=False,
        )
        if revision_result.returncode != 0:
            return {"valid": False, "error": "revision_invalid"}
        blob_result = subprocess.run(
            ["git", "-C", str(self.repo), "show", f"{revision}:{repo_relative}"],
            capture_output=True,
            check=False,
        )
        if blob_result.returncode != 0:
            return {"valid": False, "error": "revision_path_missing"}
        blob_hash = hashlib.sha256(blob_result.stdout).hexdigest()
        if blob_hash != observed_hash:
            return {"valid": False, "error": "revision_content_mismatch"}
        return {"valid": True, "error": None}

    def observe_control(self) -> None:
        if not self.control_file.exists():
            return
        raw_text = self.control_file.read_text(encoding="utf-8", errors="replace")
        lines = raw_text.splitlines()
        if raw_text and not raw_text.endswith(("\n", "\r")):
            lines = lines[:-1]
        for line_number, raw in enumerate(lines[self.control_lines_seen :], start=self.control_lines_seen + 1):
            line_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
            try:
                command = json.loads(raw)
            except json.JSONDecodeError as error:
                self.emit(
                    "runner_control_parse_error",
                    line_number=line_number,
                    line_sha256=line_hash,
                    error=str(error),
                )
                continue
            request_id = command.get("request_id") if isinstance(command, dict) else None
            action = command.get("action") if isinstance(command, dict) else None
            packet_id = command.get("packet_id") if isinstance(command, dict) else None
            observed = self.emit_control_observed(line_number, line_hash, request_id, action, packet_id)
            if not isinstance(request_id, str) or not request_id.strip():
                self.reject_control(observed, request_id, action, packet_id, ["request_id_missing"])
                continue
            if request_id in self.control_request_ids:
                self.reject_control(observed, request_id, action, packet_id, ["request_id_duplicate"])
                continue
            self.control_request_ids.add(request_id)
            if not isinstance(packet_id, str) or not PACKET_ID_RE.fullmatch(packet_id):
                self.reject_control(observed, request_id, action, packet_id, ["packet_id_invalid"])
                continue
            packet_id = packet_id.upper()
            if action == "sample":
                self.handle_sample(observed, request_id, packet_id, command.get("paths"))
            elif action == "verify":
                self.handle_verify(observed, request_id, packet_id, command.get("sample_request_id"))
            else:
                self.reject_control(observed, request_id, action, packet_id, ["action_invalid"])
        self.control_lines_seen = len(lines)

    def emit_control_observed(
        self,
        line_number: int,
        line_hash: str,
        request_id: Any,
        action: Any,
        packet_id: Any,
    ) -> dict[str, Any]:
        self.emit(
            "runner_control_request_observed",
            line_number=line_number,
            line_sha256=line_hash,
            request_id=request_id,
            action=action,
            packet_id=packet_id,
        )
        return self.events[-1]

    def reject_control(
        self,
        observed: dict[str, Any],
        request_id: Any,
        action: Any,
        packet_id: Any,
        errors: list[str],
    ) -> None:
        self.emit(
            "runner_control_rejected",
            request_event_seq=observed["event_seq"],
            request_id=request_id,
            action=action,
            packet_id=packet_id,
            validation_errors=errors,
        )

    def handle_sample(
        self,
        observed: dict[str, Any],
        request_id: str,
        packet_id: str,
        paths: Any,
    ) -> None:
        errors: list[str] = []
        if not isinstance(paths, list) or not paths:
            self.reject_control(observed, request_id, "sample", packet_id, ["paths_empty_or_invalid"])
            return
        if len(set(value for value in paths if isinstance(value, str))) != len(paths):
            errors.append("paths_duplicate_or_invalid")
        sampled_items: list[dict[str, Any]] = []
        for index, raw_path in enumerate(paths):
            prefix = f"path_{index}"
            if not isinstance(raw_path, str) or not raw_path.strip() or Path(raw_path).is_absolute():
                errors.append(f"{prefix}_invalid")
                continue
            try:
                candidate = (self.output / raw_path).resolve(strict=True)
            except (OSError, RuntimeError):
                errors.append(f"{prefix}_missing")
                continue
            if not is_relative_to(candidate, self.output) or not candidate.is_file():
                errors.append(f"{prefix}_outside_or_not_file")
                continue
            relative = candidate.relative_to(self.output).as_posix()
            observed_hash = sha256(candidate)
            matching_writes = [
                event
                for event in self.events
                if event.get("path") == relative
                and event.get("sha256") == observed_hash
                and event.get("event_type") in {"output_file_created", "output_file_modified"}
                and event["event_seq"] < observed["event_seq"]
            ]
            if not matching_writes:
                errors.append(f"{prefix}_write_not_observed")
                continue
            write_event = matching_writes[-1]
            role = classify_file(relative)
            item = {
                "path": relative,
                "sha256": observed_hash,
                "size": candidate.stat().st_size,
                "role": role,
                "packet_id": packet_from(relative),
                "observed_write_event_seq": write_event["event_seq"],
            }
            sampled_items.append(item)
            self.emit(
                "runner_artifact_sampled",
                request_id=request_id,
                request_event_seq=observed["event_seq"],
                **item,
            )
        if errors:
            self.reject_control(observed, request_id, "sample", packet_id, errors)
            return
        manifest_hash = hashlib.sha256(
            json.dumps(sampled_items, ensure_ascii=False, sort_keys=True).encode("utf-8")
        ).hexdigest()
        self.emit(
            "runner_sample_completed",
            request_id=request_id,
            request_event_seq=observed["event_seq"],
            packet_id=packet_id,
            sampled_paths=sampled_items,
            manifest_sha256=manifest_hash,
        )
        self.samples[request_id] = self.events[-1]

    def handle_verify(
        self,
        observed: dict[str, Any],
        request_id: str,
        packet_id: str,
        sample_request_id: Any,
    ) -> None:
        errors: list[str] = []
        if not isinstance(sample_request_id, str) or sample_request_id not in self.samples:
            errors.append("accepted_sample_request_missing")
            sample = None
        else:
            sample = self.samples[sample_request_id]
        report_item = None
        evidence_item = None
        if sample is not None:
            if sample.get("packet_id") != packet_id:
                errors.append("sample_packet_mismatch")
            packet_items = [item for item in sample["sampled_paths"] if item.get("packet_id") == packet_id]
            report_item = next((item for item in packet_items if item.get("role") == "worker_report"), None)
            evidence_item = next((item for item in packet_items if item.get("role") == "worker_evidence"), None)
            if report_item is None:
                errors.append("sampled_worker_report_missing")
            if evidence_item is None:
                errors.append("sampled_worker_evidence_missing")
            if report_item is not None and evidence_item is not None and not (
                report_item["observed_write_event_seq"]
                < evidence_item["observed_write_event_seq"]
                < sample["event_seq"]
                < observed["event_seq"]
            ):
                errors.append("report_evidence_sample_verify_order_invalid")
        if errors:
            self.reject_control(observed, request_id, "verify", packet_id, errors)
            return
        self.emit(
            "runner_verification_accepted",
            request_id=request_id,
            request_event_seq=observed["event_seq"],
            packet_id=packet_id,
            sample_request_id=sample_request_id,
            sample_event_seq=sample["event_seq"],
            report_path=report_item["path"],
            report_sha256=report_item["sha256"],
            report_write_event_seq=report_item["observed_write_event_seq"],
            evidence_path=evidence_item["path"],
            evidence_sha256=evidence_item["sha256"],
            evidence_write_event_seq=evidence_item["observed_write_event_seq"],
        )

    def production_cross_check_summary(self) -> dict[str, Any]:
        files: dict[str, Any] = {}
        for path, stream in self.production_streams.items():
            files[path] = {
                key: value.isoformat().replace("+00:00", "Z") if isinstance(value, datetime) else value
                for key, value in stream.items()
            }
            files[path]["valid"] = bool(
                stream["parse_valid"]
                and stream["append_only_valid"]
                and stream["source_sequence_valid"]
                and stream["source_timestamps_valid"]
                and stream["references_valid"]
            )
        return {
            "files": files,
            "claims": self.production_claims,
            "boundary": "Production EVENTS claims are validated cross-checks only and never runner sampling or verification evidence.",
        }

    def lifecycle_summary(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        packet_ids = sorted({event.get("packet_id") for event in self.events if event.get("packet_id")})
        for packet_id in packet_ids:
            report = next((e for e in self.events if e.get("packet_id") == packet_id and e.get("role") == "worker_report" and e["event_type"] == "output_file_created"), None)
            evidence = next((e for e in self.events if e.get("packet_id") == packet_id and e.get("role") == "worker_evidence" and e["event_type"] == "output_file_created"), None)
            sampled = next((e for e in self.events if e.get("packet_id") == packet_id and e["event_type"] == "runner_sample_completed"), None)
            verified = next((e for e in self.events if e.get("packet_id") == packet_id and e["event_type"] == "runner_verification_accepted"), None)
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
                "note": "Strict order uses runner-observed report/evidence writes plus runner-owned sampling and verification control requests; production EVENTS claims are cross-checks only.",
            }
        return result

    def finalize(self) -> None:
        self.observe_files()
        self.observe_production_events()
        self.observe_control()
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
            "production_cross_checks": self.production_cross_check_summary(),
            "observation_scope": {
                "observed": [
                    "assigned output-root file creation/modification/deletion with SHA-256 and mtime",
                    "repository tracked HEAD and tracked status at runner start/end",
                    "repository nonignored untracked path set at runner start/end",
                    "production EVENTS.jsonl append lines as cross-check claims",
                    "runner control requests and observer-owned reads/hashes of explicitly sampled output paths",
                ],
                "unaudited": [
                    "network and remote service side effects",
                    "filesystem writes outside the repository/worktree",
                    "ignored paths outside the assigned output and runner-audit roots",
                    "credential stores, messages, publishing, purchases, deployments, and external process state",
                    "host-private tool transcripts and read syscalls outside explicit runner sample requests",
                ],
                "clean_claim_boundary": "Only observed scopes above are eligible for clean/no-change claims. Every listed external channel remains unaudited.",
            },
        }
        self.summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        self.emit("runner_finalized", summary_path=str(self.summary_path), summary_sha256=sha256(self.summary_path))

    def run(self) -> None:
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        if self.control_file.exists() and self.control_file.stat().st_size:
            raise SystemExit("control file must be absent or empty at runner start")
        self.events_path.write_text("", encoding="utf-8")
        self.emit(
            "runner_started",
            repo_root=str(self.repo),
            assigned_output_root=str(self.output),
            runner_control_file=str(self.control_file),
            initial_git_head=self.initial_git["head"],
            initial_tracked_status=self.initial_git["tracked_status"]["stdout_lines"],
        )
        while not self.stop_file.exists():
            self.observe_files()
            self.observe_production_events()
            self.observe_control()
            time.sleep(self.poll_seconds)
        self.emit("runner_stop_requested", stop_file=str(self.stop_file))
        self.finalize()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--audit-dir", type=Path, required=True)
    parser.add_argument("--stop-file", type=Path, required=True)
    parser.add_argument("--control-file", type=Path)
    parser.add_argument("--poll-ms", type=int, default=100)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo = args.repo.resolve()
    output = args.output_root.resolve()
    audit_dir = args.audit_dir.resolve()
    stop_file = args.stop_file.resolve()
    control_file = (args.control_file or (audit_dir / "runner-control.jsonl")).resolve()
    if not is_relative_to(output, repo):
        raise SystemExit("output root must be inside repository/worktree")
    if not is_relative_to(audit_dir, repo) or is_relative_to(audit_dir, output):
        raise SystemExit("audit dir must be inside repository/worktree but outside assigned output root")
    if stop_file.parent != audit_dir:
        raise SystemExit("stop file must be directly inside audit dir")
    if control_file.parent != audit_dir or control_file == stop_file:
        raise SystemExit("control file must be distinct and directly inside audit dir")
    if args.poll_ms < 20:
        raise SystemExit("poll interval must be at least 20 ms")
    Audit(repo, output, audit_dir, stop_file, control_file, args.poll_ms).run()


if __name__ == "__main__":
    main()
