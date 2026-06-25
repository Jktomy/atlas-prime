from __future__ import annotations

import unittest

from tools.spear.models import PolicyError, SpearError
from tools.spear.policy import IMPLEMENTED_SCANNER_CATEGORIES, effective_limits, load_controlling_policies, validate_content, validate_path_policy, validate_scanner_category_coverage
from tools.spear.validate import assert_no_path_collisions, load_json_file, load_json_policy, normalize_spear_path, validate_schema
from .helpers import POLICY, ROOT, SCHEMA, fixture, init_repo


class PolicyTests(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.td = tempfile.TemporaryDirectory()
        from pathlib import Path
        self.repo = Path(self.td.name) / "repo"
        self.commit = init_repo(self.repo)
        self.schema = load_json_file(str(SCHEMA))
        self.overlay = load_json_policy(str(POLICY))
        self.controlling = load_controlling_policies(str(self.repo), self.commit)
        self.limits = effective_limits(self.schema, self.overlay, self.controlling)

    def tearDown(self):
        self.td.cleanup()

    def test_path_rules_and_collisions_fail(self) -> None:
        for path in ["/abs.md", "C:/abs.md", "projects\\spear\\x.md", "projects/spear/../x.md", "projects/./x.md", "projects//x.md", "projects/spear/bad. ", "projects/spear/bad."]:
            with self.assertRaises(SpearError, msg=path): normalize_spear_path(path, max_path_bytes=500)
        with self.assertRaises(SpearError): assert_no_path_collisions(["projects/spear/A.md", "projects/spear/a.md"], max_path_bytes=500)
        with self.assertRaises(SpearError): assert_no_path_collisions(["projects/spear/Ã©.md", "projects/spear/e\u0301.md"], max_path_bytes=500)

    def test_official_denials_override_overlay(self) -> None:
        for path in [".github/workflows/x.yml", "schemas/spear/x.json", "policies/operations/spear/x.yaml", "tools/spear/x.py", "tests/spear/x.py", "generated/index.md", "migration/x.json", "codex/governance/x.md", "codex/quests/x.json", "codex/golden-wing/x.json", "README.md", "phoenix-reborn.md"]:
            with self.assertRaises(PolicyError, msg=path): validate_path_policy(path, self.overlay, self.controlling, self.limits)
        permissive = dict(self.overlay); permissive["ordinary_packet_allowed_prefixes"] = ["tools/"]
        with self.assertRaises(PolicyError): validate_path_policy("tools/spear/x.py", permissive, self.controlling, self.limits)

    def test_operator_policy_path_uses_prime_protected_operations_prefix(self) -> None:
        expected_policy_path = "/".join(["policies", "operations", "spear", "spear-policy-v1.yaml"])
        retired_policy_prefix = "/".join(["policies", "spear", ""])
        protected = next(item for item in self.controlling["protected_sets"] if item["id"] == "spear-self-protection")
        prefixes = protected["match"]["prefixes"]
        self.assertIn("/".join(["policies", "operations", "spear"]), prefixes)
        self.assertNotIn(retired_policy_prefix, prefixes)
        self.assertEqual(POLICY.relative_to(ROOT).as_posix(), expected_policy_path)
        self.assertTrue(POLICY.exists())

    def test_unknown_path_class_and_bad_extension_fail(self) -> None:
        with self.assertRaises(PolicyError): validate_path_policy("random/place.md", self.overlay, self.controlling, self.limits)
        with self.assertRaises(PolicyError): validate_path_policy("projects/spear/image.png", self.overlay, self.controlling, self.limits)

    def test_content_scanner_redacts_values_and_category_coverage(self) -> None:
        validate_scanner_category_coverage(self.overlay)
        self.assertTrue(set(self.overlay["protected_warning_categories"]).issubset(IMPLEMENTED_SCANNER_CATEGORIES))
        token_probe = "TOKEN=" + "abcd" + "1234" + "synthetic" + "\n"
        private_key_probe = "-----BEGIN " + "PRIVATE KEY-----" + "\nabc\n"
        private_ip_probe = "Internal host " + ".".join(["192", "168", "1", "10"]) + "\n"
        probes = [
            token_probe,
            private_key_probe,
            private_ip_probe,
            "account number " + "1234" + "56789\n",
            "MRN patient id " + "ABCD" + "-" + "1234\n",
            "version https://git-lfs.github.com/spec/v1\n",
            "bad" + "\x00" + "nul\n",
        ]
        for content in probes:
            with self.assertRaises(PolicyError) as ctx:
                validate_content("projects/spear/x.md", content, self.limits)
            self.assertNotIn(token_probe.strip().split("=", 1)[1], str(ctx.exception))
            self.assertNotIn(private_ip_probe.strip().rsplit(" ", 1)[1], str(ctx.exception))

    def test_policy_drift_fails(self) -> None:
        bad = dict(self.overlay); bad["limits"] = dict(bad["limits"]); bad["limits"]["max_operations"] = 4
        with self.assertRaises(PolicyError): effective_limits(self.schema, bad, self.controlling)
        bad = dict(self.overlay); bad["protected_warning_categories"] = list(bad["protected_warning_categories"]) + ["unimplemented"]
        with self.assertRaises(PolicyError): validate_scanner_category_coverage(bad)

    def test_policy_identity_from_git_objects(self) -> None:
        self.assertEqual(self.controlling["destination_identity"].policy_id, "atlas-prime-destination-policy")
        self.assertEqual(self.controlling["protected_identity"].policy_id, "atlas-prime-protected-paths")
        self.assertEqual(len(self.controlling["destination_identity"].git_blob_sha), 40)
        self.assertEqual(len(self.controlling["destination_identity"].sha256), 64)


if __name__ == "__main__":
    unittest.main()
