# Agentic warrant validator

`validate_warrant` enforces the closed warrant schema plus lifecycle, expiry,
path, approval, and parent/child subset rules. `validate_receipt` binds an
observed receipt to the canonical warrant digest, identity, principal, base,
route, actions, and paths. The module is read-only and grants no authority.
