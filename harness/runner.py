from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Callable

from token_estimator import estimate_tokens


def load_scenarios(root: Path, include_holdout: bool = False) -> list[dict]:
    scenarios: list[dict] = []
    for path in sorted(root.rglob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if not include_holdout and data.get("split") == "holdout":
            continue
        scenarios.append(data)
    return scenarios


def baseline_no_memory(scenario: dict) -> dict:
    return make_run("baseline:no_memory", scenario, [])


def baseline_naive_topk(scenario: dict) -> dict:
    selected = sorted(
        scenario["candidate_memories"],
        key=lambda item: (item["validity"] != "valid", len(item["content"])),
    )[:4]
    return make_run("baseline:naive_topk", scenario, selected)


def baseline_session_only(scenario: dict) -> dict:
    selected = [
        item
        for item in scenario["candidate_memories"]
        if item["tier"] == "session" and item["validity"] == "valid"
    ][:4]
    return make_run("baseline:session_only", scenario, selected)


def baseline_heuristic_tiered(scenario: dict) -> dict:
    rank = {
        ("session", "critical", "valid"): 0,
        ("project", "critical", "valid"): 1,
        ("long_term", "critical", "valid"): 2,
        ("session", "supporting", "valid"): 3,
        ("project", "supporting", "valid"): 4,
        ("long_term", "supporting", "valid"): 5,
    }
    selected = sorted(
        scenario["candidate_memories"],
        key=lambda item: rank.get((item["tier"], item["bucket"], item["validity"]), 99),
    )[:6]
    return make_run("baseline:heuristic_tiered", scenario, selected)


BASELINES: dict[str, Callable[[dict], dict]] = {
    "baseline:no_memory": baseline_no_memory,
    "baseline:naive_topk": baseline_naive_topk,
    "baseline:session_only": baseline_session_only,
    "baseline:heuristic_tiered": baseline_heuristic_tiered,
}


def make_run(system_name: str, scenario: dict, selected: list[dict]) -> dict:
    order = [item["id"] for item in selected]
    token_estimate = sum(estimate_tokens(item["content"]) for item in selected)
    passed = any(item["id"] in scenario["gold_valid_ids"] for item in selected)
    score = scenario["task_outcome_baselines"]["ideal"] if passed else scenario["task_outcome_baselines"]["no_memory"]
    return {
        "system_name": system_name,
        "scenario_id": scenario["scenario_id"],
        "selected_memories": [
            {"id": item["id"], "tier": item["tier"], "content": item["content"]} for item in selected
        ],
        "final_injection_order": order,
        "token_estimate": token_estimate,
        "task_outcome": {
            "passed": passed,
            "score": score,
            "notes": "baseline heuristic run",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario-root", required=True)
    parser.add_argument("--system", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--include-holdout", action="store_true")
    args = parser.parse_args()

    system = args.system
    if system not in BASELINES:
        raise SystemExit(f"unsupported system {system!r}")

    scenarios = load_scenarios(Path(args.scenario_root), include_holdout=args.include_holdout)
    runs = [BASELINES[system](scenario) for scenario in scenarios]
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({"runs": runs}, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
