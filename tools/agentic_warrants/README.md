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
read-only and grants no authority. Action approvals bind the same request
digest; rejection receipts for inactive or invalid warrants are accepted only
when their recorded error matches the validator's observed reason.

The generic v1 path is structural RP-C02 evidence only for permanence. It
rejects every v1 READY, MERGE, or `SHARDBLADE_PERMANENCE` warrant with
`SHARDBLADE_DEDICATED_CONTRACT_REQUIRED`. Current Shardblade validation uses
`permanence.py` and the dedicated request, direct approval, and receipt schemas.
That module is also read-only and `CONTRACT_ONLY_NOT_ACTIVATED`: callers must
supply trusted Jayson verification, fresh GitHub readbacks, and one durable
reservation ledger that binds each accepted receipt to its prior request and
approval reservation before any mutation.
