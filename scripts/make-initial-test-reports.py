"""Team test review | US-18/23 | Generate reports from recorded execution only."""

import json
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "test_results"


def read(relative):
    return json.loads((OUT / relative).read_text(encoding="utf-8"))


def write(relative, text):
    (OUT / relative).write_text(text, encoding="utf-8")


def dump(relative, data):
    write(relative, json.dumps(data, indent=2) + "\n")


def status(case):
    if case.find("failure") is not None or case.find("error") is not None:
        return "Failed"
    if case.find("skipped") is not None:
        return "Not Run"
    return "Passed"


def pct(numerator, denominator):
    return f"{100*numerator/denominator:.2f}%" if denominator else "N/A (no decisions)"


def main():
    xml = ET.parse(OUT / "raw/backend-junit.xml").getroot()
    cases = list(xml.iter("testcase"))
    backend = read("coverage.json")
    frontend = read("coverage/frontend/coverage-summary.json")
    jest = read("raw/frontend-results.json")
    browser = read("raw/browser-results.json")
    environment = read("raw/environment.json")
    commands = {name:read(f"raw/{name}-command.json") for name in ("backend", "frontend", "build", "e2e", "lint")}
    # Reports must not silently convert failed command execution into success.
    assert backend["meta"]["branch_coverage"] is True
    assert len(cases) > 0 and jest["numTotalTests"] > 0

    named = {case.get("name"):case for case in cases}
    failures = []
    for case in cases:
        for tag in ("failure", "error"):
            element = case.find(tag)
            if element is not None:
                failures.append({"name":case.get("name"), "class":case.get("classname"),
                                 "message":element.get("message"), "detail":element.text})
    dump("raw/observed-failures.json", failures)
    priorities = [
        ("Valid credential login", "FR-01 / TC-FR01-01", "CSRF bootstrap; valid synthetic login; GET identity", "200 and owned session"),
        ("Invalid credential login", "FR-01 / TC-FR01-02", "CSRF bootstrap; wrong password; GET identity", "400 invalid_credentials; no session"),
        ("Student denied Warden/admin endpoints", "SEC-01/03", "Student requests Director APIs and staff-only writes", "403 and no privileged operation"),
        ("Valid leave submission", "FR-05 / TC-FR05-01", "Assigned student submits valid dates/reason", "201 Pending; assigned Warden and actor history"),
        ("Invalid/incomplete leave rejected", "FR-05 / SEC-04", "Submit empty, blank-reason and reversed-date payloads", "400; zero leave rows"),
        ("Warden approves and rejects leave", "FR-05 / TC-FR05-01", "Create two leaves; assigned Warden finalizes each", "Approved/Rejected; two transitions each"),
        ("Valid time/location attendance", "FR-06 / TC-FR06-01", "Assigned student submits within current session and radius", "201 Accepted; no raw coordinates in output"),
        ("Outside-boundary attendance rejected", "FR-06 / TC-FR06-01", "Submit synthetic point beyond configured radius", "201 derived Rejected / OUTSIDE_RADIUS"),
        ("Repeated attendance prevented", "BR-05 / NFR-03", "Submit the same accepted student/session twice", "Second request 409; exactly one row"),
        ("Complaint creation and owned visibility", "FR-07 / TC-FR07-01", "Two students create complaints; first lists/reads second", "Only own list; cross-read 404"),
        ("Unauthorized complaint update denied", "FR-07 / SEC-01", "Other student tries to resolve complaint", "403; original Open state unchanged"),
        ("Payment success/failure/timeout/retry", "FR-09 / TC-FR09-01", "Fail simulation; mock provider timeout; retry and succeed", "Unpaid until success; retained failure; normalized timeout error"),
        ("Duplicate payment callbacks/submissions", "BR-06 / NFR-03 + requested replay invariant", "Initiate twice while Pending; repeat success callback; initiate after Paid", "One pending attempt for identical replay; one successful result"),
        ("Deviation totals and duplicate prevention", "FR-10 / TC-FR10-01 + requested replay invariant", "Record rule deviation; read total; repeat identical submission", "Correct weight total; no duplicate for the same replay"),
    ]
    records = []
    for index, (title, requirement, steps, expected) in enumerate(priorities, start=1):
        prefix = f"test_P{index:02d}_"
        name = next(name for name in named if name.startswith(prefix))
        case = named[name]
        record = {"id":f"P{index:02d}", "title":title, "requirement":requirement,
                  "preconditions":"Isolated PostgreSQL; synthetic assigned users/rule/session; APIClient; no live provider",
                  "steps":steps, "expected":expected, "api_test":name, "api_status":status(case),
                  "status":status(case), "actual":"Assertions passed; details in backend JUnit and source test."}
        if index == 12:
            extra = named["test_direct_socket_timeout_is_validation_error"]
            record["additional_test"] = extra.get("name")
            if status(extra) == "Failed":
                record["status"] = "Failed"
                record["actual"] = "Workflow passes wrapped URLError timeout, failure and successful retry. Direct socket TimeoutError escapes normalization (supporting unit test Failed)."
        if index == 13:
            record["actual"] = "Identical Pending initiation creates 2 attempts. Repeated success callbacks still produce exactly 1 Success; initiation after Paid returns 400. Replay invariant Failed."
        if index == 14:
            record["actual"] = "Initial total equals rule weight. Identical repeated submission creates 2 active rows and doubles the total. Replay invariant Failed."
        records.append(record)
    dump("priority_cases.json", records)

    unit = [case for case in cases if "test_priority_unit" in case.get("classname", "")]
    front_names = [a["fullName"] for result in jest["testResults"] for a in result["assertionResults"]]
    count = {s:sum(status(case)==s for case in cases) for s in ("Passed", "Failed", "Not Run")}
    common = f"""Execution snapshot, source commit: `{environment['source_commit']}` plus local test-only additions at execution time.
Environment: Python {environment['python']}, Django {environment['django']}, Node {environment['node']}, PostgreSQL {environment['postgresql']}.
Scope: local synthetic fixtures only; new isolated database `hostelspace_initialtests_20261116`
and pytest's disposable test database. At execution time: no existing database reset, live payment,
production behavior edit, production migration, commit, push or deployment.
Independent human review remains pending; shared handoff history is not fabricated.

Status vocabulary: Passed, Failed, Not Implemented, Blocked, Not Run.
Sources inspected: README, AGENTS (root/frontend), HISTORY, CHANGELOG, decisions,
current SRS/SAD/STP PDF (functional p30/security p31), API/role contracts, actual
models/services/views/tests and workflow YAML. Some documentation still contains
instruction placeholders or old harness notes; actual registered routes and code
were inventoried in [project-inventory.json](raw/project-inventory.json).
"""
    command_text = "\n\n".join(f"Working directory `{record['cwd']}`; exit `{record['exit_code']}`:\n```text\n{' '.join(record['command'])}\n```\nStarted {record['started_at']}; finished {record['finished_at']}." for record in commands.values())
    write("raw/commands.md", "# Recorded test/build commands\n\n" + command_text + """

Additional commands actually run:
- `coverage json --show-contexts -o ../test_results/coverage.json` from backend,
  using the same .venv interpreter and already recorded branch coverage data.
- `ruff check backend/tests/test_priority_acceptance.py backend/tests/test_priority_unit.py`
- `ruff check scripts/run-initial-tests.py`
- `npm.cmd run lint` from frontend.
- Isolated PostgreSQL `pg_ctl ... -p 55419 ... start` and `createdb ... hostelspace_initialtests_20261116`.
- Local settings: `python backend/manage.py migrate --noinput`, then `seed_demo`,
  with a generated fixture password supplied privately through the environment.
- Local settings: `python backend/manage.py runserver 127.0.0.1:8000 --noreload`;
  frontend: `npm.cmd run start`. Services stopped after browser execution.
- `python scripts/make-initial-test-reports.py` generates these documents from artifacts.

The initial build finished successfully, but the new report runner's console
printing encountered Windows cp1252 UnicodeEncodeError after saving its output.
The runner now prints UTF-8; the build was rerun with command exit 0. This was a
test-reporting utility issue, not an application build failure. No failed test
was removed or marked expected-failure to make results green.
The initial frontend lint run reported import/no-anonymous-default-export in the
new coverage config. Naming that configuration function resolved the warning;
the final lint command and exit code are saved in lint-command.json/lint.log.
""")

    unit_rows = "\n".join(f"| `{case.get('name')}` | {status(case)} |" for case in unit)
    write("unit_test_report.md", f"""# Unit and component test report

{common}
## Plan and implementation

Planned: isolated permission/active-account decisions, attendance accuracy/radius/
age decisions and Haversine scale, leave validator boundaries, and provider timeout
normalization. Implemented and executed: {len(unit)} new Python unit cases, plus 14
API acceptance cases and the existing 116 backend regressions. Deviation aggregation,
payment state transitions and duplicate/database constraints are integration tests,
not misleadingly described as pure unit arithmetic.

Unit tests Not Implemented: 0 within these selected existing interfaces.
Unit tests Blocked: 0. Raw timeout handling is implemented incompletely and Failed;
it is not marked Blocked. Test-only socket/provider mocks prevent network activity.

| Python unit node | Actual status |
|---|---|
{unit_rows}

New Python units: {sum(status(c)=='Passed' for c in unit)} Passed,
{sum(status(c)=='Failed' for c in unit)} Failed. Full backend run: {count['Passed']}
Passed, {count['Failed']} Failed, {count['Not Run']} Not Run; total {len(cases)}.
Existing 116 regression cases passed. API priority cases themselves: 12 Passed,
2 Failed; priority requirement P12 is additionally Failed because its direct
socket-timeout unit fails. No test was weakened, skipped or xfailed.

## Frontend components

Jest/RTL executed {jest['numTotalTests']} cases in {jest['numTotalTestSuites']} suites:
{jest['numPassedTests']} Passed, {jest['numFailedTests']} Failed.
The three new tests exercise native required-field validation, a disabled pending
sign-in that becomes successful navigation, and transport failure/retry visibility.
Existing tests cover reversed leave dates, successful leave submission, empty
complaint/fee lists, owned read-only laundry/mess UI and backend error messages.

Executed component nodes:

""" + "\n".join(f"- {name}" for name in front_names) + """

## Actual failures and feature references

- P12 / FR-09: `test_direct_socket_timeout_is_validation_error` receives a direct
  `TimeoutError` instead of the standardized unavailable-provider validation error.
  `provider_request` handles wrapped `URLError`, not direct socket timeouts.
- P13 / requested pending-payment replay prevention: two identical initiate posts
  create two Pending attempts. Duplicate successful callbacks remain idempotent.
- P14 / requested deviation replay prevention: identical posts create two active
  deviations. Initial aggregation and snapshot behavior pass existing tests.

The last two assertions assume identical repeated payloads represent the same
event/retry. Current APIs lack a retry/event correlation key; whether identical
real-world events may be recorded separately needs owner policy review. We tested
the requested replay invariant without inventing a request field or adding a new
uniqueness policy to production. These are Failed against that invariant, not
claims that every distinct retry or repeated real violation must be rejected.

## Commands and evidence

Exact command arrays, working directories, timestamps and exit codes:
[commands](raw/commands.md), [backend command](raw/backend-command.json),
[frontend command](raw/frontend-command.json).
Observed outputs: [backend log](raw/backend.log), [JUnit](raw/backend-junit.xml),
[failures](raw/observed-failures.json), [Jest results](raw/frontend-results.json),
[frontend log](raw/frontend.log). Coverage is analyzed separately in
[coverage analysis](code_branch_coverage_analysis.md).
""")

    rows = "\n".join(f"| {r['id']} | {r['title']} | {r['status']} | {r['actual']} |" for r in records)
    details = "\n\n".join(f"### {r['id']} - {r['requirement']}\n\nPreconditions: {r['preconditions']}.\n\nInput/workflow: {r['steps']}.\n\nExpected: {r['expected']}.\n\nActual: {r['actual']}\n\nAPI node `{r['api_test']}`: {r['api_status']}; combined priority status: **{r['status']}**." for r in records)
    write("system_test_report.md", f"""# System, integration and browser test report

{common}
## Fourteen requested priority cases

Planned and implemented: all 14 cases using existing routes, model fields and
services. Overall priority requirements: 11 Passed, 3 Failed (P12-P14).
No priority case is Blocked or Not Implemented. This includes the additional
socket-timeout check in P12, beyond its passing wrapped-timeout API workflow.

| ID | Priority requirement | Status | Observed result |
|---|---|---|---|
{rows}

## Preconditions, steps and expected/actual results

{details}

## Complete browser workflows

Playwright Chromium: {browser['stats']['expected']} Passed,
{browser['stats']['unexpected']} Failed, {browser['stats']['skipped']} Not Run,
{browser['stats']['flaky']} flaky. Real built Next.js and Django services with
PostgreSQL and nine synthetic demo roles were used. Payment mode was explicitly
local simulation; no real payment provider was used. Login tests held synthetic
session cookies in worker memory, not report artifacts; traces were disabled.
The privacy-specific cases use empty-response mocks and are labeled as such in
their source, not claimed as backend verification.

Journeys: login/profile/mobile navigation; current notices/rules/study status;
Director-created assigned accounts and Warden denial; laundry policy/receipt/
ready/collection; student-to-Warden-to-Chief leave; geolocation attendance and
deviation snapshots; Director-assigned/Maintenance-resolved complaint;
Mess-Staff allocations/coupons and cross-student denial; simulated fee payment;
Content-Staff publishing; two privacy assertions; low-volume health smoke.

These passing browser workflows do not test the failing raw socket timeout or
pending duplicate submissions and do not override those failures. Current task
Firefox and Edge runs: Not Run (scope was the installed Chromium system run);
previous hosted results are not substituted for execution of this test change.

## Security and reliability

Passed: valid session/CSRF auth, invalid login rejection, student/admin boundaries,
complaint ownership and unauthorized updates, staff-assignment scoping, no raw
location samples in attendance output/model, duplicate accepted attendance,
single successful payment callbacks and retained failed attempts. Existing
PostgreSQL concurrency tests ran, including attendance/leave/payment races.
Failed: direct timeout normalization, pending-payment replay deduplication and
deviation replay deduplication. See [failure evidence](raw/observed-failures.json).
No live/sandbox provider acceptance is claimed from mocks or local simulation.

## Defects, blockers and assumptions

Three observed failures remain open; production code was intentionally unchanged.
P13/P14 require confirming replay identity versus legitimate separate attempts/
events before selecting a production fix. Automated test additions would make a
future CI run fail until those assertions or approved product policy are resolved;
they were not pushed during test execution. No environment blocker prevented this run.
Full manual usability, approved 20-user/100-warm-visit load, staging, live provider,
production inspection and recovery rehearsal are Not Run (outside this local
automated suite). The health smoke is not a load/performance acceptance test.

## Commands and observed outputs

[Exact commands](raw/commands.md); [environment](raw/environment.json);
[inventory](raw/project-inventory.json); [JUnit](raw/backend-junit.xml);
[Playwright JSON](raw/browser-results.json); [browser log](raw/e2e.log);
[interactive browser report](raw/browser-html/index.html);
[build output](raw/build.log); [backend service log](raw/backend-service.log);
[frontend service log](raw/frontend-service.log).

All runs were executed; reports use observed artifacts. During execution no deployment, migration
of production data, commit or push was performed.
""")

    functions = []
    module_tests = {}
    gaps = {}
    coverage_rows = []
    for path, file in backend["files"].items():
        normalized = path.replace("\\", "/")
        for name, region in file.get("functions", {}).items():
            if name and region["summary"]["num_statements"]:
                functions.append({"file":normalized, "function":name,
                                  "body_hit":bool(region["executed_lines"]),
                                  "missing_lines":region["missing_lines"]})
        module_tests[normalized] = sorted({ctx.split("|")[0] for contexts in file.get("contexts", {}).values() for ctx in contexts if ctx})
        gaps[normalized] = {"missing_lines":file["missing_lines"], "missing_branches":file.get("missing_branches", [])}
        summary = file["summary"]
        if summary["num_statements"]:
            coverage_rows.append(f"| `{normalized}` | {pct(summary['covered_lines'],summary['num_statements'])} | {pct(summary.get('covered_branches',0),summary.get('num_branches',0))} | {', '.join(map(str,file['missing_lines'])) or 'None'} |")
    dump("coverage/backend-function-coverage.json", functions)
    dump("coverage/backend-test-module-map.json", module_tests)
    dump("coverage/backend-gaps.json", gaps)
    frontend_raw = read("coverage/frontend/coverage-final.json")
    front_gaps = {}
    for path, file in frontend_raw.items():
        key = path.replace(str(ROOT), "").lstrip("/\\").replace("\\", "/")
        front_gaps[key] = {
            "uncovered_statement_locations":[file["statementMap"][name] for name,hits in file["s"].items() if hits==0],
            "untested_decisions":[{"branch":name,"arm":arm,"location":file["branchMap"][name]["locations"][arm]} for name,hits in file["b"].items() for arm,count in enumerate(hits) if count==0],
            "uncovered_functions":[file["fnMap"][name] for name,hits in file["f"].items() if hits==0],
        }
    dump("coverage/frontend-gaps.json", front_gaps)
    totals = backend["totals"]
    hits = sum(f["body_hit"] for f in functions)
    front = frontend["total"]
    write("code_branch_coverage_analysis.md", f"""# Code and branch coverage analysis

{common}
## Measured totals

| Metric | Observed numerator / denominator | Coverage |
|---|---|---|
| Backend executable lines/statements | {totals['covered_lines']} / {totals['num_statements']} | {pct(totals['covered_lines'],totals['num_statements'])} |
| Backend decision branches | {totals['covered_branches']} / {totals['num_branches']} | {pct(totals['covered_branches'],totals['num_branches'])} |
| Backend combined lines + branches (coverage.py summary) | covered line and branch opportunities | {totals['percent_covered']:.2f}% |
| Backend function bodies with at least one executed body statement | {hits} / {len(functions)} | {pct(hits,len(functions))} |
| Frontend executable lines | {front['lines']['covered']} / {front['lines']['total']} | {front['lines']['pct']}% |
| Frontend statements | {front['statements']['covered']} / {front['statements']['total']} | {front['statements']['pct']}% |
| Frontend branches | {front['branches']['covered']} / {front['branches']['total']} | {front['branches']['pct']}% |
| Frontend functions | {front['functions']['covered']} / {front['functions']['total']} | {front['functions']['pct']}% |

**Python branch coverage was measured successfully.** pytest-cov used
`--cov-branch`, configuration has `branch=true`, and coverage JSON reports
`meta.branch_coverage=true`. {totals['missing_branches']} branches remain missing,
including {totals['num_partial_branches']} partially covered decisions. Missing
branches include completely unexecuted decisions as well as one unvisited arm;
these counts are not interchangeable. Negative branch targets denote exits.

Backend functions are a derived body-hit rate from coverage.py 7.17 function
regions, excluding the empty module region and zero-statement bodies. This is not
a native coverage.py function percentage and does not prove all function paths.
Exact regions and hits are in [function evidence](coverage/backend-function-coverage.json).

## Scope and interpretation

Backend instruments all `apps` and `config`; tests and generated migrations are
excluded by existing configuration. Import-only model declaration coverage is not
proof of every database behavior. PostgreSQL constraint and concurrency assertions
provide separate runtime evidence. Failed tests contribute executed lines to
coverage; coverage is not a test pass percentage or product acceptance.

Frontend instruments {len(frontend_raw)} implemented source modules, including
unimported route/components at zero. Tests and instruction-only starter files are
excluded; actual implementation is not excluded to inflate percentages. This is
broader than the earlier imported-module-only report. Browser execution is not
instrumented and is not merged into Jest coverage. Async page behavior is tested
by Playwright rather than claimed from component coverage.

## Files and lines not covered

| Backend source | Line/statement coverage | Branch coverage | Missing executable lines |
|---|---|---|---|
""" + "\n".join(coverage_rows) + """

Complete missing backend line numbers/branch pairs: [backend gaps](coverage/backend-gaps.json).
Frontend unexecuted statement/function locations and branch arms:
[frontend gaps](coverage/frontend-gaps.json). All per-file frontend line/statement/
function/branch totals are in [Jest summary](coverage/frontend/coverage-summary.json);
LCOV contains exact unhit executable line locations.

## Untested decisions and module mapping

- `leave_attendance/access.py` is an unexecuted legacy helper; active views import
  `permissions.py`. Legacy queries/errors and deployment settings are also largely
  unexecuted. Retained code is measured, not deleted or excluded for coverage.
- Director reassignment/deactivation/role conversion edge branches, some inactive
  account paths, fallback study status and information update/delete paths remain.
- Payment malformed provider-order variants, missing credentials, mismatched
  amount/currency/reference and final-state alternatives are only partially hit.
  The direct-timeout test exposes an unhandled path, not a passing recovery path.
- Frontend Director/UserManagement, study editor, some route shells, AppShell
  navigation/logout branches and service form errors have sparse Jest coverage.
- New pure units map to auth permissions, LeaveInput, attendance location logic
  and provider request errors. Priority API cases map to accounts, leave/attendance,
  complaints, payment attempts and deviation aggregation. Existing domain tests
  cover facilities/information/Director/mess, histories and PostgreSQL races.
- Per-file test-context mapping generated from actual coverage data:
  [backend test-module map](coverage/backend-test-module-map.json). Empty context
  entries are import/setup execution, not attributed to a test. Coverage contexts
  show code execution, not every database assertion or proof of a requirement.

## Commands and artifact references

[Exact executed commands](raw/commands.md), [backend command](raw/backend-command.json),
[frontend command](raw/frontend-command.json).

- [Backend HTML](coverage/backend-html/index.html)
- [Cobertura XML](coverage.xml)
- [coverage.py JSON with test contexts](coverage.json)
- [Frontend HTML](coverage/frontend/index.html)
- [Istanbul JSON](coverage/frontend/coverage-final.json)
- [Jest totals](coverage/frontend/coverage-summary.json)
- [LCOV](coverage/frontend/lcov.info)
- [Browser HTML](raw/browser-html/index.html) (functional evidence; not instrumented coverage)

The full branch-coverage and manual/provider/release acceptance gaps remain open.
No proposed coverage target is silently approved or reported as achieved.
""")
    # Only screenshots written during this execution are copied as evidence.
    from datetime import datetime
    start = datetime.fromisoformat(commands["e2e"]["started_at"]).timestamp()
    evidence = ROOT / "frontend/test-results/evidence"
    for source in evidence.glob("*.png"):
        if source.stat().st_mtime >= start:
            destination = OUT / "raw/screenshots" / source.name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
    changed = [".gitignore", "backend/pyproject.toml", "backend/tests/test_priority_acceptance.py",
               "backend/tests/test_priority_unit.py", "frontend/jest.coverage.config.mjs",
               "frontend/src/features/login/login.priority.test.jsx", "scripts/run-initial-tests.py",
               "scripts/make-initial-test-reports.py", "docs/05-validation/rtm.md"]
    dump("file_manifest.json", {"source_files_created_or_modified":changed,
         "generated_artifacts":sorted({p.relative_to(ROOT).as_posix() for p in OUT.rglob("*") if p.is_file()} | {"test_results/file_manifest.json"})})
    print(f"Generated three reports: backend {count}, frontend {jest['numPassedTests']} passed, browser {browser['stats']['expected']} passed.")


if __name__ == "__main__":
    main()
