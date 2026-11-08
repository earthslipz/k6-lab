import http from 'k6/http';

// Step 0.8 - useful for checking exact spelling and capitalization.
const params = { headers: { Authorization: 'token abcdef0123456789' } };
export default function () {
  const base = 'https://quickpizza.grafana.com';
  const ingredients = http.get(`${base}/api/ingredients/topping`, params);
  const tools = http.get(`${base}/api/tools`, params);
  console.log('Toppings:', ingredients.body);
  console.log('Tools:', tools.body);
}
