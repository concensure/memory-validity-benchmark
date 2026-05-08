# Scoring

The benchmark publishes both component metrics and the composite `mvi_composite`.

Primary scoring must be:

- deterministic
- replayable
- audit-driven

LLM judges must not be primary scorers for long-horizon orchestration tracks.

## Core Public Metrics

- `validity_precision`
- `validity_recall`
- `ordering_quality`
- `noise_load`
- `staleness_penalty`
- `budget_efficiency`
- `task_outcome_delta`
- `mvi_composite`

## Additional Required Metrics For Long-Horizon Orchestration

- `stale_fact_rate`
- `contradiction_rate`
- `invalid_recall_rate`
- `time_to_correction`
- `steps_to_completion`
- `retry_count`
- `dead_end_branches`
- `handoff_integrity`
- `promotion_integrity`
- `role_boundary_violation_rate`

## Recommended Public Composite

```text
MVI = 0.25 * validity_precision
    + 0.20 * validity_recall
    + 0.15 * ordering_quality
    - 0.20 * staleness_penalty
    - 0.10 * noise_load
    + 0.10 * budget_efficiency
    + 0.10 * task_outcome_delta
```

This composite is acceptable for the public retrieval-and-packing layer, but it is not sufficient by itself for long-horizon multi-agent claims.

## Orchestration Reporting Requirement

Any system claiming strong long-horizon multi-agent performance must also report:

- step-level failure location
- role involved at failure
- whether stale or contradicted memory was used
- whether correction happened after the next perturbation window
- whether project scope or role scope was violated

## Primary Validation Rule

If a metric can be verified by:

- execution
- deterministic rules
- structural checks
- replay logs

then that method should be used instead of an LLM judge.

This formula and these rules are versioned and must remain public.

## Machine-Readable Report Contract

Scoring output must be published in a versioned machine-readable report shape:

- `benchmark_spec/report_schema.json`

At minimum, each report must include:

- scoring version
- scored run count
- whether holdouts were included
- average values for each public metric
- per-family `mvi_composite` summary
- per-scenario score rows
