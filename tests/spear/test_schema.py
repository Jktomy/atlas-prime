from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from tools.spear.models import DuplicateKeyError, SpearError
from tools.spear.validate import load_json_file, parse_json_bytes, validate_schema
from .helpers import FIXTURES, SCHEMA


def fixture(name: str) -> dict:
    return load_json_file(str(FIXTURES / name))


class SchemaTests(unittest.TestCase):
    def assert_schema_fails(self, packet: dict) -> None:
        with self.assertRaises(SpearError):
            validate_schema(packet, load_json_file(str(SCHEMA)))

    def test_valid_create_update_and_multi_packets_validate(self) -> None:
        schema = load_json_file(str(SCHEMA))
        for name in ["valid-create.json", "valid-update.json", "valid-multi.json"]:
            validate_schema(fixture(name), schema)

    def test_malformed_json_duplicate_keys_and_invalid_utf8_fail(self) -> None:
        with self.assertRaises(SpearError): parse_json_bytes(b'{"packet_version":', max_bytes=1000)
        with self.assertRaises(DuplicateKeyError): parse_json_bytes(b'{"a":1,"a":2}', max_bytes=1000)
        with self.assertRaises(SpearError): parse_json_bytes(b'\xff', max_bytes=1000)

    def test_wrong_version_unknown_missing_invalid_id_fail(self) -> None:
        p = fixture("valid-create.json"); p["packet_version"] = "2.0"; self.assert_schema_fails(p)
        p = fixture("valid-create.json"); p["branch_name"] = "evil"; self.assert_schema_fails(p)
        p = fixture("valid-create.json"); del p["authority"]; self.assert_schema_fails(p)
        self.assert_schema_fails(fixture("invalid/invalid-packet-id.json"))

    def test_invalid_sha_unsupported_action_and_excessive_counts_fail(self) -> None:
        p = fixture("valid-update.json"); p["operations"][0]["expected_blob_sha"] = "abc"; self.assert_schema_fails(p)
        p = fixture("valid-create.json"); p["operations"][0]["content_sha256"] = "abc"; self.assert_schema_fails(p)
        p = fixture("valid-create.json"); p["operations"][0]["action"] = "DELETE"; self.assert_schema_fails(p)
        p = fixture("valid-create.json"); p["operations"] = [copy.deepcopy(p["operations"][0]) for _ in range(6)]
        for i, op in enumerate(p["operations"]): op["path"] = f"projects/spear/file-{i}.md"
        self.assert_schema_fails(p)

    def test_excessive_file_and_packet_size_fail(self) -> None:
        p = fixture("valid-create.json"); p["operations"][0]["content_utf8"] = "x" * 17000; p["operations"][0]["content_sha256"] = "0" * 64
        self.assert_schema_fails(p)
        payload = json.dumps({"x": "y" * (49 * 1024)}).encode("utf-8")
        with self.assertRaises(SpearError): parse_json_bytes(payload, max_bytes=48 * 1024)


if __name__ == "__main__":
    unittest.main()