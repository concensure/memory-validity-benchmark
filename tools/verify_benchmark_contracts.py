"""
@file: verify_benchmark_contracts.py
@description: Verifies benchmark contract integrity by checking scenario validity, scoring version, baseline disclosure, live split health, and historical manifest structure.
@author: OpenAI Codex
@created: 2026-04-28
@modified: 2026-04-28
@dependencies: argparse, json, pathlib, sys
@usage: Run `python tools/verify_benchmark_contracts.py --scenario-root scenarios` before freezing or publishing benchmark artifacts.
@notes: Uses stdlib only and fails fast with actionable messages when contract drift is detected. Historical alpha manifests are validated structurally but are not expected to regenerate from the expanded live corpus.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HARNESS_ROOT = REPO_ROOT / "harness"
if str(HARNESS_ROOT) not in sys.path:
    sys.path.insert(0, str(HARNESS_ROOT))

from validation import validate_scenario  # noqa: E402
from validation import SCENARIO_SCHEMA_VERSION  # noqa: E402
def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_scenarios(scenario_root: Path) -> list[dict]:
    scenarios: list[dict] = []
    for path in sorted(scenario_root.rglob("*.json")):
        if "_archived" in path.parts:
            continue
        scenario = load_json(path)
        validate_scenario(scenario, path=path)
        require(
            scenario.get("schema_version") == SCENARIO_SCHEMA_VERSION,
            f"{path} does not use {SCENARIO_SCHEMA_VERSION}",
        )
        scenarios.append(scenario)
    require(scenarios, "no scenarios found")
    return scenarios


def verify_scoring_version() -> dict:
    scoring_path = REPO_ROOT / "benchmark_spec" / "scoring_version.json"
    scoring = load_json(scoring_path)
    require(isinstance(scoring.get("version"), str) and scoring["version"].strip(), "scoring version is missing")
    require(isinstance(scoring.get("weights"), dict) and scoring["weights"], "scoring weights are missing")
    return scoring


def verify_baseline_manifest() -> dict:
    manifest_path = REPO_ROOT / "baselines" / "baseline_manifest.json"
    manifest = load_json(manifest_path)
    require(manifest.get("manifest_version") == "mvi-baseline-manifest-v1", "baseline manifest version mismatch")
    baselines = manifest.get("baselines")
    require(isinstance(baselines, list) and baselines, "baseline manifest has no baselines")
    for baseline in baselines:
        require(isinstance(baseline.get("id"), str) and baseline["id"].strip(), "baseline id missing")
        require(isinstance(baseline.get("description"), str) and baseline["description"].strip(), "baseline description missing")
    return manifest


def verify_pack_manifest(
    pack_path: Path,
    pack_type: str,
    expected_status: str,
) -> dict:
    manifest = load_json(pack_path)
    require(manifest.get("schema_version") == "mvi-pack-manifest-v1", f"{pack_path} schema version mismatch")
    require(manifest.get("pack_type") == pack_type, f"{pack_path} pack_type mismatch")
    require(manifest.get("status") == expected_status, f"{pack_path} status mismatch")
    require(isinstance(manifest.get("scenario_count"), int), f"{pack_path} scenario_count missing")
    require(isinstance(manifest.get("scenario_ids"), list), f"{pack_path} scenario_ids missing")
    require(isinstance(manifest.get("families"), dict), f"{pack_path} families missing")
    require(manifest["scenario_count"] == len(manifest["scenario_ids"]), f"{pack_path} scenario_count does not match ids")
    require(
        manifest["scenario_count"] == sum(int(count) for count in manifest["families"].values()),
        f"{pack_path} scenario_count does not match family totals",
    )
    return manifest


def summarize_active_split(scenarios: list[dict], pack_type: str) -> tuple[int, int]:
    filtered = [item for item in scenarios if item.get("split", "public") == pack_type]
    families = {item["family"] for item in filtered}
    return len(filtered), len(families)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario-root", default="scenarios")
    args = parser.parse_args()

    scenario_root = Path(args.scenario_root)
    scenarios = verify_scenarios(scenario_root)
    scoring = verify_scoring_version()
    baseline_manifest = verify_baseline_manifest()
    public_manifest = verify_pack_manifest(
        REPO_ROOT / "governance" / "packs" / "public_alpha_manifest.json",
        "public",
        "frozen-local",
    )
    holdout_manifest = verify_pack_manifest(
        REPO_ROOT / "governance" / "packs" / "holdout_alpha_manifest.json",
        "holdout",
        "restricted-holdout",
    )
    active_public_count, active_public_family_count = summarize_active_split(scenarios, "public")
    active_holdout_count, active_holdout_family_count = summarize_active_split(scenarios, "holdout")

    summary = {
        "status": "ok",
        "active_scenario_count": len(scenarios),
        "active_public_count": active_public_count,
        "active_holdout_count": active_holdout_count,
        "active_public_family_count": active_public_family_count,
        "active_holdout_family_count": active_holdout_family_count,
        "historical_public_alpha_count": public_manifest["scenario_count"],
        "historical_holdout_alpha_count": holdout_manifest["scenario_count"],
        "scoring_version": scoring["version"],
        "baseline_count": len(baseline_manifest["baselines"]),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
