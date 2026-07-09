"""Pilot-disabled Atlas Thread Engine fixture implementation."""

from importlib import import_module

__all__ = ["ENGINE_STATE", "MODE", "VERSION", "execute_weave", "tree_hash"]


def __getattr__(name: str) -> object:
    if name not in __all__:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = import_module(".thread_engine", __name__)
    value = getattr(module, name)
    globals()[name] = value
    return value
