from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_FILES = [
    ROOT / "engine" / "thread_engine.py",
    ROOT / "Invoke-AtlasThreadEngine.ps1",
    ROOT / "tools" / "build_package.py",
]

DANGEROUS_PYTHON = [
    "eval",
    "exec",
    "compile",
    "__import__",
]

DANGEROUS_TEXT = [
    r"\bsubprocess\b",
    r"\bos\.system\b",
    r"Invoke-Expression",
    r"Read-Host",
    r"Start-Process",
    r"\brequests\b",
    r"\burllib\b",
    r"\bhttp\.client\b",
    r"\bsocket\b",
]

RUNTIME_BYPRODUCTS = {"__pycache__", ".pytest_cache"}
RUNTIME_SUFFIXES = {".pyc", ".pyo"}


def check_python_ast() -> None:
    for path in [ROOT / "engine" / "thread_engine.py", ROOT / "tools" / "build_package.py", Path(__file__)]:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def check_runtime_text() -> None:
    for path in RUNTIME_FILES:
        text = path.read_text(encoding="utf-8")
        for pattern in DANGEROUS_TEXT:
            if re.search(pattern, text):
                raise AssertionError(f"forbidden runtime token {pattern!r} in {path}")


def check_python_dynamic_execution() -> None:
    for path in [ROOT / "engine" / "thread_engine.py", ROOT / "tools" / "build_package.py"]:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in DANGEROUS_PYTHON:
                raise AssertionError(f"forbidden dynamic execution {node.func.id} in {path}")


def check_runtime_byproducts() -> None:
    for path in ROOT.rglob("*"):
        if path.name in RUNTIME_BYPRODUCTS or path.suffix in RUNTIME_SUFFIXES:
            raise AssertionError(f"runtime byproduct present: {path}")


def main() -> int:
    check_python_ast()
    check_runtime_text()
    check_python_dynamic_execution()
    check_runtime_byproducts()
    print("static checks PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
