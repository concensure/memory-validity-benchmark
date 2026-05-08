"""
@file: generate_pack_manifest.py
@description: Generates deterministic public or holdout scenario pack manifests from scenario metadata so publication and scoring scope can be frozen and verified.
@author: OpenAI Codex
@created: 2026-04-28
@modified: 2026-04-28
@dependencies: argparse, json, pathlib, collections
@usage: Run `python tools/generate_pack_manifest.py --scenario-root scenarios --pack-type public --out governance/packs/public_alpha_manifest.json` to regenerate a manifest.
@notes: Uses only stdlib and derives pack membership from each scenario's split field.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


PACK_SCHEMA_VERSION = "mvi-pack-manifest-v1"


def load_scenarios(root: Path) -> list[dict]:
    scenarios: list[dict] = []
    for path in sorted(root.rglob("*.json")):
        scenarios.append(json.loads(path.read_text(encoding="utf-8")))
    return scenarios


def build_manifest(scenarios: list[dict], pack_type: str, pack_id: str, status: str, description: str) -> dict:
    filtered = sorted(
        [item for item in scenarios if item.get("split", "public") == pack_type],
        key=lambda item: item["scenario_id"],
    )
    family_counts = Counter(item["family"] for item in filtered)
    return {
        "schema_version": PACK_SCHEMA_VERSION,
        "pack_id": pack_id,
        "pack_type": pack_type,
        "status": status,
        "description": description,
        "scenario_count": len(filtered),
        "families": dict(sorted(family_counts.items())),
        "scenario_ids": [item["scenario_id"] for item in filtered],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario-root", required=True)
    parser.add_argument("--pack-type", choices=["public", "holdout"], required=True)
    parser.add_argument("--pack-id", required=True)
    parser.add_argument("--status", required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    scenarios = load_scenarios(Path(args.scenario_root))
    manifest = build_manifest(scenarios, args.pack_type, args.pack_id, args.status, args.description)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
