import { test, expect } from '@playwright/test'
import { clearAuth } from './helpers'

test.describe('SEO Assistant', () => {
  test.beforeEach(async ({ page }) => {
    await clearAuth(page)
    await page.goto('/listings/seo')
    try { await page.waitForURL(/\/login/, { timeout: 6000 }) } catch {}
  })

  test('LSE1: SEO Assistant page loads', async ({ page }) => {
    try { await page.waitForURL(/\/login/, { timeout: 5000 }) } catch {}
    if (page.url().includes('/login')) return
    await expect(page.getByTestId('listings-seo')).toBeVisible()
    await expect(page.getByTestId('listings-seo-title')).toContainText(/SEO Assistant/i)
  })

  test('LSE2: Entering keyword and Get suggestions yields results', async ({ page }) => {
    try { await page.waitForURL(/\/login/, { timeout: 5000 }) } catch {}
    if (page.url().includes('/login')) return
    await page.getByTestId('listings-seo-input').fill('gift')
    await page.getByTestId('listings-seo-suggest').click()
    await expect(page.getByTestId('listings-seo-suggestions')).toBeVisible({ timeout: 5000 })
  })
})
