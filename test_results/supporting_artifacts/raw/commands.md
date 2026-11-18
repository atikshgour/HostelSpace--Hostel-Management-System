# Recorded commands

## backend

Directory: `backend`; exit: 0.
Started 2026-11-17T07:06:55.032939+00:00; finished 2026-11-17T07:07:37.064978+00:00.

```text
D:\HostelSpace--Hostel-Management-System\.venv\Scripts\python.exe -m pytest --tb=short -q --junitxml=../test_results/raw/backend-junit.xml --cov=apps --cov=config --cov-branch --cov-context=test --cov-report=term-missing --cov-report=xml:../test_results/coverage.xml --cov-report=json:../test_results/coverage.json --cov-report=html:../test_results/coverage/backend-html
```

Branch gate: {"covered": 315, "total": 348, "percent": 90.51724137931035, "required": "strictly above 90%", "passed": true}

## frontend

Directory: `frontend`; exit: 0.
Started 2026-11-17T07:05:49.767215+00:00; finished 2026-11-17T07:06:24.786847+00:00.

```text
npm.cmd run test:ci -- --config=jest.coverage.config.mjs --runInBand --coverageDirectory=../test_results/coverage/frontend --json --outputFile=../test_results/raw/frontend-results.json
```

Branch gate: {"covered": 843, "total": 866, "percent": 97.34411085450347, "required": "strictly above 90%", "passed": true}

## build

Directory: `frontend`; exit: 0.
Started 2026-11-17T07:05:41.919442+00:00; finished 2026-11-17T07:05:56.002401+00:00.

```text
npm.cmd run build
```

Branch gate: "not applicable"

## e2e

Directory: `frontend`; exit: 0.
Started 2026-11-17T07:09:06.490022+00:00; finished 2026-11-17T07:10:24.699611+00:00.

```text
npx.cmd playwright test --project=chromium --trace=off --reporter=list,json,html --output=../test_results/raw/browser-output
```

Branch gate: "not applicable"

## lint

Directory: `frontend`; exit: 0.
Started 2026-11-17T07:05:41.921728+00:00; finished 2026-11-17T07:06:03.623984+00:00.

```text
npm.cmd run lint
```

Branch gate: "not applicable"

## coverage-export

Directory: `backend`; exit: 0.
Started 2026-11-17T07:08:19.036429+00:00; finished 2026-11-17T07:08:21.731405+00:00.

```text
D:\HostelSpace--Hostel-Management-System\.venv\Scripts\python.exe -m coverage json --show-contexts -o ../test_results/coverage.json
```

Branch gate: "not applicable"