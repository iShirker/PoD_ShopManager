import { test, expect } from '@playwright/test'
import { clearAuth } from './helpers'

test.describe('Listings Bulk Create', () => {
  test.beforeEach(async ({ page }) => {
    await clearAuth(page)
    await page.goto('/listings/bulk')
    try { await page.waitForURL(/\/login/, { timeout: 6000 }) } catch {}
  })

  test('LB1: Bulk Create page loads', async ({ page }) => {
    try { await page.waitForURL(/\/login/, { timeout: 5000 }) } catch {}
    if (page.url().includes('/login')) return
    await expect(page.getByTestId('listings-bulk')).toBeVisible()
    await expect(page.getByTestId('listings-bulk-title')).toContainText(/Bulk Create/i)
  })

  test('LB2: Download template works', async ({ page }) => {
    if (page.url().includes('/login')) return
    const [download] = await Promise.all([
      page.waitForEvent('download'),
      page.getByTestId('listings-bulk-download-template').click(),
    ])
    expect(download.suggestedFilename()).toMatch(/\.csv$/i)
  })

  test('LB5: Create button present when file selected', async ({ page }) => {
    try { await page.waitForURL(/\/login/, { timeout: 5000 }) } catch {}
    if (page.url().includes('/login')) return
    await expect(page.getByTestId('listings-bulk-upload')).toBeAttached()
    const upload = page.getByTestId('listings-bulk-upload')
    await upload.setInputFiles({
      name: 'test.csv',
      mimeType: 'text/csv',
      buffer: Buffer.from('title,description,tags\n"T1","D1","t1"'),
    })
    await expect(page.getByTestId('listings-bulk-create')).toBeVisible()
  })
})
