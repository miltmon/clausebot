// Smoke test - Verifies app actually mounts and renders
// Prevents "blank page" bugs from reaching production
import { test, expect } from '@playwright/test';

test.describe('Critical smoke tests', () => {
  test('homepage mounts and renders', async ({ page }) => {
    // Navigate to app
    await page.goto(process.env.E2E_BASE_URL || 'http://localhost:4173');
    
    // Verify body is visible (basic mount check)
    await expect(page.locator('body')).toBeVisible();
    
    // Verify React actually rendered content
    await expect(page.locator('text=Start ClauseBot Quiz')).toBeVisible({ timeout: 10000 });
    
    // Verify navigation bar exists
    await expect(page.locator('nav, header')).toBeVisible();
    
    // Verify footer with SystemHealth widget
    await expect(page.locator('footer')).toBeVisible();
  });

  test('no blocking JavaScript errors', async ({ page }) => {
    const errors: string[] = [];
    
    // Capture console errors
    page.on('pageerror', (error) => {
      errors.push(error.message);
    });
    
    await page.goto(process.env.E2E_BASE_URL || 'http://localhost:4173');
    
    // Wait for content to load
    await page.waitForSelector('text=Start ClauseBot Quiz', { timeout: 10000 });
    
    // Filter out known non-blocking warnings
    const blockingErrors = errors.filter(err => 
      !err.includes('theme-color') && // Known PWA warning
      !err.includes('404') // Some 404s are expected (preview assets)
    );
    
    expect(blockingErrors).toHaveLength(0);
  });

  test('quiz modal opens', async ({ page }) => {
    await page.goto(process.env.E2E_BASE_URL || 'http://localhost:4173');
    
    // Click quiz button
    await page.click('text=Start ClauseBot Quiz');
    
    // Verify modal opens
    await expect(page.locator('[role="dialog"]')).toBeVisible({ timeout: 5000 });
  });

  test('health page loads', async ({ page }) => {
    await page.goto(`${process.env.E2E_BASE_URL || 'http://localhost:4173'}/health`);
    
    // Verify health page renders
    await expect(page.locator('text=System Health', { timeout: 5000 })).toBeVisible();
  });
});

