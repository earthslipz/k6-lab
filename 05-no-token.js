import http from 'k6/http';
import { check, sleep } from 'k6';

// Step 0.5 - this request is SUPPOSED to be rejected.
export default function () {
  const response = http.post(
    'https://quickpizza.grafana.com/api/pizza',
    JSON.stringify({ mustBeVegetarian: true }),
    {
      headers: { 'Content-Type': 'application/json' },
      responseCallback: http.expectedStatuses(401),
    },
  );
  check(response, { 'missing token gets 401': (r) => r.status === 401 });
  sleep(1);
}
