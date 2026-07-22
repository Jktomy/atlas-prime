from __future__ import annotations
import json, unittest
from pathlib import Path
from tools.athena_routes.schema import validate_schema

ROOT = Path(__file__).resolve().parents[2]

class NotumGlassCodexHealthTests(unittest.TestCase):
    def setUp(self):
        self.schema = json.loads((ROOT / 'schemas/notum-glass-codex-health-v1.schema.json').read_text(encoding='utf-8'))
        self.record = json.loads((ROOT / 'governance/notum-glass-codex-health-v1.json').read_text(encoding='utf-8'))
        self.contract = (ROOT / 'governance/notum-glass-codex-health-contract.md').read_text(encoding='utf-8')

    def test_record_validates_and_states_are_explicit(self):
        validate_schema(self.schema, self.record)
        self.assertEqual(set(self.record['states']), {'CURRENT', 'STALE', 'OFFLINE', 'UNKNOWN', 'LAST_KNOWN_GOOD'})
        self.assertIn('EXPIRED_IS_STALE', self.record['freshness_rules'])
        self.assertIn('LAST_KNOWN_GOOD_IS_CONTEXT_ONLY', self.record['freshness_rules'])

    def test_presentation_has_no_control_or_protected_data(self):
        self.assertEqual(self.record['access'], 'READ_ONLY_MINIMIZED_PROJECTION')
        self.assertTrue({'POWER', 'RESTART', 'NETWORK_CHANGE', 'RESTORE', 'FAILOVER', 'DEPLOYMENT', 'DELETION', 'AUTOMATED_RECOVERY'} <= set(self.record['denied_actions']))
        self.assertTrue({'CREDENTIALS', 'PRIVATE_NETWORK_MAPS', 'UNRESTRICTED_LOGS', 'RAW_TOPOLOGY', 'CONTROL_ENDPOINTS'} <= set(self.record['excluded_data']))

    def test_monitoring_and_recovery_remain_independent(self):
        independent = set(self.record['failure_independence'])
        self.assertIn('MONITORING_COLLECTION_CONTINUES', independent)
        self.assertIn('NOTUM_FAILURE_DOES_NOT_BLOCK_CLOUD_ATLAS', independent)
        self.assertIn('NOTUM_FAILURE_DOES_NOT_BLOCK_PRIME_RECOVERY', independent)
        self.assertIn('NW-C01', self.contract)

if __name__ == '__main__': unittest.main()
