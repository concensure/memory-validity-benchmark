"""
@file: estimate_pack_tokens.py
@description: Estimates aggregate token pressure for a pack manifest using declared scenario budgets and deterministic content-length token estimates.
@author: OpenAI Codex
@created: 2026-05-08
@modified: 2026-05-08
@dependencies: json, pathlib, sys
@usage: Run `python tools/estimate_pack_tokens.py --scenario-root scenarios --manifest governance/packs/public_demo_100_manifest.json`.
@notes: This is an estimation utility for pack planning and demo sizing; it does not replace scored run artifacts.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HARNESS_ROOT = REPO_ROOT / "harness"
if str(HARNESS_ROOT) not in sys.path:
    sys.path.insert(0, str(HARNESS_ROOT))

from token_estimator import estimate_tokens  # noqa: E402


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_scenarios(root: Path) -> dict[str, dict]:
    scenarios: dict[str, dict] = {}
    for path in sorted(root.rglob("*.json")):
        data = load_json(path)
        if "_archived" in path.parts:
            continue
        scenarios[data["scenario_id"]] = data
    return scenarios


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario-root", required=True)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()

    scenarios = load_scenarios(Path(args.scenario_root))
    manifest = load_json(Path(args.manifest))
    selected = []
    for scenario_id in manifest["scenario_ids"]:
        if scenario_id not in scenarios:
            raise SystemExit(f"scenario {scenario_id!r} not found under {args.scenario_root}")
        selected.append(scenarios[scenario_id])

    family_counts = Counter(item["family"] for item in selected)
    declared_total = sum(int(item["token_budget"]) for item in selected)
    candidate_total = 0
    gold_valid_total = 0
    for scenario in selected:
        candidate_total += sum(estimate_tokens(item["content"]) for item in scenario["candidate_memories"])
        candidate_lookup = {item["id"]: item for item in scenario["candidate_memories"]}
        gold_valid_total += sum(
            estimate_tokens(candidate_lookup[memory_id]["content"])
            for memory_id in scenario["gold_valid_ids"]
            if memory_id in candidate_lookup
        )

    count = len(selected)
    summary = {
        "manifest": manifest["pack_id"],
        "scenario_count": count,
        "family_count": len(family_counts),
        "families": dict(sorted(family_counts.items())),
        "declared_token_budget_total": declared_total,
        "declared_token_budget_average": round(declared_total / max(1, count), 2),
        "estimated_candidate_tokens_total": candidate_total,
        "estimated_candidate_tokens_average": round(candidate_total / max(1, count), 2),
        "estimated_gold_valid_tokens_total": gold_valid_total,
        "estimated_gold_valid_tokens_average": round(gold_valid_total / max(1, count), 2),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
