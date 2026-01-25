import type { Page } from '@playwright/test'

/** Clear auth storage so protected routes redirect to /login. */
export async function clearAuth(page: Page) {
  await page.goto('/')
  await page.evaluate(() => localStorage.clear())
  await page.reload()
}
