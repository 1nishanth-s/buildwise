import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import { isValidPdfBuffer, hasUtf8Bom } from './helpers';

test.describe('PDF and CSV Export End-to-End Tests', () => {
  test('Downloads and verifies valid Build Mode PDF and CSV reports via browser controls', async ({
    page,
  }) => {
    // 1. Generate a Build Recommendation
    await page.goto('/build');
    await page.locator('#budget-input').fill('80000');
    await page.locator('button[type="submit"]', { hasText: 'Generate My PC Build' }).click();
    await expect(page).toHaveURL(/\/workflow\/p_/, { timeout: 30000 });

    const pdfBtn = page.locator('button', { hasText: 'PDF' });
    const csvBtn = page.locator('button', { hasText: 'CSV' });
    await expect(pdfBtn).toBeVisible({ timeout: 15000 });
    await expect(csvBtn).toBeVisible({ timeout: 15000 });

    // 2. Download PDF report via UI button
    const [pdfDownload] = await Promise.all([
      page.waitForEvent('download', { timeout: 20000 }),
      pdfBtn.click(),
    ]);

    const suggestedPdfName = pdfDownload.suggestedFilename();
    expect(suggestedPdfName).toMatch(/\.pdf$/i);

    const tempPdfPath = path.resolve('scratch/e2e_build_download.pdf');
    await pdfDownload.saveAs(tempPdfPath);

    // Verify downloaded PDF file
    expect(fs.existsSync(tempPdfPath)).toBe(true);
    const pdfBuffer = fs.readFileSync(tempPdfPath);
    expect(pdfBuffer.length).toBeGreaterThan(15000);
    expect(isValidPdfBuffer(pdfBuffer)).toBe(true);

    // 3. Download CSV report via UI button
    const [csvDownload] = await Promise.all([
      page.waitForEvent('download', { timeout: 20000 }),
      csvBtn.click(),
    ]);

    const suggestedCsvName = csvDownload.suggestedFilename();
    expect(suggestedCsvName).toMatch(/\.csv$/i);

    const tempCsvPath = path.resolve('scratch/e2e_build_download.csv');
    await csvDownload.saveAs(tempCsvPath);

    // Verify downloaded CSV file
    expect(fs.existsSync(tempCsvPath)).toBe(true);
    const csvBuffer = fs.readFileSync(tempCsvPath);
    expect(csvBuffer.length).toBeGreaterThan(1000);
    expect(hasUtf8Bom(csvBuffer)).toBe(true);

    const csvText = csvBuffer.toString('utf-8');
    expect(csvText).toContain('# BuildWise-AI PC Build Recommendation Specification');
    expect(csvText).toContain('Category,Brand,Model,Component Full Name');
    expect(csvText).toContain('Price (INR)');
    expect(csvText).toContain('Empirical Benchmark Score');
    expect(csvText).toContain('ML Predicted Score');
  });

  test('Downloads and verifies valid Upgrade Mode PDF and CSV reports via browser controls', async ({
    page,
  }) => {
    // 1. Generate an Upgrade Recommendation
    await page.goto('/upgrade');
    await page.locator('#upgrade-budget').fill('45000');
    await page.locator('button[type="submit"]', { hasText: /Analyze My PC/i }).click();
    await expect(page).toHaveURL(/\/workflow\/p_up_/, { timeout: 35000 });

    const pdfBtn = page.locator('button', { hasText: 'PDF' });
    const csvBtn = page.locator('button', { hasText: 'CSV' });
    await expect(pdfBtn).toBeVisible({ timeout: 15000 });
    await expect(csvBtn).toBeVisible({ timeout: 15000 });

    // 2. Download Upgrade PDF report
    const [pdfDownload] = await Promise.all([
      page.waitForEvent('download', { timeout: 20000 }),
      pdfBtn.click(),
    ]);

    const tempPdfPath = path.resolve('scratch/e2e_upgrade_download.pdf');
    await pdfDownload.saveAs(tempPdfPath);

    expect(fs.existsSync(tempPdfPath)).toBe(true);
    const pdfBuffer = fs.readFileSync(tempPdfPath);
    expect(pdfBuffer.length).toBeGreaterThan(15000);
    expect(isValidPdfBuffer(pdfBuffer)).toBe(true);

    // 3. Download Upgrade CSV report
    const [csvDownload] = await Promise.all([
      page.waitForEvent('download', { timeout: 20000 }),
      csvBtn.click(),
    ]);

    const tempCsvPath = path.resolve('scratch/e2e_upgrade_download.csv');
    await csvDownload.saveAs(tempCsvPath);

    expect(fs.existsSync(tempCsvPath)).toBe(true);
    const csvBuffer = fs.readFileSync(tempCsvPath);
    expect(csvBuffer.length).toBeGreaterThan(1000);
    expect(hasUtf8Bom(csvBuffer)).toBe(true);

    const csvText = csvBuffer.toString('utf-8');
    expect(csvText).toContain('# BuildWise-AI PC Upgrade Recommendation Report');
    expect(csvText).toContain('Action');
    expect(csvText).toContain('Existing Component');
    expect(csvText).toContain('Recommended Component');
    expect(csvText).toContain('Upgrade Cost (INR)');
  });
});
