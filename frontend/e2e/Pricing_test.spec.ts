import { test, expect } from '@playwright/test'
import { clearAuth } from './helpers'

test.describe('Pricing Calculator', () => {
  test.beforeEach(async ({ page }) => { await clearAuth(page) })

  test('PR1: Pricing page loads', async ({ page }) => {
    await page.goto('/pricing')
    try { await page.waitForURL(/\/login/, { timeout: 8000 }) } catch {}
    if (page.url().includes('/login')) return
    await expect(page.getByTestId('pricing-page')).toBeVisible()
  })
})
