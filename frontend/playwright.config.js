import { defineConfig, devices } from '@playwright/test';

const TEST_DATABASE_URL = 'sqlite+aiosqlite:///./data/gym_trac_e2e.db';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: 0,
  workers: 1,
  reporter: 'list',
  use: {
    baseURL: 'http://127.0.0.1:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: [
    {
      command: 'C:/Users/Parsa/AppData/Local/Programs/Python/Python311/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000',
      cwd: '../backend',
      port: 8000,
      reuseExistingServer: !process.env.CI,
      timeout: 60000,
      env: {
        PYTHONPATH: '../backend',
        DATABASE_URL: 'sqlite+aiosqlite:///./data/gym_trac_e2e.db',
        JWT_SECRET_KEY: 'e2e-test-secret-key-not-for-production',
        ADMIN_USERNAME: 'e2eadmin',
        ADMIN_PASSWORD: 'e2eadminpass123',
        FRONTEND_ORIGIN: 'http://127.0.0.1:5173',
      },
    },
    {
      command: 'npx vite --host 127.0.0.1 --port 5173',
      port: 5173,
      reuseExistingServer: !process.env.CI,
      timeout: 60000,
    },
  ],
  globalSetup: './playwright.global-setup.js',
});
