# Baselines

The benchmark ships with transparent baselines:

- `no_memory`
- `naive_topk`
- `session_only`
- `heuristic_tiered`

Every published result should disclose whether it is being compared against these baselines or a modified variant.

Baseline metadata is frozen in:

- `baselines/baseline_manifest.json`

Published benchmark reports should disclose:

- baseline id
- whether the baseline is exactly the frozen reference version
- any changes to retrieval ordering, token budgeting, or tier access
