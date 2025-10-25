import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  const testEmail = `test+${Date.now()}@clausebot.test`;
  const testPassword = 'SecureP@ssw0rd!2024';

  test('should complete full auth flow: signup → dashboard → upload → clausebot gate', async ({ page }) => {
    // Navigate to auth page
    await page.goto('/auth');
    await expect(page).toHaveTitle(/ClauseBot/i);

    // Sign up
    await page.getByRole('tab', { name: /sign up/i }).click();
    await page.getByLabel(/email/i).fill(testEmail);
    await page.getByLabel(/password/i).fill(testPassword);
    await page.getByRole('button', { name: /sign up/i }).click();

    // Wait for redirect to dashboard
    await page.waitForURL('**/dashboard', { timeout: 10000 });
    await expect(page.getByRole('heading', { name: /dashboard|welcome/i })).toBeVisible();

    // Verify authenticated state in navbar
    await expect(page.getByText(/dashboard|logout/i).first()).toBeVisible();

    // Test ClauseBot gate (should show locked state with feature flag off)
    await page.goto('/clausebot');
    await expect(
      page.getByText(/private testing|preview mode|locked/i)
    ).toBeVisible({ timeout: 5000 });

    // Verify preview card structure
    await expect(page.getByText(/clause intelligence/i)).toBeVisible();
    await expect(page.getByText(/capabilities in development/i)).toBeVisible();
  });

  test('should prevent unauthenticated access to protected routes', async ({ page }) => {
    // Try to access protected routes without auth
    const protectedRoutes = ['/dashboard', '/kb', '/admin'];

    for (const route of protectedRoutes) {
      await page.goto(route);
      // Should redirect to auth page
      await page.waitForURL('**/auth', { timeout: 5000 });
      await expect(page.getByRole('heading', { name: /clausebot/i })).toBeVisible();
    }
  });

  test('should handle invalid login credentials', async ({ page }) => {
    await page.goto('/auth');
    
    await page.getByRole('tab', { name: /sign in/i }).click();
    await page.getByLabel(/email/i).fill('invalid@test.com');
    await page.getByLabel(/password/i).fill('wrongpassword');
    await page.getByRole('button', { name: /sign in/i }).click();

    // Should show error message
    await expect(
      page.getByText(/invalid|failed|incorrect/i)
    ).toBeVisible({ timeout: 5000 });
  });

  test('should persist session after page refresh', async ({ page, context }) => {
    // Sign up
    await page.goto('/auth');
    await page.getByRole('tab', { name: /sign up/i }).click();
    await page.getByLabel(/email/i).fill(`persist+${Date.now()}@test.com`);
    await page.getByLabel(/password/i).fill(testPassword);
    await page.getByRole('button', { name: /sign up/i }).click();

    await page.waitForURL('**/dashboard');

    // Reload page
    await page.reload();

    // Should still be on dashboard (not redirected to auth)
    await expect(page).toHaveURL(/dashboard/);
    await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();
  });

  test('should logout successfully', async ({ page }) => {
    // Sign up and login
    await page.goto('/auth');
    await page.getByRole('tab', { name: /sign up/i }).click();
    await page.getByLabel(/email/i).fill(`logout+${Date.now()}@test.com`);
    await page.getByLabel(/password/i).fill(testPassword);
    await page.getByRole('button', { name: /sign up/i }).click();

    await page.waitForURL('**/dashboard');

    // Logout
    await page.getByText(/logout/i).click();

    // Should redirect to home or auth
    await page.waitForURL(/\/(auth)?$/);

    // Verify can't access protected route
    await page.goto('/dashboard');
    await page.waitForURL('**/auth');
  });
});

test.describe('SEO and Robots', () => {
  test('should have noindex on protected pages', async ({ page }) => {
    await page.goto('/auth');
    
    const metaRobots = await page.locator('meta[name="robots"]').getAttribute('content');
    expect(metaRobots).toContain('noindex');
    expect(metaRobots).toContain('nofollow');
  });

  test('robots.txt should disallow sensitive paths', async ({ page }) => {
    const response = await page.request.get('/robots.txt');
    expect(response.status()).toBe(200);
    
    const content = await response.text();
    expect(content).toContain('Disallow: /clausebot');
    expect(content).toContain('Disallow: /admin');
    expect(content).toContain('Disallow: /dashboard');
    expect(content).toContain('Disallow: /preview/');
  });
});