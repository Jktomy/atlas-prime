from __future__ import annotations
import json, unittest
from pathlib import Path
from tools.athena_routes.schema import validate_schema

ROOT = Path(__file__).resolve().parents[2]

class ApolloRemoteOperatorContinuityTests(unittest.TestCase):
    def setUp(self):
        self.schema = json.loads((ROOT / 'schemas/apollo-remote-operator-continuity-v1.schema.json').read_text(encoding='utf-8'))
        self.record = json.loads((ROOT / 'governance/apollo-remote-operator-continuity-v1.json').read_text(encoding='utf-8'))
        self.contract = (ROOT / 'governance/apollo-remote-operator-continuity-contract.md').read_text(encoding='utf-8')

    def test_record_validates_and_roles_are_independent(self):
        validate_schema(self.schema, self.record)
        self.assertEqual(self.record['independent_operator'], 'HERMES_PORTABLE_ADMIN_AND_PRIME_RECOVERY')
        self.assertEqual(set(self.record['nonblocking_clients']), {'IRIS', 'ZEUS'})
        self.assertIn('NO_MICROSOFT_REMOTE_TUNNELS_DEPENDENCY', self.record['remote_route'])

    def test_environments_and_source_state_are_isolated(self):
        self.assertEqual(set(self.record['environment_isolation']), {'PRIVATE', 'ENGINEERING', 'WORLDHOPPER'})
        self.assertTrue({'CREDENTIALS', 'WORKSPACES', 'PROCESSES', 'EXTENSION_STORAGE', 'CACHES', 'CLEANUP', 'REVOCATION'} <= set(self.record['isolation_dimensions']))
        self.assertTrue({'PROTECTED_ORIGINAL', 'MISSION_STATE', 'COPPERMIND_STATE', 'CREDENTIAL', 'CANONICAL_REPOSITORY', 'UNPUSHED_COMMIT'} <= set(self.record['prohibited_unique_state']))

    def test_recovery_degraded_and_runtime_gates_remain_truthful(self):
        self.assertIn('VERIFIED_VERSIONED_GLASS_INSTALLER', self.record['recovery_assets'])
        self.assertIn('PRIME_CLEAN_CLONE_RECOVERY_CONTINUES', self.record['degraded_behavior'])
        self.assertEqual(self.record['runtime_state'], 'PENDING_PROTECTED_EXECUTE')
        self.assertEqual(self.record['pf_c01_m02_state'], 'READY_FOR_PREVIEW_NOT_PROVEN')
        self.assertIn('no runtime acceptance is claimed', self.contract)

if __name__ == '__main__': unittest.main()
