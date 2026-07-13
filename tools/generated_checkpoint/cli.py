from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import build_hash_register, compare_hash_registers, publish, stable_json


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prime generated checkpoint controls")
    commands = parser.add_subparsers(dest="command", required=True)
    parity = commands.add_parser("parity")
    parity.add_argument("--repo-root", type=Path, required=True)
    parity.add_argument("--output-dir", type=Path, required=True)
    compare = commands.add_parser("compare")
    compare.add_argument("--left", type=Path, required=True)
    compare.add_argument("--right", type=Path, required=True)
    publisher = commands.add_parser("publish")
    publisher.add_argument("--repo-root", type=Path, required=True)
    publisher.add_argument("--repository", required=True)
    publisher.add_argument("--base-sha", required=True)
    publisher.add_argument("--replay-nonce", required=True)
    publisher.add_argument("--run-id", required=True)
    publisher.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "parity":
        result = build_hash_register(args.repo_root, args.output_dir)
    elif args.command == "compare":
        left = json.loads(args.left.read_text(encoding="utf-8"))
        right = json.loads(args.right.read_text(encoding="utf-8"))
        compare_hash_registers(left, right)
        result = {"result": "PASS", "parity": "BYTE_IDENTICAL"}
    else:
        result = publish(args.repo_root, repository=args.repository, base_sha=args.base_sha, replay_nonce=args.replay_nonce, run_id=args.run_id, receipt_path=args.receipt)
    print(stable_json(result).decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
