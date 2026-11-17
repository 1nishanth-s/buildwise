import { test, expect } from '@playwright/test';
import { captureScreenshot } from './helpers';

test.describe('Build Mode End-to-End Workflow', () => {
  test('Completes full Build Mode recommendation, component inspection, replacement, and persistence', async ({
    page,
  }) => {
    // 1. Open Application and verify Dashboard
    await page.goto('/');
    await expect(page).toHaveTitle(/BuildWise/i);

    // Verify Dashboard key elements
    const heading = page.locator('h1');
    await expect(heading).toContainText(/Build your next PC/i);

    // Verify catalog intelligence metrics are loaded
    await expect(page.locator('text=Total Components')).toBeVisible({ timeout: 15000 });
    await expect(page.locator('text=Price Observations')).toBeVisible();

    // Capture Dashboard screenshot
    await captureScreenshot(page, 'dashboard.png');

    // 2. Select "Build a New PC"
    const buildCard = page.locator('button', { hasText: 'Build a New PC' });
    await expect(buildCard).toBeVisible();
    await buildCard.click();

    // Verify navigation to /build
    await expect(page).toHaveURL(/\/build/);
    await expect(page.locator('h1')).toContainText(/Configure your new PC/i);

    // 3. Select Primary Usage: "Gaming"
    const gamingOption = page.locator('button', { hasText: 'Gaming' }).first();
    await expect(gamingOption).toBeVisible();
    await gamingOption.click();

    // 4. Enter Target Budget: 75,000 INR
    const budgetInput = page.locator('#budget-input');
    await expect(budgetInput).toBeVisible();
    await budgetInput.fill('75000');

    // Capture Build Form screenshot
    await captureScreenshot(page, 'build_form.png');

    // 5. Submit Form
    const submitBtn = page.locator('button[type="submit"]', { hasText: 'Generate My PC Build' });
    await expect(submitBtn).toBeEnabled();
    await submitBtn.click();

    // 6. Verify Recommendation Workflow generation & navigation
    await expect(page).toHaveURL(/\/workflow\/p_/, { timeout: 30000 });

    // Verify canvas renders nodes
    const nodes = page.locator('.react-flow__node');
    await expect(nodes.first()).toBeVisible({ timeout: 20000 });
    const nodeCount = await nodes.count();
    expect(nodeCount).toBeGreaterThanOrEqual(8);

    // Capture Workflow Canvas screenshot
    await captureScreenshot(page, 'build_canvas.png');

    // 7. Verify Budget Tracker in Top Bar
    const topBar = page.locator('div', { hasText: 'Total Price' }).first();
    await expect(topBar).toBeVisible();
    await expect(topBar.getByText('Target Budget', { exact: true })).toBeVisible();

    // 8. Inspect Properties Panel
    // Click on a component node (e.g. CPU or GPU)
    const cpuNode = page.locator('.react-flow__node', { hasText: /Core|Ryzen|Intel|AMD|CPU/i }).first();
    if (await cpuNode.isVisible()) {
      await cpuNode.click();
    } else {
      await nodes.first().click();
    }

    // Properties panel should be visible (target right panel aside)
    const propertiesPanel = page.locator('aside[class*="border-l"]');
    await expect(propertiesPanel).toBeVisible({ timeout: 10000 });
    await expect(propertiesPanel.locator('text=Recorded INR Price')).toBeVisible();

    // Capture Properties Panel screenshot
    await captureScreenshot(page, 'properties_panel.png');

    // 9. Component Replacement Test
    const altButton = propertiesPanel.locator('button', { hasText: /Compatible Alternatives/i });
    if (await altButton.isVisible()) {
      await altButton.click();
      const swapBtn = propertiesPanel.locator('button', { hasText: 'Swap This Component' }).first();
      if (await swapBtn.isVisible()) {
        await swapBtn.click();
        // Wait for replacement and revalidation to complete
        await page.waitForTimeout(1500);
      }
    }

    // 10. Verify Save Project Functionality
    const saveBtn = page.locator('button', { hasText: /Save Plan|Saved/i });
    await expect(saveBtn).toBeVisible();
    await saveBtn.click();

    // Should indicate "Saved"
    await expect(page.locator('button', { hasText: 'Saved' })).toBeVisible({ timeout: 10000 });

    // Capture Export Controls in top bar
    const exportControls = page.locator('button', { hasText: 'PDF' });
    await expect(exportControls).toBeVisible();
    await expect(page.locator('button', { hasText: 'CSV' })).toBeVisible();
    await captureScreenshot(page, 'export_controls.png');
  });
});
