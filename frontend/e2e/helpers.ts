import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { Page } from '@playwright/test';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export const SCREENSHOTS_DIR = path.resolve(__dirname, 'screenshots');
export const ARTIFACT_SCREENSHOTS_DIR = process.env.ARTIFACT_SCREENSHOTS_DIR || path.resolve(__dirname, 'screenshots');

// Ensure directories exist
if (!fs.existsSync(SCREENSHOTS_DIR)) {
  fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });
}
if (ARTIFACT_SCREENSHOTS_DIR && !fs.existsSync(ARTIFACT_SCREENSHOTS_DIR)) {
  try {
    fs.mkdirSync(ARTIFACT_SCREENSHOTS_DIR, { recursive: true });
  } catch (err) {
    // Graceful fallback if path is not creatable on different environment
  }
}

/**
 * Captures a screenshot to both the local e2e/screenshots directory
 * and the conversation artifact screenshots directory.
 */
export async function captureScreenshot(page: Page, filename: string): Promise<void> {
  const localPath = path.join(SCREENSHOTS_DIR, filename);
  const artifactPath = path.join(ARTIFACT_SCREENSHOTS_DIR, filename);

  await page.screenshot({ path: localPath, fullPage: true });

  try {
    fs.copyFileSync(localPath, artifactPath);
  } catch (err) {
    console.warn(`Could not copy screenshot to artifact dir: ${err}`);
  }
}

/**
 * Validates that a buffer starts with the standard PDF header bytes (%PDF-)
 */
export function isValidPdfBuffer(buffer: Buffer): boolean {
  if (buffer.length < 10) return false;
  const header = buffer.subarray(0, 5).toString('ascii');
  return header === '%PDF-';
}

/**
 * Validates that a buffer starts with the UTF-8 BOM (\xef\xbb\xbf)
 */
export function hasUtf8Bom(buffer: Buffer): boolean {
  if (buffer.length < 3) return false;
  return buffer[0] === 0xef && buffer[1] === 0xbb && buffer[2] === 0xbf;
}
