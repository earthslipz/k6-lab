import http from 'k6/http';
import { check, sleep } from 'k6';

const p95Limit = Number(__ENV.P95 || 1500);

export const options = {
  vus: 3,
  duration: '30s',
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: [`p(95)<${p95Limit}`],
    checks: ['rate>0.99'],
  },
};

// Step 0.6 - compare the normal p95 threshold with P95=300.
export default function () {
  const response = http.post(
    'https://quickpizza.grafana.com/api/pizza',
    JSON.stringify({ mustBeVegetarian: true }),
    {
      headers: {
        'Content-Type': 'application/json',
        Authorization: 'token abcdef0123456789',
      },
    },
  );
  check(response, {
    'response status is 200': (r) => r.status === 200,
    'pizza has a name': (r) => Boolean(r.json('pizza.name')),
  });
  sleep(1);
}
