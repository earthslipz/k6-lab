import { journey } from './journey.js';

// Quick check before running any heavier tests.
export const options = {
  vus: 1,
  duration: '30s',
  thresholds: {
    checks: ['rate>0.99'],
    http_req_failed: ['rate<0.01'],
  },
};

export default function () {
  journey();
}
