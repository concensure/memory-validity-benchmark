from __future__ import annotations

import argparse
import json
from pathlib import Path

from validation import coerce_legacy_bundle, coerce_legacy_run, validate_bundle, validate_run, validate_scenario

REPORT_SCHEMA_VERSION = "mvi-score-report-v1"


def load_scenarios(root: Path) -> dict[str, dict]:
    scenarios: dict[str, dict] = {}
    for path in root.rglob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        validate_scenario(data, path=path)
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


def load_scoring_version() -> str:
    version_path = Path(__file__).resolve().parent.parent / "benchmark_spec" / "scoring_version.json"
    data = json.loads(version_path.read_text(encoding="utf-8"))
    return str(data["version"])


def average_metric(scores: list[dict], metric: str) -> float:
    return round(sum(item[metric] for item in scores) / max(1, len(scores)), 4)


def build_report(
    scores: list[dict],
    scenarios: dict[str, dict],
    scenario_root: Path,
    run_path: Path,
    include_holdout: bool,
    suite_name: str,
    system_name: str,
) -> dict:
    metric_names = [
        "validity_precision",
        "validity_recall",
        "ordering_quality",
        "noise_load",
        "staleness_penalty",
        "budget_efficiency",
        "task_outcome_delta",
        "mvi_composite",
    ]
    family_averages: dict[str, list[float]] = {}
    for item in scores:
        family = scenarios[item["scenario_id"]]["family"]
        family_averages.setdefault(family, []).append(item["mvi_composite"])
    metric_averages = {metric: average_metric(scores, metric) for metric in metric_names}
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "scoring_version": load_scoring_version(),
        "scope": {
            "scenario_root": str(scenario_root),
            "run_path": str(run_path),
            "include_holdout": bool(include_holdout),
            "suite_name": suite_name,
            "system_name": system_name,
            "scored_run_count": len(scores),
        },
        "summary": {
            "average_mvi_composite": metric_averages["mvi_composite"],
            "metric_averages": metric_averages,
            "by_family": {
                family: round(sum(values) / max(1, len(values)), 4) for family, values in sorted(family_averages.items())
            },
        },
        "scores": scores,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario-root", required=True)
    parser.add_argument("--run", required=True)
    parser.add_argument("--include-holdout", action="store_true")
    parser.add_argument("--out")
    args = parser.parse_args()

    scenario_root = Path(args.scenario_root)
    scenarios = load_scenarios(scenario_root)
    run_path = Path(args.run)
    run_bundle = json.loads(run_path.read_text(encoding="utf-8"))
    normalized_bundle = coerce_legacy_bundle(run_bundle) if isinstance(run_bundle, dict) and "runs" in run_bundle else None
    runs = (
        validate_bundle(normalized_bundle, scenarios, path=run_path)
        if isinstance(run_bundle, dict) and "runs" in run_bundle
        else [validate_run(coerce_legacy_run(run_bundle), scenarios[run_bundle["scenario_id"]], path=run_path)]
    )
    if not args.include_holdout:
        runs = [run for run in runs if scenarios[run["scenario_id"]].get("split") != "holdout"]
    scores = [score_run(run, scenarios[run["scenario_id"]]) for run in runs]
    report = build_report(
        scores=scores,
        scenarios=scenarios,
        scenario_root=scenario_root,
        run_path=run_path,
        include_holdout=bool(args.include_holdout),
        suite_name=(normalized_bundle or {}).get("suite_name", ""),
        system_name=(normalized_bundle or {}).get("system_name", runs[0]["system_name"] if runs else ""),
    )
    output = json.dumps(report, indent=2)
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
