from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


def load_scenarios(root: Path, include_holdout: bool = False) -> list[Path]:
    paths: list[Path] = []
    for path in sorted(root.rglob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if not include_holdout and data.get("split") == "holdout":
            continue
        paths.append(path)
    return paths


def run_command(command: list[str], cwd: Path, env: dict[str, str]) -> str:
    completed = subprocess.run(
        command,
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"command failed ({completed.returncode}): {' '.join(command)}\n{completed.stdout}\n{completed.stderr}")
    return completed.stdout


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--omnymem", required=True)
    parser.add_argument("--scenario-root", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--system-name", default="omnymem-local")
    parser.add_argument("--include-holdout", action="store_true")
    args = parser.parse_args()

    omnymem = Path(args.omnymem).resolve()
    scenario_root = Path(args.scenario_root).resolve()
    out_path = Path(args.out).resolve()
    runs: list[dict] = []

    for scenario_path in load_scenarios(scenario_root, include_holdout=args.include_holdout):
        with tempfile.TemporaryDirectory(prefix="omnymem-bench-") as tmp:
            work = Path(tmp) / "repo"
            home = Path(tmp) / "home"
            work.mkdir(parents=True, exist_ok=True)
            home.mkdir(parents=True, exist_ok=True)
            env = os.environ.copy()
            env["USERPROFILE"] = str(home)
            env["HOME"] = str(home)
            run_command([str(omnymem), "init"], work, env)
            run_command([str(omnymem), "benchmark", "import-scenario", "--scenario", str(scenario_path)], work, env)
            output = run_command(
                [str(omnymem), "benchmark", "export-run", "--scenario", str(scenario_path), "--system-name", args.system_name],
                work,
                env,
            )
            runs.append(json.loads(output))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({"runs": runs}, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
