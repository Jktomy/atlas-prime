from __future__ import annotations

import json
from pathlib import Path
import unittest
from unittest.mock import patch

from tools.athena_routes import spear_issue_client as issue_client
from tools.athena_routes import spear_issue_ingress as ingress


def manifest() -> dict:
    return {
        "mission_id": "MISSION-TEST",
        "attempt_id": "MISSION-TEST-ATTEMPT-01",
        "objective": "harmless fixture",
        "source_binding": {"base_sha": "a" * 40},
    }


def _carrier() -> bytes:
    import io
    import zipfile

    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("SPEAR-WEAVE.json", "{}")
        zf.writestr("PACKAGE-MANIFEST.json", "{}")
        zf.writestr("PAYLOADS/fixture.txt", "fixture\n")
    return out.getvalue()


class SpearIssueIngressTests(unittest.TestCase):
    def test_envelope_identity_is_exact(self) -> None:
        body = {
            "schema_version": "atlas.athena.spear-issue-envelope.v1",
            "mode": "KEY_REQUEST",
            "repository": "Jktomy/atlas-prime",
            "mission_id": "MISSION-TEST",
            "attempt_id": "MISSION-TEST-ATTEMPT-01",
            "base_sha": "a" * 40,
            "request_id": "request-000001",
            "requesting_surface": "CHATGPT_ATLAS_PROJECT",
            "semantic_operator": "ATHENA",
            "authorizer": "JAYSON",
        }
        ingress._validate_envelope(body, manifest(), 346, "KEY_REQUEST")
        body["semantic_operator"] = "OTHER"
        with self.assertRaises(ingress.SpearIssueIngressError) as caught:
            ingress._validate_envelope(body, manifest(), 346, "KEY_REQUEST")
        self.assertEqual(caught.exception.code, "ENVELOPE_IDENTITY_REJECTED")

    def test_receipt_base_denies_permanence(self) -> None:
        receipt = ingress._receipt_base("PREVIEW", "PREVIEW_ACCEPTED", 346, manifest(), "request-000001")
        self.assertIs(receipt["automatic_retry"], False)
        self.assertTrue(all(value is False for value in receipt["forbidden_actions"].values()))

    def test_envelope_rejects_unknown_properties(self) -> None:
        body = {
            "schema_version": "atlas.athena.spear-issue-envelope.v1",
            "mode": "KEY_REQUEST",
            "repository": "Jktomy/atlas-prime",
            "mission_id": "MISSION-TEST",
            "attempt_id": "MISSION-TEST-ATTEMPT-01",
            "base_sha": "a" * 40,
            "request_id": "request-000001",
            "requesting_surface": "CHATGPT_ATLAS_PROJECT",
            "semantic_operator": "ATHENA",
            "authorizer": "JAYSON",
            "unexpected": True,
        }
        with self.assertRaises(ingress.SpearIssueIngressError) as caught:
            ingress._validate_envelope(body, manifest(), 346, "KEY_REQUEST")
        self.assertEqual(caught.exception.code, "ENVELOPE_SCHEMA_REJECTED")

    def test_server_reconstructs_exact_owner_authored_ciphertext(self) -> None:
        from tools.athena_routes.spear_issue_client import (
            PREVIEW,
            bind_chunk_comment_ids,
            build_encrypted_comments,
            parse_comment,
        )
        from tools.athena_routes.spear_issue_crypto import generate_keypair, sha256_bytes

        private_b64, public_b64, key_id = generate_keypair()
        authorization = "Jayson authorizes exact harmless fixture"
        result = build_encrypted_comments(
            _carrier(),
            repository="Jktomy/atlas-prime",
            issue_number=346,
            mission_id="MISSION-TEST",
            attempt_id="MISSION-TEST-ATTEMPT-01",
            base_sha="a" * 40,
            request_id="request-000001",
            authorization_comment_id=99,
            authorization_comment_sha256=sha256_bytes(authorization.encode()),
            public_key_b64=public_b64,
            key_id=key_id,
            max_chunk_characters=64,
        )
        ids = list(range(100, 100 + len(result["chunks"])))
        _marker, preview = parse_comment(bind_chunk_comment_ids(result["preview_template"], ids), PREVIEW)
        comments = {
            99: {"id": 99, "body": authorization, "user": {"login": "Jktomy"}},
            **{
                comment_id: {
                    "id": comment_id,
                    "body": body,
                    "user": {"login": "Jktomy"},
                    "issue_url": "https://api.github.com/repos/Jktomy/atlas-prime/issues/346",
                }
                for comment_id, body in zip(ids, result["chunks"])
            },
        }
        with (
            patch.object(issue_client, "_comment", side_effect=lambda comment_id: comments[comment_id]),
            patch.object(issue_client, "_keys", return_value=(private_b64, public_b64, key_id)),
        ):
            ingress._authorization(preview)
            restored, _aad = ingress._reconstruct_preview(preview, 346)
        self.assertEqual(restored, _carrier())

    def test_server_rejects_non_owner_chunk(self) -> None:
        from tools.athena_routes.spear_issue_client import (
            PREVIEW,
            bind_chunk_comment_ids,
            build_encrypted_comments,
            parse_comment,
        )
        from tools.athena_routes.spear_issue_crypto import generate_keypair, sha256_bytes

        private_b64, public_b64, key_id = generate_keypair()
        authorization = "Jayson authorizes exact harmless fixture"
        result = build_encrypted_comments(
            _carrier(),
            repository="Jktomy/atlas-prime",
            issue_number=346,
            mission_id="MISSION-TEST",
            attempt_id="MISSION-TEST-ATTEMPT-01",
            base_sha="a" * 40,
            request_id="request-000002",
            authorization_comment_id=99,
            authorization_comment_sha256=sha256_bytes(authorization.encode()),
            public_key_b64=public_b64,
            key_id=key_id,
            max_chunk_characters=100000,
        )
        ids = [100]
        _marker, preview = parse_comment(bind_chunk_comment_ids(result["preview_template"], ids), PREVIEW)
        non_owner = {
            "id": 100,
            "body": result["chunks"][0],
            "user": {"login": "intruder"},
            "issue_url": "https://api.github.com/repos/Jktomy/atlas-prime/issues/346",
        }
        with (
            patch.object(issue_client, "_keys", return_value=(private_b64, public_b64, key_id)),
            patch.object(issue_client, "_comment", return_value=non_owner),
            self.assertRaises(ingress.SpearIssueIngressError) as caught,
        ):
            ingress._reconstruct_preview(preview, 346)
        self.assertEqual(caught.exception.code, "CHUNK_IDENTITY_REJECTED")


if __name__ == "__main__":
    unittest.main()
