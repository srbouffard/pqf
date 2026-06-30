import { test, expect } from '@playwright/test'

test.describe('PQF navigation smoke tests', () => {
  test('homepage loads with Portfolio heading', async ({ page }) => {
    await page.goto('/')
    await expect(page.getByRole('heading', { name: /portfolio/i })).toBeVisible()
  })

  test('About page loads', async ({ page }) => {
    await page.goto('/#/about')
    await expect(page.getByRole('heading', { name: /about pqf/i })).toBeVisible()
    await expect(page.getByRole('heading', { name: /medal levels/i })).toBeVisible()
  })

  test('unknown route redirects to homepage', async ({ page }) => {
    await page.goto('/#/this-does-not-exist')
    await expect(page.getByRole('heading', { name: /portfolio/i })).toBeVisible()
  })

  test('nav links are present', async ({ page }) => {
    await page.goto('/')
    await expect(page.getByRole('link', { name: 'Portfolio' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'About' })).toBeVisible()
  })
})
