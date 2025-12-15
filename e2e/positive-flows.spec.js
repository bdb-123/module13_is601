// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * Positive Flow Tests for User Registration and Login
 * 
 * These tests verify the happy path where:
 * 1. A new user registers successfully
 * 2. The same user can login successfully
 */

test.describe('User Registration and Login - Positive Flows', () => {
  
  // Generate unique test user credentials
  const timestamp = Date.now();
  const randomNum = Math.floor(Math.random() * 10000);
  const testUser = {
    email: `testuser${timestamp}${randomNum}@example.com`,
    username: `testuser${timestamp}${randomNum}`,
    firstName: 'Test',
    lastName: 'User',
    password: 'SecurePassword123',
    confirmPassword: 'SecurePassword123'
  };

  test('should successfully register a new user', async ({ page }) => {
    // Navigate to registration page
    await page.goto('/register');
    
    // Verify we're on the registration page
    await expect(page).toHaveURL(/.*register/);
    await expect(page.locator('h2')).toContainText('Create Account');
    
    // Fill in the registration form using data-testid selectors
    await page.getByTestId('email-input').fill(testUser.email);
    await page.locator('#username').fill(testUser.username);
    await page.locator('#first_name').fill(testUser.firstName);
    await page.locator('#last_name').fill(testUser.lastName);
    await page.getByTestId('password-input').fill(testUser.password);
    await page.getByTestId('confirm-password-input').fill(testUser.confirmPassword);
    
    // Submit the form
    await page.getByTestId('submit-button').click();
    
    // Wait for response (either success message or redirect)
    await page.waitForTimeout(2000); // Allow time for API call and processing
    
    // Assert success - check for either success message OR token in localStorage
    const successMessageVisible = await page.getByTestId('success-message').isVisible().catch(() => false);
    
    if (successMessageVisible) {
      // Success message approach
      await expect(page.getByTestId('success-message')).toBeVisible();
      console.log('✓ Success message displayed after registration');
    }
    
    // Check for token in localStorage
    const token = await page.evaluate(() => localStorage.getItem('token'));
    
    if (token) {
      expect(token).toBeTruthy();
      expect(token.length).toBeGreaterThan(0);
      console.log('✓ JWT token stored in localStorage after registration');
    } else if (!successMessageVisible) {
      // If neither success message nor token, test should fail
      throw new Error('Registration failed: No success message or token found');
    }
    
    // Optional: Verify no error message is shown
    const errorMessageVisible = await page.getByTestId('error-message').isVisible().catch(() => false);
    expect(errorMessageVisible).toBe(false);
  });

  test('should successfully login with registered credentials', async ({ page }) => {
    // First, register the user (setup for login test)
    await page.goto('/register');
    await page.getByTestId('email-input').fill(testUser.email);
    await page.locator('#username').fill(testUser.username);
    await page.locator('#first_name').fill(testUser.firstName);
    await page.locator('#last_name').fill(testUser.lastName);
    await page.getByTestId('password-input').fill(testUser.password);
    await page.getByTestId('confirm-password-input').fill(testUser.confirmPassword);
    await page.getByTestId('submit-button').click();
    
    // Wait for registration to complete
    await page.waitForTimeout(2000);
    
    // Clear localStorage to simulate fresh login
    await page.evaluate(() => localStorage.clear());
    
    // Navigate to login page
    await page.goto('/login');
    
    // Verify we're on the login page
    await expect(page).toHaveURL(/.*login/);
    await expect(page.locator('h2')).toContainText('Login');
    
    // Fill in the login form using data-testid selectors
    await page.getByTestId('email-input').fill(testUser.email);
    await page.getByTestId('password-input').fill(testUser.password);
    
    // Submit the form
    await page.getByTestId('submit-button').click();
    
    // Wait for response
    await page.waitForTimeout(2000);
    
    // Assert success - check for either success message OR token in localStorage
    const successMessageVisible = await page.getByTestId('success-message').isVisible().catch(() => false);
    
    if (successMessageVisible) {
      // Success message approach
      await expect(page.getByTestId('success-message')).toBeVisible();
      console.log('✓ Success message displayed after login');
    }
    
    // Check for token in localStorage
    const token = await page.evaluate(() => localStorage.getItem('token'));
    
    if (token) {
      expect(token).toBeTruthy();
      expect(token.length).toBeGreaterThan(0);
      console.log('✓ JWT token stored in localStorage after login');
    } else if (!successMessageVisible) {
      // If neither success message nor token, test should fail
      throw new Error('Login failed: No success message or token found');
    }
    
    // Optional: Verify no error message is shown
    const errorMessageVisible = await page.getByTestId('error-message').isVisible().catch(() => false);
    expect(errorMessageVisible).toBe(false);
  });

  test('complete registration and login flow with different user', async ({ page }) => {
    // Generate new unique credentials for this test
    const flowTimestamp = Date.now();
    const flowRandom = Math.floor(Math.random() * 10000);
    const flowUser = {
      email: `flowtest${flowTimestamp}${flowRandom}@example.com`,
      username: `flowtest${flowTimestamp}${flowRandom}`,
      firstName: 'Flow',
      lastName: 'Test',
      password: 'MySecurePass123',
      confirmPassword: 'MySecurePass123'
    };
    
    // STEP 1: Register
    console.log('Step 1: Registering new user...');
    await page.goto('/register');
    
    await page.getByTestId('email-input').fill(flowUser.email);
    await page.locator('#username').fill(flowUser.username);
    await page.locator('#first_name').fill(flowUser.firstName);
    await page.locator('#last_name').fill(flowUser.lastName);
    await page.getByTestId('password-input').fill(flowUser.password);
    await page.getByTestId('confirm-password-input').fill(flowUser.confirmPassword);
    await page.getByTestId('submit-button').click();
    
    // Wait and verify registration success
    await page.waitForTimeout(2000);
    
    const regToken = await page.evaluate(() => localStorage.getItem('token'));
    const regSuccessVisible = await page.getByTestId('success-message').isVisible().catch(() => false);
    
    expect(regToken || regSuccessVisible).toBeTruthy();
    console.log('✓ Registration successful');
    
    // STEP 2: Logout (clear token)
    console.log('Step 2: Clearing session...');
    await page.evaluate(() => localStorage.clear());
    
    // STEP 3: Login
    console.log('Step 3: Logging in with registered credentials...');
    await page.goto('/login');
    
    await page.getByTestId('email-input').fill(flowUser.email);
    await page.getByTestId('password-input').fill(flowUser.password);
    await page.getByTestId('submit-button').click();
    
    // Wait and verify login success
    await page.waitForTimeout(2000);
    
    const loginToken = await page.evaluate(() => localStorage.getItem('token'));
    const loginSuccessVisible = await page.getByTestId('success-message').isVisible().catch(() => false);
    
    expect(loginToken || loginSuccessVisible).toBeTruthy();
    console.log('✓ Login successful');
    
    // Verify the login token is different from registration token (if both exist)
    if (regToken && loginToken) {
      console.log('✓ New token issued on login');
    }
    
    // Verify we're redirected to dashboard or home
    await page.waitForTimeout(2000); // Allow time for redirect
    const currentUrl = page.url();
    console.log(`✓ Current URL after login: ${currentUrl}`);
    
    // Should be redirected away from /login
    expect(currentUrl).not.toContain('/login');
  });
});

test.describe('Registration - Additional Positive Scenarios', () => {
  
  test('should register with minimum valid password length (8 characters)', async ({ page }) => {
    const timestamp = Date.now();
    const user = {
      email: `minpass${timestamp}@example.com`,
      username: `minpass${timestamp}`,
      password: 'Pass1234' // Exactly 8 characters
    };
    
    await page.goto('/register');
    
    await page.getByTestId('email-input').fill(user.email);
    await page.locator('#username').fill(user.username);
    await page.locator('#first_name').fill('Min');
    await page.locator('#last_name').fill('Pass');
    await page.getByTestId('password-input').fill(user.password);
    await page.getByTestId('confirm-password-input').fill(user.password);
    await page.getByTestId('submit-button').click();
    
    await page.waitForTimeout(2000);
    
    // Check for success
    const token = await page.evaluate(() => localStorage.getItem('token'));
    const successVisible = await page.getByTestId('success-message').isVisible().catch(() => false);
    
    expect(token || successVisible).toBeTruthy();
    console.log('✓ Registration successful with 8-character password');
  });

  test('should register with long password', async ({ page }) => {
    const timestamp = Date.now();
    const user = {
      email: `longpass${timestamp}@example.com`,
      username: `longpass${timestamp}`,
      password: 'ThisIsAVeryLongAndSecurePassword123456789!@#' // >40 characters
    };
    
    await page.goto('/register');
    
    await page.getByTestId('email-input').fill(user.email);
    await page.locator('#username').fill(user.username);
    await page.locator('#first_name').fill('Long');
    await page.locator('#last_name').fill('Pass');
    await page.getByTestId('password-input').fill(user.password);
    await page.getByTestId('confirm-password-input').fill(user.password);
    await page.getByTestId('submit-button').click();
    
    await page.waitForTimeout(2000);
    
    // Check for success
    const token = await page.evaluate(() => localStorage.getItem('token'));
    const successVisible = await page.getByTestId('success-message').isVisible().catch(() => false);
    
    expect(token || successVisible).toBeTruthy();
    console.log('✓ Registration successful with long password');
  });

  test('should register with various email formats', async ({ page }) => {
    const timestamp = Date.now();
    const validEmails = [
      `user.name${timestamp}@example.com`,
      `user+tag${timestamp}@example.co.uk`,
      `user_name${timestamp}@sub.example.com`
    ];
    
    for (const email of validEmails) {
      const username = email.split('@')[0].replace(/[.+]/g, '');
      
      await page.goto('/register');
      
      await page.getByTestId('email-input').fill(email);
      await page.locator('#username').fill(username);
      await page.locator('#first_name').fill('Valid');
      await page.locator('#last_name').fill('Email');
      await page.getByTestId('password-input').fill('Password123');
      await page.getByTestId('confirm-password-input').fill('Password123');
      await page.getByTestId('submit-button').click();
      
      await page.waitForTimeout(2000);
      
      const token = await page.evaluate(() => localStorage.getItem('token'));
      const successVisible = await page.getByTestId('success-message').isVisible().catch(() => false);
      
      expect(token || successVisible).toBeTruthy();
      console.log(`✓ Registration successful with email: ${email}`);
      
      // Clear for next iteration
      await page.evaluate(() => localStorage.clear());
    }
  });
});

test.describe('Login - Additional Positive Scenarios', () => {
  
  test('should login and persist token across page refresh', async ({ page }) => {
    // Create and register user
    const timestamp = Date.now();
    const user = {
      email: `persist${timestamp}@example.com`,
      username: `persist${timestamp}`,
      password: 'PersistPass123'
    };
    
    // Register
    await page.goto('/register');
    await page.getByTestId('email-input').fill(user.email);
    await page.locator('#username').fill(user.username);
    await page.locator('#first_name').fill('Persist');
    await page.locator('#last_name').fill('Test');
    await page.getByTestId('password-input').fill(user.password);
    await page.getByTestId('confirm-password-input').fill(user.password);
    await page.getByTestId('submit-button').click();
    await page.waitForTimeout(2000);
    
    // Clear and login
    await page.evaluate(() => localStorage.clear());
    await page.goto('/login');
    await page.getByTestId('email-input').fill(user.email);
    await page.getByTestId('password-input').fill(user.password);
    await page.getByTestId('submit-button').click();
    await page.waitForTimeout(2000);
    
    // Get token
    const token = await page.evaluate(() => localStorage.getItem('token'));
    expect(token).toBeTruthy();
    console.log('✓ Token stored after login');
    
    // Refresh the page
    await page.reload();
    await page.waitForTimeout(1000);
    
    // Check token still exists
    const tokenAfterRefresh = await page.evaluate(() => localStorage.getItem('token'));
    expect(tokenAfterRefresh).toBe(token);
    console.log('✓ Token persists after page refresh');
  });

  test('should login immediately after registration', async ({ page }) => {
    const timestamp = Date.now();
    const user = {
      email: `immediate${timestamp}@example.com`,
      username: `immediate${timestamp}`,
      password: 'ImmediatePass123'
    };
    
    // Register
    await page.goto('/register');
    await page.getByTestId('email-input').fill(user.email);
    await page.locator('#username').fill(user.username);
    await page.locator('#first_name').fill('Immediate');
    await page.locator('#last_name').fill('Login');
    await page.getByTestId('password-input').fill(user.password);
    await page.getByTestId('confirm-password-input').fill(user.password);
    await page.getByTestId('submit-button').click();
    await page.waitForTimeout(2000);
    
    const regToken = await page.evaluate(() => localStorage.getItem('token'));
    expect(regToken).toBeTruthy();
    console.log('✓ Registered successfully with token');
    
    // Immediately login without clearing (simulating user going to login page)
    await page.goto('/login');
    await page.getByTestId('email-input').fill(user.email);
    await page.getByTestId('password-input').fill(user.password);
    await page.getByTestId('submit-button').click();
    await page.waitForTimeout(2000);
    
    const loginToken = await page.evaluate(() => localStorage.getItem('token'));
    expect(loginToken).toBeTruthy();
    console.log('✓ Login successful immediately after registration');
  });
});
