import http from 'k6/http';
import { check, group, sleep } from 'k6';

const base = 'https://quickpizza.grafana.com';
const pizzaHeaders = {
  headers: {
    'Content-Type': 'application/json',
    Authorization: 'token abcdef0123456789',
  },
};

// One visitor checks the front page, looks at quotes and orders a recommendation.
export function journey() {
  group('home', () => {
    const response = http.get(`${base}/`);
    check(response, { 'home loads': (r) => r.status === 200 });
  });
  sleep(1 + Math.random() * 2);

  group('quotes', () => {
    const response = http.get(`${base}/api/quotes`);
    check(response, {
      'quotes are available': (r) => {
        const quotes = r.json('quotes');
        return r.status === 200 && Array.isArray(quotes) && quotes.length > 0;
      },
    });
  });
  sleep(1);

  group('recommendation', () => {
    const response = http.post(
      `${base}/api/pizza`,
      JSON.stringify({ mustBeVegetarian: true }),
      pizzaHeaders,
    );
    check(response, {
      'recommendation responds': (r) => r.status === 200,
      'recommended pizza is named': (r) => Boolean(r.json('pizza.name')),
    });
  });
  sleep(1 + Math.random() * 2);
}
