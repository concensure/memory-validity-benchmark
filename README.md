# Memory Validity Index

`memory-validity-index`, or `MVI`, is a compact benchmark for evaluating whether memory injected into an agent context window is valid, well ordered, budget efficient, and helpful for realistic agent tasks such as coding, resume workflows, and OpenClaw-style tool use.

This benchmark is intentionally not tied to `omnymem`. It is designed to evaluate any agent memory system that can emit a run artifact conforming to the benchmark schema.

## What It Measures

`MVI` evaluates memory as a context injection problem, not just retrieval:

- `validity_precision`
- `validity_recall`
- `ordering_quality`
- `noise_load`
- `staleness_penalty`
- `budget_efficiency`
- `task_outcome_delta`
- `mvi_composite`

## Why Three Layers Matter

The benchmark models three memory layers because realistic agent systems use distinct forms of memory:

- Session: active short-lived task state
- Project: repo-scoped durable context
- Long-term: cross-project trusted knowledge

Selection and order are both scored. A system can lose points by retrieving the right memory but injecting it too late.

## Repository Layout

```text
memory-validity-index/
  benchmark_spec/
  scenarios/
  baselines/
  harness/
  holdouts/
  governance/
  reports/
```

## Running The Benchmark

The harness uses only the Python standard library.

Example:

```powershell
python harness/runner.py --scenario-root scenarios --system baseline:heuristic_tiered --out reports/generated/heuristic.json
python harness/scorer.py --scenario-root scenarios --run reports/generated/heuristic.json
```

The scorer accepts either:

- a bundle file containing `{"runs":[...]}`
- a single run artifact emitted by an external system

## Baselines

Built-in baselines:

- `baseline:no_memory`
- `baseline:naive_topk`
- `baseline:session_only`
- `baseline:heuristic_tiered`

## Omnymem Integration

`omnymem` can emit benchmark-compatible run artifacts through its benchmark export command. The benchmark consumes only the emitted run schema; it does not require direct knowledge of omnymem internals.

Example flow:

```powershell
omnymem benchmark import-scenario --scenario C:\path\to\cb001.json
omnymem benchmark export-run --scenario C:\path\to\cb001.json --out cb001-run.json
python harness/scorer.py --scenario-root scenarios --run cb001-run.json
```

## Governance

This repo includes governance materials so the benchmark can remain objective:

- frozen public scenario pack
- hidden holdout guidance
- scoring versioning
- contribution policy
- baseline disclosure requirements
