from __future__ import annotations
import json, unittest
from pathlib import Path
from tools.athena_routes.schema import validate_schema
ROOT = Path(__file__).resolve().parents[2]

class GlassCodexClientTests(unittest.TestCase):
    def setUp(self):
        self.schema=json.loads((ROOT/'schemas/glass-codex-client-v1.schema.json').read_text(encoding='utf-8'))
        self.record=json.loads((ROOT/'governance/glass-codex-client-v1.json').read_text(encoding='utf-8'))
        self.contract=(ROOT/'governance/glass-codex-client-contract.md').read_text(encoding='utf-8')
    def test_record_validates_and_surfaces_are_complete(self):
        validate_schema(self.schema,self.record)
        self.assertEqual(len(self.record['surfaces']),11)
        self.assertEqual(len(self.record['access_lanes']),2)
        self.assertEqual(self.record['deployment_state'],'ARCHITECTURE_ONLY_NOT_IMPLEMENTED')
    def test_client_has_no_backend_or_protected_authority(self):
        denied=set(self.record['denied_authorities'])
        self.assertTrue({'NO_UNRESTRICTED_SQL','NO_DIRECT_VAULT_MOUNT','NO_INFRASTRUCTURE_AUTHORITY','NO_RECOVERY_AUTHORITY','NO_PERMANENCE_AUTHORITY','NO_DIRECT_CANONICAL_WRITE'} <= denied)
        self.assertIn('NO_PROTECTED_ORDINARY_LOGS',self.record['retention'])
        self.assertIn('NO_PROFILE_NAME_SECURITY_ASSUMPTION',denied)
    def test_failure_and_packaging_are_independent(self):
        self.assertIn('APOLLO_FAILURE_REMOVES_GUI_ONLY',self.record['failure_independence'])
        self.assertIn('AUTHORITATIVE_STATE_NOT_TRAPPED_IN_EXTENSION',self.record['failure_independence'])
        self.assertIn('ROLLBACK_PACKAGE',self.record['packaging'])
        self.assertIn('FUTURE_THEIA_OR_STANDALONE_COMPONENT_ROUTE',self.record['packaging'])
        self.assertIn('Notum\'s Watch\nand Sentinel retain monitoring authority',self.contract)
if __name__=='__main__': unittest.main()
