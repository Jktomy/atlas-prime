from __future__ import annotations

import filecmp
import json
import tempfile
import unittest
from pathlib import Path

from tools.spear.cli import main, validate_output_root
from tools.spear.models import PolicyError
from .helpers import cli_args, fixture, init_repo, write_packet


def files_under(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*") if p.is_file())


class ReproducibilityAndOutputTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory(); self.tmp = Path(self.td.name); self.repo = self.tmp / "repo"; self.commit = init_repo(self.repo)
        self.packet = fixture("valid-create.json"); self.packet["base_commit"] = self.commit
        self.packet_path = self.tmp / "packet.json"; self.packet_sha = write_packet(self.packet_path, self.packet)

    def tearDown(self): self.td.cleanup()

    def test_cli_two_clean_runs_are_byte_identical(self) -> None:
        out_a = self.tmp / "out-a"; out_b = self.tmp / "out-b"
        self.assertEqual(main(cli_args(self.repo, self.packet_path, self.packet_sha, out_a)), 0)
        self.assertEqual(main(cli_args(self.repo, self.packet_path, self.packet_sha, out_b)), 0)
        rels_a = [p.relative_to(out_a).as_posix() for p in files_under(out_a)]
        rels_b = [p.relative_to(out_b).as_posix() for p in files_under(out_b)]
        self.assertEqual(rels_a, rels_b)
        for rel in rels_a: self.assertTrue(filecmp.cmp(out_a / rel, out_b / rel, shallow=False), rel)

    def test_output_root_must_not_be_inside_repo_or_nonempty(self) -> None:
        with self.assertRaises(PolicyError): validate_output_root(str(self.repo), [self.repo])
        with self.assertRaises(PolicyError): validate_output_root(str(self.repo / "nested"), [self.repo])
        out = self.tmp / "nonempty"; out.mkdir(); (out / "x.txt").write_text("x", encoding="utf-8")
        with self.assertRaises(PolicyError): validate_output_root(str(out), [self.repo])

    def test_output_root_symlink_into_repo_fails_when_supported(self) -> None:
        link = self.tmp / "link-out"
        try:
            link.symlink_to(self.repo, target_is_directory=True)
        except OSError:
            self.skipTest("symlink creation unavailable")
        with self.assertRaises(PolicyError): validate_output_root(str(link / "child"), [self.repo])

    def test_output_root_protects_atlas_codex_reference_root(self) -> None:
        src = self.tmp / "src"; init_repo(src)
        with self.assertRaises(PolicyError): validate_output_root(str(src / "x"), [self.repo, src])


if __name__ == "__main__": unittest.main()