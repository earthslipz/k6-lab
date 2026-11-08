import http from 'k6/http';
import { check, sleep } from 'k6';

// Requirement: 3 users for 30s, p95 under 1s, p99 under 1.5s,
// and fewer than 1% of requests failing.
// REQ_P95=1 is a deliberately tougher follow-up run for Step 0.7.
const maxP95 = Number(__ENV.REQ_P95 || 1000);

export const options = {
  vus: 3,
  duration: '30s',
  thresholds: {
    http_req_duration: [`p(95)<${maxP95}`, 'p(99)<1500'],
    http_req_failed: ['rate<0.01'],
  },
};

export default function () {
  const response = http.post(
    'https://quickpizza.grafana.com/api/pizza',
    JSON.stringify({ mustBeVegetarian: true }),
    { headers: {
      'Content-Type': 'application/json',
      Authorization: 'token abcdef0123456789',
    } },
  );
  check(response, {
    'valid pizza returned': (r) => r.status === 200 && Boolean(r.json('pizza.name')),
  });
  sleep(1);
}
