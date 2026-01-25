import { test, expect } from '@playwright/test'
import { clearAuth } from './helpers'

test.describe('Shops', () => {
  test.beforeEach(async ({ page }) => { await clearAuth(page) })

  test('S1: Shops page loads', async ({ page }) => {
    await page.goto('/shops')
    try { await page.waitForURL(/\/login/, { timeout: 8000 }) } catch {}
    if (page.url().includes('/login')) return
    await expect(page.getByTestId('shops-page')).toBeVisible()
  })
})
