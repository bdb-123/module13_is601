// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * Negative Flow Tests for User Registration and Login
 * 
 * These tests verify error handling whe      email: `duplicate${timestamp}@example.com`,
      us      email: `wrongpass${timestamp}@example.com`,
      username: `wrongpassuser${timestamp}`,
      correctPassword: 'CorrectPassword123!',
      wrongPassword: 'WrongPassword456!'
    };e: `duplicateuser${timestamp}`,
      password: 'DuplicatePass123!'
    };* 1. Invalid data is submitted (client-side validation)
 * 2. Server returns errors (server-side validation)
 */

test.describe('Registration - Negative Flows', () => {
  
  test('should show error for password shorter than 8 characters', async ({ page }) => {
    // Generate unique test data
    const timestamp = Date.now();
    const testUser = {
      email: `shortpass${timestamp}@example.com`,
      username: `shortpass${timestamp}`,
      password: 'Short1' // Only 6 characters (< 8)
    };
    
    // Navigate to registration page
    await page.goto('/register');
    
    // Verify we're on the registration page
    await expect(page).toHaveURL(/.*register/);
    
    // Fill in the form with short password
    await page.getByTestId('email-input').fill(testUser.email);
    await page.locator('#username').fill(testUser.username);
    await page.locator('#first_name').fill('Short');
    await page.locator('#last_name').fill('Pass');
    await page.getByTestId('password-input').fill(testUser.password);
    await page.getByTestId('confirm-password-input').fill(testUser.password);
    
    // Submit the form
    await page.getByTestId('submit-button').click();
    
    // Wait for validation/response
    await page.waitForTimeout(1500);
    
    // Assert: Error message should be visible
    const errorMessageVisible = await page.getByTestId('error-message').isVisible().catch(() => false);
    
    if (errorMessageVisible) {
      // Error message displayed
      await expect(page.getByTestId('error-message')).toBeVisible();
      
      // Get error text
      const errorText = await page.getByTestId('error-message').textContent();
      console.log(`✓ Error message shown: "${errorText}"`);
      
      // Should mention password length requirement
      expect(errorText.toLowerCase()).toMatch(/password.*8|8.*character/i);
    } else {
      // Check if HTML5 validation prevented submit (browser-level)
      const passwordInput = page.getByTestId('password-input');
      const validationMessage = await passwordInput.evaluate((el) => el.validationMessage);
      
      if (validationMessage) {
        console.log(`✓ Browser validation message: "${validationMessage}"`);
        expect(validationMessage).toBeTruthy();
      } else {
        throw new Error('No error message shown for short password');
      }
    }
    
    // Assert: Token should NOT be stored
    const token = await page.evaluate(() => localStorage.getItem('token'));
    expect(token).toBeNull();
    console.log('✓ No token stored (as expected)');
    
    // Assert: Success message should NOT be visible
    const successMessageVisible = await page.getByTestId('success-message').isVisible().catch(() => false);
    expect(successMessageVisible).toBe(false);
    console.log('✓ No success message shown (as expected)');
  });

  test('should show error for very short password (3 characters)', async ({ page }) => {
    const timestamp = Date.now();
    
    await page.goto('/register');
    
    await page.getByTestId('email-input').fill(`veryshort${timestamp}@example.com`);
    await page.locator('#username').fill(`veryshort${timestamp}`);
    await page.locator('#first_name').fill('Very');
    await page.locator('#last_name').fill('Short');
    await page.getByTestId('password-input').fill('Abc'); // Only 3 characters
    await page.getByTestId('confirm-password-input').fill('Abc');
    await page.getByTestId('submit-button').click();
    
    await page.waitForTimeout(1500);
    
    // Check for error message or browser validation
    const errorVisible = await page.getByTestId('error-message').isVisible().catch(() => false);
    const passwordInput = page.getByTestId('password-input');
    const validationMessage = await passwordInput.evaluate((el) => el.validationMessage);
    
    expect(errorVisible || validationMessage).toBeTruthy();
    console.log('✓ Error shown for 3-character password');
    
    // No token should be stored
    const token = await page.evaluate(() => localStorage.getItem('token'));
    expect(token).toBeNull();
  });

  test('should show error for mismatched passwords', async ({ page }) => {
    const timestamp = Date.now();
    
    await page.goto('/register');
    
    await page.getByTestId('email-input').fill(`mismatch${timestamp}@example.com`);
    await page.locator('#username').fill(`mismatch${timestamp}`);
    await page.locator('#first_name').fill('Mis');
    await page.locator('#last_name').fill('Match');
    await page.getByTestId('password-input').fill('Password123');
    await page.getByTestId('confirm-password-input').fill('DifferentPass456');
    await page.getByTestId('submit-button').click();
    
    await page.waitForTimeout(1500);
    
    // Should show error about passwords not matching
    const errorVisible = await page.getByTestId('error-message').isVisible().catch(() => false);
    
    if (errorVisible) {
      const errorText = await page.getByTestId('error-message').textContent();
      console.log(`✓ Error shown: "${errorText}"`);
      expect(errorText.toLowerCase()).toMatch(/password.*match|match.*password/i);
    } else {
      // Check browser validation
      const confirmInput = page.getByTestId('confirm-password-input');
      const validationMessage = await confirmInput.evaluate((el) => el.validationMessage);
      expect(validationMessage).toBeTruthy();
      console.log(`✓ Browser validation: "${validationMessage}"`);
    }
    
    const token = await page.evaluate(() => localStorage.getItem('token'));
    expect(token).toBeNull();
  });

  test('should show error for invalid email format', async ({ page }) => {
    const timestamp = Date.now();
    
    await page.goto('/register');
    
    await page.getByTestId('email-input').fill('notanemail'); // Invalid format
    await page.locator('#username').fill(`invalidemail${timestamp}`);
    await page.locator('#first_name').fill('Invalid');
    await page.locator('#last_name').fill('Email');
    await page.getByTestId('password-input').fill('Password123');
    await page.getByTestId('confirm-password-input').fill('Password123');
    await page.getByTestId('submit-button').click();
    
    await page.waitForTimeout(1500);
    
    // Check for error message or browser validation
    const errorVisible = await page.getByTestId('error-message').isVisible().catch(() => false);
    const emailInput = page.getByTestId('email-input');
    const validationMessage = await emailInput.evaluate((el) => el.validationMessage);
    
    expect(errorVisible || validationMessage).toBeTruthy();
    console.log('✓ Error shown for invalid email format');
    
    const token = await page.evaluate(() => localStorage.getItem('token'));
    expect(token).toBeNull();
  });

  test('should show error for duplicate email', async ({ page }) => {
    const timestamp = Date.now();
    const duplicateUser = {
      email: `duplicate${timestamp}@example.com`,
      username: `duplicate${timestamp}`,
      password: 'DuplicatePass123'
    };
    
    // First registration - should succeed
    await page.goto('/register');
    await page.getByTestId('email-input').fill(duplicateUser.email);
    await page.locator('#username').fill(duplicateUser.username);
    await page.locator('#first_name').fill('Dup');
    await page.locator('#last_name').fill('User');
    await page.getByTestId('password-input').fill(duplicateUser.password);
    await page.getByTestId('confirm-password-input').fill(duplicateUser.password);
    await page.getByTestId('submit-button').click();
    await page.waitForTimeout(2000);
    
    // Verify first registration succeeded
    const firstToken = await page.evaluate(() => localStorage.getItem('token'));
    const firstSuccessVisible = await page.getByTestId('success-message').isVisible().catch(() => false);
    expect(firstToken || firstSuccessVisible).toBeTruthy();
    console.log('✓ First registration successful');
    
    // Clear token
    await page.evaluate(() => localStorage.clear());
    
    // Try to register again with same email - should fail
    await page.goto('/register');
    await page.getByTestId('email-input').fill(duplicateUser.email); // Same email
    await page.locator('#username').fill(`${duplicateUser.username}2`); // Different username
    await page.locator('#first_name').fill('Dup');
    await page.locator('#last_name').fill('User');
    await page.getByTestId('password-input').fill(duplicateUser.password);
    await page.getByTestId('confirm-password-input').fill(duplicateUser.password);
    await page.getByTestId('submit-button').click();
    await page.waitForTimeout(2000);
    
    // Should show error about duplicate email
    const errorVisible = await page.getByTestId('error-message').isVisible().catch(() => false);
    expect(errorVisible).toBe(true);
    
    const errorText = await page.getByTestId('error-message').textContent();
    console.log(`✓ Duplicate email error: "${errorText}"`);
    expect(errorText.toLowerCase()).toMatch(/email.*exist|already.*registered/i);
    
    // No new token should be stored
    const secondToken = await page.evaluate(() => localStorage.getItem('token'));
    expect(secondToken).toBeNull();
  });
});

test.describe('Login - Negative Flows', () => {
  
  test('should show "Invalid credentials" error for wrong password', async ({ page }) => {
    // First, register a user
    const timestamp = Date.now();
    const testUser = {
      email: `wrongpass${timestamp}@example.com`,
      username: `wrongpass${timestamp}`,
      correctPassword: 'CorrectPassword123',
      wrongPassword: 'WrongPassword456'
    };
    
    // Register the user
    await page.goto('/register');
    await page.getByTestId('email-input').fill(testUser.email);
    await page.locator('#username').fill(testUser.username);
    await page.locator('#first_name').fill('Wrong');
    await page.locator('#last_name').fill('Pass');
    await page.getByTestId('password-input').fill(testUser.correctPassword);
    await page.getByTestId('confirm-password-input').fill(testUser.correctPassword);
    await page.getByTestId('submit-button').click();
    await page.waitForTimeout(2000);
    
    // Verify registration succeeded
    const regToken = await page.evaluate(() => localStorage.getItem('token'));
    expect(regToken).toBeTruthy();
    console.log('✓ User registered successfully');
    
    // Clear storage to simulate fresh login
    await page.evaluate(() => localStorage.clear());
    
    // Now try to login with WRONG password
    await page.goto('/login');
    
    // Verify we're on login page
    await expect(page).toHaveURL(/.*login/);
    
    // Fill login form with wrong password
    await page.getByTestId('email-input').fill(testUser.email);
    await page.getByTestId('password-input').fill(testUser.wrongPassword); // WRONG PASSWORD
    await page.getByTestId('submit-button').click();
    
    // Wait for server response
    await page.waitForTimeout(2000);
    
    // Assert: Error message should be visible
    const errorMessageVisible = await page.getByTestId('error-message').isVisible();
    expect(errorMessageVisible).toBe(true);
    console.log('✓ Error message is visible');
    
    // Get error text
    const errorText = await page.getByTestId('error-message').textContent();
    console.log(`✓ Error message text: "${errorText}"`);
    
    // Should show "Invalid credentials" or similar
    expect(errorText.toLowerCase()).toMatch(/invalid.*credential|incorrect.*password|wrong.*password|authentication.*failed/i);
    console.log('✓ Error message contains "Invalid credentials" or similar');
    
    // Assert: Token should NOT be stored
    const token = await page.evaluate(() => localStorage.getItem('token'));
    expect(token).toBeNull();
    console.log('✓ No token stored (as expected)');
    
    // Assert: Success message should NOT be visible
    const successMessageVisible = await page.getByTestId('success-message').isVisible().catch(() => false);
    expect(successMessageVisible).toBe(false);
    console.log('✓ No success message shown (as expected)');
  });

  test('should show error for non-existent user', async ({ page }) => {
    const timestamp = Date.now();
    const nonExistentEmail = `nonexistent${timestamp}@example.com`;
    
    await page.goto('/login');
    
    await page.getByTestId('email-input').fill(nonExistentEmail);
    await page.getByTestId('password-input').fill('SomePassword123');
    await page.getByTestId('submit-button').click();
    
    await page.waitForTimeout(2000);
    
    // Should show error
    const errorVisible = await page.getByTestId('error-message').isVisible();
    expect(errorVisible).toBe(true);
    
    const errorText = await page.getByTestId('error-message').textContent();
    console.log(`✓ Non-existent user error: "${errorText}"`);
    expect(errorText.toLowerCase()).toMatch(/invalid.*credential|not.*found|does.*not.*exist/i);
    
    // No token stored
    const token = await page.evaluate(() => localStorage.getItem('token'));
    expect(token).toBeNull();
  });

  test('should show error for empty password on login', async ({ page }) => {
    await page.goto('/login');
    
    await page.getByTestId('email-input').fill('someone@example.com');
    await page.getByTestId('password-input').fill(''); // Empty password
    await page.getByTestId('submit-button').click();
    
    await page.waitForTimeout(1500);
    
    // Check for error or browser validation
    const errorVisible = await page.getByTestId('error-message').isVisible().catch(() => false);
    const passwordInput = page.getByTestId('password-input');
    const validationMessage = await passwordInput.evaluate((el) => el.validationMessage);
    
    expect(errorVisible || validationMessage).toBeTruthy();
    console.log('✓ Error shown for empty password');
    
    const token = await page.evaluate(() => localStorage.getItem('token'));
    expect(token).toBeNull();
  });

  test('should show error for invalid email format on login', async ({ page }) => {
    await page.goto('/login');
    
    await page.getByTestId('email-input').fill('notanemail'); // Invalid format
    await page.getByTestId('password-input').fill('Password123');
    await page.getByTestId('submit-button').click();
    
    await page.waitForTimeout(1500);
    
    // Check for error or browser validation
    const errorVisible = await page.getByTestId('error-message').isVisible().catch(() => false);
    const emailInput = page.getByTestId('email-input');
    const validationMessage = await emailInput.evaluate((el) => el.validationMessage);
    
    expect(errorVisible || validationMessage).toBeTruthy();
    console.log('✓ Error shown for invalid email on login');
    
    const token = await page.evaluate(() => localStorage.getItem('token'));
    expect(token).toBeNull();
  });

  test('should show error for short password on login (<8 characters)', async ({ page }) => {
    await page.goto('/login');
    
    await page.getByTestId('email-input').fill('user@example.com');
    await page.getByTestId('password-input').fill('Short1'); // 6 chars
    await page.getByTestId('submit-button').click();
    
    await page.waitForTimeout(1500);
    
    // Should show error (either client-side or after server rejects)
    const errorVisible = await page.getByTestId('error-message').isVisible().catch(() => false);
    const passwordInput = page.getByTestId('password-input');
    const validationMessage = await passwordInput.evaluate((el) => el.validationMessage);
    
    expect(errorVisible || validationMessage).toBeTruthy();
    console.log('✓ Error shown for short password on login');
    
    const token = await page.evaluate(() => localStorage.getItem('token'));
    expect(token).toBeNull();
  });

  test('should prevent multiple failed login attempts', async ({ page }) => {
    const timestamp = Date.now();
    const email = `failedattempts${timestamp}@example.com`;
    
    await page.goto('/login');
    
    // Try 3 failed login attempts
    for (let i = 1; i <= 3; i++) {
      await page.getByTestId('email-input').fill(email);
      await page.getByTestId('password-input').fill(`WrongPass${i}`);
      await page.getByTestId('submit-button').click();
      await page.waitForTimeout(2000);
      
      const errorVisible = await page.getByTestId('error-message').isVisible();
      expect(errorVisible).toBe(true);
      console.log(`✓ Attempt ${i}: Error shown for failed login`);
      
      const token = await page.evaluate(() => localStorage.getItem('token'));
      expect(token).toBeNull();
      
      // Clear form for next attempt
      if (i < 3) {
        await page.evaluate(() => {
          document.getElementById('email').value = '';
          document.getElementById('password').value = '';
        });
      }
    }
    
    console.log('✓ All 3 failed login attempts properly rejected');
  });
});

test.describe('Combined Negative Scenarios', () => {
  
  test('should handle registration then failed login gracefully', async ({ page }) => {
    const timestamp = Date.now();
    const user = {
      email: `combined${timestamp}@example.com`,
      username: `combined${timestamp}`,
      correctPassword: 'CorrectPass123!',
      wrongPassword: 'WrongPass456!'
    };
    
    // Register successfully
    await page.goto('/register');
    await page.getByTestId('email-input').fill(user.email);
    await page.locator('#username').fill(user.username);
    await page.locator('#first_name').fill('Combined');
    await page.locator('#last_name').fill('Test');
    await page.getByTestId('password-input').fill(user.correctPassword);
    await page.getByTestId('confirm-password-input').fill(user.correctPassword);
    await page.getByTestId('submit-button').click();
    await page.waitForTimeout(2000);
    
    const regToken = await page.evaluate(() => localStorage.getItem('token'));
    expect(regToken).toBeTruthy();
    console.log('✓ Registration successful');
    
    // Clear storage
    await page.evaluate(() => localStorage.clear());
    
    // Try to login with wrong password
    await page.goto('/login');
    await page.getByTestId('email-input').fill(user.email);
    await page.getByTestId('password-input').fill(user.wrongPassword);
    await page.getByTestId('submit-button').click();
    await page.waitForTimeout(2000);
    
    // Should fail
    const errorVisible = await page.getByTestId('error-message').isVisible();
    expect(errorVisible).toBe(true);
    const token = await page.evaluate(() => localStorage.getItem('token'));
    expect(token).toBeNull();
    console.log('✓ Login with wrong password failed (as expected)');
    
    // Now login with correct password
    await page.getByTestId('email-input').fill(user.email);
    await page.getByTestId('password-input').fill(user.correctPassword);
    await page.getByTestId('submit-button').click();
    await page.waitForTimeout(2000);
    
    // Should succeed
    const successToken = await page.evaluate(() => localStorage.getItem('token'));
    const successVisible = await page.getByTestId('success-message').isVisible().catch(() => false);
    expect(successToken || successVisible).toBeTruthy();
    console.log('✓ Login with correct password successful');
  });
});
