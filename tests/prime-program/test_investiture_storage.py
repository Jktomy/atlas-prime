from __future__ import annotations

import contextlib
import copy
import io
import json
import os
import shutil
import tempfile
import unittest
from unittest import mock
from pathlib import Path

import tools.investiture_accounting.storage as investiture_storage
from tools.investiture_accounting.cli import main as cli_main
from tools.investiture_accounting.core import InvestitureError, ZERO_SHA256, sha256_object, stable_json
from tools.investiture_accounting.storage import (
    append_event,
    initialize_store,
    recover_generation,
    recover_interrupted,
    rollback_plan,
    validate_external_root,
    verify_store,
)


ROOT = Path(__file__).resolve().parents[2]
EVENTS = json.loads(
    (ROOT / "tests/prime-program/fixtures/investiture-events-v1.json").read_text(encoding="utf-8")
)["events"]


def initialize(parent: Path, name: str = "ledger") -> Path:
    root = parent / name
    initialize_store(
        root,
        ledger_id="FS-C01-LEDGER-R01",
        generation_id=f"FS-C01-GEN-{name.upper()}",
        created_at="2026-07-13T19:00:00Z",
    )
    return root


class InvestitureStorageTests(unittest.TestCase):
    def test_store_root_is_explicit_new_external_and_pathless_in_output(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-investiture-") as temp:
            parent = Path(temp)
            output = io.StringIO()
            root = parent / "cli-ledger"
            with contextlib.redirect_stdout(output):
                self.assertEqual(cli_main([
                    "init", "--store-root", str(root), "--ledger-id", "FS-C01-LEDGER-R01",
                    "--generation-id", "FS-C01-GEN-CLI", "--created-at", "2026-07-13T19:00:00Z",
                    "--request-id", "fs-c01-init-request-identity-0001",
                ]), 0)
            receipt = json.loads(output.getvalue())
            self.assertEqual(receipt["result"], "INITIALIZED")
            self.assertNotIn(str(parent), output.getvalue())
            with self.assertRaisesRegex(InvestitureError, "STORE_ROOT_MUST_BE_NEW"):
                initialize_store(root, ledger_id="FS-C01-LEDGER-R01", generation_id="FS-C01-GEN-AGAIN", created_at="2026-07-13T19:00:00Z")
        with self.assertRaisesRegex(InvestitureError, "STORE_ROOT_ABSOLUTE_REQUIRED"):
            initialize_store(Path("relative-ledger"), ledger_id="FS-C01-LEDGER-R01", generation_id="FS-C01-GEN-RELATIVE", created_at="2026-07-13T19:00:00Z")
        with self.assertRaisesRegex(InvestitureError, "STORE_ROOT_REPOSITORY_OVERLAP"):
            initialize_store(ROOT / ".investiture-test-ledger", ledger_id="FS-C01-LEDGER-R01", generation_id="FS-C01-GEN-REPO", created_at="2026-07-13T19:00:00Z")

    def test_append_exact_head_replay_stale_and_duplicate_scope(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-investiture-") as temp:
            root = initialize(Path(temp))
            raw = stable_json(EVENTS[0])
            receipt = append_event(root, raw, expected_head=ZERO_SHA256, request_id=EVENTS[0]["replay_identity"])
            self.assertEqual(receipt["result"], "COMMITTED")
            self.assertTrue(receipt["ledger_mutation_performed"])
            with self.assertRaisesRegex(InvestitureError, "STALE_EXPECTED_HEAD"):
                append_event(root, raw, expected_head="f" * 64, request_id=EVENTS[0]["replay_identity"])
            replay = append_event(root, raw, expected_head=ZERO_SHA256, request_id=EVENTS[0]["replay_identity"])
            self.assertEqual(replay["result"], "ALREADY_COMMITTED")
            self.assertFalse(replay["ledger_mutation_performed"])
            self.assertEqual(replay["head_sha256"], receipt["head_sha256"])
            self.assertEqual(verify_store(root)["record_count"], 1)
            with self.assertRaisesRegex(InvestitureError, "STALE_EXPECTED_HEAD"):
                append_event(root, stable_json(EVENTS[1]), expected_head=ZERO_SHA256, request_id=EVENTS[1]["replay_identity"])
            duplicate = copy.deepcopy(EVENTS[0])
            duplicate["event_id"] = "FS-C01-USAGE-OPENAI-002"
            duplicate["replay_identity"] = "fs-c01-openai-usage-replay-0002"
            with self.assertRaisesRegex(InvestitureError, "USAGE_SCOPE_REPLAY_DETECTED"):
                append_event(root, stable_json(duplicate), expected_head=receipt["head_sha256"], request_id=duplicate["replay_identity"])
            second = append_event(root, stable_json(EVENTS[1]), expected_head=receipt["head_sha256"], request_id=EVENTS[1]["replay_identity"])
            with self.assertRaisesRegex(InvestitureError, "REPLAY_SUPERSEDED_BY_LATER_HEAD"):
                append_event(root, raw, expected_head=ZERO_SHA256, request_id=EVENTS[0]["replay_identity"])
            with self.assertRaisesRegex(InvestitureError, "STALE_EXPECTED_HEAD"):
                append_event(root, raw, expected_head=second["head_sha256"], request_id=EVENTS[0]["replay_identity"])

    def test_lifecycle_binding_requires_prior_usage_and_never_changes_beu(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-investiture-") as temp:
            root = initialize(Path(temp))
            lifecycle = copy.deepcopy(EVENTS[4])
            with self.assertRaisesRegex(InvestitureError, "LIFECYCLE_USAGE_BINDING_INVALID"):
                append_event(root, stable_json(lifecycle), expected_head=ZERO_SHA256, request_id=lifecycle["replay_identity"])
            first = append_event(root, stable_json(EVENTS[0]), expected_head=ZERO_SHA256, request_id=EVENTS[0]["replay_identity"])
            lifecycle["bound_usage_event_ids"] = [EVENTS[0]["event_id"]]
            done = append_event(root, stable_json(lifecycle), expected_head=first["head_sha256"], request_id=lifecycle["replay_identity"])
            summary = verify_store(root)
            self.assertEqual(done["sequence"], 2)
            self.assertEqual(summary["light_known_beu"]["Spirallight"], 21)
            self.assertEqual(summary["known_beu_subtotal"], 21)

    def test_malformed_input_is_sanitized_quarantine_only(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-investiture-") as temp:
            root = initialize(Path(temp))
            raw = b'{"raw_prompt":"SENTINEL_PRIVATE_VALUE","schema_version":"atlas.investiture-event.v1"}'
            receipt = append_event(root, raw, expected_head=ZERO_SHA256, request_id="fs-c01-malformed-request-0001")
            self.assertEqual(receipt["result"], "QUARANTINED")
            self.assertFalse(receipt["ledger_mutation_performed"])
            self.assertEqual(verify_store(root)["record_count"], 0)
            stored = b"".join(path.read_bytes() for path in root.rglob("*") if path.is_file())
            self.assertNotIn(b"SENTINEL_PRIVATE_VALUE", stored)
            self.assertNotIn(b"raw_prompt", stored)

    def test_interruption_recovery_is_explicit_exact_and_idempotent(self) -> None:
        for point in ("lock", "intent", "temporary", "record", "receipt"):
            with self.subTest(point=point), tempfile.TemporaryDirectory(prefix="atlas-investiture-") as temp:
                root = initialize(Path(temp))
                event = EVENTS[0]
                with self.assertRaisesRegex(InvestitureError, f"INJECTED_INTERRUPTION_AFTER_{point.upper()}"):
                    append_event(root, stable_json(event), expected_head=ZERO_SHA256, request_id=event["replay_identity"], interrupt_after=point)
                if point in {"lock", "receipt"}:
                    self.assertEqual(verify_store(root)["record_count"], 0 if point == "lock" else 1)
                else:
                    with self.assertRaisesRegex(InvestitureError, "INTERRUPTED_RECOVERY_REQUIRED"):
                        verify_store(root)
                recovered = recover_interrupted(root, request_id=event["replay_identity"], expected_head=ZERO_SHA256)
                repeated = recover_interrupted(root, request_id=event["replay_identity"], expected_head=ZERO_SHA256)
                self.assertEqual(recovered, repeated)
                self.assertEqual(verify_store(root)["record_count"], 0 if point == "lock" else 1)

    def test_receipt_coverage_binding_and_quarantine_integrity_fail_closed(self) -> None:
        for mode in ("corrupt", "delete", "substitute"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory(prefix="atlas-investiture-") as temp:
                root = initialize(Path(temp))
                append_event(root, stable_json(EVENTS[0]), expected_head=ZERO_SHA256, request_id=EVENTS[0]["replay_identity"])
                receipt = next((root / "receipts").iterdir())
                if mode == "corrupt":
                    value = json.loads(receipt.read_text(encoding="utf-8"))
                    value["input_byte_count"] += 1
                    receipt.write_bytes(stable_json(value))
                    expected = "RECEIPT_DIGEST_MISMATCH"
                elif mode == "delete":
                    receipt.unlink()
                    expected = "INTERRUPTED_RECOVERY_REQUIRED"
                else:
                    wrong = receipt.with_name("f" * 64 + ".json")
                    receipt.rename(wrong)
                    expected = "INTERRUPTED_RECOVERY_REQUIRED"
                with self.assertRaisesRegex(InvestitureError, expected):
                    verify_store(root)
        with tempfile.TemporaryDirectory(prefix="atlas-investiture-") as temp:
            root = initialize(Path(temp))
            append_event(root, b'{"invalid":true}', expected_head=ZERO_SHA256, request_id="fs-c01-quarantine-request-0001")
            quarantine = next((root / "quarantine").iterdir())
            value = json.loads(quarantine.read_text(encoding="utf-8"))
            value["input_byte_count"] += 1
            quarantine.write_bytes(stable_json(value))
            with self.assertRaisesRegex(InvestitureError, "RECEIPT_DIGEST_MISMATCH"):
                verify_store(root)

    def test_recovery_closes_an_exact_interrupted_no_clobber_publication(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-investiture-") as temp:
            root = initialize(Path(temp))
            event = EVENTS[0]
            with self.assertRaisesRegex(InvestitureError, "INJECTED_INTERRUPTION_AFTER_TEMPORARY"):
                append_event(
                    root,
                    stable_json(event),
                    expected_head=ZERO_SHA256,
                    request_id=event["replay_identity"],
                    interrupt_after="temporary",
                )
            temporary = next((root / "records").glob(".*.tmp"))
            intent = json.loads(next((root / "intents").iterdir()).read_text(encoding="utf-8"))
            record = intent["record"]
            target = root / "records" / f"{record['sequence']:08d}-{record['record_sha256']}.json"
            try:
                os.link(temporary, target)
            except OSError as exc:
                self.skipTest(f"hardlink capability unavailable: {exc}")
            receipt = recover_interrupted(root, request_id=event["replay_identity"], expected_head=ZERO_SHA256)
            self.assertEqual(receipt["record_sha256"], record["record_sha256"])
            self.assertFalse(temporary.exists())
            self.assertEqual(target.stat().st_nlink, 1)
            self.assertEqual(verify_store(root)["record_count"], 1)

    def test_atomic_intent_and_receipt_publication_interruptions_are_recoverable(self) -> None:
        for kind in ("intent", "receipt"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory(prefix="atlas-investiture-") as temp:
                root = initialize(Path(temp))
                original_publish = investiture_storage._publish_no_clobber
                interrupted = False

                def interrupt_exact_evidence(temporary: Path, target: Path) -> None:
                    nonlocal interrupted
                    if not interrupted and temporary.name.endswith(f".{kind}.tmp"):
                        interrupted = True
                        raise InvestitureError(f"INJECTED_{kind.upper()}_PUBLICATION_INTERRUPTION")
                    original_publish(temporary, target)

                with mock.patch("tools.investiture_accounting.storage._publish_no_clobber", side_effect=interrupt_exact_evidence):
                    with self.assertRaisesRegex(InvestitureError, f"INJECTED_{kind.upper()}_PUBLICATION_INTERRUPTION"):
                        append_event(
                            root,
                            stable_json(EVENTS[0]),
                            expected_head=ZERO_SHA256,
                            request_id=EVENTS[0]["replay_identity"],
                        )
                with self.assertRaisesRegex(InvestitureError, "INTERRUPTED_RECOVERY_REQUIRED"):
                    verify_store(root)
                receipt = recover_interrupted(
                    root,
                    request_id=EVENTS[0]["replay_identity"],
                    expected_head=ZERO_SHA256,
                )
                self.assertEqual(receipt["result"], "COMMITTED")
                self.assertEqual(verify_store(root)["record_count"], 1)

    def test_interrupted_recovery_revalidates_complete_intent_and_recovery_evidence(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-investiture-") as temp:
            root = initialize(Path(temp))
            event = EVENTS[0]
            append_event(root, stable_json(event), expected_head=ZERO_SHA256, request_id=event["replay_identity"])
            intent_path = next((root / "intents").iterdir())
            intent = json.loads(intent_path.read_text(encoding="utf-8"))
            intent["input_byte_count"] += 1
            intent_path.write_bytes(stable_json(intent))
            with self.assertRaisesRegex(InvestitureError, "INTENT_DIGEST_MISMATCH"):
                recover_interrupted(root, request_id=event["replay_identity"], expected_head=ZERO_SHA256)
        with tempfile.TemporaryDirectory(prefix="atlas-investiture-") as temp:
            root = initialize(Path(temp))
            event = EVENTS[0]
            with self.assertRaisesRegex(InvestitureError, "INJECTED_INTERRUPTION_AFTER_INTENT"):
                append_event(
                    root,
                    stable_json(event),
                    expected_head=ZERO_SHA256,
                    request_id=event["replay_identity"],
                    interrupt_after="intent",
                )
            intent_path = next((root / "intents").iterdir())
            intent = json.loads(intent_path.read_text(encoding="utf-8"))
            intent["input_sha256"] = "f" * 64
            intent_path.write_bytes(stable_json(intent))
            with self.assertRaisesRegex(InvestitureError, "INTENT_DIGEST_MISMATCH"):
                recover_interrupted(root, request_id=event["replay_identity"], expected_head=ZERO_SHA256)
        with tempfile.TemporaryDirectory(prefix="atlas-investiture-") as temp:
            root = initialize(Path(temp))
            request_id = "fs-c01-no-record-recovery-0001"
            recover_interrupted(root, request_id=request_id, expected_head=ZERO_SHA256)
            recovery_path = next((root / "recoveries").iterdir())
            recovery = json.loads(recovery_path.read_text(encoding="utf-8"))
            recovery["result"] = "FALSE_SUCCESS"
            recovery["ledger_mutation_performed"] = True
            recovery["recovery_sha256"] = sha256_object({key: value for key, value in recovery.items() if key != "recovery_sha256"})
            recovery_path.write_bytes(stable_json(recovery))
            with self.assertRaisesRegex(InvestitureError, "RECOVERY_RECEIPT_INVALID"):
                recover_interrupted(root, request_id=request_id, expected_head=ZERO_SHA256)

    def test_recovery_evidence_identity_is_closed_and_cannot_contradict_a_commit(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-investiture-") as temp:
            root = initialize(Path(temp))
            event = EVENTS[0]
            receipt = append_event(
                root,
                stable_json(event),
                expected_head=ZERO_SHA256,
                request_id=event["replay_identity"],
            )
            identity = receipt["replay_identity_sha256"]
            body = {
                "schema_version": "atlas.investiture-interruption-recovery.v1",
                "result": "NO_RECORD_RESERVED",
                "request_id_sha256": identity,
                "head_sha256": receipt["head_sha256"],
                "ledger_mutation_performed": False,
                "retry_performed": False,
            }
            recovery = dict(body)
            recovery["recovery_sha256"] = sha256_object(body)
            (root / "recoveries" / f"{identity}.json").write_bytes(stable_json(recovery))
            with self.assertRaisesRegex(InvestitureError, "RECOVERY_RECEIPT_INVALID"):
                verify_store(root)

        with tempfile.TemporaryDirectory(prefix="atlas-investiture-") as temp:
            root = initialize(Path(temp))
            filename_identity = "a" * 64
            invalid_identity = "g" * 64
            body = {
                "schema_version": "atlas.investiture-interruption-recovery.v1",
                "result": "NO_RECORD_RESERVED",
                "request_id_sha256": invalid_identity,
                "head_sha256": ZERO_SHA256,
                "ledger_mutation_performed": False,
                "retry_performed": False,
            }
            recovery = dict(body)
            recovery["recovery_sha256"] = sha256_object(body)
            (root / "recoveries" / f"{filename_identity}.json").write_bytes(stable_json(recovery))
            with self.assertRaisesRegex(InvestitureError, "RECOVERY_RECEIPT_INVALID"):
                verify_store(root)

    def test_recovery_cannot_contradict_an_inherited_generation_replay(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-investiture-") as temp:
            parent = Path(temp)
            source = initialize(parent, "inherited-recovery-source")
            event = EVENTS[0]
            receipt = append_event(
                source,
                stable_json(event),
                expected_head=ZERO_SHA256,
                request_id=event["replay_identity"],
            )
            destination = parent / "inherited-recovery-destination"
            recover_generation(
                source,
                destination,
                expected_valid_head=receipt["head_sha256"],
                new_generation_id="FS-C01-GEN-INHERITED-RECOVERY",
                created_at="2026-07-13T20:36:00Z",
            )
            with self.assertRaisesRegex(InvestitureError, "REPLAY_FROM_PRIOR_GENERATION"):
                recover_interrupted(
                    destination,
                    request_id=event["replay_identity"],
                    expected_head=receipt["head_sha256"],
                )
            self.assertEqual(list((destination / "recoveries").iterdir()), [])
            self.assertEqual(verify_store(destination)["record_count"], 1)

            identity = receipt["replay_identity_sha256"]
            body = {
                "schema_version": "atlas.investiture-interruption-recovery.v1",
                "result": "NO_RECORD_RESERVED",
                "request_id_sha256": identity,
                "head_sha256": receipt["head_sha256"],
                "ledger_mutation_performed": False,
                "retry_performed": False,
            }
            recovery = dict(body)
            recovery["recovery_sha256"] = sha256_object(body)
            (destination / "recoveries" / f"{identity}.json").write_bytes(stable_json(recovery))
            with self.assertRaisesRegex(InvestitureError, "RECOVERY_RECEIPT_INVALID"):
                verify_store(destination)

    def test_generation_recovery_excludes_an_unreconciled_published_record(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-investiture-") as temp:
            parent = Path(temp)
            source = initialize(parent, "interrupted-source")
            event = EVENTS[0]
            with self.assertRaisesRegex(InvestitureError, "INJECTED_INTERRUPTION_AFTER_RECORD"):
                append_event(
                    source,
                    stable_json(event),
                    expected_head=ZERO_SHA256,
                    request_id=event["replay_identity"],
                    interrupt_after="record",
                )
            destination = parent / "verified-prefix"
            result = recover_generation(
                source,
                destination,
                expected_valid_head=ZERO_SHA256,
                new_generation_id="FS-C01-GEN-VERIFIED-PREFIX",
                created_at="2026-07-13T20:30:00Z",
            )
            self.assertEqual(result["verified_prefix_records"], 0)
            self.assertEqual(result["source_error_code"], "INTERRUPTED_RECOVERY_REQUIRED")
            self.assertEqual(verify_store(destination)["record_count"], 0)
            with self.assertRaisesRegex(InvestitureError, "RECOVERY_VALID_HEAD_MISMATCH"):
                recover_generation(
                    source,
                    parent / "unverified-record",
                    expected_valid_head=next((source / "records").iterdir()).stem.split("-", 1)[1],
                    new_generation_id="FS-C01-GEN-UNVERIFIED-RECORD",
                    created_at="2026-07-13T20:31:00Z",
                )

    def test_generation_recovery_rejects_source_destination_overlap_before_mutation(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-investiture-") as temp:
            source = initialize(Path(temp), "overlap-source")
            before = {path.relative_to(source).as_posix(): path.read_bytes() for path in source.rglob("*") if path.is_file()}
            with self.assertRaisesRegex(InvestitureError, "RECOVERY_STORE_OVERLAP"):
                recover_generation(
                    source,
                    source / "nested-generation",
                    expected_valid_head=ZERO_SHA256,
                    new_generation_id="FS-C01-GEN-OVERLAP",
                    created_at="2026-07-13T20:32:00Z",
                )
            self.assertEqual(before, {path.relative_to(source).as_posix(): path.read_bytes() for path in source.rglob("*") if path.is_file()})
            self.assertEqual(verify_store(source)["record_count"], 0)

    def test_generation_recovery_binds_scan_to_a_preexisting_source_snapshot(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-investiture-") as temp:
            parent = Path(temp)
            source = initialize(parent, "snapshot-source")
            append_event(
                source,
                stable_json(EVENTS[0]),
                expected_head=ZERO_SHA256,
                request_id=EVENTS[0]["replay_identity"],
            )
            record_path = next((source / "records").iterdir())
            expected_head = record_path.stem.split("-", 1)[1]
            destination = parent / "snapshot-destination"
            original_snapshot = investiture_storage._store_snapshot
            calls = 0

            def mutate_after_first_snapshot(root: Path, *, lock_handle=None):
                nonlocal calls
                snapshot = original_snapshot(root, lock_handle=lock_handle)
                calls += 1
                if calls == 1:
                    record_path.write_bytes(b"{}\n")
                return snapshot

            with mock.patch("tools.investiture_accounting.storage._store_snapshot", side_effect=mutate_after_first_snapshot):
                with self.assertRaisesRegex(InvestitureError, "RECOVERY_SOURCE_MUTATED"):
                    recover_generation(
                        source,
                        destination,
                        expected_valid_head=expected_head,
                        new_generation_id="FS-C01-GEN-SNAPSHOT-BOUND",
                        created_at="2026-07-13T20:33:00Z",
                    )
            self.assertFalse(destination.exists())

    def test_generation_recovery_invalidates_destination_on_postconstruction_source_drift(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-investiture-") as temp:
            parent = Path(temp)
            source = initialize(parent, "postconstruction-source")
            receipt = append_event(
                source,
                stable_json(EVENTS[0]),
                expected_head=ZERO_SHA256,
                request_id=EVENTS[0]["replay_identity"],
            )
            record_path = next((source / "records").iterdir())
            destination = parent / "postconstruction-destination"
            original_initialize = investiture_storage._initialize_store

            def mutate_after_destination(*args, **kwargs):
                manifest = original_initialize(*args, **kwargs)
                record_path.write_bytes(b"{}\n")
                return manifest

            with mock.patch("tools.investiture_accounting.storage._initialize_store", side_effect=mutate_after_destination):
                with self.assertRaisesRegex(InvestitureError, "RECOVERY_SOURCE_MUTATED"):
                    recover_generation(
                        source,
                        destination,
                        expected_valid_head=receipt["head_sha256"],
                        new_generation_id="FS-C01-GEN-POSTCONSTRUCTION-BOUND",
                        created_at="2026-07-13T20:34:00Z",
                    )
            self.assertTrue((destination / "recovery.invalid").is_file())
            with self.assertRaisesRegex(InvestitureError, "STORE_LAYOUT_INVALID"):
                verify_store(destination)

    def test_generation_recovery_invalidates_destination_on_late_snapshot_or_release_failure(self) -> None:
        for failure in ("snapshot", "release"):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory(prefix="atlas-investiture-") as temp:
                parent = Path(temp)
                source = initialize(parent, f"late-{failure}-source")
                destination = parent / f"late-{failure}-destination"
                if failure == "snapshot":
                    original_snapshot = investiture_storage._store_snapshot

                    def fail_after_destination(root: Path, *, lock_handle=None):
                        if destination.exists():
                            raise InvestitureError("INJECTED_FINAL_SNAPSHOT_FAILURE")
                        return original_snapshot(root, lock_handle=lock_handle)

                    patcher = mock.patch(
                        "tools.investiture_accounting.storage._store_snapshot",
                        side_effect=fail_after_destination,
                    )
                    expected = "INJECTED_FINAL_SNAPSHOT_FAILURE"
                else:
                    original_release = investiture_storage._release_mutation

                    def fail_after_release(view, lock_handle, mutation_state):
                        original_release(view, lock_handle, mutation_state)
                        raise InvestitureError("INJECTED_RELEASE_FAILURE")

                    patcher = mock.patch(
                        "tools.investiture_accounting.storage._release_mutation",
                        side_effect=fail_after_release,
                    )
                    expected = "INJECTED_RELEASE_FAILURE"
                with patcher:
                    with self.assertRaisesRegex(InvestitureError, expected):
                        recover_generation(
                            source,
                            destination,
                            expected_valid_head=ZERO_SHA256,
                            new_generation_id=f"FS-C01-GEN-LATE-{failure.upper()}",
                            created_at="2026-07-13T20:35:00Z",
                        )
                self.assertTrue((destination / "recovery.invalid").is_file())
                with self.assertRaisesRegex(InvestitureError, "STORE_LAYOUT_INVALID"):
                    verify_store(destination)

    def test_generation_recovery_and_rollback_plan_do_not_mutate_source(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-investiture-") as temp:
            parent = Path(temp)
            source = initialize(parent, "source")
            first = append_event(source, stable_json(EVENTS[0]), expected_head=ZERO_SHA256, request_id=EVENTS[0]["replay_identity"])
            rollback_target = parent / "rollback-target"
            recover_generation(
                source,
                rollback_target,
                expected_valid_head=first["head_sha256"],
                new_generation_id="FS-C01-GEN-ROLLBACK",
                created_at="2026-07-13T19:30:00Z",
            )
            second = append_event(source, stable_json(EVENTS[1]), expected_head=first["head_sha256"], request_id=EVENTS[1]["replay_identity"])
            source_before = {path.name: path.read_bytes() for path in source.rglob("*") if path.is_file()}
            records = sorted((source / "records").iterdir())
            records[1].write_bytes(records[1].read_bytes().replace(b'"token_count":3', b'"token_count":4'))
            tampered_before = {path.name: path.read_bytes() for path in source.rglob("*") if path.is_file()}
            with self.assertRaises(InvestitureError):
                verify_store(source)
            destination = parent / "recovered"
            recovery = recover_generation(
                source,
                destination,
                expected_valid_head=first["head_sha256"],
                new_generation_id="FS-C01-GEN-RECOVERED",
                created_at="2026-07-13T20:00:00Z",
            )
            self.assertEqual(recovery["verified_prefix_records"], 1)
            self.assertFalse(recovery["source_mutated"])
            self.assertEqual(tampered_before, {path.name: path.read_bytes() for path in source.rglob("*") if path.is_file()})
            recovered_summary = verify_store(destination)
            self.assertEqual(recovered_summary["head_sha256"], first["head_sha256"])
            self.assertEqual(recovered_summary["known_beu_subtotal"], 21)
            with self.assertRaisesRegex(InvestitureError, "REPLAY_FROM_PRIOR_GENERATION"):
                append_event(destination, stable_json(EVENTS[0]), expected_head=first["head_sha256"], request_id=EVENTS[0]["replay_identity"])
            lifecycle = copy.deepcopy(EVENTS[4])
            lifecycle["bound_usage_event_ids"] = [EVENTS[0]["event_id"]]
            current = append_event(destination, stable_json(lifecycle), expected_head=first["head_sha256"], request_id=lifecycle["replay_identity"])
            rollback_current = parent / "rollback-current"
            recover_generation(
                rollback_target,
                rollback_current,
                expected_valid_head=first["head_sha256"],
                new_generation_id="FS-C01-GEN-ROLLBACK-CURRENT",
                created_at="2026-07-13T20:10:00Z",
            )
            rollback_event = copy.deepcopy(EVENTS[4])
            rollback_event["replay_identity"] = "fs-c01-rollback-lifecycle-replay-0001"
            rollback_event["event_id"] = "FS-C01-ROLLBACK-LIFECYCLE-001"
            rollback_event["bound_usage_event_ids"] = [EVENTS[0]["event_id"]]
            rollback_head = append_event(
                rollback_current,
                stable_json(rollback_event),
                expected_head=first["head_sha256"],
                request_id=rollback_event["replay_identity"],
            )
            plan = rollback_plan(rollback_current, rollback_target, expected_current_head=rollback_head["head_sha256"], expected_target_head=first["head_sha256"])
            self.assertFalse(plan["mutation_performed"])
            self.assertTrue(plan["owner_managed_selection_required"])
            self.assertNotEqual(source_before, tampered_before)

    def test_rollback_rejects_an_unrelated_same_ledger_generation(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-investiture-") as temp:
            parent = Path(temp)
            current = initialize(parent, "unrelated-current")
            target = initialize(parent, "unrelated-target")
            with self.assertRaisesRegex(InvestitureError, "ROLLBACK_TARGET_NOT_DIRECT_PREDECESSOR"):
                rollback_plan(
                    current,
                    target,
                    expected_current_head=ZERO_SHA256,
                    expected_target_head=ZERO_SHA256,
                )

    def test_reparse_classifier_fails_closed_without_platform_privilege(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-investiture-") as temp:
            root = Path(temp)
            with mock.patch("tools.investiture_accounting.storage._is_reparse", side_effect=lambda path: path == root):
                with self.assertRaisesRegex(InvestitureError, "STORE_ROOT_REPARSE_REJECTED"):
                    validate_external_root(root, must_exist=True)

    def test_store_root_swap_is_blocked_or_cannot_redirect_mutation(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-investiture-") as temp:
            parent = Path(temp)
            root = initialize(parent)
            moved = parent / "ledger-moved"
            replacement_created = False
            rename_blocked = False
            original_write = investiture_storage._write_exclusive

            def swap_before_intent(path: Path, payload: bytes) -> None:
                nonlocal replacement_created, rename_blocked
                if path.parent.name == "intents" and not replacement_created and not rename_blocked:
                    try:
                        root.rename(moved)
                        shutil.copytree(moved, root)
                        replacement_created = True
                    except OSError:
                        rename_blocked = True
                original_write(path, payload)

            with mock.patch("tools.investiture_accounting.storage._write_exclusive", side_effect=swap_before_intent):
                if os.name == "nt":
                    append_event(root, stable_json(EVENTS[0]), expected_head=ZERO_SHA256, request_id=EVENTS[0]["replay_identity"])
                else:
                    with self.assertRaisesRegex(InvestitureError, "STORE_ROOT_IDENTITY_CHANGED"):
                        append_event(root, stable_json(EVENTS[0]), expected_head=ZERO_SHA256, request_id=EVENTS[0]["replay_identity"])
            if os.name == "nt":
                self.assertTrue(rename_blocked)
                self.assertEqual(verify_store(root)["record_count"], 1)
            else:
                self.assertTrue(replacement_created)
                self.assertEqual(verify_store(root)["record_count"], 0)
                self.assertEqual(verify_store(moved)["record_count"], 1)

    def test_verify_uses_one_locked_stable_directory_snapshot(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-investiture-") as temp:
            parent = Path(temp)
            root = initialize(parent, "verify-source")
            moved = parent / "verify-moved"
            replacement_created = False
            rename_blocked = False
            original_records = investiture_storage._record_files

            def swap_during_read(stable_root: Path):
                nonlocal replacement_created, rename_blocked
                if not replacement_created and not rename_blocked:
                    try:
                        root.rename(moved)
                        shutil.copytree(moved, root)
                        replacement_created = True
                    except OSError:
                        rename_blocked = True
                return original_records(stable_root)

            with mock.patch("tools.investiture_accounting.storage._record_files", side_effect=swap_during_read):
                if os.name == "nt":
                    self.assertEqual(verify_store(root)["record_count"], 0)
                else:
                    with self.assertRaisesRegex(InvestitureError, "STORE_ROOT_IDENTITY_CHANGED"):
                        verify_store(root)
            if os.name == "nt":
                self.assertTrue(rename_blocked)
            else:
                self.assertTrue(replacement_created)
                self.assertEqual(verify_store(root)["record_count"], 0)
                self.assertEqual(verify_store(moved)["record_count"], 0)

    @unittest.skipUnless(os.name == "nt", "Windows directory-handle race contract")
    def test_windows_child_reparse_swap_after_handle_open_fails_before_mutation(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-investiture-") as temp:
            root = initialize(Path(temp))
            original_classifier = investiture_storage._is_reparse
            record_checks = 0

            def swapped_classifier(path: Path) -> bool:
                nonlocal record_checks
                if path.name == "records":
                    record_checks += 1
                    if record_checks >= 3:
                        return True
                return original_classifier(path)

            with mock.patch("tools.investiture_accounting.storage._is_reparse", side_effect=swapped_classifier):
                with self.assertRaisesRegex(InvestitureError, "STORE_LAYOUT_INVALID"):
                    append_event(
                        root,
                        stable_json(EVENTS[0]),
                        expected_head=ZERO_SHA256,
                        request_id=EVENTS[0]["replay_identity"],
                    )
            self.assertEqual(verify_store(root)["record_count"], 0)

    @unittest.skipUnless(os.name == "nt", "Windows directory-handle rename contract")
    def test_windows_physical_child_rename_is_denied_after_handle_acquisition(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-investiture-") as temp:
            root = initialize(Path(temp))
            records = root / "records"
            moved = root / "records-moved"
            original_records = investiture_storage._record_files
            rename_blocked = False

            def attempt_physical_rename(stable_root: Path):
                nonlocal rename_blocked
                try:
                    records.rename(moved)
                except OSError:
                    rename_blocked = True
                return original_records(stable_root)

            with mock.patch("tools.investiture_accounting.storage._record_files", side_effect=attempt_physical_rename):
                append_event(
                    root,
                    stable_json(EVENTS[0]),
                    expected_head=ZERO_SHA256,
                    request_id=EVENTS[0]["replay_identity"],
                )
            self.assertTrue(rename_blocked)
            self.assertFalse(moved.exists())
            self.assertEqual(verify_store(root)["record_count"], 1)

    @unittest.skipUnless(os.name == "nt", "Windows directory-handle race contract")
    def test_windows_root_reparse_swap_during_handle_open_fails_before_mutation(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-investiture-") as temp:
            root = initialize(Path(temp))
            original_open = investiture_storage._open_windows_directory
            original_classifier = investiture_storage._is_reparse
            root_opened = False

            def racing_open(path: Path):
                nonlocal root_opened
                handle = original_open(path)
                if path == root:
                    root_opened = True
                return handle

            def racing_classifier(path: Path) -> bool:
                return (path == root and root_opened) or original_classifier(path)

            with (
                mock.patch("tools.investiture_accounting.storage._open_windows_directory", side_effect=racing_open),
                mock.patch("tools.investiture_accounting.storage._is_reparse", side_effect=racing_classifier),
            ):
                with self.assertRaisesRegex(InvestitureError, "STORE_ROOT_IDENTITY_CHANGED"):
                    append_event(
                        root,
                        stable_json(EVENTS[0]),
                        expected_head=ZERO_SHA256,
                        request_id=EVENTS[0]["replay_identity"],
                    )
            self.assertEqual(verify_store(root)["record_count"], 0)

    @unittest.skipUnless(os.name != "nt" and Path("/proc/self/fd").is_dir(), "Linux stable-directory lock contract")
    def test_posix_append_lock_path_replacement_cannot_split_serialization(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-investiture-") as temp:
            root = initialize(Path(temp))
            _, _, identity = investiture_storage.load_manifest(root)
            with investiture_storage._mutation_view(root, identity) as stable_root:
                first_lock = investiture_storage._acquire_append_lock(stable_root)
                try:
                    (root / "append.lock").unlink()
                    (root / "append.lock").write_bytes(b"0")
                    with self.assertRaisesRegex(InvestitureError, "APPEND_LOCK_BUSY"):
                        investiture_storage._acquire_append_lock(stable_root)
                finally:
                    investiture_storage._release_append_lock(first_lock)
            self.assertEqual(verify_store(root)["record_count"], 0)

    def test_symlink_path_fails_closed_when_supported(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-investiture-") as temp:
            parent = Path(temp)
            target = parent / "target"
            target.mkdir()
            link = parent / "link"
            try:
                link.symlink_to(target, target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"symlink capability unavailable: {exc}")
            with self.assertRaisesRegex(InvestitureError, "STORE_ROOT_REPARSE_REJECTED"):
                verify_store(link)

    def test_hardlinked_ledger_file_fails_closed_when_supported(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-investiture-") as temp:
            parent = Path(temp)
            root = initialize(parent)
            duplicate = parent / "manifest-hardlink.json"
            try:
                os.link(root / "manifest.json", duplicate)
            except OSError as exc:
                self.skipTest(f"hardlink capability unavailable: {exc}")
            with self.assertRaisesRegex(InvestitureError, "LEDGER_FILE_UNSAFE"):
                verify_store(root)


if __name__ == "__main__":
    unittest.main()
