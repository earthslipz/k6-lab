import http from 'k6/http';
import { check, sleep } from 'k6';

const url = 'https://quickpizza.grafana.com/api/pizza';
const headers = {
  'Content-Type': 'application/json',
  Authorization: 'token abcdef0123456789',
};

// Step 0.4 - check the response fields, not only its status code.
export default function () {
  const response = http.post(url, JSON.stringify({ mustBeVegetarian: true }), { headers });
  check(response, {
    'request is successful': (r) => r.status === 200,
    'pizza name exists': (r) => typeof r.json('pizza.name') === 'string',
    'ingredients are vegetarian': (r) => {
      const ingredients = r.json('pizza.ingredients');
      return Array.isArray(ingredients) && ingredients.every((i) => i.vegetarian === true);
    },
  });
  sleep(1);
}
