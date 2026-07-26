from __future__ import annotations

import io
import json
import unittest
import zipfile

from tools.athena_routes.spear_issue_client import (
    CHUNK,
    PREVIEW,
    SpearIssueClientError,
    bind_chunk_comment_ids,
    build_encrypted_comments,
    parse_comment,
    scan_public_clean_carrier,
)
from tools.athena_routes.spear_issue_crypto import decrypt, generate_keypair


def carrier(payload: bytes = b"public-clean fixture\n") -> bytes:
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("SPEAR-WEAVE.json", json.dumps({"fixture": True}))
        zf.writestr("PACKAGE-MANIFEST.json", json.dumps({"fixture": True}))
        zf.writestr("PAYLOADS/fixture.txt", payload)
    return out.getvalue()


class SpearIssueClientTests(unittest.TestCase):
    def test_crypto_round_trip_and_chunk_binding(self) -> None:
        private_b64, public_b64, key_id = generate_keypair()
        raw = carrier()
        result = build_encrypted_comments(
            raw,
            repository="Jktomy/atlas-prime",
            issue_number=346,
            mission_id="MISSION-TEST",
            attempt_id="MISSION-TEST-ATTEMPT-01",
            base_sha="a" * 40,
            request_id="request-000001",
            authorization_comment_id=99,
            authorization_comment_sha256="b" * 64,
            public_key_b64=public_b64,
            key_id=key_id,
            max_chunk_characters=64,
        )
        ids = list(range(100, 100 + len(result["chunks"])))
        rendered = bind_chunk_comment_ids(result["preview_template"], ids)
        marker, preview = parse_comment(rendered, PREVIEW)
        self.assertEqual(marker, PREVIEW)
        pieces = []
        for index, value in enumerate(result["chunks"]):
            chunk_marker, chunk = parse_comment(value, CHUNK)
            self.assertEqual(chunk_marker, CHUNK)
            self.assertEqual(chunk["index"], index)
            pieces.append(chunk["ciphertext_piece"])
        envelope = dict(preview["crypto"])
        envelope["ciphertext_b64"] = "".join(pieces)
        aad = {
            key: preview[key]
            for key in (
                "repository",
                "issue_number",
                "mission_id",
                "attempt_id",
                "base_sha",
                "request_id",
                "authorization_comment_id",
                "authorization_comment_sha256",
                "key_id",
                "carrier_sha256",
                "requesting_surface",
                "semantic_operator",
                "authorizer",
            )
        }
        self.assertEqual(decrypt(envelope, private_b64, expected_key_id=key_id, aad=aad), raw)

    def test_public_clean_scan_rejects_secret_and_traversal(self) -> None:
        with self.assertRaises(SpearIssueClientError):
            scan_public_clean_carrier(carrier(b"api_" + b'key="' + b"definitely-" + b'secret-value"'))
        out = io.BytesIO()
        with zipfile.ZipFile(out, "w") as zf:
            zf.writestr("../escape.txt", "no")
        with self.assertRaises(SpearIssueClientError):
            scan_public_clean_carrier(out.getvalue())

    def test_comment_json_rejects_duplicate_keys(self) -> None:
        with self.assertRaises(SpearIssueClientError):
            parse_comment(PREVIEW + '\n{"mode":"PREVIEW","mode":"EXECUTE"}', PREVIEW)

    def test_archive_expansion_is_bounded(self) -> None:
        out = io.BytesIO()
        with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("SPEAR-WEAVE.json", "{}")
            zf.writestr("PACKAGE-MANIFEST.json", "{}")
            zf.writestr("PAYLOADS/large.txt", b"A" * 1_100_000)
        self.assertLess(len(out.getvalue()), 524_288)
        with self.assertRaises(SpearIssueClientError):
            scan_public_clean_carrier(out.getvalue())


if __name__ == "__main__":
    unittest.main()
