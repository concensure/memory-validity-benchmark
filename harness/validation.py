"""
@file: validation.py
@description: Validates MVI scenarios, run artifacts, and run bundles using deterministic stdlib checks so the harness can reject malformed benchmark inputs before scoring.
@author: OpenAI Codex
@created: 2026-04-28
@modified: 2026-04-28
@dependencies: json, pathlib
@usage: Import validate_scenario(), validate_run(), or validate_bundle() from runner and scorer before generating or scoring benchmark artifacts.
@notes: Intentionally avoids external schema libraries to keep the harness lightweight and reproducible.
"""

from __future__ import annotations

from pathlib import Path


SCENARIO_SCHEMA_VERSION = "mvi-scenario-v1"
RUN_SCHEMA_VERSION = "mvi-run-v1"
BUNDLE_SCHEMA_VERSION = "mvi-run-bundle-v1"

VALID_TIERS = {"session", "project", "long_term"}
VALID_MEMORY_STATES = {"valid", "stale", "contradicted", "irrelevant"}
VALID_BUCKETS = {"critical", "supporting"}
VALID_SPLITS = {"public", "holdout"}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _require_keys(data: dict, keys: list[str], label: str) -> None:
    for key in keys:
        _require(key in data, f"{label} missing required field {key!r}")


def validate_scenario(data: dict, path: Path | None = None) -> dict:
    label = f"scenario {path}" if path else f"scenario {data.get('scenario_id', '<unknown>')}"
    _require_keys(
        data,
        [
            "scenario_id",
            "family",
            "task",
            "repo_state_fingerprint",
            "token_budget",
            "candidate_memories",
            "gold_valid_ids",
            "gold_invalid_ids",
            "preferred_order_buckets",
            "task_outcome_baselines",
        ],
        label,
    )
    _require(data.get("schema_version") == SCENARIO_SCHEMA_VERSION, f"{label} has unsupported schema_version")
    _require(data.get("split", "public") in VALID_SPLITS, f"{label} has invalid split")
    _require(isinstance(data["token_budget"], int) and data["token_budget"] > 0, f"{label} has invalid token_budget")
    _require(isinstance(data["candidate_memories"], list) and data["candidate_memories"], f"{label} has no candidate_memories")

    memory_ids: set[str] = set()
    for memory in data["candidate_memories"]:
        _require_keys(memory, ["id", "tier", "content", "validity", "bucket"], f"{label} memory")
        _require(memory["id"] not in memory_ids, f"{label} contains duplicate memory id {memory['id']!r}")
        memory_ids.add(memory["id"])
        _require(memory["tier"] in VALID_TIERS, f"{label} memory {memory['id']!r} has invalid tier")
        _require(memory["validity"] in VALID_MEMORY_STATES, f"{label} memory {memory['id']!r} has invalid validity")
        _require(memory["bucket"] in VALID_BUCKETS, f"{label} memory {memory['id']!r} has invalid bucket")
        _require(isinstance(memory["content"], str) and memory["content"].strip(), f"{label} memory {memory['id']!r} has empty content")

    gold_valid = set(data["gold_valid_ids"])
    gold_invalid = set(data["gold_invalid_ids"])
    _require(gold_valid.isdisjoint(gold_invalid), f"{label} gold_valid_ids and gold_invalid_ids overlap")
    _require(gold_valid <= memory_ids, f"{label} gold_valid_ids reference unknown memories")
    _require(gold_invalid <= memory_ids, f"{label} gold_invalid_ids reference unknown memories")

    for bucket in data["preferred_order_buckets"]:
        _require_keys(bucket, ["name", "memory_ids"], f"{label} preferred_order_bucket")
        _require(isinstance(bucket["memory_ids"], list), f"{label} preferred_order_bucket has invalid memory_ids")
        _require(set(bucket["memory_ids"]) <= memory_ids, f"{label} preferred_order_bucket references unknown memories")

    baselines = data["task_outcome_baselines"]
    _require_keys(baselines, ["no_memory", "ideal"], f"{label} task_outcome_baselines")
    _require(float(baselines["ideal"]) >= float(baselines["no_memory"]), f"{label} ideal baseline is below no_memory")
    return data


def validate_run(run: dict, scenario: dict, path: Path | None = None) -> dict:
    label = f"run {path}" if path else f"run {run.get('scenario_id', '<unknown>')}"
    _require_keys(
        run,
        ["schema_version", "system_name", "scenario_id", "selected_memories", "final_injection_order", "token_estimate"],
        label,
    )
    _require(run["schema_version"] == RUN_SCHEMA_VERSION, f"{label} has unsupported schema_version")
    _require(run["scenario_id"] == scenario["scenario_id"], f"{label} scenario_id does not match scenario")
    _require(isinstance(run["system_name"], str) and run["system_name"].strip(), f"{label} has invalid system_name")
    _require(isinstance(run["token_estimate"], int) and run["token_estimate"] >= 0, f"{label} has invalid token_estimate")
    _require(isinstance(run["selected_memories"], list), f"{label} selected_memories must be a list")
    _require(isinstance(run["final_injection_order"], list), f"{label} final_injection_order must be a list")

    candidate_memories = {item["id"]: item for item in scenario["candidate_memories"]}
    selected_ids: list[str] = []
    for memory in run["selected_memories"]:
        _require_keys(memory, ["id", "tier", "content"], f"{label} selected_memory")
        memory_id = memory["id"]
        _require(memory_id in candidate_memories, f"{label} references unknown memory id {memory_id!r}")
        _require(memory["tier"] == candidate_memories[memory_id]["tier"], f"{label} memory {memory_id!r} tier mismatch")
        _require(memory["content"] == candidate_memories[memory_id]["content"], f"{label} memory {memory_id!r} content mismatch")
        selected_ids.append(memory_id)

    _require(len(selected_ids) == len(set(selected_ids)), f"{label} contains duplicate selected memories")
    _require(run["final_injection_order"] == selected_ids, f"{label} final_injection_order must match selected_memories order")

    outcome = run.get("task_outcome")
    if outcome is not None:
        _require(isinstance(outcome, dict), f"{label} task_outcome must be an object when present")
        if "passed" in outcome:
            _require(isinstance(outcome["passed"], bool), f"{label} task_outcome.passed must be boolean")
        if "score" in outcome:
            _require(isinstance(outcome["score"], (int, float)), f"{label} task_outcome.score must be numeric")
    return run


def validate_bundle(bundle: dict, scenario_index: dict[str, dict], path: Path | None = None) -> list[dict]:
    label = f"bundle {path}" if path else "bundle"
    _require_keys(bundle, ["schema_version", "run_count", "runs"], label)
    _require(bundle["schema_version"] == BUNDLE_SCHEMA_VERSION, f"{label} has unsupported schema_version")
    _require(isinstance(bundle["runs"], list), f"{label} runs must be a list")
    _require(isinstance(bundle["run_count"], int) and bundle["run_count"] >= 0, f"{label} has invalid run_count")
    _require(bundle["run_count"] == len(bundle["runs"]), f"{label} run_count does not match runs length")

    seen: set[tuple[str, str]] = set()
    for run in bundle["runs"]:
        scenario_id = run.get("scenario_id")
        _require(scenario_id in scenario_index, f"{label} references unknown scenario_id {scenario_id!r}")
        key = (run.get("system_name", ""), scenario_id)
        _require(key not in seen, f"{label} contains duplicate run for system/scenario pair {key!r}")
        seen.add(key)
        validate_run(run, scenario_index[scenario_id], path=path)
    return bundle["runs"]


def coerce_legacy_run(run: dict) -> dict:
    if "schema_version" in run:
        return run
    coerced = dict(run)
    coerced["schema_version"] = RUN_SCHEMA_VERSION
    return coerced


def coerce_legacy_bundle(bundle: dict) -> dict:
    if bundle.get("schema_version") == BUNDLE_SCHEMA_VERSION:
        return bundle
    if "runs" not in bundle:
        return bundle
    runs = [coerce_legacy_run(run) for run in bundle["runs"]]
    system_name = runs[0]["system_name"] if runs else ""
    return {
        "schema_version": BUNDLE_SCHEMA_VERSION,
        "suite_name": bundle.get("suite_name", "legacy-imported-pack"),
        "system_name": bundle.get("system_name", system_name),
        "include_holdout": bundle.get("include_holdout", False),
        "run_count": len(runs),
        "runs": runs,
    }
