# Recorded test/build commands

Working directory `backend`; exit `1`:
```text
D:\HostelSpace--Hostel-Management-System\.venv\Scripts\python.exe -m pytest --tb=short -q --junitxml=../test_results/raw/backend-junit.xml --cov=apps --cov=config --cov-branch --cov-context=test --cov-report=term-missing --cov-report=xml:../test_results/coverage.xml --cov-report=json:../test_results/coverage.json --cov-report=html:../test_results/coverage/backend-html
```
Started 2026-11-16T18:15:58.902578+00:00; finished 2026-11-16T18:16:32.234826+00:00.

Working directory `frontend`; exit `0`:
```text
npm.cmd run test:ci -- --config=jest.coverage.config.mjs --runInBand --coverageDirectory=../test_results/coverage/frontend --json --outputFile=../test_results/raw/frontend-results.json
```
Started 2026-11-16T18:16:09.214282+00:00; finished 2026-11-16T18:16:33.521708+00:00.

Working directory `frontend`; exit `0`:
```text
npm.cmd run build
```
Started 2026-11-16T18:19:56.331961+00:00; finished 2026-11-16T18:20:10.136025+00:00.

Working directory `frontend`; exit `0`:
```text
npx.cmd playwright test --project=chromium --reporter=list,json,html --output=../test_results/raw/browser-output
```
Started 2026-11-16T18:18:00.588822+00:00; finished 2026-11-16T18:19:09.661561+00:00.

Working directory `frontend`; exit `0`:
```text
npm.cmd run lint
```
Started 2026-11-16T18:22:58.140540+00:00; finished 2026-11-16T18:23:12.523006+00:00.

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
