from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
THREAD_ENGINE = ROOT / "tools" / "thread-engine"
sys.path.insert(0, str(THREAD_ENGINE))

from production_adapter.authority import validate_mission  # noqa: E402
from production_adapter.path_policy import PolicyError, validate_declared_path_set  # noqa: E402
from production_adapter.protected_paths import (  # noqa: E402
    compiler_bound_safe_declared_path_scope,
    direct_spear_path_scope,
)
from production_adapter.receipt import stable_json  # noqa: E402
from spear_bridge.compiler import MANIFEST_IDENTITY, compile_package  # noqa: E402
from spear_bridge.git_reader import SourceAbsentError  # noqa: E402

BASE = "a" * 40


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class AbsentReader:
    observed_base = BASE

    def prepare(self) -> None:
        return None

    def read_source(self, path: str):
        raise SourceAbsentError(f"source absent: {path}")

    def close(self) -> None:
        return None


def write_package(root: Path) -> tuple[Path, str]:
    threads = [
        {
            "thread_id": "governance-add",
            "operation": "ADD",
            "path": "governance/spear-universal-proof.md",
            "payload": "governance.md",
        },
        {
            "thread_id": "thread-engine-add",
            "operation": "ADD",
            "path": "tools/thread-engine/spear-universal-proof.py",
            "payload": "thread-engine.py",
        },
    ]
    weave = {
        "schema_version": "atlas-thread-engine-spear-weave-v1",
        "implementation_state": "SPEAR_BRIDGE_DISABLED",
        "bridge_mode": "COMPILE_ONLY",
        "route": "SPEAR_DIRECT",
        "persistent_writer": "ABSENT",
        "dispatch_authority": "ABSENT",
        "activation_authority": "ABSENT",
        "standing_authority": "NO",
        "weave_id": "SPEAR-UNIVERSAL-PATHS-R01",
        "authority_id": "SPEAR-UNIVERSAL-PATHS-R01-AUTHORITY",
        "build_identity": "SPEAR-UNIVERSAL-PATHS-R01-BUILD",
        "execute_identity": "SPEAR-UNIVERSAL-PATHS-R01-EXECUTE",
        "repository": "Jktomy/atlas-prime",
        "base_sha": BASE,
        "branch": "source/spear-universal-paths-r01",
        "commit_message": "prove universal Spear repository paths",
        "pr_title": "Prove universal Spear repository paths",
        "pr_body": "Bounded draft-PR-only universal path proof.\n",
        "threads": threads,
        "output_mission_filename": "mission.json",
        "compile_receipt_filename": "compile-receipt.json",
        "stop_point": "MISSION_COMPILED",
    }
    payloads = {
        "PAYLOADS/governance.md": b"# Spear universal path proof\n",
        "PAYLOADS/thread-engine.py": b"PROOF = True\n",
    }
    weave_bytes = (stable_json(weave) + "\n").encode("utf-8")
    observed = {"SPEAR-WEAVE.json": weave_bytes, **payloads}
    manifest = {
        "manifest_identity": MANIFEST_IDENTITY,
        "files": [
            {"path": path, "bytes": len(data), "sha256": digest(data)}
            for path, data in sorted(observed.items())
        ],
    }
    package = root / "spear.zip"
    with zipfile.ZipFile(package, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("SPEAR-WEAVE.json", weave_bytes)
        archive.writestr("PACKAGE-MANIFEST.json", stable_json(manifest).encode("utf-8"))
        for path, data in payloads.items():
            archive.writestr(path, data)
    return package, digest(package.read_bytes())


class SpearUniversalPathTests(unittest.TestCase):
    def test_direct_spear_compiles_governance_and_thread_engine_paths(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-spear-universal-") as temporary:
            root = Path(temporary)
            package, package_sha = write_package(root)
            output = root / "output"
            with direct_spear_path_scope():
                receipt = compile_package(
                    package,
                    package_sha256=package_sha,
                    output_dir=output,
                    disabled_proof=True,
                    compile_only=True,
                    reader=AbsentReader(),
                )
            mission = json.loads((output / "mission.json").read_text(encoding="utf-8"))
            validated = validate_mission(mission)

        self.assertEqual(receipt["result"], "SUCCESS")
        self.assertEqual(validated.payload_root, "PAYLOADS")
        self.assertEqual(validated.receipt_name, "production-adapter-receipt.json")
        self.assertEqual(
            set(validated.declared_paths),
            {
                "governance/spear-universal-proof.md",
                "tools/thread-engine/spear-universal-proof.py",
            },
        )
        self.assertIsNone(validated.aegis_break_authority)

    def test_direct_spear_scope_closes_after_compile(self) -> None:
        with self.assertRaises(PolicyError) as raised:
            validate_declared_path_set(["governance/noctua.md"])
        self.assertEqual(raised.exception.code, "PROTECTED_PATH")

    def test_route_neutral_compiler_scope_is_bounded(self) -> None:
        with self.assertRaises(PolicyError):
            validate_declared_path_set(["lifecycle/feathers/example.json"])
        with compiler_bound_safe_declared_path_scope():
            declared = validate_declared_path_set(["lifecycle/feathers/example.json"])
            self.assertEqual([path.as_posix() for path in declared], ["lifecycle/feathers/example.json"])
        with self.assertRaises(PolicyError):
            validate_declared_path_set(["lifecycle/feathers/example.json"])


if __name__ == "__main__":
    unittest.main()
