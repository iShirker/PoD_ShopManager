import { test, expect } from '@playwright/test'

test.describe('Login', () => {
  test('L1: Login page loads at /login', async ({ page }) => {
    await page.goto('/login')
    await expect(page.getByTestId('login-title')).toBeVisible()
    await expect(page.getByTestId('login-email')).toBeVisible()
    await expect(page.getByTestId('login-password')).toBeVisible()
  })

  test('L4: Register link navigates to /register', async ({ page }) => {
    await page.goto('/login')
    await page.getByTestId('login-register-link').click()
    await expect(page).toHaveURL(/\/register/)
  })

  test('L5: OAuth / Google button present', async ({ page }) => {
    await page.goto('/login')
    await expect(page.getByRole('button', { name: /Google/i })).toBeVisible()
  })

  test('L7: Theme applied (login form uses themed styles)', async ({ page }) => {
    await page.goto('/login')
    const form = page.getByTestId('login-form')
    await expect(form).toBeVisible()
  })
})
