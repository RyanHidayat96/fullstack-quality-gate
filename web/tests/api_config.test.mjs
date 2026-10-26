// DOC-01 and INVITE-03 — source-level config regressions, no dependency install.
// This is NOT a browser UI test; browser/DOM tests remain a separately required gate.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const env = readFileSync(resolve(root, '.env.example'), 'utf8');
const client = readFileSync(resolve(root, 'src/services/api.ts'), 'utf8');
const configValue = (key) => env.match(new RegExp(`^${key}=(.+)$`, 'm'))?.[1]?.trim();

test('DOC-01: documented REST API points to Rails port 3001', () => {
  assert.equal(configValue('VITE_API_BASE_URL'), 'http://localhost:3001/api/v1');
  assert.match(client, /http:\/\/localhost:3001\/api\/v1/);
});

test('INVITE-03: WebSocket client and example target Rails port 3001', () => {
  assert.equal(configValue('VITE_WS_BASE_URL'), 'ws://localhost:3001');
  assert.match(client, /ws:\/\/localhost:3001/);
});

test('SIGNUP-01: public signup is absent until account enrollment is specified', () => {
  const routes = readFileSync(resolve(root, 'src/App.tsx'), 'utf8');
  const auth = readFileSync(resolve(root, 'src/services/auth.ts'), 'utf8');
  assert.match(routes, /path="\\/login"/);
  assert.doesNotMatch(routes, /path="\\/signup"/);
  assert.doesNotMatch(auth, /signup\\s*:/);
  assert.equal(existsSync(resolve(root, 'src/pages/auth/SignupPage.tsx')), false);
});
