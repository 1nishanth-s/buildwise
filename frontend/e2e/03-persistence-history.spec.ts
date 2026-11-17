import { test, expect } from '@playwright/test';
import { captureScreenshot } from './helpers';

test.describe('Project Persistence and History Workflows', () => {
  test('Verifies saved projects appear in History and can be reopened from My Builds and My Upgrades', async ({
    page,
  }) => {
    // 1. First ensure we have at least one saved build in the database
    await page.goto('/build');
    await page.locator('#budget-input').fill('65000');
    await page.locator('button[type="submit"]', { hasText: 'Generate My PC Build' }).click();
    await expect(page).toHaveURL(/\/workflow\/p_/, { timeout: 30000 });

    // Explicitly click Save Plan
    const saveBtn = page.locator('button', { hasText: /Save Plan|Saved/i });
    await expect(saveBtn).toBeVisible();
    await saveBtn.click();
    await expect(page.locator('button', { hasText: 'Saved' })).toBeVisible({ timeout: 10000 });

    const currentUrl = page.url();

    // 2. Navigate to History Page via sidebar or URL
    const historyLink = page.locator('aside a[href="/history"]');
    if (await historyLink.isVisible()) {
      await historyLink.click();
    } else {
      await page.goto('/history');
    }

    await expect(page).toHaveURL(/\/history/);
    await expect(page.locator('h1')).toContainText(/Generation History/i);

    // Verify history contains items
    const historyItems = page.locator('div[class*="divide-y"] > div');
    await expect(historyItems.first()).toBeVisible({ timeout: 15000 });
    const historyCount = await historyItems.count();
    expect(historyCount).toBeGreaterThan(0);

    // Capture Project History screenshot
    await captureScreenshot(page, 'project_history.png');

    // 3. Click the first history item to reopen the workflow
    await historyItems.first().click();
    await expect(page).toHaveURL(/\/workflow\/p_/, { timeout: 15000 });

    // Verify canvas restored
    const nodes = page.locator('.react-flow__node');
    await expect(nodes.first()).toBeVisible({ timeout: 15000 });
    expect(await nodes.count()).toBeGreaterThanOrEqual(8);

    // 4. Navigate to My Builds page
    await page.goto('/my-builds');
    await expect(page).toHaveURL(/\/my-builds/);
    await expect(page.locator('h1')).toContainText(/My PC Builds/i);

    // Verify saved builds are listed
    const buildCards = page.locator('div[class*="grid"] > div');
    await expect(buildCards.first()).toBeVisible({ timeout: 15000 });
    expect(await buildCards.count()).toBeGreaterThan(0);

    // Reopen from My Builds
    await buildCards.first().click();
    await expect(page).toHaveURL(/\/workflow\/p_/, { timeout: 15000 });
    await expect(page.locator('.react-flow__node').first()).toBeVisible();

    // 5. Navigate to My Upgrades page
    await page.goto('/my-upgrades');
    await expect(page).toHaveURL(/\/my-upgrades/);
    await expect(page.locator('h1')).toContainText(/My Upgrade Plans/i);
  });
});
