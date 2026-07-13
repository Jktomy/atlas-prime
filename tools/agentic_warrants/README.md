# Agentic warrant validator

`validate_warrant` enforces the closed warrant schema plus the 24-hour maximum
lifetime, closed route/action mapping, protected-path policy, trusted activation
record, and cascading parent/child subset rules. The caller must supply a
verifier backed by trusted authorizer readback; fixture strings or agent claims
do not create authority.

`validate_receipt` binds an observed receipt to the exact request and canonical
warrant digests, identity, principal, base, route, actions, paths, evidence,
approvals, and rollback boundary. Its required replay guard must atomically
consume both the request digest and receipt/attempt/nonce tuple. The module is
read-only and grants no authority.
