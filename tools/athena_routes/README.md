# Athena Routes

This module is a thin intake and invocation boundary. It accepts one locally
pre-screened, public-clean, immutable Arrow carrier from the owner-only hosted
workflow, binds trusted GitHub run identity, rejects replay and protected paths,
invokes the existing Spear compiler, and passes the compiler output unchanged to
the singular Prime Thread Engine production adapter.

It contains no git tree, commit, push, or pull-request implementation. It has no
direct-main, force-push, ready, merge, settings, cleanup, workflow-dispatch,
standing credential, or second-writer authority. Thread Engine self-change is
handed to Aegis Break → Oathbringer before mutation.

The hosted result stops at draft-PR readback. A `PARTIAL` Thread Engine result is
preserved exactly and blocks retry. Generated projections and protected paths
are not accepted by this ordinary hosted route.

## Ordinary free-form intake

`python -B -m tools.athena_routes.free_form_intake --fields <fields.json>
--output-dir <new-directory>` accepts a closed local public-clean mission-fields
object and atomically creates one new output directory outside the canonical
repository. That directory contains `carrier.zip`, `preview.json`,
`intake-receipt.json`, and retained `compiled/` mission, compiler receipt, and
payload files.

The constructor binds an exact expected main SHA and fresh mission/carrier
nonce, normalizes text to UTF-8/LF, sorts ordinary `ADD`/`REPLACE` changes,
builds fixed-metadata deterministic carrier bytes, performs the existing
read-only guided Preview, and requires a second retained compiler result to
match Preview exactly. It screens content locally and prints only bounded
identity hashes. Existing or in-repository output paths, stale main, replay,
privacy matches, unsafe or colliding paths, protected/generated/self-change
paths, compiler rejection, or retained-output drift fail without publishing a
partial output directory.

The constructor has no workflow dispatch or remote write authority. Its receipt
explicitly classifies the origin as owner-guided local—not fresh Work/Athena
origin—and requires exact Preview confirmation through the existing Execute
command. Construction and tests cannot promote M08, CAP-015, AJ-01, RP-C01,
permanence, or standing authority; live hosted acceptance and a separate
authored reconciliation remain mandatory.

## Owner-guided publisher

`python -B -m tools.athena_routes.guided_publisher preview` audits one immutable
carrier against exact canonical `main`, the hosted workflow blob, privacy and
ordinary-path policy, and the existing compile-only Spear compiler. It writes a
closed sanitized Preview receipt and performs no adapter, branch, commit, PR,
workflow, ready, merge, settings, or direct-main action.

`python -B -m tools.athena_routes.guided_publisher execute` requires the exact
Preview SHA-256, re-runs the full Preview, requires an owner GitHub session and
a fresh public-clean launch nonce plus the exact explicit
`PUBLIC_CLEAN_CONFIRMED` value, and dispatches only
`.github/workflows/athena-bow-hosted.yml`. The carrier and its Base64 encoding
travel to `gh` only as JSON on standard input; they are never command-line
arguments or normal output. The publisher then reads back the new hosted run
identity and stops. The hosted workflow and singular Thread Engine retain all
write, replay, partial-state, receipt, and draft-PR boundaries.

If dispatch may have occurred but exact run readback fails, Execute writes a
`PARTIAL_STATE_PRESERVED` receipt and requires preserve-and-review with no
retry. Before dispatch it exclusively reserves the requested receipt path and
durably journals that no-retry state; exact readback then atomically replaces
the journal. The hosted workflow serializes every valid carrier sharing the
same decoded mission and base, and revalidates that deterministic lock before
the adapter is reachable. Preview also rejects a nondeterministic branch or any
current or historical branch/PR replay identity before Execute is available.

This guided component does not prove CAP-010 until a fresh live Preview and
Execute journey, hosted receipt, exact draft-PR readback, exact-head CI,
detached review, merge, and canonical readback are accepted separately. It does
not prove fresh Work/Athena origin or CAP-015.

## Fresh Work/Athena origin construction

`tools.athena_routes.fresh_work_bridge` is currently a read-only construction
boundary. It validates one canonical, short-lived, public-safe origin receipt,
re-hashes the exact carrier and Preview, and can compare them with a full-binding
platform readback supplied through a library seam.

It contains no import or call to the guided publisher, no workflow-dispatch
implementation, and no Git, branch, pull-request, adapter, ready, merge,
cleanup, settings, credential, or second-writer path. Even an untrusted test
callback can produce only `READ_ONLY_CANDIDATE_NOT_EXECUTABLE` with
`remote_dispatch_authority=false` and `guided_execute_invoked=false`.

The command-line entry point never accepts a verifier. It records only the
truthful `TRUSTED_ORIGIN_VERIFIER_UNAVAILABLE` blocked journey receipt with no
remote dispatch possibility. Caller-authored JSON, prompt text, screenshots,
transcripts, command arguments, environment strings, repository files, or
arbitrary callables cannot activate CAP-015.

A later protected transaction may wire an independently trusted platform
readback to the existing guided Execute route only after a real ChatGPT Work
trust anchor exists and Jayson approves that integration. That later transaction
must add durable no-retry intent and truthful partial-state conservation before
any dispatch is possible.

Construction, schemas, tests, and read-only plans do not prove CAP-015, AJ-01,
RP-C01-M02, or the RP-C01 gate. Acceptance still requires a genuinely fresh
Jayson-started Work/Athena task, one live hosted journey through the singular
Thread Engine, exact draft-PR and blob readback, exact-head Ubuntu and Windows
validation, detached review, and separate authored reconciliation.

## RP-C01-M05 parity join

Preview retains the exact Spear compile receipt and every compiled file digest,
including the canonical mission, candidate tree, and final pathset. Hosted
Thread Engine evidence separately identifies the raw adapter receipt and the
sanitized evidence wrapper. `build_m05_parity_evidence` in
`tools.athena_routes.m05_parity` accepts only an exact guided Preview, Execute
receipt, hosted receipt, sanitized adapter evidence, and the retained direct
compiled files from one run. It rejects
carrier, mission, compiler, tree, branch, PR, head, checkpoint, stop-boundary,
or forbidden-action drift and emits the closed schema
`schemas/rp-c01-m05-parity-evidence-v1.schema.json`.

The parity record is evidence only. It cannot execute, retry, merge, confer
permanence, promote a capability or Quest, or mark RP-C01-M05 proven; those
decisions require their separate authored reconciliation.
