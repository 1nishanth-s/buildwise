import { test, expect } from '@playwright/test';

test.describe('Negative and Edge-Case End-to-End Tests', () => {
  test('Validates budget boundaries and disables submission for invalid budgets in Build Mode', async ({
    page,
  }) => {
    await page.goto('/build');

    const budgetInput = page.locator('#budget-input');
    const submitBtn = page.locator('button[type="submit"]', { hasText: 'Generate My PC Build' });

    // Test with insufficient budget (e.g. 5,000)
    await budgetInput.fill('5000');
    await expect(page.locator('text=Minimum viable budget for a complete PC with catalog components is ₹18,000')).toBeVisible();
    await expect(submitBtn).toBeDisabled();

    // Test with empty budget
    await budgetInput.fill('');
    await expect(submitBtn).toBeDisabled();

    // Test with valid budget (e.g. 25,000)
    await budgetInput.fill('25000');
    await expect(submitBtn).toBeEnabled();
  });

  test('Validates budget boundaries and input constraints in Upgrade Mode', async ({
    page,
  }) => {
    await page.goto('/upgrade');

    const budgetInput = page.locator('#upgrade-budget');
    const submitBtn = page.locator('button[type="submit"]', { hasText: /Analyze My PC/i });

    // Budget below 5,000
    await budgetInput.fill('2000');
    await expect(submitBtn).toBeDisabled();

    // Valid budget >= 5,000
    await budgetInput.fill('15000');
    await expect(submitBtn).toBeEnabled();
  });

  test('Gracefully displays error page for nonexistent project IDs and allows returning to Dashboard', async ({
    page,
  }) => {
    // Navigate to an invalid project workflow URL
    await page.goto('/workflow/nonexistent_project_uuid_99999');

    // Should not crash or produce an uncaught error white screen
    await expect(page.locator('text=Workflow Project Not Found')).toBeVisible({ timeout: 15000 });
    const returnBtn = page.locator('button', { hasText: 'Return to Dashboard' });
    await expect(returnBtn).toBeVisible();

    // Click Return to Dashboard
    await returnBtn.click();
    await expect(page).toHaveURL('/');
  });

  test('Verifies API export returns 404 for nonexistent projects', async ({ request }) => {
    const pdfRes = await request.get('/api/export/nonexistent_test_proj/pdf');
    expect(pdfRes.status()).toBe(404);

    const csvRes = await request.get('/api/export/nonexistent_test_proj/csv');
    expect(csvRes.status()).toBe(404);
  });
});
