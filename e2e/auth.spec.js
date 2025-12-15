// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Authentication Flow', () => {
  
  test('should load login page', async ({ page }) => {
    await page.goto('/login');
    
    await expect(page).toHaveTitle(/Login/);
    await expect(page.locator('h2')).toContainText('Login');
    
    // Check form elements exist using data-testid
    await expect(page.getByTestId('email-input')).toBeVisible();
    await expect(page.getByTestId('password-input')).toBeVisible();
    await expect(page.getByTestId('submit-button')).toBeVisible();
  });
  
  test('should load register page', async ({ page }) => {
    await page.goto('/register');
    
    await expect(page).toHaveTitle(/Register/);
    await expect(page.locator('h2')).toContainText('Create Account');
    
    // Check form elements exist using data-testid
    await expect(page.getByTestId('email-input')).toBeVisible();
    await expect(page.getByTestId('password-input')).toBeVisible();
    await expect(page.getByTestId('confirm-password-input')).toBeVisible();
    await expect(page.getByTestId('submit-button')).toBeVisible();
  });
  
  test('should show validation error for invalid email on login', async ({ page }) => {
    await page.goto('/login');
    
    await page.getByTestId('email-input').fill('invalid-email');
    await page.getByTestId('password-input').fill('password123');
    await page.getByTestId('submit-button').click();
    
    // Check for error message
    await expect(page.getByTestId('error-message')).toBeVisible();
  });
  
  test('should show validation error for short password on login', async ({ page }) => {
    await page.goto('/login');
    
    await page.getByTestId('email-input').fill('user@example.com');
    await page.getByTestId('password-input').fill('short');
    await page.getByTestId('submit-button').click();
    
    // Check for error message
    await expect(page.getByTestId('error-message')).toBeVisible();
  });
  
  test('should show validation error for password mismatch on register', async ({ page }) => {
    await page.goto('/register');
    
    await page.getByTestId('email-input').fill('newuser@example.com');
    await page.locator('#username').fill('testuser');
    await page.locator('#first_name').fill('Test');
    await page.locator('#last_name').fill('User');
    await page.getByTestId('password-input').fill('password123');
    await page.getByTestId('confirm-password-input').fill('different123');
    await page.getByTestId('submit-button').click();
    
    // Check for error message
    await expect(page.getByTestId('error-message')).toBeVisible();
  });
  
  test('should navigate from login to register page', async ({ page }) => {
    await page.goto('/login');
    
    await page.click('text=Register here');
    await expect(page).toHaveURL(/.*register/);
    await expect(page.locator('h2')).toContainText('Create Account');
  });
  
  test('should navigate from register to login page', async ({ page }) => {
    await page.goto('/register');
    
    await page.click('text=Login here');
    await expect(page).toHaveURL(/.*login/);
    await expect(page.locator('h2')).toContainText('Login');
  });
});
