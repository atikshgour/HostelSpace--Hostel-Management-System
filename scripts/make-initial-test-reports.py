"""US-22/23 | Regenerate reports from saved executions, never assumed outcomes."""

import json
import shutil
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "test_results"


def read(name):
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def write(name, text):
    (OUT / name).write_text(text, encoding="utf-8")


def dump(name, data):
    write(name, json.dumps(data, indent=2) + "\n")


def status(case):
    if case.find("failure") is not None or case.find("error") is not None:
        return "Failed"
    return "Not Run" if case.find("skipped") is not None else "Passed"


def percent(covered, total):
    return f"{100 * covered / total:.2f}%" if total else "N/A"


def main():
    cases = list(ET.parse(OUT / "raw/backend-junit.xml").iter("testcase"))
    backend = read("coverage.json")
    frontend = read("coverage/frontend/coverage-summary.json")
    frontend_raw = read("coverage/frontend/coverage-final.json")
    jest = read("raw/frontend-results.json")
    browser = read("raw/browser-results.json")
    commands = {
        phase: read(f"raw/{phase}-command.json")
        for phase in ("backend", "frontend", "build", "e2e", "lint")
    }
    if (OUT / "raw/coverage-export-command.json").exists():
        commands["coverage-export"] = read("raw/coverage-export-command.json")
    assert backend["meta"]["branch_coverage"] and cases and jest["numTotalTests"]
    counts = Counter(status(case) for case in cases)
    b, f = backend["totals"], frontend["total"]
    branch_counts = {
        "backend": (b["covered_branches"], b["num_branches"]),
        "frontend": (f["branches"]["covered"], f["branches"]["total"]),
    }
    branch_counts["overall"] = tuple(
        sum(pair[i] for pair in branch_counts.values()) for i in (0, 1)
    )
    summary = {
        name: {
            "covered": pair[0],
            "total": pair[1],
            "percent": 100 * pair[0] / pair[1],
            "passed": pair[0] / pair[1] > 0.90,
        }
        for name, pair in branch_counts.items()
    }
    dump("branch-coverage-summary.json", summary)
    common = f"""Generated {datetime.now(UTC).isoformat()} from recorded artifacts.
Backend execution: {commands["backend"]["started_at"]}; frontend: {commands["frontend"]["started_at"]}.
Source HEAD: `{commands["backend"].get("source_commit", "not recorded")}` plus uncommitted test/config/script changes.
Local synthetic PostgreSQL only. No production data changes, live payments, commit or push.
Each command's own timestamp/exit is preserved in [commands](raw/commands.md).
Independent human review remains pending. Coverage success does not override failing tests.
"""
    failures = []
    for case in cases:
        for tag in ("failure", "error"):
            error = case.find(tag)
            if error is not None:
                failures.append(
                    {
                        "name": case.get("name"),
                        "class": case.get("classname"),
                        "message": error.get("message"),
                        "detail": error.text,
                    }
                )
    dump("raw/observed-failures.json", failures)
    failure_text = (
        "\n".join(f"- `{item['name']}`: {item['message']}" for item in failures)
        or "None."
    )
    unit = [case for case in cases if "test_priority_unit" in case.get("classname", "")]
    expanded = [
        case for case in cases if "test_branch_workflows" in case.get("classname", "")
    ]
    original = [
        case
        for case in cases
        if "test_priority" not in case.get("classname", "")
        and "test_branch_workflows" not in case.get("classname", "")
    ]
    records = read("priority_cases.json")
    for record in records:
        case = next(c for c in cases if c.get("name") == record["api_test"])
        record["api_status"] = record["status"] = status(case)
        record["actual"] = "Assertions passed; see JUnit and source test."
        if record["id"] == "P12":
            supporting = next(
                c
                for c in cases
                if c.get("name") == "test_direct_socket_timeout_is_validation_error"
            )
            if status(supporting) != "Passed":
                record["status"] = status(supporting)
                record["actual"] = (
                    "Wrapped-timeout API workflow passes; direct socket TimeoutError escapes normalization."
                )
        if record["api_status"] == "Failed":
            record["actual"] = next(
                item["message"]
                for item in failures
                if item["name"] == record["api_test"]
            )
    dump("priority_cases.json", records)
    write(
        "raw/commands.md",
        "# Recorded commands\n\n"
        + "\n\n".join(
            f"## {phase}\n\nDirectory: `{record['cwd']}`; exit: {record['exit_code']}.\n"
            f"Started {record['started_at']}; finished {record['finished_at']}.\n\n```text\n{' '.join(record['command'])}\n```\n\n"
            f"Branch gate: {json.dumps(record.get('branch_coverage', 'not applicable'))}"
            for phase, record in commands.items()
        ),
    )
    test_rows = "\n".join(
        f"| `{case.get('classname')}.{case.get('name')}` | {status(case)} |"
        for case in cases
    )
    component_rows = "\n".join(
        f"- {assertion['fullName']}: {assertion['status']}"
        for suite in jest["testResults"]
        for assertion in suite["assertionResults"]
    )
    write(
        "unit_test_report.md",
        f"""# Unit, API and component test report

{common}
## Recorded totals

Backend: **{len(cases)} executions; {counts["Passed"]} passed, {counts["Failed"]} failed, {counts["Not Run"]} not run**.
Original regressions: {len(original)}, {sum(status(c) == "Passed" for c in original)} passed.
Supporting priority units: {len(unit)}. Priority API workflows: {len(records)}.
Added branch-focused Python executions: {len(expanded)}; {sum(status(c) == "Passed" for c in expanded)} passed.
Jest/RTL: **{jest["numTotalTests"]} executions; {jest["numPassedTests"]} passed, {jest["numFailedTests"]} failed** in {jest["numTotalTestSuites"]} suites.
Backend subtests are assertions within parent executions; do not count them again.

## What the expanded tests cover

Python: unsafe account transitions and assignments, active/legacy scope adapters,
staff directories, content edits, mess capacity and coupon reassignment, final complaint
states, attendance boundaries, malformed provider orders/captured payloads, reference
mismatches, local seed safety/idempotence, error envelopes and settings validation.
Real PostgreSQL fixtures exercise database behavior; external provider I/O is mocked.
Configuration tests use temporary files and isolated environment/module boundaries.
These are unit/API/integration tests, not all pure units.

Frontend: secure transport and pagination; shared form coercion/errors; role navigation
and keyboard focus; account/content/settings edits; leave review and filtering;
attendance location errors; deviation recording/deactivation; laundry policy/receipt/
collection; mess options, assignment and coupons; simulated/provider-adapter UI errors.
Transport/navigation are mocked in component tests. The retained unregistered legacy
LeaveWorkspace is tested with its unavailable old UI adapter mocked; this does not
claim it is an active integrated route. No implemented source was excluded for coverage.

## Observed failures

{failure_text}

The replay assertions distinguish requested retry invariants from legitimate separate
events. Payment initiation/deviation event identity needs owner policy review.
Duplicate successful callbacks and initial deviation calculations still pass.
No application behavior was changed or existing assertion skipped/weakened.

## Executed backend cases

| Executed node | Outcome |
|---|---|
{test_rows}

## Executed component cases

{component_rows}

[JUnit](raw/backend-junit.xml), [Jest JSON](raw/frontend-results.json),
[backend log](raw/backend.log), [frontend log](raw/frontend.log),
[raw failures](raw/observed-failures.json), [coverage analysis](code_branch_coverage_analysis.md).
""",
    )
    priority_rows = "\n".join(
        f"| {r['id']} | {r['title']} | {r['api_status']} | {r['status']} | {r['actual']} |"
        for r in records
    )
    details = "\n\n".join(
        f"### {r['id']} — {r['requirement']}\n\nPreconditions: {r['preconditions']}.\n\nSteps: {r['steps']}.\n\nExpected: {r['expected']}.\n\nActual: {r['actual']}"
        for r in records
    )
    write(
        "system_test_report.md",
        f"""# System, integration and browser test report

{common}
## Priority requirements

| ID | Requirement | API test | Combined requirement | Actual result |
|---|---|---|---|---|
{priority_rows}

P12 includes the supporting direct-timeout unit. Its API test alone is not sufficient.
{details}

## Browser execution

Chromium command started **{commands["e2e"]["started_at"]}**, exit {commands["e2e"]["exit_code"]}.
Recorded Playwright results: **{browser["stats"]["expected"]} passed, {browser["stats"]["unexpected"]} failed,
{browser["stats"]["skipped"]} skipped, {browser["stats"]["flaky"]} flaky**.
Journeys cover login/profile/navigation, information/study status, Director accounts,
laundry receipt/collection, leave/escalation, attendance/deviations, complaints,
mess/coupons, simulated fees and content publishing, plus privacy and health checks.
Privacy response mocks prove UI behavior only. Health smoke is not load acceptance.
Payment simulation and mocked provider tests do not establish provider acceptance.
Firefox/Edge were not run for this update. Browser runtime is not merged into Jest coverage.

## Open defects and acceptance limits

{failure_text}

Passing branch coverage does not make these failures passing. Backend suite remains
nonzero. Independent review, complete manual usability, agreed load acceptance,
external provider acceptance, staging/release and recovery rehearsal remain pending.
No commit or push was performed for this update.

[Commands](raw/commands.md), [browser JSON](raw/browser-results.json),
[browser log](raw/e2e.log), [browser HTML](raw/browser-html/index.html),
[JUnit](raw/backend-junit.xml), [failures](raw/observed-failures.json).
""",
    )
    backend_gaps, contexts, functions, rows = {}, {}, [], []
    for name, file in backend["files"].items():
        name = name.replace("\\", "/")
        backend_gaps[name] = {
            "missing_lines": file["missing_lines"],
            "missing_branches": file.get("missing_branches", []),
        }
        contexts[name] = sorted(
            {
                ctx.split("|")[0]
                for items in file.get("contexts", {}).values()
                for ctx in items
                if ctx
            }
        )
        for function, region in file.get("functions", {}).items():
            if function and region["summary"]["num_statements"]:
                functions.append(
                    {
                        "file": name,
                        "function": function,
                        "body_hit": bool(region["executed_lines"]),
                        "missing_lines": region["missing_lines"],
                    }
                )
        s = file["summary"]
        if s["num_statements"]:
            rows.append(
                f"| `{name}` | {percent(s['covered_lines'], s['num_statements'])} | {percent(s.get('covered_branches', 0), s.get('num_branches', 0))} |"
            )
    dump("coverage/backend-gaps.json", backend_gaps)
    dump("coverage/backend-test-module-map.json", contexts)
    dump("coverage/backend-function-coverage.json", functions)
    gaps = {}
    for name, file in frontend_raw.items():
        name = name.replace("\\", "/").split("/frontend/", 1)[-1]
        gaps["frontend/" + name] = {
            "uncovered_statement_locations": [
                file["statementMap"][key] for key, hits in file["s"].items() if not hits
            ],
            "untested_decisions": [
                {
                    "branch": key,
                    "arm": arm,
                    "location": file["branchMap"][key]["locations"][arm],
                }
                for key, hits in file["b"].items()
                for arm, hit in enumerate(hits)
                if not hit
            ],
            "uncovered_functions": [
                file["fnMap"][key] for key, hits in file["f"].items() if not hits
            ],
        }
    dump("coverage/frontend-gaps.json", gaps)
    branch_rows = "\n".join(
        f"| {name.title()} | {item['covered']} / {item['total']} | {item['percent']:.2f}% | {'Passed' if item['passed'] else 'Failed'} |"
        for name, item in summary.items()
    )
    write(
        "code_branch_coverage_analysis.md",
        f"""# Code and branch coverage analysis

{common}
## Branch target: strictly above 90%

| Layer | Covered / total branch opportunities | Coverage | Target |
|---|---|---|---|
{branch_rows}

Overall is the opportunity-weighted ratio `(Python covered + Istanbul covered) /
(Python total + Istanbul total)`, not an average of percentages. The tools use
different branch models, so the separate layer gates are authoritative. Both
must exceed 90%; one cannot compensate for the other.

Backend line coverage: **{percent(b["covered_lines"], b["num_statements"])}**;
frontend line coverage: **{percent(f["lines"]["covered"], f["lines"]["total"])}**.
Backend combined line/branch coverage.py summary: {b["percent_covered"]:.2f}%.
Backend remaining branches: {b["missing_branches"]}. Frontend remaining branch arms:
{f["branches"]["total"] - f["branches"]["covered"]}.

## Scope and reproducibility

Python instruments all apps/config with branch measurement; tests and generated
migrations retain their existing exclusions. Frontend instruments all {len(frontend_raw)}
implemented modules, including unimported modules at zero; only tests and instruction
placeholders retain their existing exclusions. No production code or coverage exclusions
were changed to reach this target. The denominator is {b['num_branches']} Python and {f['branches']['total']} frontend
branch opportunities in this snapshot. Failed tests also contribute coverage.

`python scripts/run-initial-tests.py coverage` runs both layers even if one fails,
records timestamps/commands/exits, rejects missing/stale coverage, and checks each
layer strictly above 90%. A failing test still makes the command fail. Default Jest
also measures the full implemented scope and enforces >90% global branch coverage.

Retained legacy scope code is tested directly; the orphan frontend LeaveWorkspace
uses mocked legacy adapters and is not claimed as a registered route. Unreachable
old role branches remain visible as gaps rather than bypassing permission checks.
Mocked provider and configuration boundaries do not exercise a live service/deployment.

## Measured Python modules

| File | Lines | Branches |
|---|---|---|
"""
        + "\n".join(rows)
        + """

## Remaining gaps and raw evidence

[Backend exact missing lines/branches](coverage/backend-gaps.json),
[frontend exact unexecuted arms/functions](coverage/frontend-gaps.json),
[Python test contexts](coverage/backend-test-module-map.json),
[Python function-body hits](coverage/backend-function-coverage.json).
Empty contexts are import/setup execution or unavailable context data, not test evidence.
Function-body hit rate is not complete path coverage.

[Python JSON](coverage.json), [XML](coverage.xml), [Python HTML](coverage/backend-html/index.html),
[Istanbul JSON](coverage/frontend/coverage-final.json),
[Jest summary](coverage/frontend/coverage-summary.json), [frontend HTML](coverage/frontend/index.html),
[LCOV](coverage/frontend/lcov.info), [branch totals](branch-coverage-summary.json),
[commands](raw/commands.md). HTML/XML/JSON are regenerated by the actual test tools.
""",
    )
    changed = [
        "backend/tests/test_branch_workflows.py",
        "frontend/jest.config.mjs",
        "frontend/jest.coverage.config.mjs",
        "frontend/test-support/fixtures.jsx",
        "frontend/src/lib/branches.test.js",
        "frontend/src/components/ui/branches.test.jsx",
        "frontend/src/features/director/branches.test.jsx",
        "frontend/src/features/mess/branches.test.jsx",
        "frontend/src/features/leave/branches.test.jsx",
        "frontend/src/features/leave/legacy-branches.test.jsx",
        "scripts/run-initial-tests.py",
        "scripts/make-initial-test-reports.py",
    ]
    dump(
        "file_manifest.json",
        {
            "source_files_created_or_modified": changed,
            "generated_artifacts": sorted(
                p.relative_to(ROOT).as_posix() for p in OUT.rglob("*") if p.is_file()
            ),
        },
    )
    # Copy only screenshots produced by this browser execution.
    started = datetime.fromisoformat(commands["e2e"]["started_at"]).timestamp()
    screenshots = OUT / "raw/screenshots"
    screenshots.mkdir(exist_ok=True)
    for source in (ROOT / "frontend/test-results/evidence").glob("*.png"):
        if source.stat().st_mtime >= started:
            shutil.copy2(source, screenshots / source.name)
    print(
        f"Reports regenerated: backend {dict(counts)}, Jest {jest['numPassedTests']}/{jest['numTotalTests']}; branch targets {summary}"
    )


if __name__ == "__main__":
    main()
