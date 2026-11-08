# ITCS386 — k6 performance testing lab

I used Grafana k6 to test the [QuickPizza demo API](https://quickpizza.grafana.com/) for the Week 10 Software Verification and Validation lab. The main idea is to start with a simple request, add checks and performance thresholds, and then compare the five types of load tests using the same user journey.

**GitHub:** `https://github.com/earthslipz/k6-lab` (create the repository and push before submitting)

## Requirements

- Windows PowerShell, macOS, or Linux
- Grafana k6 (the lab was tested with k6 v2.2.0)
- Python 3 for the optional results helper (no packages to install)
- Git

On Windows, install k6 with:

```powershell
winget install k6 --source winget
```

Close and reopen PowerShell after installation, then check:

```powershell
k6 version
```

If the command is still missing, try reopening VS Code or install it from the [k6 installer](https://dl.k6.io/msi/k6-latest-amd64.msi).

## Running the exercises on Windows

Open PowerShell inside this `k6-lab` directory. You can copy and run the commands below in order.

### Part 0: Getting started

```powershell
k6 run 01-first-test.js
k6 run --vus 5 --duration 20s 01-first-test.js
k6 run --vus 5 --iterations 20 01-first-test.js
k6 run 04-pizza-api.js
k6 run 05-no-token.js
```

Step 0.6 compares two response-time thresholds. Check `$LASTEXITCODE` immediately after each run:

```powershell
k6 run 06-thresholds.js
$LASTEXITCODE

k6 run -e P95=300 06-thresholds.js
$LASTEXITCODE
```

For Step 0.7, the standard requirement is p95 < 1000 ms, p99 < 1500 ms, and failure rate < 1%. The second run changes **only the p95 limit** to 1 ms to demonstrate a failing threshold.

```powershell
k6 run 07-requirement.js
$LASTEXITCODE

k6 run -e REQ_P95=1 07-requirement.js
$LASTEXITCODE
```

The original bug-hunt script uses lowercase names. `explore.js` shows the names used by the API, and `08-bug-hunt.js` contains the corrected request:

```powershell
k6 run --vus 5 --duration 20s 08-bug-hunt-original.js
k6 run explore.js
k6 run --vus 5 --duration 20s 08-bug-hunt.js
```

### Part A: User journey and reports

The shared journey in `journey.js` visits the home page, reads quotes and requests a vegetarian pizza. Each load test imports the same journey so the results are easier to compare.

Create the report folder if it does not exist:

```powershell
New-Item -ItemType Directory -Force reports
```

Then run the scenarios **one at a time**:

```powershell
k6 run a1-smoke.js
k6 run --out web-dashboard=export=reports/a2-average.html a2-average.js
k6 run --out web-dashboard=export=reports/a3-stress.html a3-stress.js
k6 run --out web-dashboard=export=reports/a4-spike.html a4-spike.js
k6 run --out web-dashboard=export=reports/a5-soak.html a5-soak.js
```

The expected test shapes are:

| Test | Users | Duration and shape |
| --- | ---: | --- |
| Smoke | 1 | 30 seconds |
| Average | max 3 | 30s up, 2m hold, 30s down |
| Stress | max 5 | 30s up, 2m hold, 30s down |
| Spike | max 5 | 1 user, 5-user spike, then recovery |
| Soak | max 2 | 30s up, 10m hold, 30s down |

The four HTML reports should appear in `reports/`. If an HTML report is not generated, check the k6 version and the terminal warnings. See [Grafana's HTML report guide](https://grafana.com/docs/k6/latest/results-output/web-dashboard/).

### Optional: one script to run and save the numbers

The PowerShell helper runs the exercises sequentially, exports JSON metrics and HTML reports, and then fills the measured fields in `RESULTS.md`:

```powershell
.\run-lab.ps1 -IncludeSoak
```

This runs the full lab, including the **11-minute 2-user soak test**. If you only want the shorter runs, use `./run-lab.ps1` and run the soak separately later. On a restricted PowerShell system, open a terminal with normal script permissions or run the individual commands above. Avoid a permanent machine-wide execution policy change.

After running the helper, review `RESULTS.md` before pushing. In particular, use the spike and soak HTML graphs for the *recovery time* and *beginning versus end* discussion; those observations should come from your own run.

If you ran the scenarios manually with `--summary-export` into `reports/metrics/`, you can refresh the Markdown file with:

```powershell
python tools/build_results.py
```

## What the files are for

| File | Purpose |
| --- | --- |
| `01-first-test.js` | Single request, 5-user duration, and 20 iterations |
| `04-pizza-api.js` | Vegetarian pizza API checks |
| `05-no-token.js` | Expected 401 response |
| `06-thresholds.js` | Basic thresholds, including the P95 variable |
| `07-requirement.js` | Translate a performance requirement into thresholds |
| `08-bug-hunt-original.js` | The initial request with lowercase exclusions |
| `08-bug-hunt.js` | Fixed bug-hunt request |
| `explore.js` | Print available topping and tool names |
| `journey.js` | Shared home → quotes → recommendation flow |
| `a1-smoke.js` to `a5-soak.js` | Five load testing scenarios |
| `reports/` | HTML reports and measured metric JSON files |
| `RESULTS.md` | Recorded numbers, comparison and reflection questions |
| `run-lab.ps1` | Windows helper to run the exercise in order |

## Notes about the results

- `http_reqs` is the total request count and requests/second.
- `http_req_duration` reports response times in milliseconds, including p(95) and max.
- `http_req_failed` is the failed-request rate.
- `checks` is the proportion of checks that passed.
- A threshold can make a run exit with code `99`. That is expected in the deliberately strict examples; it does not mean k6 is broken.
- A 401 is expected in `05-no-token.js` and is treated as a successful negative test.

**QuickPizza is a public demo service.** I keep each test to at most five virtual users, and the only test longer than three minutes is the two-user soak case allowed by the lab instructions. I do not run breakpoint tests or large-load attacks on this service.

## Submit on MyCourses

1. Check that `reports/a2-average.html`, `reports/a3-stress.html`, `reports/a4-spike.html`, and `reports/a5-soak.html` exist.
2. Check that the measured values and Part B answers in `RESULTS.md` match the run.
3. Create a **public** GitHub repository named `k6-lab` under `earthslipz`, then push these files.
4. Submit **`https://github.com/earthslipz/k6-lab`** on MyCourses.

If the GitHub repository is empty, you can push your local work with:

```powershell
git init
git branch -M main
git add .
git commit -m "Add Week 10 k6 lab scripts and notes"
git remote add origin https://github.com/earthslipz/k6-lab.git
git push -u origin main
```

If `origin` already exists, use `git remote set-url origin https://github.com/earthslipz/k6-lab.git` instead of `git remote add`.
