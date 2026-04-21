# Injection Rules

Preferred order:

1. session critical
2. project critical
3. long-term critical
4. session supporting
5. project supporting
6. long-term supporting

The benchmark scores both membership and placement. Good systems must not only retrieve the right memories, but inject them in an order that helps realistic agent execution.

## Additional Long-Horizon Rules

For orchestration and replay-heavy tracks, systems must also respect:

- role scope
  A memory intended only for one role should not automatically leak into another role's context.
- project scope
  Project-scoped memory must not be injected into another project unless the scenario explicitly allows cross-project transfer.
- validity before recency
  A newer but stale or contradicted memory should lose to an older still-valid memory.
- critical safety before procedural convenience
  Destructive-action constraints and contradiction blockers should be injected before procedural optimization hints.
- promotion integrity
  Long-term memories should not be injected as trusted context if the scenario indicates promotion should still be blocked or under review.

## Non-Injection Cases

The benchmark should also score scenarios where the correct action is:

- inject nothing
- inject only a single memory
- inject session memory without long-term memory
- suppress all contradicted or stale memories even if they are topically similar
