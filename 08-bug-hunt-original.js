import http from 'k6/http';
import { check, sleep } from 'k6';

// Step 0.8 before fixing the inputs. Keep this to compare the two runs.
export default function () {
  const response = http.post(
    'https://quickpizza.grafana.com/api/pizza',
    JSON.stringify({
      excludedIngredients: ['pepperoni'],
      excludedTools: ['knife'],
    }),
    { headers: {
      'Content-Type': 'application/json',
      Authorization: 'token abcdef0123456789',
    } },
  );
  check(response, {
    'status 200': (r) => r.status === 200,
    'pepperoni not included': (r) => {
      const ingredients = r.json('pizza.ingredients');
      return Array.isArray(ingredients) && !ingredients.some((i) => i.name === 'Pepperoni');
    },
    'knife not used': (r) => r.json('pizza.tool') !== 'Knife',
  });
  sleep(1);
}
