# Benchmark Roadmap

## Short-Term Goal

Launch the benchmark at:

- `150` total scenarios
- `100` public
- `50` holdout

Current local draft status has reached that launch-size target:

- `150` total scenarios
- `100` public
- `50` holdout
- `10` families with near-balanced coverage

Known frozen draft imbalance:

- `consensus_promotion`: `9` public / `6` holdout
- `neutral_minimal`: `11` public / `4` holdout

These scenarios remain draft-local pending the final publication decision.

This is the minimum credible launch size for stable public metrics across:

- `mvi_composite`
- `validity_precision`
- `validity_recall`
- `noise_load`
- `staleness_penalty`
- `budget_efficiency`

## Medium-Term Goal

After the harness is battle-tested:

- expand to `500+` scenarios

This larger set should improve:

- family coverage
- statistical reliability
- holdout strength
- resistance to benchmark-specific overfitting

## Immediate Implementation Steps

1. Freeze `v1` scenario, run, and bundle schemas.
2. Freeze `v1` scoring, baseline disclosure, and reporting rules.
3. Build and freeze the first official public and holdout pack manifests.
4. Implement the reference harness for deterministic retrieval, orchestration replay, and execution-based tracks.
5. Add a one-shot contract verifier for scenarios, manifests, and scoring metadata.
6. Publish baseline runs from multiple systems, not only one memory implementation.

## Recognition Path

The benchmark becomes externally credible only after:

- reproducible public runs
- stable scoring versions
- external baseline submissions
- audited holdout governance
- visible use outside the originating project
