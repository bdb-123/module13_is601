// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * Example test to verify Playwright setup is working
 */
test.describe('Playwright Setup Verification', () => {
  
  test('should verify server is running', async ({ page }) => {
    // Navigate to home page
    await page.goto('/');
    
    // Check that we get a response (not a connection error)
    await expect(page).toHaveURL(/localhost:8000/);
  });
  
  test('should have accessible health endpoint', async ({ page }) => {
    // Try to access the health endpoint
    const response = await page.request.get('/health');
    
    // Check that it returns 200 OK
    expect(response.ok()).toBeTruthy();
    expect(response.status()).toBe(200);
  });
});
