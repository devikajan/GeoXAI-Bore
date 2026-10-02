import { readFileSync } from 'node:fs'
import vm from 'node:vm'
import test from 'node:test'
import assert from 'node:assert/strict'
import ts from 'typescript'

// Exercise the real API client with network responses, without a browser dependency.
function client(fetch) {
  const source = readFileSync(new URL('../src/api.ts', import.meta.url), 'utf8')
    .replaceAll('import.meta.env.PROD', 'true')
    .replaceAll('import.meta.env.VITE_API_URL', 'undefined')
  const output = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS } }).outputText
  const exports = {}
  vm.runInNewContext(output, { exports, fetch, AbortController, AbortSignal, Date,
    window: { setTimeout, clearTimeout }, Error, Promise, DOMException, TypeError })
  return exports
}

test('a Render loading page with HTTP 200 is not a healthy API', async () => {
  const api = client(async () => ({ ok: true, json: async () => { throw new SyntaxError('HTML') } }))
  assert.equal(await api.checkApiHealth(), false)
})

test('healthy status is checked and requested without cached responses', async () => {
  let requested
  const api = client(async (url, options) => {
    requested = { url, options }
    return { ok: true, json: async () => ({ status: 'healthy' }) }
  })
  assert.equal(await api.checkApiHealth(), true)
  assert.equal(requested.url, '/api/health')
  assert.equal(requested.options.cache, 'no-store')
})

test('overlapping health probes share one request', async () => {
  let calls = 0
  let resolve
  const api = client(() => { calls++; return new Promise(done => { resolve = done }) })
  const first = api.checkApiHealth()
  const second = api.checkApiHealth()
  assert.equal(calls, 1)
  resolve({ ok: true, json: async () => ({ status: 'healthy' }) })
  assert.equal(await first, true)
  assert.equal(await second, true)
})

test('a failed probe can recover on the next probe', async () => {
  let calls = 0
  const api = client(async () => ({ ok: ++calls > 1, json: async () => ({ status: 'healthy' }) }))
  assert.equal(await api.checkApiHealth(), false)
  assert.equal(await api.checkApiHealth(), true)
})

test('wrong JSON status is rejected', async () => {
  const api = client(async () => ({ ok: true, json: async () => ({ status: 'starting' }) }))
  assert.equal(await api.checkApiHealth(), false)
})
