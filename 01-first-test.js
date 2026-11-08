import http from 'k6/http';
import { check, sleep } from 'k6';

// Step 0.1 - one user checking whether QuickPizza is reachable.
export default function () {
  const response = http.get('https://quickpizza.grafana.com/');
  check(response, { 'home page returns 200': (r) => r.status === 200 });
  sleep(1);
}
