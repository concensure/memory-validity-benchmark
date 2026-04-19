# Scoring

The benchmark publishes both component metrics and the composite `mvi_composite`.

Recommended formula:

```text
MVI = 0.25 * validity_precision
    + 0.20 * validity_recall
    + 0.15 * ordering_quality
    - 0.20 * staleness_penalty
    - 0.10 * noise_load
    + 0.10 * budget_efficiency
    + 0.10 * task_outcome_delta
```

This formula is versioned and must remain public.
