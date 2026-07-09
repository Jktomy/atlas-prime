from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .compiler import SpearBridgeError, compile_package


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile a disabled Spear package into a Thread Engine mission.")
    parser.add_argument("--package", required=True)
    parser.add_argument("--package-sha256", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--read-only-remote-url")
    parser.add_argument("--spear-bridge-disabled-proof", action="store_true")
    parser.add_argument("--compile-only", action="store_true")
    args = parser.parse_args(argv)
    try:
        receipt = compile_package(
            Path(args.package),
            package_sha256=args.package_sha256,
            output_dir=Path(args.output_dir),
            disabled_proof=args.spear_bridge_disabled_proof,
            compile_only=args.compile_only,
            read_only_remote_url=args.read_only_remote_url,
        )
    except SpearBridgeError as exc:
        print(json.dumps({"result": "REJECTED", "error_code": exc.code, "error_stage": exc.stage, "message": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
