from __future__ import annotations

import json
import os
import shutil
import stat
import tempfile
import unittest
from unittest import mock
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import sys

sys.path.insert(0, str(ROOT))

from production_adapter.authority import validate_mission
from production_adapter.receipt import sha256_file, stable_json
import spear_bridge.compiler as compiler_module
from spear_bridge.compiler import MANIFEST_IDENTITY, SpearBridgeError, compile_package
from spear_bridge.git_reader import GitReader, GitReaderError, SourceAbsentError, SourceFile


BASE = "d6e81106707dab43981ee62c3c7a660407fa89fb"


def sha256(data: bytes) -> str:
    import hashlib

    return hashlib.sha256(data).hexdigest()


class FakeReader:
    def __init__(self, *, observed_base: str | None = BASE) -> None:
        self.prepared = False
        self.observed_base = observed_base
        self.closed = False
        self.files = {
            "docs/replace.txt": SourceFile(b"existing replace\n", sha256(b"existing replace\n"), "b" * 40),
            "docs/delete.txt": SourceFile(b"existing delete\n", sha256(b"existing delete\n"), "c" * 40),
            "docs/existing-add.txt": SourceFile(b"already here\n", sha256(b"already here\n"), "d" * 40),
        }

    def prepare(self) -> None:
        self.prepared = True

    def read_source(self, path: str) -> SourceFile:
        if path not in self.files:
            raise SourceAbsentError(f"source missing: {path}")
        return self.files[path]

    def close(self) -> None:
        self.closed = True


class FailingAddReader(FakeReader):
    def read_source(self, path: str) -> SourceFile:
        if path == "docs/add.txt":
            raise GitReaderError("simulated source read failure")
        return super().read_source(path)


def base_weave(threads: list[dict], *, delete_authority_id: str | None = None, mission_name: str = "mission.json", receipt_name: str = "receipt.json") -> dict:
    weave = {
        "schema_version": "atlas-thread-engine-spear-weave-v1",
        "implementation_state": "SPEAR_BRIDGE_DISABLED",
        "bridge_mode": "COMPILE_ONLY",
        "route": "SPEAR_DIRECT",
        "persistent_writer": "ABSENT",
        "dispatch_authority": "ABSENT",
        "activation_authority": "ABSENT",
        "standing_authority": "NO",
        "weave_id": "GATE-7G-A-UNIT-WEAVE",
        "authority_id": "GATE-7G-A-UNIT-AUTHORITY",
        "build_identity": "GATE-7G-A-UNIT-BUILD",
        "execute_identity": "GATE-7G-A-UNIT-EXECUTE",
        "repository": "Jktomy/atlas-prime",
        "base_sha": BASE,
        "branch": "source/gate-7g-a-unit",
        "commit_message": "codex: unit Spear bridge mission",
        "pr_title": "codex: unit Spear bridge mission",
        "pr_body": "Unit Spear bridge mission.\n",
        "threads": threads,
        "output_mission_filename": mission_name,
        "compile_receipt_filename": receipt_name,
        "stop_point": "MISSION_COMPILED",
    }
    if delete_authority_id is not None:
        weave["delete_authority_id"] = delete_authority_id
    return weave


def manifest_for(files: dict[str, bytes], *, extra: dict | None = None, entries: list[dict] | None = None) -> dict:
    manifest = {
        "manifest_identity": MANIFEST_IDENTITY,
        "files": entries
        if entries is not None
        else [
            {"path": path, "bytes": len(data), "sha256": sha256(data)}
            for path, data in sorted(files.items())
        ],
    }
    if extra:
        manifest.update(extra)
    return manifest


def write_package(root: Path, weave: dict, payloads: dict[str, bytes] | None = None, *, name: str = "spear.zip", manifest: dict | None = None) -> tuple[Path, str]:
    payloads = payloads if payloads is not None else payloads_for_weave(weave)
    weave_bytes = (stable_json(weave) + "\n").encode("utf-8")
    files = {"SPEAR-WEAVE.json": weave_bytes, **payloads}
    manifest = manifest or manifest_for(files)
    archive_path = root / name
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("SPEAR-WEAVE.json", weave_bytes)
        archive.writestr("PACKAGE-MANIFEST.json", stable_json(manifest).encode("utf-8"))
        for path, data in payloads.items():
            archive.writestr(path, data)
    return archive_path, sha256(archive_path.read_bytes())


def write_custom_package(root: Path, weave: dict, *, extra_entries: list[zipfile.ZipInfo] | None = None, omit_extra_from_manifest: bool = True) -> tuple[Path, str]:
    payloads = payloads_for_weave(weave)
    weave_bytes = (stable_json(weave) + "\n").encode("utf-8")
    files = {"SPEAR-WEAVE.json": weave_bytes, **payloads}
    archive_path = root / "custom.zip"
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        write_zip_entry(archive, "SPEAR-WEAVE.json", weave_bytes, 0o100644)
        write_zip_entry(archive, "PACKAGE-MANIFEST.json", stable_json(manifest_for(files)).encode("utf-8"), 0o100644)
        for path, data in payloads.items():
            write_zip_entry(archive, path, data, 0o100644)
        for info in extra_entries or []:
            data = b"" if info.is_dir() else b"extra\n"
            archive.writestr(info, data)
    return archive_path, sha256(archive_path.read_bytes())


def zip_info(name: str, mode: int) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name)
    info.external_attr = mode << 16
    return info


def write_zip_entry(archive: zipfile.ZipFile, name: str, data: bytes, mode: int) -> None:
    archive.writestr(zip_info(name, mode), data)


def payloads_for_weave(weave: dict) -> dict[str, bytes]:
    values = {
        "add.txt": b"added\n",
        "replace.txt": b"replaced\n",
    }
    payloads: dict[str, bytes] = {}
    for thread in weave["threads"]:
        if thread["operation"] in {"ADD", "REPLACE"}:
            name = thread["payload"]
            payloads[f"PAYLOADS/{name}"] = values.get(name, f"payload for {name}\n".encode("utf-8"))
    return payloads


def compile_success(root: Path, weave: dict, payloads: dict[str, bytes] | None = None, *, reader: FakeReader | None = None) -> tuple[Path, dict, dict]:
    package, package_sha = write_package(root, weave, payloads)
    output = root / "out"
    receipt = compile_package(package, package_sha256=package_sha, output_dir=output, disabled_proof=True, compile_only=True, reader=reader or FakeReader())
    mission = json.loads((output / weave["output_mission_filename"]).read_text(encoding="utf-8"))
    return output, mission, receipt


class SpearBridgeTests(unittest.TestCase):
    def test_compile_add_replace_outputs_adapter_ready_package(self) -> None:
        threads = [
            {"thread_id": "add", "operation": "ADD", "path": "docs/add.txt", "payload": "add.txt"},
            {"thread_id": "replace", "operation": "REPLACE", "path": "docs/replace.txt", "payload": "replace.txt"},
        ]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output, mission, receipt = compile_success(root, base_weave(threads))
            validate_mission(mission)
            self.assertEqual(sorted(path.relative_to(output).as_posix() for path in output.rglob("*") if path.is_file()), ["PAYLOADS/add.txt", "PAYLOADS/replace.txt", "mission.json", "receipt.json"])
            self.assertEqual(receipt["result"], "SUCCESS")
            self.assertEqual(receipt["base_expected"], BASE)
            self.assertEqual(receipt["base_observed"], BASE)
            self.assertEqual(receipt["compile_receipt_filename"], "receipt.json")
            self.assertEqual(receipt["payload_inventory"], [
                {"path": "add.txt", "bytes": 6, "sha256": sha256(b"added\n")},
                {"path": "replace.txt", "bytes": 9, "sha256": sha256(b"replaced\n")},
            ])
            self.assertEqual(receipt["forbidden_action_confirmation"]["adapter_invoked"], False)
            self.assertEqual(receipt["forbidden_action_confirmation"]["github_mutation"], False)
            self.assertEqual(receipt["forbidden_action_confirmation"]["production_authority_activated"], False)
            self.assertEqual(receipt["forbidden_action_confirmation"]["standing_authority"], "NO")
            self.assertNotIn("read_only_clone_disposed", receipt)

    def test_compiled_output_satisfies_payload_hash_preconditions_without_reauthoring(self) -> None:
        threads = [
            {"thread_id": "add", "operation": "ADD", "path": "docs/add.txt", "payload": "add.txt"},
            {"thread_id": "replace", "operation": "REPLACE", "path": "docs/replace.txt", "payload": "replace.txt"},
        ]
        with tempfile.TemporaryDirectory() as temp:
            output, mission, _receipt = compile_success(Path(temp), base_weave(threads))
            payload_root = output / mission["payload_root"]
            self.assertTrue(payload_root.is_dir())
            for operation in mission["operations"]:
                if operation["operation"] in {"ADD", "REPLACE"}:
                    payload = payload_root / operation["payload"]
                    self.assertTrue(payload.is_file())
                    self.assertEqual(sha256_file(payload), operation["payload_sha256"])

    def test_delete_requires_matching_authority_and_compiles(self) -> None:
        authority = "GATE-7G-A-DELETE-AUTHORITY"
        thread = {"thread_id": "delete", "operation": "DELETE", "path": "docs/delete.txt", "delete_authority_id": authority}
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            compile_success(root, base_weave([thread], delete_authority_id=authority))
            bad = dict(thread)
            bad["delete_authority_id"] = "WRONG"
            bad_package, bad_sha = write_package(root, base_weave([bad], delete_authority_id=authority), name="bad.zip")
            with self.assertRaises(SpearBridgeError) as raised:
                compile_package(bad_package, package_sha256=bad_sha, output_dir=root / "bad-out", disabled_proof=True, compile_only=True, reader=FakeReader())
            self.assertEqual(raised.exception.code, "DELETE_AUTHORITY_REQUIRED")

    def test_unused_payload_rejected(self) -> None:
        threads = [{"thread_id": "add", "operation": "ADD", "path": "docs/add.txt", "payload": "add.txt"}]
        payloads = {"PAYLOADS/add.txt": b"added\n", "PAYLOADS/unused.txt": b"unused\n"}
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package, package_sha = write_package(root, base_weave(threads), payloads)
            with self.assertRaises(SpearBridgeError) as raised:
                compile_package(package, package_sha256=package_sha, output_dir=root / "out", disabled_proof=True, compile_only=True, reader=FakeReader())
            self.assertEqual(raised.exception.code, "PAYLOAD_SET_MISMATCH")

    def test_true_absent_add_accepted_but_existing_or_uncertain_add_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            compile_success(root, base_weave([{"thread_id": "add", "operation": "ADD", "path": "docs/add.txt", "payload": "add.txt"}]))
        cases = [
            (base_weave([{"thread_id": "add", "operation": "ADD", "path": "docs/existing-add.txt", "payload": "add.txt"}]), FakeReader(), "THREAD_REJECTED"),
            (base_weave([{"thread_id": "add", "operation": "ADD", "path": "docs/add.txt", "payload": "add.txt"}]), FailingAddReader(), "SPEAR_BRIDGE_REJECTED"),
        ]
        for weave, reader, code in cases:
            with self.subTest(code=code):
                with tempfile.TemporaryDirectory() as temp:
                    root = Path(temp)
                    package, package_sha = write_package(root, weave)
                    with self.assertRaises(SpearBridgeError) as raised:
                        compile_package(package, package_sha256=package_sha, output_dir=root / "out", disabled_proof=True, compile_only=True, reader=reader)
                    self.assertEqual(raised.exception.code, code)

    def test_source_nonregular_add_target_rejected(self) -> None:
        class NonRegularReader(FakeReader):
            def read_source(self, path: str) -> SourceFile:
                raise GitReaderError("source file is not a regular file")

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package, package_sha = write_package(root, base_weave([{"thread_id": "add", "operation": "ADD", "path": "docs/add.txt", "payload": "add.txt"}]))
            with self.assertRaises(SpearBridgeError) as raised:
                compile_package(package, package_sha256=package_sha, output_dir=root / "out", disabled_proof=True, compile_only=True, reader=NonRegularReader())
            self.assertEqual(raised.exception.code, "SPEAR_BRIDGE_REJECTED")

    def test_mission_receipt_filename_collision_rejected(self) -> None:
        weave = base_weave([{"thread_id": "add", "operation": "ADD", "path": "docs/add.txt", "payload": "add.txt"}], mission_name="same.json", receipt_name="same.json")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package, package_sha = write_package(root, weave)
            with self.assertRaises(SpearBridgeError) as raised:
                compile_package(package, package_sha256=package_sha, output_dir=root / "out", disabled_proof=True, compile_only=True, reader=FakeReader())
            self.assertEqual(raised.exception.code, "OUTPUT_COLLISION")

    def test_failure_leaves_output_absent_or_empty(self) -> None:
        weave = base_weave([{"thread_id": "add", "operation": "ADD", "path": "docs/add.txt", "payload": "add.txt"}])
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package, package_sha = write_package(root, weave)
            output = root / "out"
            with self.assertRaises(SpearBridgeError):
                compile_package(package, package_sha256=package_sha, output_dir=output, disabled_proof=True, compile_only=True, reader=FakeReader(observed_base="0" * 40))
            self.assertTrue((not output.exists()) or list(output.iterdir()) == [])

    def test_manifest_strictness(self) -> None:
        weave = base_weave([{"thread_id": "add", "operation": "ADD", "path": "docs/add.txt", "payload": "add.txt"}])
        weave_bytes = (stable_json(weave) + "\n").encode("utf-8")
        payload = b"added\n"
        files = {"SPEAR-WEAVE.json": weave_bytes, "PAYLOADS/add.txt": payload}
        manifest_cases = [
            manifest_for(files, extra={"unexpected": True}),
            manifest_for(files, entries=[
                {"path": "SPEAR-WEAVE.json", "bytes": len(weave_bytes), "sha256": sha256(weave_bytes)},
                {"path": "spear-weave.json", "bytes": len(weave_bytes), "sha256": sha256(weave_bytes)},
                {"path": "PAYLOADS/add.txt", "bytes": len(payload), "sha256": sha256(payload)},
            ]),
            manifest_for(files, entries=[{"path": "SPEAR-WEAVE.json", "bytes": True, "sha256": sha256(weave_bytes)}, {"path": "PAYLOADS/add.txt", "bytes": len(payload), "sha256": sha256(payload)}]),
            manifest_for(files, entries=[{"path": "SPEAR-WEAVE.json", "bytes": "1", "sha256": sha256(weave_bytes)}, {"path": "PAYLOADS/add.txt", "bytes": len(payload), "sha256": sha256(payload)}]),
            manifest_for(files, entries=[{"path": "SPEAR-WEAVE.json", "bytes": 1.5, "sha256": sha256(weave_bytes)}, {"path": "PAYLOADS/add.txt", "bytes": len(payload), "sha256": sha256(payload)}]),
            manifest_for(files, entries=[{"path": "SPEAR-WEAVE.json", "bytes": len(weave_bytes), "sha256": "g" * 64}, {"path": "PAYLOADS/add.txt", "bytes": len(payload), "sha256": sha256(payload)}]),
        ]
        for manifest in manifest_cases:
            with self.subTest(manifest=manifest):
                with tempfile.TemporaryDirectory() as temp:
                    root = Path(temp)
                    package, package_sha = write_package(root, weave, {"PAYLOADS/add.txt": payload}, manifest=manifest)
                    with self.assertRaises(SpearBridgeError):
                        compile_package(package, package_sha256=package_sha, output_dir=root / "out", disabled_proof=True, compile_only=True, reader=FakeReader())

    def test_carrier_optional_payloads_directory_entry_accepted(self) -> None:
        weave = base_weave([{"thread_id": "add", "operation": "ADD", "path": "docs/add.txt", "payload": "add.txt"}])
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package, package_sha = write_custom_package(root, weave, extra_entries=[zip_info("PAYLOADS/", 0o040755)])
            receipt = compile_package(package, package_sha256=package_sha, output_dir=root / "out", disabled_proof=True, compile_only=True, reader=FakeReader())
            self.assertEqual(receipt["result"], "SUCCESS")

    def test_carrier_entry_classification_rejections(self) -> None:
        weave = base_weave([{"thread_id": "add", "operation": "ADD", "path": "docs/add.txt", "payload": "add.txt"}])
        cases = [
            zip_info("PAYLOADS/link/", 0o120777),
            zip_info("PAYLOADS/link.txt", 0o120777),
            zip_info("PAYLOADS/fifo", 0o010644),
            zip_info("SPEAR-WEAVE.json/extra", 0o100644),
            zip_info("PACKAGE-MANIFEST.json/extra", 0o100644),
            zip_info("PAYLOADS", 0o100644),
            zip_info("PAYLOADS/bad.ZIP", 0o100644),
            zip_info("../escape/", 0o040755),
            zip_info("PAYLOADS/Dir/", 0o040755),
        ]
        for entry in cases:
            with self.subTest(entry=entry.filename):
                with tempfile.TemporaryDirectory() as temp:
                    root = Path(temp)
                    extras = [entry]
                    if entry.filename == "PAYLOADS/Dir/":
                        extras.append(zip_info("PAYLOADS/dir/", 0o040755))
                    package, package_sha = write_custom_package(root, weave, extra_entries=extras)
                    with self.assertRaises(SpearBridgeError):
                        compile_package(package, package_sha256=package_sha, output_dir=root / "out", disabled_proof=True, compile_only=True, reader=FakeReader())

    def test_manifest_matches_complete_regular_file_set(self) -> None:
        weave = base_weave([{"thread_id": "add", "operation": "ADD", "path": "docs/add.txt", "payload": "add.txt"}])
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package, package_sha = write_custom_package(root, weave, extra_entries=[zip_info("PAYLOADS/unmanifested.txt", 0o100644)])
            with self.assertRaises(SpearBridgeError) as raised:
                compile_package(package, package_sha256=package_sha, output_dir=root / "out", disabled_proof=True, compile_only=True, reader=FakeReader())
            self.assertEqual(raised.exception.code, "MANIFEST_TAMPER")

    def test_output_directory_symlink_rejected_and_target_untouched(self) -> None:
        weave = base_weave([{"thread_id": "add", "operation": "ADD", "path": "docs/add.txt", "payload": "add.txt"}])
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / "target"
            target.mkdir()
            marker = target / "marker.txt"
            marker.write_text("keep\n", encoding="utf-8")
            output = root / "out-link"
            try:
                output.symlink_to(target, target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"filesystem symlink capability unavailable: {exc}")
            package, package_sha = write_package(root, weave)
            with self.assertRaises(SpearBridgeError) as raised:
                compile_package(package, package_sha256=package_sha, output_dir=output, disabled_proof=True, compile_only=True, reader=FakeReader())
            self.assertEqual(raised.exception.code, "OUTPUT_COLLISION")
            self.assertEqual(marker.read_text(encoding="utf-8"), "keep\n")

    def test_empty_directory_does_not_traverse_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / "target"
            target.mkdir()
            marker = target / "marker.txt"
            marker.write_text("keep\n", encoding="utf-8")
            link = root / "link"
            try:
                link.symlink_to(target, target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"filesystem symlink capability unavailable: {exc}")
            compiler_module._empty_directory(link)
            self.assertEqual(marker.read_text(encoding="utf-8"), "keep\n")

    def test_internal_reader_closed_before_publication_and_receipt_records_disposal(self) -> None:
        class InternalReader(FakeReader):
            instances: list["InternalReader"] = []

            def __init__(self, *, base_sha: str) -> None:
                super().__init__(observed_base=base_sha)
                self.base_sha = base_sha
                InternalReader.instances.append(self)

        original = compiler_module.GitReader
        compiler_module.GitReader = InternalReader  # type: ignore[assignment]
        try:
            weave = base_weave([{"thread_id": "add", "operation": "ADD", "path": "docs/add.txt", "payload": "add.txt"}])
            with tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                package, package_sha = write_package(root, weave)
                receipt = compile_package(package, package_sha256=package_sha, output_dir=root / "out", disabled_proof=True, compile_only=True)
                self.assertTrue(InternalReader.instances[0].closed)
                self.assertEqual(receipt["read_only_clone_disposed"], True)
        finally:
            compiler_module.GitReader = original  # type: ignore[assignment]

    def test_reader_disposal_failure_rejects_without_output(self) -> None:
        class FailingCloseReader(FakeReader):
            def __init__(self, *, base_sha: str) -> None:
                super().__init__(observed_base=base_sha)

            def close(self) -> None:
                raise GitReaderError("dispose failed")

        original = compiler_module.GitReader
        compiler_module.GitReader = FailingCloseReader  # type: ignore[assignment]
        try:
            weave = base_weave([{"thread_id": "add", "operation": "ADD", "path": "docs/add.txt", "payload": "add.txt"}])
            with tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                package, package_sha = write_package(root, weave)
                output = root / "out"
                with self.assertRaises(SpearBridgeError):
                    compile_package(package, package_sha256=package_sha, output_dir=output, disabled_proof=True, compile_only=True)
                self.assertTrue((not output.exists()) or list(output.iterdir()) == [])
        finally:
            compiler_module.GitReader = original  # type: ignore[assignment]

    def test_caller_supplied_reader_is_not_closed(self) -> None:
        reader = FakeReader()
        weave = base_weave([{"thread_id": "add", "operation": "ADD", "path": "docs/add.txt", "payload": "add.txt"}])
        with tempfile.TemporaryDirectory() as temp:
            _output, _mission, receipt = compile_success(Path(temp), weave, reader=reader)
            self.assertFalse(reader.closed)
            self.assertNotIn("read_only_clone_disposed", receipt)

    def test_git_reader_disposes_nested_readonly_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            reader = GitReader(base_sha=BASE, work_root=Path(temp))
            target = reader.root / "checkout" / "nested" / "readonly.txt"
            target.parent.mkdir(parents=True)
            target.write_text("readonly\n", encoding="utf-8")
            target.chmod(stat.S_IREAD)
            reader.close()
            self.assertFalse(reader.root.exists())
            reader.close()

    def test_git_reader_disposes_nested_readonly_directory_when_supported(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            reader = GitReader(base_sha=BASE, work_root=Path(temp))
            target = reader.root / "checkout" / "readonly-dir"
            target.mkdir(parents=True)
            marker = target / "marker.txt"
            marker.write_text("marker\n", encoding="utf-8")
            try:
                target.chmod(stat.S_IREAD | stat.S_IEXEC)
            except OSError as exc:
                reader.close()
                self.skipTest(f"filesystem cannot represent read-only directory capability: {exc}")
            reader.close()
            self.assertFalse(reader.root.exists())

    def test_git_reader_disposes_nested_readonly_tree_before_rmtree(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            reader = GitReader(base_sha=BASE, work_root=Path(temp))
            nested = reader.root / "checkout" / "nested" / "deeper"
            nested.mkdir(parents=True)
            marker = nested / "marker.txt"
            marker.write_text("marker\n", encoding="utf-8")
            for target in (marker, nested, nested.parent):
                target.chmod(stat.S_IREAD | stat.S_IEXEC)

            original = shutil.rmtree
            observed_modes: list[int] = []

            def assert_writable(path, *args, **kwargs):
                observed_modes.append(marker.stat().st_mode)
                return original(path, *args, **kwargs)

            with mock.patch("spear_bridge.git_reader.shutil.rmtree", side_effect=assert_writable):
                reader.close()
            self.assertTrue(observed_modes[0] & stat.S_IWUSR)
            self.assertFalse(reader.root.exists())

    def test_git_reader_bounded_retry_handles_transient_rmtree_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            reader = GitReader(base_sha=BASE, work_root=Path(temp))
            marker = reader.root / "checkout" / "file.txt"
            marker.parent.mkdir(parents=True)
            marker.write_text("content\n", encoding="utf-8")
            original = shutil.rmtree
            calls: list[str] = []

            def transient(path, *args, **kwargs):
                calls.append(str(path))
                if len(calls) == 1:
                    raise PermissionError("transient busy handle")
                return original(path, *args, **kwargs)

            with mock.patch("spear_bridge.git_reader.shutil.rmtree", side_effect=transient), mock.patch("spear_bridge.git_reader.time.sleep") as sleep:
                reader.close()
            self.assertFalse(reader.root.exists())
            self.assertEqual(len(calls), 2)
            sleep.assert_called_once()

    def test_git_reader_callback_clears_readonly_and_retries_failed_operation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            reader = GitReader(base_sha=BASE, work_root=Path(temp))
            target = reader.root / "checkout" / "readonly.txt"
            target.parent.mkdir(parents=True)
            target.write_text("content\n", encoding="utf-8")
            target.chmod(stat.S_IREAD)

            def remove(path: Path) -> None:
                self.assertTrue(path.stat().st_mode & stat.S_IWUSR)
                path.unlink()

            reader._clear_readonly_and_retry(remove, str(target), PermissionError("readonly"))  # type: ignore[attr-defined]
            self.assertFalse(target.exists())
            reader.close()

    def test_git_reader_allows_only_canonical_or_tokenized_remote_and_redacts_errors(self) -> None:
        token_remote = "https://x-access-token:secret-token@github.com/Jktomy/atlas-prime.git"
        reader = GitReader(remote_url=token_remote, base_sha=BASE)
        try:
            reader._validate(["git", "ls-remote", token_remote, "refs/heads/main"])  # type: ignore[attr-defined]
            self.assertIn("https://github.com/Jktomy/atlas-prime.git", reader._sanitize_git_message(token_remote))  # type: ignore[attr-defined]
            self.assertNotIn("secret-token", reader._sanitize_git_message(token_remote))  # type: ignore[attr-defined]
        finally:
            reader.close()

        with tempfile.TemporaryDirectory() as temp:
            bad_reader = GitReader(remote_url="https://github.com/example/other.git", base_sha=BASE, work_root=Path(temp))
            try:
                with self.assertRaises(GitReaderError):
                    bad_reader._validate(["git", "ls-remote", "https://github.com/example/other.git", "refs/heads/main"])  # type: ignore[attr-defined]
            finally:
                bad_reader.close()

    def test_git_reader_persistent_disposal_failure_preserves_root_for_inspection(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            reader = GitReader(base_sha=BASE, work_root=Path(temp))
            marker = reader.root / "checkout" / "file.txt"
            marker.parent.mkdir(parents=True)
            marker.write_text("content\n", encoding="utf-8")
            with mock.patch("spear_bridge.git_reader.shutil.rmtree", side_effect=PermissionError("persistent")), mock.patch("spear_bridge.git_reader.time.sleep") as sleep:
                with self.assertRaises(GitReaderError) as raised:
                    reader.close()
            self.assertEqual(str(raised.exception), "failed to dispose read-only clone")
            self.assertTrue(reader.root.exists())
            self.assertEqual(sleep.call_count, 4)
            reader.close()
            self.assertFalse(reader.root.exists())

    def test_git_reader_rejects_tampered_owned_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            reader = GitReader(base_sha=BASE, work_root=root)
            original = reader.root
            tampered = root / "atlas-spear-bridge-git-tampered"
            tampered.mkdir()
            reader.root = tampered
            with self.assertRaises(GitReaderError):
                reader.close()
            reader.root = original
            reader.close()

    def test_git_reader_rejects_symlink_root_and_leaves_target_untouched(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            reader = GitReader(base_sha=BASE, work_root=root)
            original = reader.root
            target = root / "target"
            target.mkdir()
            marker = target / "marker.txt"
            marker.write_text("keep\n", encoding="utf-8")
            link = root / "atlas-spear-bridge-git-link"
            try:
                link.symlink_to(target, target_is_directory=True)
            except OSError as exc:
                reader.close()
                self.skipTest(f"filesystem symlink capability unavailable: {exc}")
            reader.root = link
            reader._owned_root = link.resolve(strict=False)  # type: ignore[attr-defined]
            with self.assertRaises(GitReaderError):
                reader.close()
            self.assertEqual(marker.read_text(encoding="utf-8"), "keep\n")
            reader.root = original
            reader._owned_root = original.resolve(strict=False)  # type: ignore[attr-defined]
            reader.close()

    def test_observed_base_required_and_recorded(self) -> None:
        weave = base_weave([{"thread_id": "add", "operation": "ADD", "path": "docs/add.txt", "payload": "add.txt"}])
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _output, _mission, receipt = compile_success(root, weave, reader=FakeReader(observed_base=BASE))
            self.assertEqual(receipt["base_observed"], BASE)
        for observed in (None, "0" * 40):
            with self.subTest(observed=observed):
                with tempfile.TemporaryDirectory() as temp:
                    root = Path(temp)
                    package, package_sha = write_package(root, weave)
                    with self.assertRaises(SpearBridgeError) as raised:
                        compile_package(package, package_sha256=package_sha, output_dir=root / "out", disabled_proof=True, compile_only=True, reader=FakeReader(observed_base=observed))
                    self.assertEqual(raised.exception.code, "BASE_MISMATCH")

    def test_deterministic_repeated_compile_output(self) -> None:
        weave = base_weave([
            {"thread_id": "add", "operation": "ADD", "path": "docs/add.txt", "payload": "add.txt"},
            {"thread_id": "replace", "operation": "REPLACE", "path": "docs/replace.txt", "payload": "replace.txt"},
        ])
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package, package_sha = write_package(root, weave)
            out1 = root / "out1"
            out2 = root / "out2"
            compile_package(package, package_sha256=package_sha, output_dir=out1, disabled_proof=True, compile_only=True, reader=FakeReader())
            compile_package(package, package_sha256=package_sha, output_dir=out2, disabled_proof=True, compile_only=True, reader=FakeReader())
            self.assertEqual(snapshot(out1), snapshot(out2))

    def test_prior_rejections_remain(self) -> None:
        threads = [{"thread_id": "add", "operation": "ADD", "path": "docs/add.txt", "payload": "add.txt"}]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package, package_sha = write_package(root, base_weave(threads))
            with self.assertRaises(SpearBridgeError) as raised:
                compile_package(package, package_sha256="0" * 64, output_dir=root / "out", disabled_proof=True, compile_only=True, reader=FakeReader())
            self.assertEqual(raised.exception.code, "CARRIER_SHA_MISMATCH")
            with self.assertRaises(SpearBridgeError) as raised:
                compile_package(package, package_sha256=package_sha, output_dir=root / "out2", disabled_proof=True, compile_only=False, reader=FakeReader())
            self.assertEqual(raised.exception.code, "INTENT_REQUIRED")

    def test_duplicate_json_and_path_rejections_remain(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package = root / "dup.zip"
            weave = b'{"schema_version":"atlas-thread-engine-spear-weave-v1","schema_version":"x"}'
            manifest = manifest_for({"SPEAR-WEAVE.json": weave})
            with zipfile.ZipFile(package, "w") as archive:
                archive.writestr("SPEAR-WEAVE.json", weave)
                archive.writestr("PACKAGE-MANIFEST.json", stable_json(manifest).encode("utf-8"))
            with self.assertRaises(SpearBridgeError) as raised:
                compile_package(package, package_sha256=sha256(package.read_bytes()), output_dir=root / "out", disabled_proof=True, compile_only=True, reader=FakeReader())
            self.assertEqual(raised.exception.code, "DUPLICATE_JSON_KEY")
        cases = [
            ("../x", "PATH_REJECTED"),
            ("codex/atlas-active-workboard.md", "PROTECTED_PATH"),
        ]
        for path, code in cases:
            with self.subTest(path=path):
                threads = [{"thread_id": "add", "operation": "ADD", "path": path, "payload": "add.txt"}]
                with tempfile.TemporaryDirectory() as temp:
                    root = Path(temp)
                    package, package_sha = write_package(root, base_weave(threads))
                    with self.assertRaises(SpearBridgeError) as raised:
                        compile_package(package, package_sha256=package_sha, output_dir=root / "out", disabled_proof=True, compile_only=True, reader=FakeReader())
                    self.assertEqual(raised.exception.code, code)


def snapshot(root: Path) -> list[tuple[str, str]]:
    return [
        (path.relative_to(root).as_posix(), sha256(path.read_bytes()))
        for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix())
        if path.is_file()
    ]


if __name__ == "__main__":
    unittest.main()
