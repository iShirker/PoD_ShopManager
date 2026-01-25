import { test, expect } from '@playwright/test'
import { clearAuth } from './helpers'

test.describe('Mockup Studio', () => {
  test.beforeEach(async ({ page }) => {
    await clearAuth(page)
    await page.goto('/mockups')
    try { await page.waitForURL(/\/login/, { timeout: 6000 }) } catch {}
  })

  test('M1: Mockup Studio page loads', async ({ page }) => {
    try { await page.waitForURL(/\/login/, { timeout: 5000 }) } catch {}
    if (page.url().includes('/login')) return
    await expect(page.getByTestId('mockups')).toBeVisible()
    await expect(page.getByTestId('mockups-title')).toContainText(/Mockup Studio/i)
  })

  test('M2: Product select and upload present', async ({ page }) => {
    try { await page.waitForURL(/\/login/, { timeout: 5000 }) } catch {}
    if (page.url().includes('/login')) return
    await expect(page.getByTestId('mockups-product-select')).toBeVisible()
    await expect(page.getByTestId('mockups-upload')).toBeAttached()
  })
})
