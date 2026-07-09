# Gate 7B Test Contract

These tests verify the disabled fixture-only source candidate. Passing Gate 7B tests does not prove Windows/Linux parity, GitHub proof, linked partial-state recovery, positive DELETE execution, merge eligibility, production adapter readiness, or activation authority.

Default tests execute ADD and REPLACE only. DELETE is validated as a separately gated contract and must fail without matching runtime authority.

The real-filesystem symlink integration test may report `SKIP_PLATFORM_CAPABILITY` only when the operating system denies symlink creation. The platform-independent symlink classification test is mandatory and must pass.
