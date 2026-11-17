import { test, expect } from '@playwright/test';
import { captureScreenshot, isValidPdfBuffer } from './helpers';

test.describe('Phase 13: Multi-Component Dependency-Aware Upgrade Journey', () => {
  test('Complete journey: High-end GPU upgrade requiring PSU dependency, retained hardware verification, properties panel justifications, and exports', async ({
    page,
    request,
  }) => {
    // 1. Navigate to Upgrade Mode
    await page.goto('/');
    const upgradeLink = page.locator('button', { hasText: 'Upgrade Existing PC' });
    await expect(upgradeLink).toBeVisible({ timeout: 15000 });
    await upgradeLink.click();

    await expect(page).toHaveURL(/\/upgrade/);
    await expect(page.locator('h1')).toContainText(/Upgrade your existing PC/i);

    // 2. Fill Existing PC Hardware with a low-wattage 450W PSU
    const cpuInput = page.locator('input[placeholder*="AMD Ryzen"]');
    if (await cpuInput.isVisible()) {
      await cpuInput.fill('AMD Ryzen 5 3600');
    }

    const gpuInput = page.locator('input[placeholder*="GTX"]');
    if (await gpuInput.isVisible()) {
      await gpuInput.fill('NVIDIA GeForce GTX 1650 4GB');
    }

    const mbInput = page.locator('input[placeholder*="B450"]');
    if (await mbInput.isVisible()) {
      await mbInput.fill('MSI B450 TOMAHAWK MAX');
    }

    const ramInput = page.locator('input[placeholder*="16GB"]');
    if (await ramInput.isVisible()) {
      await ramInput.fill('16GB DDR4');
    }

    const psuInput = page.locator('input[placeholder*="650W"], input[placeholder*="Corsair"]');
    if (await psuInput.isVisible()) {
      await psuInput.fill('Corsair CV450 450W');
    }

    // 3. Select Upgrade Goal: "Better Gaming Performance"
    const goalBtn = page.locator('button', { hasText: 'Better Gaming Performance' }).first();
    await expect(goalBtn).toBeVisible();
    await goalBtn.click();

    // 4. Enter High Budget (90,000 INR) to comfortably select a powerful GPU
    const budgetInput = page.locator('#upgrade-budget');
    await expect(budgetInput).toBeVisible();
    await budgetInput.fill('90000');

    // 5. Submit Upgrade Form
    const submitBtn = page.locator('button[type="submit"]', { hasText: /Analyze My PC/i });
    await expect(submitBtn).toBeEnabled();
    await submitBtn.click();

    // 6. Wait for recommendation workflow canvas to load
    await expect(page).toHaveURL(/\/workflow\/p_up_/, { timeout: 35000 });

    // Verify nodes render on horizontal workflow canvas
    const canvasNodes = page.locator('.react-flow__node');
    await expect(canvasNodes.first()).toBeVisible({ timeout: 20000 });
    const nodeCount = await canvasNodes.count();
    expect(nodeCount).toBeGreaterThanOrEqual(6);

    // 7. Verify Multiple Component Replacements: Primary GPU + Required Dependent PSU
    // Verify presence of Primary Upgrade badge
    const primaryBadge = page.locator('text=Primary Upgrade').first();
    await expect(primaryBadge).toBeVisible({ timeout: 10000 });

    // Verify presence of Required Dependency badge on the canvas
    const dependencyBadge = page.locator('text=Required Dependency').first();
    await expect(dependencyBadge).toBeVisible({ timeout: 10000 });

    // Verify presence of Retained badges for preserved components (e.g., CPU, RAM, MB)
    const retainedBadge = page.locator('text=Retained').first();
    await expect(retainedBadge).toBeVisible({ timeout: 10000 });

    // 8. Click the PSU node to inspect Properties Panel justifications
    // Find node with PSU category or text
    const psuNode = canvasNodes.filter({ hasText: /psu/i }).first();
    if (await psuNode.isVisible()) {
      await psuNode.click();
    } else {
      // Click the node that has the Required Dependency badge
      await dependencyBadge.click();
    }

    const propertiesPanel = page.locator('aside[class*="border-l"]');
    await expect(propertiesPanel).toBeVisible({ timeout: 10000 });

    // Verify Properties Panel displays Required Dependency Reason and current hardware
    await expect(propertiesPanel.locator('text=Required Dependency').first()).toBeVisible();
    await expect(propertiesPanel.locator('text=Required Dependency Reason')).toBeVisible();
    await expect(propertiesPanel.locator('text=Current Installed')).toBeVisible();

    // Capture screenshot of Multi-Component Upgrade Canvas and Properties Panel
    await captureScreenshot(page, 'multi_component_upgrade_canvas.png');

    // 9. Verify Top Bar Budget Tracker calculates combined upgrade cost
    const topBar = page.locator('div', { hasText: 'Total Price' }).first();
    await expect(topBar).toBeVisible();
    await expect(topBar.locator('text=Target Budget')).toBeVisible();

    // 10. Save the Multi-Component Upgrade Project
    const saveBtn = page.locator('button', { hasText: /Save Plan|Saved/i });
    await expect(saveBtn).toBeVisible();
    await saveBtn.click();
    await expect(page.locator('button', { hasText: 'Saved' })).toBeVisible({ timeout: 10000 });

    // 11. Test Export Endpoints for this saved project
    const currentUrl = page.url();
    const projectIdMatch = currentUrl.match(/\/workflow\/(p_up_[a-zA-Z0-9_]+)/);
    expect(projectIdMatch).not.toBeNull();
    const projectId = projectIdMatch![1];

    // Verify CSV export
    const csvResponse = await request.get(`/api/export/${projectId}/csv`);
    expect(csvResponse.status()).toBe(200);
    const csvContent = await csvResponse.text();
    expect(csvContent).toContain('PRIMARY UPGRADE');
    expect(csvContent).toContain('REQUIRED DEPENDENCY');
    expect(csvContent).toContain('RETAINED');

    // Verify PDF export
    const pdfResponse = await request.get(`/api/export/${projectId}/pdf`);
    expect(pdfResponse.status()).toBe(200);
    expect(pdfResponse.headers()['content-type']).toBe('application/pdf');
    const pdfBuffer = await pdfResponse.body();
    expect(isValidPdfBuffer(pdfBuffer)).toBe(true);
  });
});
