# Holdout Policy

Official benchmark comparisons should use:

- public frozen scenarios for transparent iteration
- private holdout scenarios for anti-overfitting checks

Holdout scenarios should not be required for local development runs.

For long-horizon orchestration claims, holdouts should preferentially contain:

- role disagreement cases
- branch and merge drift cases
- cross-project leakage traps
- long-horizon tool workflows
- promotion-integrity and contradiction scenarios
