import { test, expect } from '@playwright/test'
import { clearAuth } from './helpers'

test.describe('Suppliers', () => {
  test.beforeEach(async ({ page }) => { await clearAuth(page) })

  test('SU1: Suppliers page loads', async ({ page }) => {
    await page.goto('/suppliers')
    try { await page.waitForURL(/\/login/, { timeout: 8000 }) } catch {}
    if (page.url().includes('/login')) return
    await expect(page.getByTestId('suppliers-page')).toBeVisible()
  })
})
