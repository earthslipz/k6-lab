"""Fill RESULTS.md from k6 JSON summary files (no fake measurements)."""

import json
import math
import statistics
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
METRICS = ROOT / "reports" / "metrics"
SAMPLES = ROOT / "reports" / "samples"


def read_json(path):
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        print(f"Could not read {path}: {exc}")
        return {}


def metric(summary_id, metric_name):
    data = read_json(METRICS / f"{summary_id}.json")
    return data.get("metrics", {}).get(metric_name, {}).get("values", {})


def nval(key, name):
    return metric(key, "http_req_duration").get(name)


def number(value, digits=1, suffix=""):
    if not isinstance(value, (int, float)) or not math.isfinite(value):
        return "not recorded"
    return f"{value:.{digits}f}{suffix}"


def ratio(value):
    return number(100 * value, 2, "%") if isinstance(value, (int, float)) else "not recorded"


def count(value):
    if value is None:
        return "not recorded"
    return str(round(value)) if isinstance(value, (int, float)) else str(value)


def get_exit_code(identifier, codes):
    status = codes.get(identifier)
    return f"{status}" if status is not None else "not recorded"


def row(key, label, users):
    reqs = metric(key, "http_reqs")
    duration = metric(key, "http_req_duration")
    failures = metric(key, "http_req_failed")
    checks = metric(key, "checks")
    return (f"| {key.split('-')[0].upper()} | {label} | {users} | "
            f"{number(reqs.get('rate'), 2)} | "
            f"{number(duration.get('p(95)'), 1)} | "
            f"{number(duration.get('max'), 1)} | "
            f"{ratio(failures.get('rate'))} | "
            f"{ratio(checks.get('rate'))} |")


def points(id_, metric_name):
    path = SAMPLES / f"{id_}.json"
    if not path.exists():
        return []
    result = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
            if item.get("type") != "Point" or item.get("metric") != metric_name:
                continue
            item_data = item["data"]
            stamp = datetime.fromisoformat(item_data["time"].replace("Z", "+00:00"))
            result.append((stamp, float(item_data["value"])))
        except (ValueError, TypeError, KeyError):
            continue
    return sorted(result, key=lambda obj: obj[0])


def quantile95(values):
    if not values:
        return None
    values = sorted(values)
    pos = 0.95 * (len(values) - 1)
    low = int(math.floor(pos))
    high = int(math.ceil(pos))
    return values[low] * (high - pos) + values[high] * (pos - low)


def timeslice(series, origin, start, end):
    return [v for t, v in series if start <= (t - origin).total_seconds() < end]


def trend_notes(id_, windows):
    durations = points(id_, "http_req_duration")
    failures = points(id_, "http_req_failed")
    if not durations:
        return "Time-series samples have not been recorded. Check the HTML graph after the run."
    start = durations[0][0]
    out = []
    for name, left, right in windows:
        window_values = timeslice(durations, start, left, right)
        window_failures = timeslice(failures, start, left, right)
        failrate = statistics.mean(window_failures) if window_failures else None
        out.append(f"{name}: about {number(quantile95(window_values), 1)} ms p(95) "
                   f"({len(window_values)} requests; failure rate {ratio(failrate)})")
    return "; ".join(out) + ". The time windows are approximate, based on the first sample."


def generate():
    codes = read_json(ROOT / "reports" / "exit_codes.json")
    first_duration = metric("0.1-first", "http_req_duration")
    five_users = metric("0.2-five-vus", "http_reqs")
    five_duration = metric("0.2-five-vus", "http_req_duration")
    basic = metric("0.6-normal", "http_req_duration")
    strict = metric("0.6-p95-300", "http_req_duration")
    required = metric("0.7-requirement", "http_req_duration")
    required_failures = metric("0.7-requirement", "http_req_failed")
    tight = metric("0.7-tightened", "http_req_duration")
    original = metric("0.8-original", "checks")
    fixed = metric("0.8-fixed", "checks")
    avg = nval("a2-average", "p(95)")
    stress = nval("a3-stress", "p(95)")

    if isinstance(avg, (float, int)) and isinstance(stress, (float, int)):
        relation = ("increased" if stress > avg else "decreased" if stress < avg else "was unchanged")
        comparison = (f"The overall p(95) {relation} from {number(avg)} ms at 3 users "
                      f"to {number(stress)} ms at 5 users. At these small loads this does not "
                      "tell us where QuickPizza's actual limit is.")
    else:
        comparison = ("Compare the measured overall p(95) in the A2 and A3 rows. "
                      "Five users is still a small load, so it cannot establish the server's real limit.")

    spike = trend_notes("a4-spike", [
        ("before the spike (first 30s)", 0, 30),
        ("during 5-VU peak (about 35-65s)", 35, 65),
        ("after the spike (about 70-130s)", 70, 130),
    ])
    soak = trend_notes("a5-soak", [
        ("early soak (about 30-150s)", 30, 150),
        ("late soak (about 510-630s)", 510, 630),
    ])

    text = f"""# K6 lab results

These notes are for the QuickPizza Week 10 lab. Values marked **not recorded** need an actual k6 run; they are not estimated. Response times are in milliseconds unless stated otherwise.

## Part 0

- **Step 0.1:** `http_req_duration` = {number(first_duration.get('avg'))} ms average ({number(first_duration.get('p(95)'))} ms p(95)). With one request, the other duration statistics should be the same.
- **Step 0.2:** {count(five_users.get('count'))} requests, {number(five_users.get('rate'), 2)} req/s, p(95) = {number(five_duration.get('p(95)'))} ms. The rate stays below 5 requests per second because each user waits one second after every request and also spends time waiting for the response.
- **Step 0.3:** The run requested exactly 20 total iterations across five VUs. Recorded iterations: {count(metric('0.3-iterations', 'iterations').get('count'))}.
- **Step 0.4:** Pizza checks passed: {ratio(metric('0.4-pizza', 'checks').get('rate'))}. This checks the content of the API response, not just HTTP 200.
- **Step 0.5:** Requests without a token should get 401. Checks passed: {ratio(metric('0.5-no-token', 'checks').get('rate'))}; the expected response is not treated as an HTTP failure.
- **Step 0.6:** Normal P95=1500: measured p(95) {number(basic.get('p(95)'))} ms, exit code **{get_exit_code('0.6-normal', codes)}**. P95=300: measured p(95) {number(strict.get('p(95)'))} ms, exit code **{get_exit_code('0.6-p95-300', codes)}**. The stricter rule may fail with code 99; use the observed exit code above rather than assuming it did.
- **Step 0.7:** Requirements: p(95) < 1000 ms, p(99) < 1500 ms, failure rate < 1%. Measured p(95) **{number(required.get('p(95)'))} ms**, p(99) **{number(required.get('p(99)'))} ms**, failure rate **{ratio(required_failures.get('rate'))}**, run exit code **{get_exit_code('0.7-requirement', codes)}**. I then changed the p(95) rule to 1 ms (one number) and got p(95) **{number(tight.get('p(95)'))} ms** and exit code **{get_exit_code('0.7-tightened', codes)}**.
- **Step 0.8:** Original request check pass rate: **{ratio(original.get('rate'))}**. Corrected request check pass rate: **{ratio(fixed.get('rate'))}**. The original payload uses lowercase `pepperoni` and `knife`, while the API lists `Pepperoni` and `Knife` as names. The fixed script sends the exact names. A repeated test can catch intermittent wrong recommendations that a single manual request might miss.

## Part A results

`Users` is the maximum VU count. `Req/s` is the request rate; `p(95)` and `Max` are values from `http_req_duration`; `Failed` is `http_req_failed`; `Checks` is the percentage of successful checks.

| Step | Test type | Users | Req/s | p(95) | Max | Failed | Checks |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
{row('a1-smoke','Smoke',1)}
{row('a2-average','Average load',3)}
{row('a3-stress','Stress',5)}
{row('a4-spike','Spike',5)}
{row('a5-soak','Soak',2)}

All figures should be taken from the JSON summaries of the actual tests. HTML dashboards are saved as `reports/a2-average.html` through `reports/a5-soak.html` after the four load tests finish.

## Part B — Reflection

1. The results of Steps A1 to A5 are in the table above. The main things I compared were request rate, p(95), maximum response time, failed requests and checks.

2. Even with five virtual users, I was not sending five requests every second. Each iteration contains a one-second sleep, and the HTTP request itself takes time. That is why the request rate is lower.

3. {comparison} The **operational envelope** is the range of load the system can handle while meeting its requirements. This lab only checks a small part of it because QuickPizza is a shared demo server.

4. Spike test: {spike} **After checking `reports/a4-spike.html`, write the approximate recovery time here:** [check the graph before submitting].

5. Soak test: {soak} **After checking `reports/a5-soak.html`, state whether latency/errors got worse:** [check the graph before submitting]. A longer soak test could reveal memory leaks or resources that are not cleaned up properly.

6. I used p(95) because an average can hide slow requests. If a few users experience very long delays, the average might still look fine. The 95th percentile gives a better idea of the slower experiences.

7. Our Internet connection adds latency and can vary during the test. Also, QuickPizza is shared with other users who may be sending traffic at the same time. A test on a local lab system could therefore give different numbers.

8. A large stress, spike or breakpoint test could slow down or crash a system other people are using. Testing a public site with hundreds of users without permission is not appropriate. That is why I stayed within the five-user limit.

9. Vague requirement: *The chat app should load messages quickly.* A testable version would be: *With three concurrent users for 60 seconds, 95% of message-list requests should finish in under 800 ms, 99% in under 1500 ms, and fewer than 1% should fail.* In k6 I would use these thresholds:

   ```javascript
   thresholds: {{
     http_req_duration: ['p(95)<800', 'p(99)<1500'],
     http_req_failed: ['rate<0.01'],
   }}
   ```

   This is an example requirement, **not a measurement of a real chat app**.

## Final check before submitting

- [ ] Check the actual outcome of the thresholds in Steps 0.6 and 0.7.
- [ ] Read the spike and soak graphs and replace the two bracketed notes in Part B.
- [ ] Confirm that the four Part A HTML files exist.
- [ ] Push the latest `RESULTS.md`, scripts and HTML reports to GitHub.
"""
    (ROOT / "RESULTS.md").write_text(text, encoding="utf-8")
    print(f"Wrote {ROOT / 'RESULTS.md'}")


if __name__ == "__main__":
    generate()
