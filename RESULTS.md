# K6 lab results

These notes are for the QuickPizza Week 10 lab. Values marked **not recorded** need an actual k6 run; they are not estimated. Response times are in milliseconds unless stated otherwise.

## Part 0

- **Step 0.1:** `http_req_duration` = not recorded ms average (not recorded ms p(95)). With one request, the other duration statistics should be the same.
- **Step 0.2:** not recorded requests, not recorded req/s, p(95) = not recorded ms. The rate stays below 5 requests per second because each user waits one second after every request and also spends time waiting for the response.
- **Step 0.3:** The run requested exactly 20 total iterations across five VUs. Recorded iterations: not recorded.
- **Step 0.4:** Pizza checks passed: not recorded. This checks the content of the API response, not just HTTP 200.
- **Step 0.5:** Requests without a token should get 401. Checks passed: not recorded; the expected response is not treated as an HTTP failure.
- **Step 0.6:** Normal P95=1500: measured p(95) not recorded ms, exit code **not recorded**. P95=300: measured p(95) not recorded ms, exit code **not recorded**. The stricter rule may fail with code 99; use the observed exit code above rather than assuming it did.
- **Step 0.7:** Requirements: p(95) < 1000 ms, p(99) < 1500 ms, failure rate < 1%. Measured p(95) **not recorded ms**, p(99) **not recorded ms**, failure rate **not recorded**, run exit code **not recorded**. I then changed the p(95) rule to 1 ms (one number) and got p(95) **not recorded ms** and exit code **not recorded**.
- **Step 0.8:** Original request check pass rate: **not recorded**. Corrected request check pass rate: **not recorded**. The original payload uses lowercase `pepperoni` and `knife`, while the API lists `Pepperoni` and `Knife` as names. The fixed script sends the exact names. A repeated test can catch intermittent wrong recommendations that a single manual request might miss.

## Part A results

`Users` is the maximum VU count. `Req/s` is the request rate; `p(95)` and `Max` are values from `http_req_duration`; `Failed` is `http_req_failed`; `Checks` is the percentage of successful checks.

| Step | Test type | Users | Req/s | p(95) | Max | Failed | Checks |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A1 | Smoke | 1 | not recorded | not recorded | not recorded | not recorded | not recorded |
| A2 | Average load | 3 | not recorded | not recorded | not recorded | not recorded | not recorded |
| A3 | Stress | 5 | not recorded | not recorded | not recorded | not recorded | not recorded |
| A4 | Spike | 5 | not recorded | not recorded | not recorded | not recorded | not recorded |
| A5 | Soak | 2 | not recorded | not recorded | not recorded | not recorded | not recorded |

All figures should be taken from the JSON summaries of the actual tests. HTML dashboards are saved as `reports/a2-average.html` through `reports/a5-soak.html` after the four load tests finish.

## Part B — Reflection

1. The results of Steps A1 to A5 are in the table above. The main things I compared were request rate, p(95), maximum response time, failed requests and checks.

2. Even with five virtual users, I was not sending five requests every second. Each iteration contains a one-second sleep, and the HTTP request itself takes time. That is why the request rate is lower.

3. Compare the measured overall p(95) in the A2 and A3 rows. Five users is still a small load, so it cannot establish the server's real limit. The **operational envelope** is the range of load the system can handle while meeting its requirements. This lab only checks a small part of it because QuickPizza is a shared demo server.

4. Spike test: Time-series samples have not been recorded. Check the HTML graph after the run. **After checking `reports/a4-spike.html`, write the approximate recovery time here:** [check the graph before submitting].

5. Soak test: Time-series samples have not been recorded. Check the HTML graph after the run. **After checking `reports/a5-soak.html`, state whether latency/errors got worse:** [check the graph before submitting]. A longer soak test could reveal memory leaks or resources that are not cleaned up properly.

6. I used p(95) because an average can hide slow requests. If a few users experience very long delays, the average might still look fine. The 95th percentile gives a better idea of the slower experiences.

7. Our Internet connection adds latency and can vary during the test. Also, QuickPizza is shared with other users who may be sending traffic at the same time. A test on a local lab system could therefore give different numbers.

8. A large stress, spike or breakpoint test could slow down or crash a system other people are using. Testing a public site with hundreds of users without permission is not appropriate. That is why I stayed within the five-user limit.

9. Vague requirement: *The chat app should load messages quickly.* A testable version would be: *With three concurrent users for 60 seconds, 95% of message-list requests should finish in under 800 ms, 99% in under 1500 ms, and fewer than 1% should fail.* In k6 I would use these thresholds:

   ```javascript
   thresholds: {
     http_req_duration: ['p(95)<800', 'p(99)<1500'],
     http_req_failed: ['rate<0.01'],
   }
   ```

   This is an example requirement, **not a measurement of a real chat app**.

## Final check before submitting

- [ ] Check the actual outcome of the thresholds in Steps 0.6 and 0.7.
- [ ] Read the spike and soak graphs and replace the two bracketed notes in Part B.
- [ ] Confirm that the four Part A HTML files exist.
- [ ] Push the latest `RESULTS.md`, scripts and HTML reports to GitHub.
