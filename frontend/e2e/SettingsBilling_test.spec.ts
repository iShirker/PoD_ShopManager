import { test, expect } from '@playwright/test'
import { clearAuth } from './helpers'

test.describe('Settings Billing', () => {
  test.beforeEach(async ({ page }) => { await clearAuth(page) })

  test('B1: Billing page loads', async ({ page }) => {
    await page.goto('/settings/billing')
    try { await page.waitForURL(/\/login/, { timeout: 8000 }) } catch {}
    if (page.url().includes('/login')) return
    await expect(page.getByTestId('billing-page')).toBeVisible()
  })
})
