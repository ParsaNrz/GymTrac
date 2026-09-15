import { test, expect } from '@playwright/test';

async function loginAs(page, username, password) {
  await page.goto('/login');
  await page.fill('#username', username);
  await page.fill('#password', password);
  await page.click('.btn-primary[type="submit"]');
  await page.waitForURL('**/dashboard');
}

async function signupAs(page, username, password) {
  await page.goto('/signup');
  await page.waitForURL('**/signup');
  await page.fill('#username', username);
  await page.fill('#password', password);
  await page.click('.btn-primary[type="submit"]');
  // After signup, success page is shown
  await expect(page.locator('text=Account Created')).toBeVisible();
  // Click "Go to Login" to proceed
  await page.click('text=Go to Login');
  await page.waitForURL('**/login');
}

test.beforeEach(async ({ page }) => {
  await page.goto('/');
});

test.describe('Authentication', () => {
  test('user can login and redirect to dashboard', async ({ page }) => {
    await page.goto('/login');
    await expect(page.locator('h1')).toContainText('Login');
    await page.fill('#username', 'e2eadmin');
    await page.fill('#password', 'e2eadminpass123');
    await page.click('.btn-primary[type="submit"]');
    await page.waitForURL('**/dashboard');
    await expect(page.locator('.dashboard')).toBeVisible();
  });

  test('protected pages redirect to login when logged out', async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForURL('**/login');
    await expect(page.locator('h1')).toContainText('Login');
  });
});

test.describe('User Flow', () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, 'e2eadmin', 'e2eadminpass123');
  });

  test('navigate to Workout page', async ({ page }) => {
    await page.click('.nav-link:text("Workout")');
    await page.waitForURL('**/workout');
    await expect(page.locator('.workout-page')).toBeVisible();
  });

  test('navigate to Exercises page', async ({ page }) => {
    await page.click('.nav-link:text("Exercises")');
    await page.waitForURL('**/exercises');
    await expect(page.locator('.exercises-page')).toBeVisible();
  });

  test('navigate to Calendar page', async ({ page }) => {
    await page.click('.nav-link:text("Calendar")');
    await page.waitForURL('**/calendar');
    await expect(page.locator('.calendar-page')).toBeVisible();
  });

  test('navigate to Settings and update profile', async ({ page }) => {
    await page.click('.nav-link:text("Settings")');
    await page.waitForURL('**/settings');
    await expect(page.locator('h1')).toContainText('Settings');

    // Change age
    await page.fill('#settings-age', '35');
    await page.click('.settings-section button[type="submit"]');
    await expect(page.locator('.alert-success').first()).toContainText('updated');
  });

  test('theme toggle persists after reload', async ({ page }) => {
    // Check default theme
    await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');

    // Toggle
    await page.click('.theme-toggle');
    await expect(page.locator('html')).toHaveAttribute('data-theme', 'light');

    // Reload and verify
    await page.reload();
    await expect(page.locator('html')).toHaveAttribute('data-theme', 'light');
  });
});

test.describe('Admin Flow', () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, 'e2eadmin', 'e2eadminpass123');
  });

  test('Admin nav item visible for admin', async ({ page }) => {
    await expect(page.locator('.nav-link:text("Admin")')).toBeVisible();
  });

  test('Admin page shows Users and Exercises tabs', async ({ page }) => {
    await page.click('.nav-link:text("Admin")');
    await page.waitForURL('**/admin');
    await expect(page.locator('.admin-tab:text("Users")')).toBeVisible();
    await expect(page.locator('.admin-tab:text("Exercises")')).toBeVisible();
  });

  test('can create an exercise via admin', async ({ page }) => {
    await page.click('.nav-link:text("Admin")');
    await page.waitForURL('**/admin');
    await page.locator('.admin-tab:text("Exercises")').click();

    // Click the Add Exercise button
    await page.locator('.admin-controls .btn-primary').click();

    // Fill form
    const uniqueName = `E2E Test ${Date.now()}`;
    await page.fill('#admin-ex-name', uniqueName);
    await page.selectOption('#admin-ex-muscle', 'Chest');
    await page.fill('#admin-ex-equipment', 'E2E Equipment');

    await page.click('.admin-form-card button[type="submit"]');

    // Verify it appears in the list
    await expect(page.locator(`text=${uniqueName}`).first()).toBeVisible();
  });

  test('can delete an exercise via admin', async ({ page }) => {
    await page.click('.nav-link:text("Admin")');
    await page.waitForURL('**/admin');
    await page.locator('.admin-tab:text("Exercises")').click();

    // Click the Add Exercise button
    await page.locator('.admin-controls .btn-primary').click();

    const uniqueName = `E2E Delete ${Date.now()}`;
    await page.fill('#admin-ex-name', uniqueName);
    await page.selectOption('#admin-ex-muscle', 'Legs');
    await page.click('.admin-form-card button[type="submit"]');
    await expect(page.locator(`text=${uniqueName}`).first()).toBeVisible();

    // Set up dialog handler BEFORE clicking delete
    page.once('dialog', dialog => dialog.accept());

    // Delete it
    const row = page.locator('tr', { hasText: uniqueName });
    await row.locator('.btn-danger').click();

    // Wait for the success message to appear
    await expect(page.locator('.alert-success')).toContainText('deleted');
  });
});

test.describe('Authorization', () => {
  test('normal user does not see Admin nav', async ({ page }) => {
    await loginAs(page, 'e2eadmin', 'e2eadminpass123');
    await page.click('.nav-link:text("Logout")');
    await page.waitForURL('**/login');

    // Signup as normal user with unique username
    const uniqueUser = `e2enormal_${Date.now()}`;
    await signupAs(page, uniqueUser, 'e2epass123');

    // Login as the new user
    await page.fill('#username', uniqueUser);
    await page.fill('#password', 'e2epass123');
    await page.click('.btn-primary[type="submit"]');
    await page.waitForURL('**/dashboard');

    // Admin nav should not be visible
    await expect(page.locator('.nav-link:text("Admin")')).not.toBeVisible();
  });

  test('normal user redirected from /admin', async ({ page }) => {
    await loginAs(page, 'e2eadmin', 'e2eadminpass123');
    await page.click('.nav-link:text("Logout")');
    await page.waitForURL('**/login');

    // Signup as normal user with unique username
    const uniqueUser = `e2enormal2_${Date.now()}`;
    await signupAs(page, uniqueUser, 'e2epass123');

    // Login as the new user
    await page.fill('#username', uniqueUser);
    await page.fill('#password', 'e2epass123');
    await page.click('.btn-primary[type="submit"]');
    await page.waitForURL('**/dashboard');

    await page.goto('/admin');
    await page.waitForURL('**/dashboard');
    await expect(page.locator('.dashboard')).toBeVisible();
  });
});
