import { journey } from './journey.js';

// Build up a baseline, jump to 5 users, then watch recovery.
export const options = {
  stages: [
    { duration: '30s', target: 1 },
    { duration: '5s', target: 5 },
    { duration: '30s', target: 5 },
    { duration: '5s', target: 1 },
    { duration: '1m', target: 1 },
    { duration: '10s', target: 0 },
  ],
  thresholds: {
    checks: ['rate>0.99'],
    http_req_failed: ['rate<0.01'],
  },
};

export default function () {
  journey();
}
