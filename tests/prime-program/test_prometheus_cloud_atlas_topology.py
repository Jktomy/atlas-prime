from __future__ import annotations
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class PrometheusCloudAtlasTopologyTests(unittest.TestCase):
    def setUp(self):
        self.contract=(ROOT/'governance/prometheus-cloud-atlas-topology-contract.md').read_text(encoding='utf-8')
        self.quest=(ROOT/'quests/prometheus-fire.md').read_text(encoding='utf-8')
    def test_resource_envelope_is_conservative_and_household_first(self):
        for marker in ('Harmony 24 + Atlas 12 + Plex maximum 16','protected host reserve 8','flexible headroom 4','No ballooning or overcommit','Plex playback, DVR\nrecording, and persistent Forge services outrank'):
            self.assertIn(marker,self.contract)
    def test_services_retain_identity_and_recovery(self):
        for marker in ('Harmony VM','Atlas VM','Plex LXC','Proxmox host','Forge','Notum/Sentinel','Glass Codex on Apollo','Complete VM plus selective service restore','PostgreSQL base/WAL/PITR','independent mirror'):
            self.assertIn(marker,self.contract)
        self.assertIn('co-located Emberdark, Coppermind, Phoenix remain separate',self.contract)
    def test_no_runtime_or_gate_advances(self):
        for marker in ('does not claim measured deployment capacity','GitHub remains canonical','PF-C01-M02','future Glass Codex client with governed APIs'):
            self.assertIn(marker,self.contract+self.quest)
        for forbidden in ('deployment is complete','restore is proven','gitea is active'):
            self.assertNotIn(forbidden,(self.contract+self.quest).lower())
if __name__=='__main__': unittest.main()
