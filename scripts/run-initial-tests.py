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
PYTHON = str(ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python"))
NPM = "npm.cmd" if os.name == "nt" else "npm"
NPX = "npx.cmd" if os.name == "nt" else "npx"

COMMANDS = {
    "backend": ("backend", [PYTHON, "-m", "pytest", "--tb=short", "-q",
        "--junitxml=../test_results/raw/backend-junit.xml", "--cov=apps", "--cov=config",
        "--cov-branch", "--cov-context=test", "--cov-report=term-missing",
        "--cov-report=xml:../test_results/coverage.xml",
        "--cov-report=json:../test_results/coverage.json",
        "--cov-report=html:../test_results/coverage/backend-html"]),
    "frontend": ("frontend", [NPM, "run", "test:ci", "--", "--config=jest.coverage.config.mjs",
        "--runInBand", "--coverageDirectory=../test_results/coverage/frontend", "--json",
        "--outputFile=../test_results/raw/frontend-results.json"]),
    "build": ("frontend", [NPM, "run", "build"]),
    "lint": ("frontend", [NPM, "run", "lint"]),
    "e2e": ("frontend", [NPX, "playwright", "test", "--project=chromium",
        "--reporter=list,json,html", "--output=../test_results/raw/browser-output"]),
}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=COMMANDS)
    args = parser.parse_args()
    directory, command = COMMANDS[args.phase]
    (RESULTS / "raw").mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["NEXT_TELEMETRY_DISABLED"] = "1"
    if args.phase == "e2e":
        env["PLAYWRIGHT_JSON_OUTPUT_FILE"] = str(RESULTS / "raw" / "browser-results.json")
        env["PLAYWRIGHT_HTML_OUTPUT_DIR"] = str(RESULTS / "raw" / "browser-html")
        env["PLAYWRIGHT_HTML_OPEN"] = "never"
    start = datetime.now(UTC).isoformat()
    result = subprocess.run(command, cwd=ROOT / directory, env=env, capture_output=True, check=False)
    log = result.stdout + b"\n" + result.stderr
    (RESULTS / "raw" / f"{args.phase}.log").write_bytes(log)
    record = {"phase":args.phase, "cwd":directory, "command":command,
              "started_at":start, "finished_at":datetime.now(UTC).isoformat(),
              "exit_code":result.returncode}
    (RESULTS / "raw" / f"{args.phase}-command.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(json.dumps(record, indent=2))
    print(log.decode("utf-8", errors="replace")[-9000:])
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
