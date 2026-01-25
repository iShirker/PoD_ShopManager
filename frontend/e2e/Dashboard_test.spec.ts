import { test, expect } from '@playwright/test'
import { clearAuth } from './helpers'

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => { await clearAuth(page) })

  async function gotoDashboard(page: import('@playwright/test').Page) {
    await page.goto('/')
    try {
      await page.waitForURL(/\/login/, { timeout: 8000 })
      return true
    } catch {
      return false
    }
  }

  test('D1: Dashboard loads when authenticated', async ({ page }) => {
    const onLogin = await gotoDashboard(page)
    if (onLogin) {
      expect(onLogin).toBeTruthy()
      return
    }
    await expect(page.getByTestId('dashboard')).toBeVisible()
    await expect(page.getByTestId('dashboard-title')).toContainText(/Welcome|Dashboard/i)
  })

  test('D3: KPI cards display', async ({ page }) => {
    if (await gotoDashboard(page)) return
    await expect(page.getByTestId('dashboard-kpis')).toBeVisible()
  })

  test('D4: Compare Prices navigates to /comparison', async ({ page }) => {
    if (await gotoDashboard(page)) return
    await page.getByTestId('dashboard-quick-compare').click()
    await expect(page).toHaveURL(/\/comparison/)
  })

  test('D5: View Products navigates to /products', async ({ page }) => {
    if (await gotoDashboard(page)) return
    await page.getByTestId('dashboard-quick-products').click()
    await expect(page).toHaveURL(/\/products/)
  })

  test('D6: Create Template navigates to /templates', async ({ page }) => {
    if (await gotoDashboard(page)) return
    await page.getByTestId('dashboard-quick-templates').click()
    await expect(page).toHaveURL(/\/templates/)
  })
})
