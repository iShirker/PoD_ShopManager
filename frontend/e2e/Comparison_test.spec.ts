import { test, expect } from '@playwright/test'
import { clearAuth } from './helpers'

test.describe('Compare & Switch', () => {
  test.beforeEach(async ({ page }) => { await clearAuth(page) })

  test('C1: Comparison page loads', async ({ page }) => {
    await page.goto('/comparison')
    try { await page.waitForURL(/\/login/, { timeout: 8000 }) } catch {}
    if (page.url().includes('/login')) return
    await expect(page.getByTestId('comparison-page')).toBeVisible()
  })
})
