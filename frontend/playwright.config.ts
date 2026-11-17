import { defineConfig, devices } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');
const defaultVenv = path.resolve(rootDir, '.venv/Scripts/python.exe');
const altVenv = path.resolve(rootDir, 'venv/Scripts/python.exe');
const pythonExe = process.env.PYTHON_PATH || (fs.existsSync(defaultVenv) ? defaultVenv : (fs.existsSync(altVenv) ? altVenv : 'python'));
const testDbPath = path.resolve(rootDir, 'data/e2e_test_projects.db');

export default defineConfig({
  testDir: './e2e',
  timeout: 60000,
  expect: {
    timeout: 15000,
  },
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter: [
    ['list'],
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
    ['json', { outputFile: 'playwright-report/test-results.json' }],
  ],
  use: {
    baseURL: 'http://127.0.0.1:8000',
    trace: 'retain-on-failure',
    screenshot: 'on',
    video: 'retain-on-failure',
    headless: true,
    viewport: { width: 1440, height: 900 },
    actionTimeout: 15000,
    navigationTimeout: 30000,
  },
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1440, height: 900 },
      },
    },
  ],
  webServer: {
    command: `"${pythonExe}" -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000`,
    url: 'http://127.0.0.1:8000/api/health',
    reuseExistingServer: false,
    cwd: rootDir,
    env: {
      BUILDWISE_DB_PATH: testDbPath,
    },
    timeout: 45000,
  },
});
