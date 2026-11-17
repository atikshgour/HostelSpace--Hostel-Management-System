"""Team test review | US-18/23 | Capture real commands, outputs and exit codes.

Runs only tests/coverage/build commands. PostgreSQL and browser test services must
already be running against isolated synthetic data. Does not commit or push.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "test_results"
PYTHON = str(
    ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
)
NPM = "npm.cmd" if os.name == "nt" else "npm"
NPX = "npx.cmd" if os.name == "nt" else "npx"

COMMANDS = {
    "coverage-export": (
        "backend",
        [
            PYTHON,
            "-m",
            "coverage",
            "json",
            "--show-contexts",
            "-o",
            "../test_results/coverage.json",
        ],
    ),
    "backend": (
        "backend",
        [
            PYTHON,
            "-m",
            "pytest",
            "--tb=short",
            "-q",
            "--junitxml=../test_results/raw/backend-junit.xml",
            "--cov=apps",
            "--cov=config",
            "--cov-branch",
            "--cov-context=test",
            "--cov-report=term-missing",
            "--cov-report=xml:../test_results/coverage.xml",
            "--cov-report=json:../test_results/coverage.json",
            "--cov-report=html:../test_results/coverage/backend-html",
        ],
    ),
    "frontend": (
        "frontend",
        [
            NPM,
            "run",
            "test:ci",
            "--",
            "--config=jest.coverage.config.mjs",
            "--runInBand",
            "--coverageDirectory=../test_results/coverage/frontend",
            "--json",
            "--outputFile=../test_results/raw/frontend-results.json",
        ],
    ),
    "build": ("frontend", [NPM, "run", "build"]),
    "lint": ("frontend", [NPM, "run", "lint"]),
    "e2e": (
        "frontend",
        [
            NPX,
            "playwright",
            "test",
            "--project=chromium",
            "--trace=off",
            "--reporter=list,json,html",
            "--output=../test_results/raw/browser-output",
        ],
    ),
}


def run(phase):
    directory, command = COMMANDS[phase]
    (RESULTS / "raw").mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["NEXT_TELEMETRY_DISABLED"] = "1"
    if phase == "e2e":
        env["PLAYWRIGHT_JSON_OUTPUT_FILE"] = str(
            RESULTS / "raw" / "browser-results.json"
        )
        env["PLAYWRIGHT_HTML_OUTPUT_DIR"] = str(RESULTS / "raw" / "browser-html")
        env["PLAYWRIGHT_HTML_OPEN"] = "never"
    start = datetime.now(UTC).isoformat()
    result = subprocess.run(
        command, cwd=ROOT / directory, env=env, capture_output=True, check=False
    )
    log = result.stdout + b"\n" + result.stderr
    (RESULTS / "raw" / f"{phase}.log").write_bytes(log)
    sha = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    record = {
        "phase": phase,
        "cwd": directory,
        "command": command,
        "started_at": start,
        "finished_at": datetime.now(UTC).isoformat(),
        "source_commit": sha,
        "working_tree_changes": bool(dirty),
        "exit_code": result.returncode,
    }
    gate_failed = False
    if phase in ("backend", "frontend"):
        coverage_file = RESULTS / (
            "coverage.json"
            if phase == "backend"
            else "coverage/frontend/coverage-summary.json"
        )
        # Refuse stale coverage when a process fails before writing its report.
        if (
            coverage_file.exists()
            and coverage_file.stat().st_mtime
            >= datetime.fromisoformat(start).timestamp()
        ):
            measured = json.loads(coverage_file.read_text(encoding="utf-8"))
            if phase == "backend":
                covered, total = (
                    measured["totals"]["covered_branches"],
                    measured["totals"]["num_branches"],
                )
            else:
                branches = measured["total"]["branches"]
                covered, total = branches["covered"], branches["total"]
            passed = total > 0 and covered / total > 0.90
            record["branch_coverage"] = {
                "covered": covered,
                "total": total,
                "percent": 100 * covered / total if total else 0,
                "required": "strictly above 90%",
                "passed": passed,
            }
            gate_failed = not passed
        else:
            gate_failed = True
            record["branch_coverage"] = {
                "passed": False,
                "reason": "No fresh coverage artifact",
            }
    record["exit_code"] = result.returncode or int(gate_failed)
    (RESULTS / "raw" / f"{phase}-command.json").write_text(
        json.dumps(record, indent=2), encoding="utf-8"
    )
    print(json.dumps(record, indent=2))
    print(log.decode("utf-8", errors="replace")[-9000:])
    return record["exit_code"]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        description="Record tests and enforce >90% branches per layer without hiding test failures."
    )
    parser.add_argument("phase", choices=[*COMMANDS, "coverage"])
    args = parser.parse_args()
    if args.phase == "coverage":
        # Run both layers even if one fails; neither can mask the other's result.
        codes = [run(phase) for phase in ("backend", "frontend")]
        return int(any(codes))
    return run(args.phase)


if __name__ == "__main__":
    sys.exit(main())
