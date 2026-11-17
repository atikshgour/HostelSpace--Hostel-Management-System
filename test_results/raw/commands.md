# Recorded commands

## backend

Directory: `backend`; exit: 1.
Started 2026-11-17T06:49:25.602301+00:00; finished 2026-11-17T06:50:01.960724+00:00.

```text
D:\HostelSpace--Hostel-Management-System\.venv\Scripts\python.exe -m pytest --tb=short -q --junitxml=../test_results/raw/backend-junit.xml --cov=apps --cov=config --cov-branch --cov-context=test --cov-report=term-missing --cov-report=xml:../test_results/coverage.xml --cov-report=json:../test_results/coverage.json --cov-report=html:../test_results/coverage/backend-html
```

Branch gate: {"covered": 309, "total": 340, "percent": 90.88235294117646, "required": "strictly above 90%", "passed": true}

## frontend

Directory: `frontend`; exit: 0.
Started 2026-11-17T06:50:01.985933+00:00; finished 2026-11-17T06:50:36.473510+00:00.

```text
npm.cmd run test:ci -- --config=jest.coverage.config.mjs --runInBand --coverageDirectory=../test_results/coverage/frontend --json --outputFile=../test_results/raw/frontend-results.json
```

Branch gate: {"covered": 842, "total": 864, "percent": 97.45370370370371, "required": "strictly above 90%", "passed": true}

## build

Directory: `frontend`; exit: 0.
Started 2026-11-17T06:49:36.559840+00:00; finished 2026-11-17T06:49:53.277440+00:00.

```text
npm.cmd run build
```

Branch gate: "not applicable"

## e2e

Directory: `frontend`; exit: 0.
Started 2026-11-17T06:52:53.802596+00:00; finished 2026-11-17T06:54:18.989855+00:00.

```text
npx.cmd playwright test --project=chromium --reporter=list,json,html --output=../test_results/raw/browser-output
```

Branch gate: "not applicable"

## lint

Directory: `frontend`; exit: 0.
Started 2026-11-17T06:53:04.772505+00:00; finished 2026-11-17T06:53:24.676226+00:00.

```text
npm.cmd run lint
```

Branch gate: "not applicable"

## coverage-export

Directory: `backend`; exit: 0.
Started 2026-11-17T06:53:58.562272+00:00; finished 2026-11-17T06:54:01.726171+00:00.

```text
D:\HostelSpace--Hostel-Management-System\.venv\Scripts\python.exe -m coverage json --show-contexts -o ../test_results/coverage.json
```

Branch gate: "not applicable"