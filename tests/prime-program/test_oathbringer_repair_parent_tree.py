from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from oathbringer_test_support import FakeGitHubClient, base_mission, og


class OathbringerRepairParentTreeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.payload = self.root / "payload/oathbringer-harmless.txt"
        self.payload.parent.mkdir(parents=True)
        self.payload.write_text("Oathbringer harmless proof.\n", encoding="utf-8", newline="\n")
        self.lessons = self.root / "source/methods/sword-lessons.json"
        self.lessons.parent.mkdir(parents=True)
        self.lessons.write_text('{"schema_version":"prime-sword-lessons-v1"}\n', encoding="utf-8", newline="\n")
        self.client = FakeGitHubClient()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _mission(self) -> dict:
        return base_mission(
            hashlib.sha256(self.payload.read_bytes()).hexdigest(),
            hashlib.sha256(self.lessons.read_bytes()).hexdigest(),
        )

    def _seal(self, mission: dict) -> None:
        mission_path = self.root / "mission.json"
        mission_path.write_text(
            json.dumps(mission, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        members = [
            "mission.json",
            "payload/oathbringer-harmless.txt",
            "source/methods/sword-lessons.json",
        ]
        files = []
        for relative in members:
            member = self.root / relative
            files.append(
                {
                    "path": relative,
                    "sha256": hashlib.sha256(member.read_bytes()).hexdigest(),
                    "size": member.stat().st_size,
                }
            )
        (self.root / "MANIFEST.json").write_text(
            json.dumps({"files": files}, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    def _run(self, mission: dict):
        self._seal(mission)
        return og.execute_mission(
            mission,
            self.root,
            self.client,
            mission_relative_path="mission.json",
            json_mode=True,
        )

    def _build_then_repair_mission(self) -> tuple[dict, dict]:
        build, _ = self._run(self._mission())
        path = "proof/oathbringer-harmless.txt"
        prior_blob = build["payload_blobs"][path]
        self.payload.write_text("Oathbringer repaired proof.\n", encoding="utf-8", newline="\n")
        repair = self._mission()
        repair.update(
            {
                "lane": "REPAIR",
                "expected_head": build["commit_sha"],
                "pull_request": 1,
                "commit_message": "Proof: repair harmless Oathbringer fixture",
            }
        )
        repair.pop("pull_request_contract")
        repair["declared_paths"][0].update(
            {
                "operation": "REPLACE",
                "source_blob": prior_blob,
            }
        )
        return build, repair

    def test_repair_replaces_path_added_by_build_using_current_pr_head(self) -> None:
        build, repair = self._build_then_repair_mission()
        result, _ = self._run(repair)
        path = "proof/oathbringer-harmless.txt"
        self.assertEqual(result["status"], "OATHBRINGER_REPAIR_PASS")
        self.assertEqual(self.client.commits[result["commit_sha"]]["parent"], build["commit_sha"])
        self.assertEqual(self.client.refs[repair["branch"]], result["commit_sha"])
        self.assertEqual(result["changed_paths"], [path])
        self.assertNotEqual(result["payload_blobs"][path], repair["declared_paths"][0]["source_blob"])
        self.assertTrue(self.client.pull_requests[1]["draft"])

    def test_repair_rejects_stale_source_blob_against_current_pr_head(self) -> None:
        _build, repair = self._build_then_repair_mission()
        repair["declared_paths"][0]["source_blob"] = "f" * 40
        with self.assertRaisesRegex(og.OathbringerError, "source blob drift"):
            self._run(repair)


if __name__ == "__main__":
    unittest.main()
