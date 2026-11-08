import http from 'k6/http';
import { check, sleep } from 'k6';

const params = {
  headers: {
    'Content-Type': 'application/json',
    Authorization: 'token abcdef0123456789',
  },
};

// Step 0.8 fixed: use the exact ingredient and tool names exposed by the API.
export default function () {
  const restrictions = {
    excludedIngredients: ['Pepperoni'],
    excludedTools: ['Knife'],
  };
  const response = http.post(
    'https://quickpizza.grafana.com/api/pizza',
    JSON.stringify(restrictions),
    params,
  );
  check(response, {
    'pizza request accepted': (r) => r.status === 200,
    'pepperoni is excluded': (r) => {
      const ingredients = r.json('pizza.ingredients');
      return Array.isArray(ingredients) && ingredients.every((i) => i.name !== 'Pepperoni');
    },
    'no knife needed': (r) => r.json('pizza.tool') !== 'Knife',
  });
  sleep(1);
}
