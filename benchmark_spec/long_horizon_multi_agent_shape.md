# Long-Horizon Multi-Agent Benchmark Shape

## Definition

The benchmark should be defined as:

`a deterministic task replay system with verifiable end states and memory integrity checks`

This is the correct shape for evaluating memory validity in:

- coding workflows
- session continuity
- project continuity
- multi-agent orchestration
- cross-tier promotion under change

## Core Components

## A. Task Suites

Each long-horizon task should:

- run for `20` to `100` steps
- span multiple sessions
- involve multiple files
- include multiple agent roles
- include changing requirements or repo state

Supported roles should include:

- planner
- architect
- coder
- reviewer

Additional roles may be added later, but those four are the minimum useful set.

## B. Environment

Each task should execute inside:

- a real local Git repo
- a fixed starting commit
- deterministic environment settings
- controlled repo perturbations

The benchmark should prefer real repo state over purely textual simulation wherever practical.

## C. Event Timeline

Each long-horizon scenario should support an event timeline with deterministic perturbations such as:

- code refactor
- dependency upgrade
- requirement change
- conflicting instruction
- branch divergence
- merge event
- memory supersession
- memory invalidation
- promotion approval or rejection event

These events are necessary because long-horizon memory validity is mostly about how systems behave after change.

## D. Memory Variants

The same task should be runnable under:

- no memory baseline
- naive context baseline
- session-only baseline
- project-only baseline
- vector or RAG baseline where applicable
- system under test

## E. Replay Engine

The replay engine should:

- rerun tasks identically from the same seed and repo state
- apply perturbations at defined steps
- emit audit-grade logs
- support repeated-run statistics

## What Must Be Logged

Every long-horizon run should log:

- step number
- active role
- prompt or instruction summary
- tool calls
- repo state changes
- memory reads
- memory writes
- memory promotions
- memory invalidations
- failures and retries

This log should be machine-readable and suitable for replay and audit.

## Primary Measurement Areas

### Outcome Correctness

Primary checks:

- build passes
- tests pass
- expected files changed
- expected config updated
- expected output or API behavior holds

### Memory Integrity

Primary checks:

- stale fact rate
- contradiction rate
- invalid recall
- time-to-correction
- promotion integrity
- role-boundary integrity

### Long-Horizon Stability

Primary checks:

- success rate across 20 to 100 steps
- step at which failures occur
- recovery behavior after perturbation

### Efficiency

Primary checks:

- total tokens per run
- tokens per successful step
- retries
- dead-end branches

## LLM Judge Policy

Primary success metrics must not depend on LLM judgement.

LLM judgement may be used only for:

- bounded qualitative analysis
- secondary explanation review
- non-primary tie-break support

## What This Benchmark Is Not

It is not:

- a generic long-chat memory benchmark
- a pure retrieval benchmark
- a pure tool-use benchmark
- a pure coding benchmark

It is specifically a benchmark for memory validity under long-horizon orchestration and change.
