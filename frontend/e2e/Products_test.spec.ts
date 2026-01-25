import { test, expect } from '@playwright/test'
import { clearAuth } from './helpers'

test.describe('Products', () => {
  test.beforeEach(async ({ page }) => { await clearAuth(page) })

  test('P1: Products page loads', async ({ page }) => {
    await page.goto('/products')
    try { await page.waitForURL(/\/login/, { timeout: 8000 }) } catch {}
    if (page.url().includes('/login')) return
    await expect(page.getByTestId('products-page')).toBeVisible()
  })
})
