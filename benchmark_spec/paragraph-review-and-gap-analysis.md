# Paragraph Review And Gap Analysis

## Purpose

This document evaluates the proposed design paragraphs for long-horizon multi-agent benchmarking and compares them against the current state of `memory-validity-index`.

The goal is not to accept the paragraphs uncritically. The goal is to decide:

- which points are valid
- which points are too strong or too broad
- what gaps exist between those valid points and the current benchmark
- what needs to change

## Overall Assessment

The paragraphs are directionally correct.

Their strongest claims are valid:

- long-horizon, multi-agent evaluation is exactly where weak memory benchmarks break down
- LLM-judge-heavy evaluation is not suitable as the primary scoring layer
- the benchmark should be deterministic, replayable, and audit-driven
- real Git repos and controlled perturbations are necessary for credible coding workflows
- memory validity should be measured over time, not only at a single retrieval moment

However, some statements are too absolute if read literally.

The benchmark should not ban every use of LLM judgement. It should instead:

- ban LLM judges from primary success criteria
- allow them only for secondary analysis or tightly bounded tie-break cases

That is a better balance than a total ban.

## What In The Paragraphs Makes Sense

### 1. Deterministic replay is the right benchmark foundation

Valid.

If the benchmark claims to measure memory validity under change, then:

- repo state must be controlled
- perturbations must be scheduled
- replay must be possible
- the same task should be rerunnable

Without that, failure analysis becomes weak and comparisons become noisy.

### 2. Real Git repos and controlled perturbations are necessary

Valid.

Long-horizon memory validity in coding cannot be tested credibly using only flat QA or static transcript tasks.

The benchmark needs:

- fixed starting commits
- scripted repo drift
- branch and merge events
- requirement changes
- contradictory instructions

### 3. Outcome correctness must be machine-checkable

Valid and non-negotiable for primary scoring.

Where possible, the benchmark should use:

- exit codes
- tests
- build success
- file diffs
- config checks
- API or CLI outputs

### 4. Memory validity over time is the core differentiator

Valid.

The benchmark should measure:

- stale fact rate
- contradiction rate
- invalid recall
- time-to-correction

But these should be defined carefully and backed by deterministic labels or replay traces.

### 5. Long-horizon stability, token efficiency, and agent efficiency all matter

Valid.

A system that retrieves the right memory but burns huge tokens, retries excessively, or collapses at step 40 is not strong in practical use.

### 6. Replayability, repeated runs, and cross-model checks all improve credibility

Valid.

The most important parts are:

- replayability
- repeated runs
- published logs and scripts

Cross-model testing is useful, but it is secondary to deterministic benchmark design.

## Where The Paragraphs Need Tightening

### 1. "No LLM judgement" is too absolute

The valid principle is:

- no LLM judgement as primary metric

The invalid overreach would be:

- never use LLM judgement anywhere

Better benchmark rule:

- use deterministic or executable scoring for primary outcomes
- use LLM judges only for bounded secondary analysis

### 2. "Expected commands" should not be over-weighted

For coding workflows, expected commands can be useful audit signals.

But the benchmark should not require only one exact command sequence unless the scenario specifically tests sequencing.

Otherwise it may reward rigid reproduction rather than valid problem solving.

### 3. "Ground truth file diffs" should be used carefully

Exact diffs are good for some tasks.

But some tasks should allow multiple valid solutions and rely on:

- executable test oracles
- structural validators
- interface constraints

instead of exact diff matching only.

## Current Gaps In This Project

Compared with the valid points in the paragraphs, the current benchmark still has the following gaps.

### Gap 1: The benchmark is still more context-selection-oriented than replay-oriented

Current state:

- strong scenario and scoring structure
- good retrieval and packing focus

Missing:

- benchmark-wide deterministic replay model for long-horizon task execution
- explicit event timeline model in the official benchmark shape

Needed change:

- define task replay as a first-class benchmark mode

### Gap 2: Multi-agent orchestration is present, but not yet operationally specified deeply enough

Current state:

- multi-agent scenarios are in scope
- role boundaries and consensus are mentioned

Missing:

- precise role contracts
- session-to-session handoff requirements
- cross-agent contamination checks at the harness level

Needed change:

- formalize orchestration track requirements and audit artifacts

### Gap 3: Memory mutation events are not yet a first-class artifact type

Current state:

- scenarios model validity and perturbation conceptually

Missing:

- explicit memory mutation events:
  invalidation, supersession, override, contradiction, promotion eligibility, promotion rejection

Needed change:

- add benchmark event types for memory mutation and expected handling

### Gap 4: The benchmark needs stronger audit-log requirements

Current state:

- run artifacts exist

Missing:

- required audit fields for:
  memory reads, writes, promotions, invalidations, role actions, and replay step numbers

Needed change:

- expand run artifact expectations for orchestration tracks

### Gap 5: Long-horizon execution tracks need to be more explicit

Current state:

- execution-based scoring is recognized

Missing:

- exact definition of:
  20 to 100 step task replay tracks
  step-level perturbations
  failure-point reporting

Needed change:

- document a dedicated long-horizon replay track

## Required Changes

To align the benchmark with the valid parts of the paragraphs, the project should change in the following ways.

1. Add a benchmark shape document centered on deterministic long-horizon replay.
2. Add an orchestration contract document covering:
   architect, coder, reviewer, planner, role boundaries, shared/private scope, and cross-session handoff.
3. Add an event timeline contract for:
   repo drift, requirement change, conflicting instruction, and memory mutation events.
4. Expand scoring docs so step-level failures, stale memory use, contradiction use, and time-to-correction are explicit metrics.
5. Expand the run artifact contract for audit-driven replay.
6. Keep LLM judges secondary and non-blocking.

## Conclusion

The paragraphs are substantially right about the shape of a credible benchmark.

The strongest valid idea is this:

`the benchmark must be deterministic, replayable, and audit-driven`

The current project is directionally aligned with that idea, but it still needs stronger benchmark-wide treatment of:

- deterministic replay
- event timelines
- orchestration contracts
- audit artifacts
- long-horizon failure analysis

