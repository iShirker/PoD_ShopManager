import { test, expect } from '@playwright/test'

test.describe('Register', () => {
  test('R1: Register page loads', async ({ page }) => {
    await page.goto('/register')
    await expect(page.getByText(/Register|Create|account/i).first()).toBeVisible()
  })

  test('R4: Log in link navigates to /login', async ({ page }) => {
    await page.goto('/register')
    await page.getByRole('link', { name: /log in|sign in/i }).first().click()
    await expect(page).toHaveURL(/\/login/)
  })
})
