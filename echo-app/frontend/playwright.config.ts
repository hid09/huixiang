import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'https://localhost:5175',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    ignoreHTTPSErrors: true,
  },

  projects: [
    {
      name: 'iPhone 14 - Chromium',
      use: {
        ...devices['iPhone 14'],
        browserName: 'chromium',
      },
    },
    {
      name: 'Pixel 5 - Chromium',
      use: {
        ...devices['Pixel 5'],
        browserName: 'chromium',
      },
    },
  ],

});
