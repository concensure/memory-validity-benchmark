# Memory Validity Index

`memory-validity-index`, or `MVI`, is a deterministic benchmark for evaluating whether memory injected into an agent context window is valid, well ordered, budget efficient, and helpful for realistic long-horizon agent workflows such as coding, multi-agent orchestration, resume workflows, and OpenClaw-style tool use.

This benchmark is intentionally not tied to `omnymem`. It is designed to evaluate any agent memory system that can emit a run artifact conforming to the benchmark schema.

## What It Measures

`MVI` evaluates memory as a context injection and workflow integrity problem, not just retrieval:

- `validity_precision`
- `validity_recall`
- `ordering_quality`
- `noise_load`
- `staleness_penalty`
- `budget_efficiency`
- `task_outcome_delta`
- `mvi_composite`

It is specifically intended to measure whether a memory system can survive:

- multiple sessions
- multiple agent roles
- requirement changes
- Git drift
- cross-tier promotion pressure
- project isolation and controlled long-term transfer

## Why Three Layers Matter

The benchmark models three memory layers because realistic agent systems use distinct forms of memory:

- Session: active short-lived task state
- Project: repo-scoped durable context
- Long-term: cross-project trusted knowledge

Selection and order are both scored. A system can lose points by retrieving the right memory but injecting it too late, from the wrong tier, from the wrong project, or after it is already stale or contradicted.

## Benchmark Shape

The intended end-state shape is:

- deterministic task replay
- fixed starting repo state
- machine-checkable success criteria
- controlled perturbations over time
- multi-agent role structure
- audit-friendly run artifacts

The benchmark should behave like:

`a deterministic task replay system with verifiable end states and memory integrity checks`

It is explicitly not intended to be:

- a pure long-conversation QA benchmark
- an LLM-judge-first benchmark
- a benchmark of raw coding model skill without memory controls

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

## Current Draft Status

Current active local corpus:

- `525` active scenarios
- `360` public
- `165` holdout
- `24` active families
- `75` archived scenarios retained outside the active corpus

The current public and holdout splits are intentionally frozen by scenario metadata and manifest, not by assuming perfectly even family sizes.

Historical MVP launch manifests remain in:

- `governance/packs/public_alpha_manifest.json`
- `governance/packs/holdout_alpha_manifest.json`

Those alpha manifests are useful for regression continuity, but they do not represent the current active corpus breadth.

## Public Demo Pack

The repository now also includes a bounded public demonstration pack:

- `governance/packs/public_demo_100_manifest.json`

This pack is not a new scoring contract and not a special-case `omnymem` track. It is a neutral, broad public subset intended for:

- credible public demonstrations
- faster regression runs than the full `360`-scenario public set
- coverage across retrieval, injection, long-horizon, and multi-agent families

Selection policy and rationale are documented in:

- `governance/public_demo_policy.md`

## Running The Benchmark

The harness uses only the Python standard library.

Example:

```powershell
python harness/runner.py --scenario-root scenarios --system baseline:heuristic_tiered --out reports/generated/heuristic.json
python harness/scorer.py --scenario-root scenarios --run reports/generated/heuristic.json
python harness/scorer.py --scenario-root scenarios --run reports/generated/heuristic.json --out reports/generated/heuristic_report.json
python tools/verify_benchmark_contracts.py --scenario-root scenarios
python tools/estimate_pack_tokens.py --scenario-root scenarios --manifest governance/packs/public_demo_100_manifest.json
```

The scorer accepts either:

- a bundle file conforming to `benchmark_spec/bundle_schema.json`
- a single run artifact emitted by an external system

Scenario and run contracts are versioned in:

- `benchmark_spec/scenario_schema.json`
- `benchmark_spec/run_schema.json`
- `benchmark_spec/bundle_schema.json`
- `benchmark_spec/report_schema.json`
- `benchmark_spec/pack_schema.json`

Frozen local launch pack manifests live in:

- `governance/packs/public_alpha_manifest.json`
- `governance/packs/holdout_alpha_manifest.json`

## Primary Evaluation Philosophy

Primary metrics should be:

- deterministic
- replayable
- auditable

Primary success should be established by:

- execution checks
- structural checks
- rule-based validators
- memory audit logs

LLM judges may be used only as secondary analysis tools, never as the primary success criterion for long-horizon orchestration tracks.

## Baselines

Built-in baselines:

- `baseline:no_memory`
- `baseline:naive_topk`
- `baseline:session_only`
- `baseline:heuristic_tiered`

Reference disclosure metadata for these baselines lives in:

- `baselines/baseline_manifest.json`

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

See also:

- `benchmark_spec/long_horizon_multi_agent_shape.md`
- `benchmark_spec/paragraph-review-and-gap-analysis.md`
- `governance/public_demo_policy.md`
- `governance/roadmap.md`
- `governance/packs/`
