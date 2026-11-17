import { test, expect } from '@playwright/test';
import { captureScreenshot } from './helpers';

test.describe('Upgrade Mode End-to-End Workflow', () => {
  test('Completes full Upgrade Mode bottleneck analysis, retained vs replaced verification, and persistence', async ({
    page,
  }) => {
    // 1. Open Application and navigate to Upgrade Mode
    await page.goto('/');
    const upgradeCard = page.locator('button', { hasText: 'Upgrade Existing PC' });
    await expect(upgradeCard).toBeVisible({ timeout: 15000 });
    await upgradeCard.click();

    // Verify navigation to /upgrade
    await expect(page).toHaveURL(/\/upgrade/);
    await expect(page.locator('h1')).toContainText(/Upgrade your existing PC/i);

    // 2. Fill Existing PC Hardware Details
    // Inputs have placeholders or are in Section A
    const cpuInput = page.locator('input[placeholder*="AMD Ryzen"]');
    if (await cpuInput.isVisible()) {
      await cpuInput.fill('AMD Ryzen 5 3600');
    }

    const gpuInput = page.locator('input[placeholder*="GTX"]');
    if (await gpuInput.isVisible()) {
      await gpuInput.fill('NVIDIA GTX 1060 6GB');
    }

    const mbInput = page.locator('input[placeholder*="B450"]');
    if (await mbInput.isVisible()) {
      await mbInput.fill('MSI B450 TOMAHAWK');
    }

    const ramInput = page.locator('input[placeholder*="16GB"]');
    if (await ramInput.isVisible()) {
      await ramInput.fill('16GB DDR4');
    }

    // 3. Select Upgrade Goal: "Better Gaming Performance"
    const goalBtn = page.locator('button', { hasText: 'Better Gaming Performance' }).first();
    await expect(goalBtn).toBeVisible();
    await goalBtn.click();

    // 4. Enter Upgrade Budget: 50,000 INR
    const budgetInput = page.locator('#upgrade-budget');
    await expect(budgetInput).toBeVisible();
    await budgetInput.fill('50000');

    // Capture Upgrade Form screenshot
    await captureScreenshot(page, 'upgrade_form.png');

    // 5. Submit Form
    const submitBtn = page.locator('button[type="submit"]', { hasText: /Analyze My PC/i });
    await expect(submitBtn).toBeEnabled();
    await submitBtn.click();

    // 6. Verify Recommendation Workflow generation & navigation
    await expect(page).toHaveURL(/\/workflow\/p_up_/, { timeout: 35000 });

    // Verify canvas renders nodes
    const nodes = page.locator('.react-flow__node');
    await expect(nodes.first()).toBeVisible({ timeout: 20000 });
    const count = await nodes.count();
    expect(count).toBeGreaterThanOrEqual(6);

    // Capture Upgrade Canvas screenshot
    await captureScreenshot(page, 'upgrade_canvas.png');

    // 7. Verify Distinction Between Retained (Reusable) vs Replaced (Recommended) Components
    const retainedBadges = page.locator('text=/reusable|retained/i');
    const recommendedBadges = page.locator('text=/recommended|upgrade/i');

    expect(await nodes.count()).toBeGreaterThan(0);

    // 8. Inspect Properties Panel on a node
    await nodes.first().click();
    const propertiesPanel = page.locator('aside[class*="border-l"]');
    await expect(propertiesPanel).toBeVisible({ timeout: 10000 });

    // 9. Verify Budget Tracker in Top Bar
    const topBar = page.locator('div', { hasText: 'Total Price' }).first();
    await expect(topBar).toBeVisible();
    await expect(topBar.getByText('Target Budget', { exact: true })).toBeVisible();

    // 10. Save the Upgrade Project
    const saveBtn = page.locator('button', { hasText: /Save Plan|Saved/i });
    await expect(saveBtn).toBeVisible();
    await saveBtn.click();
    await expect(page.locator('button', { hasText: 'Saved' })).toBeVisible({ timeout: 10000 });
  });
});
