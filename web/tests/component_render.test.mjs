// TEST-GATE-06: render real React components rather than relying on test filenames.
// Runs after npm ci, using the esbuild package already provided by Vite.
import test, { after } from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { mkdtempSync, rmSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildSync } from 'esbuild';
import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const scratch = mkdtempSync(join(root, 'node_modules', '.component-test-'));
after(() => rmSync(scratch, { recursive: true, force: true }));

buildSync({
  entryPoints: [
    resolve(root, 'src/components/interview/ConnectionStatus.tsx'),
    resolve(root, 'src/components/portfolio/ConfidenceIndicator.tsx'),
    resolve(root, 'src/lib/utils.ts')
  ],
  bundle: true,
  packages: 'external',
  platform: 'node',
  format: 'cjs',
  jsx: 'automatic',
  outdir: scratch,
  outExtension: { '.js': '.cjs' },
  logLevel: 'silent'
});

const require = createRequire(import.meta.url);
const ConnectionStatus = require(join(scratch, 'ConnectionStatus.cjs')).default;
const ConfidenceIndicator = require(join(scratch, 'ConfidenceIndicator.cjs')).default;
const { cn } = require(join(scratch, 'utils.cjs'));

for (const [state, expected] of [
  ['connected', 'Connected'],
  ['reconnecting', 'Reconnecting...'],
  ['lost', 'Connection lost'],
]) {
  test(`connection state ${state} is visible to the user`, () => {
    const html = renderToStaticMarkup(React.createElement(ConnectionStatus, { state }));
    assert.match(html, new RegExp(expected.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
  });
}

for (const [confidence, expected] of [
  ['high', 'Confidence: HIGH'],
  ['medium', 'Confidence: MEDIUM'],
  ['low', 'Confidence: LOW'],
]) {
  test(`portfolio confidence ${confidence} has the correct label`, () => {
    const html = renderToStaticMarkup(React.createElement(ConfidenceIndicator, { confidence }));
    assert.ok(html.includes(expected), `missing ${expected} in ${html}`);
  });
}

test('utility classes retain distinct values and omit falsy flags', () => {
  assert.equal(cn('px-2', 'py-1'), 'px-2 py-1');
  assert.equal(cn('p-4', false && 'hidden', undefined, 'bg-white'), 'p-4 bg-white');
});
