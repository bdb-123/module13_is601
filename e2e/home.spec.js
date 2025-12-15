// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Home Page', () => {
  
  test('should load home page', async ({ page }) => {
    await page.goto('/');
    
    // Check that the page loads
    await expect(page).toHaveURL('/');
    
    // Check for common elements (adjust based on your actual home page)
    await expect(page.locator('body')).toBeVisible();
  });
  
  test('should have navigation to login and register', async ({ page }) => {
    await page.goto('/');
    
    // Try to find links to auth pages (adjust selectors based on your layout)
    const loginLink = page.locator('a[href="/login"]');
    const registerLink = page.locator('a[href="/register"]');
    
    // At least one should exist if navigation is present
    const hasAuthLinks = await loginLink.count() > 0 || await registerLink.count() > 0;
    expect(hasAuthLinks).toBeTruthy();
  });
});
