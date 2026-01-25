import { test, expect } from '@playwright/test'

test.describe('Version / Deployment check', () => {
  test('V1: /version loads', async ({ page }) => {
    await page.goto('/version')
    await expect(page.getByTestId('frontend-build')).toBeVisible()
    await expect(page.getByText('Deployment check')).toBeVisible()
  })

  test('V2: Backend health fetched', async ({ page }) => {
    await page.goto('/version')
    await page.waitForSelector('[data-testid="backend-status"], [data-testid="backend-error"]', { timeout: 10000 })
    const status = page.getByTestId('backend-status')
    const err = page.getByTestId('backend-error')
    const hasStatus = await status.isVisible().catch(() => false)
    const hasError = await err.isVisible().catch(() => false)
    expect(hasStatus || hasError).toBeTruthy()
  })

  test('V3: deployment-ok when healthy', async ({ page }) => {
    await page.goto('/version')
    await page.waitForSelector('[data-testid="backend-status"], [data-testid="backend-error"]', { timeout: 10000 })
    const err = page.getByTestId('backend-error')
    const hasError = await err.isVisible().catch(() => false)
    if (hasError) return
    const ok = page.getByTestId('deployment-ok')
    await expect(ok).toBeVisible({ timeout: 5000 })
  })
})
