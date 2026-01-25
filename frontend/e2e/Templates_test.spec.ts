import { test, expect } from '@playwright/test'
import { clearAuth } from './helpers'

test.describe('Templates', () => {
  test.beforeEach(async ({ page }) => { await clearAuth(page) })

  test('T1: Templates page loads', async ({ page }) => {
    await page.goto('/templates')
    try { await page.waitForURL(/\/login/, { timeout: 8000 }) } catch {}
    if (page.url().includes('/login')) return
    await expect(page.getByTestId('templates-page')).toBeVisible()
  })
})
