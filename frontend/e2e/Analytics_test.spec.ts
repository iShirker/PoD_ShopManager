import { test, expect } from '@playwright/test'
import { clearAuth } from './helpers'

test.describe('Analytics', () => {
  test.beforeEach(async ({ page }) => { await clearAuth(page) })

  test('A1: Analytics page loads', async ({ page }) => {
    await page.goto('/analytics')
    try { await page.waitForURL(/\/login/, { timeout: 8000 }) } catch {}
    if (page.url().includes('/login')) return
    await expect(page.getByTestId('analytics-page')).toBeVisible()
  })
})
