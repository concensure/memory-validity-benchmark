# Public Demo Pack Policy

`MVI` should stay objective: the benchmark core measures memory validity, ordering, staleness, and budget behavior through the published scenario and run contracts. It should not be reshaped around any one system's internal storage model, tracing model, or explanation format.

The `public_demo_100_manifest.json` pack exists for a different purpose:

- provide a bounded public run set that is large enough to be credible
- span retrieval, injection, long-horizon, and multi-agent failure modes
- let stronger systems demonstrate capability breadth without changing the primary score contract

## Selection Rules

The demo pack should follow these rules:

- keep the existing `mvi-scenario-v1` scenario shape and scorer semantics unchanged
- select only from the public split
- preserve broad family coverage before deepening any one family
- add extra slots only for capability classes that matter to many systems, not one implementation
- avoid any scenario that depends on implementation-private metadata

`public-demo-100-balanced-v1` therefore uses:

- `4` public scenarios from every active public family
- `1` additional scenario for `retrieval_deduplication`
- `1` additional scenario for `long_horizon_accumulation`
- `1` additional scenario for `multi_agent_belief_propagation`
- `1` additional scenario for `token_pressure_scale`

Those four families get the extra depth because they stress general benchmark objectives that advanced systems often handle differently:

- near-duplicate suppression under retrieval pressure
- truth maintenance across time
- correction propagation across agents
- budget resilience under compression

This framing keeps the benchmark neutral while still making capability differences visible.

## Optional Audit Artifacts

Supplemental artifacts may be published with benchmark runs, but they must not affect the primary score. Useful optional artifacts include:

- deduplication trace: which near-duplicate memories were collapsed and why
- invalidation trace: which stale or superseded memories caused downstream review flags
- change delta report: what facts changed between checkpoints or resumes
- budget rationale: which contradiction or counter-signal was retained under tight budget

These artifacts help demonstrate explainability and operational maturity without prejudicing the core benchmark toward any one product shape.
