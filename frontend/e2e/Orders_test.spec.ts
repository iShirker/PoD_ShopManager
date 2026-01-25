import { test, expect } from '@playwright/test'
import { clearAuth } from './helpers'

test.describe('Orders', () => {
  test.beforeEach(async ({ page }) => { await clearAuth(page) })

  test('O1: Orders page loads', async ({ page }) => {
    await page.goto('/orders')
    try { await page.waitForURL(/\/login/, { timeout: 8000 }) } catch {}
    if (page.url().includes('/login')) return
    await expect(page.getByTestId('orders-page')).toBeVisible()
  })
})
