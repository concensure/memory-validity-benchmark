# Contribution Policy

New scenarios must:

- include at least one invalid or stale distractor
- include explicit order buckets
- include a realistic token budget
- avoid assumptions tied to a single implementation
- disclose whether the scenario is public or holdout-only
- state whether the scenario is retrieval-only, execution-based, or orchestration-focused
- include deterministic success criteria for any primary scored outcome
- include role and project scope where orchestration or cross-project behavior is being tested
- include at least one replay-relevant perturbation for long-horizon scenarios

Scenarios should not rely on open-ended LLM judgement as the primary success criterion.
