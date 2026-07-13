# RP-C01 M07 live rejection reconciliation R01

RP-C01-M07 remains `PARTIAL` and AJ-03 remains `UNPROVEN`. Four previously
missing live no-mutation cases are now proven. A genuine non-owner trial remains
the exact smallest missing action.

## Controlled fixture

Fresh mission `RP-C01-M07-LIVE-REJECTIONS-R02` bound immutable carrier
`68f89707f31ebd95fd35940b343babb646d430d6522d4582dabee8add89d2674`
and canonical main `50e8646e0267e20ec31e2d970216039ffb3844ae` to deterministic branch
`source/athena-bow-a7cf70c90d9269cedd18`. Hosted run `29234164212` passed
read-only preflight job `86764887097` and singular Thread Engine job
`86764919716`; its route receipt hashes to
`3d9e589855e656a93f5d92b712c65f5042858d444a3601ee7b5236d902fecc7d`.
The route created draft fixture PR `#156` at exact head
`ede455ca734b1e4fc0f6ff1268a3ebb54f980326` with one ordinary authored path.

The fixture was setup, not acceptance. It was never made ready or merged. After
the branch-present replay, PR `#156` was closed and its branch deleted. Main
remained unchanged and the fixture path never entered canonical source.

## Accepted no-mutation rejections

- Edited input: run `29234357420` submitted one altered carrier byte while
  retaining the exact original claimed digest and correct R02 mission lock.
  Preflight job `86765500916` produced `CARRIER_SHA_REJECTED`; invoke job
  `86765530638` was skipped. Receipt
  `5ab457745773ba3209a6bafa07d87a26fe870a7eddd8e43dac1c18fd8c98dae8`
  records the observed altered digest, `PRE_MUTATION_REJECTION`, and no
  mutation.
- Intentional replay with the fixture branch and draft PR present: run
  `29234223758` produced `REPLAY_BRANCH_EXISTS`; invoke job `86765105402`
  was skipped. The existing head and PR were unchanged and no second PR was
  created. Receipt
  `5643cec504467bd934abb310274899483980907ce9b0643b8df04ed0ac2336dd`
  proves replay plus duplicate-branch rejection without mutation.
- Intentional replay after PR closure and branch deletion: run `29234280578`
  produced `REPLAY_PULL_REQUEST_EXISTS`; invoke job `86765307833` was
  skipped. The branch remained absent and historical PR `#156` remained closed
  and unmerged. Receipt
  `f6801c35b5aab6fcb4143359f385f97f9d8b5caa720cfbb5273e8f08bce345da`
  proves replay plus duplicate-PR rejection without mutation.

The negative workflows correctly conclude failure because the route CLI exits
nonzero on rejection. In each case the evidence upload succeeded, compiler and
adapter receipt hashes are null, all forbidden actions are false, and rollback
is `NO_MUTATION_REQUIRED`.

## Boundary

`NON_OWNER` remains missing. An owner-authenticated session cannot honestly
simulate that condition; a genuine non-owner with legitimate dispatch
permission must produce a live `OWNER_IDENTITY_REJECTED` receipt. Therefore
M07 and AJ-03 cannot be promoted.

This proof does not promote CAP-015, CAP-027, RP-C01, Repairing Prime, the
Quest, permanence, or standing authority.
