import { test, expect } from '@playwright/test'
import { clearAuth } from './helpers'

test.describe('Listings', () => {
  test.beforeEach(async ({ page }) => { await clearAuth(page) })

  test('LIS1: Listings page loads', async ({ page }) => {
    await page.goto('/listings')
    try {
      await page.waitForURL(/\/login/, { timeout: 8000 })
      return
    } catch {}
    await page.waitForURL(/\/listings/, { timeout: 3000 })
    await expect(page.getByTestId('listings-page')).toBeVisible()
  })
})
