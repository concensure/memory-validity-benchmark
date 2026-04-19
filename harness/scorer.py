from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_scenarios(root: Path) -> dict[str, dict]:
    scenarios: dict[str, dict] = {}
    for path in root.rglob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        scenarios[data["scenario_id"]] = data
    return scenarios


def score_run(run: dict, scenario: dict) -> dict:
    selected_ids = [item["id"] for item in run["selected_memories"]]
    selected_set = set(selected_ids)
    gold_valid = set(scenario["gold_valid_ids"])
    gold_invalid = set(scenario["gold_invalid_ids"])
    valid_selected = len(selected_set & gold_valid)
    invalid_selected = len(selected_set & gold_invalid)
    precision = valid_selected / len(selected_ids) if selected_ids else 0.0
    recall = valid_selected / len(gold_valid) if gold_valid else 1.0

    ordering_hits = 0
    ordering_total = 0
    for bucket in scenario["preferred_order_buckets"]:
        for idx, memory_id in enumerate(bucket["memory_ids"]):
            ordering_total += 1
            if memory_id in selected_ids:
                actual = selected_ids.index(memory_id)
                if actual <= idx + 2:
                    ordering_hits += 1
    ordering_quality = ordering_hits / ordering_total if ordering_total else 1.0

    noise_load = max(0.0, (len(selected_ids) - valid_selected) / max(1, len(selected_ids)))
    staleness_penalty = invalid_selected / max(1, len(selected_ids))
    budget_efficiency = min(1.0, valid_selected / max(1, run["token_estimate"] / 50))
    no_memory = scenario["task_outcome_baselines"]["no_memory"]
    ideal = scenario["task_outcome_baselines"]["ideal"]
    actual = float((run.get("task_outcome") or {}).get("score", no_memory))
    task_outcome_delta = 0.0 if ideal == no_memory else max(0.0, min(1.0, (actual - no_memory) / (ideal - no_memory)))

    composite = (
        0.25 * precision
        + 0.20 * recall
        + 0.15 * ordering_quality
        - 0.20 * staleness_penalty
        - 0.10 * noise_load
        + 0.10 * budget_efficiency
        + 0.10 * task_outcome_delta
    )

    return {
        "scenario_id": scenario["scenario_id"],
        "validity_precision": round(precision, 4),
        "validity_recall": round(recall, 4),
        "ordering_quality": round(ordering_quality, 4),
        "noise_load": round(noise_load, 4),
        "staleness_penalty": round(staleness_penalty, 4),
        "budget_efficiency": round(budget_efficiency, 4),
        "task_outcome_delta": round(task_outcome_delta, 4),
        "mvi_composite": round(composite, 4),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario-root", required=True)
    parser.add_argument("--run", required=True)
    args = parser.parse_args()

    scenarios = load_scenarios(Path(args.scenario_root))
    run_bundle = json.loads(Path(args.run).read_text(encoding="utf-8"))
    runs = run_bundle["runs"] if isinstance(run_bundle, dict) and "runs" in run_bundle else [run_bundle]
    scores = [score_run(run, scenarios[run["scenario_id"]]) for run in runs]
    average = round(sum(item["mvi_composite"] for item in scores) / max(1, len(scores)), 4)
    print(json.dumps({"scores": scores, "average_mvi_composite": average}, indent=2))


if __name__ == "__main__":
    main()
