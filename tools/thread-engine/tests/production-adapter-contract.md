# Gate 7F Production Adapter Contract Tests

These tests cover the disabled-by-default source candidate only.

They verify mission-authority validation, duplicate-key rejection, exact path-set enforcement, protected-route denial, Aegis Break protected-route launch intent, `WORKBOARD_ROW_UPDATE_V1` launch intent, launch authority binding, authenticated GitHub operator readback, protected source-blob coverage, Workboard row identity and row-hash coverage, Thread Engine self-change exclusion, DELETE authority separation, positive DELETE behavior, draft-PR-only routing, deterministic rejection receipts, PowerShell parser preflight, exact Git/GitHub command templates, Windows long-path checkout, command-scoped LF checkout normalization under hostile `core.autocrlf=true`, readback mismatch rejection, recovery classification, and static denial of dynamic execution, shell evaluation, workflow mutation, ready transition, merge, force push, and repository-setting routes.

Aegis Break remains a narrow protected-route profile. It does not weaken ordinary protected-path rejection, does not authorize Thread Engine self-change, and does not create direct-main write, force-push, ready, merge, workflow-dispatch, cleanup, or standing authority.

`WORKBOARD_ROW_UPDATE_V1` is a separate narrow profile for routine updates to exactly one declared Active Workboard row. It requires exact Workboard source blob, row identity, allowed field list, before-row SHA-256, after-row SHA-256, operation-set SHA-256, explicit launcher intent, exact authority ID, one draft PR, and independent readback. It does not authorize Workboard front matter, schema, columns, vocabulary, Prime successor model, unrelated rows, row deletion, bulk rewrite, Thread Engine self-change, direct-main write, force-push, ready, merge, workflow dispatch, cleanup, branch deletion, or standing authority.

Passing these tests does not activate the adapter, prove isolated GitHub behavior, merge Gate 7F, or authorize Gate 7G.
