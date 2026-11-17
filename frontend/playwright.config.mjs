// Owner: Atiksh Gour | US-20/22 | Synthetic full-stack checks
import { defineConfig } from '@playwright/test';
export default defineConfig({
  projects: [{ name: 'chromium', use: {browserName: 'chromium', channel: 'chromium'} },
    {name: 'firefox', use: {browserName: 'firefox'}},
    {name: 'msedge', use: {browserName: 'chromium', channel: 'msedge'}}],
  testDir: './e2e', testMatch: '**/*.spec.js', workers: 1, retries: 0,
  timeout: 60000, reporter: [['list'], ['html', { open: 'never' }]],
  use: { baseURL: process.env.BASE_URL || 'http://127.0.0.1:3000',
    headless: true, trace: 'retain-on-failure', screenshot: 'only-on-failure' },
});
