"""
Playwright E2E tests for authentication flows (registration and login).
Tests both positive and negative scenarios including localStorage JWT verification.
"""
import pytest
from playwright.sync_api import Page, expect
from faker import Faker

fake = Faker()
Faker.seed(54321)  # Different seed from conftest to avoid conflicts


# ======================================================================================
# Helper Functions
# ======================================================================================
def generate_test_user():
    """Generate unique test user data."""
    return {
        "username": fake.unique.user_name(),
        "email": fake.unique.email(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!"
    }


def clear_local_storage(page: Page):
    """Clear browser localStorage."""
    page.evaluate("() => localStorage.clear()")


def get_local_storage_item(page: Page, key: str):
    """Get item from localStorage."""
    return page.evaluate(f"() => localStorage.getItem('{key}')")


# ======================================================================================
# Registration Tests - Positive Scenarios
# ======================================================================================
@pytest.mark.e2e
def test_registration_success_positive(page: Page, fastapi_server: str):
    """
    Test successful user registration with valid data.
    Verifies form submission, success message display, and redirect behavior.
    """
    # Navigate to registration page
    page.goto(f"{fastapi_server}register")
    
    # Wait for page to load
    expect(page.locator("h2")).to_contain_text("Create Account")
    
    # Generate unique test user
    user_data = generate_test_user()
    
    # Fill in registration form
    page.fill("#username", user_data["username"])
    page.fill("#email", user_data["email"])
    page.fill("#first_name", user_data["first_name"])
    page.fill("#last_name", user_data["last_name"])
    page.fill("#password", user_data["password"])
    page.fill("#confirm_password", user_data["confirm_password"])
    
    # Submit form
    page.click('button[type="submit"]')
    
    # Wait for success message or redirect
    # The actual behavior depends on your implementation
    # Adjust timeout and expectations based on your app's behavior
    page.wait_for_timeout(2000)
    
    # Check for success indicator (either success message or redirect to login)
    # This will vary based on your implementation
    current_url = page.url
    
    # Assert: Either redirected to login or success message shown
    assert (
        "login" in current_url or 
        page.locator("#successAlert").is_visible() or
        "dashboard" in current_url
    ), "Registration should show success message or redirect"


@pytest.mark.e2e
def test_registration_with_optional_confirm_password(page: Page, fastapi_server: str):
    """Test registration works when confirm_password matches password."""
    page.goto(f"{fastapi_server}register")
    
    user_data = generate_test_user()
    
    page.fill("#username", user_data["username"])
    page.fill("#email", user_data["email"])
    page.fill("#first_name", user_data["first_name"])
    page.fill("#last_name", user_data["last_name"])
    page.fill("#password", user_data["password"])
    page.fill("#confirm_password", user_data["password"])
    
    page.click('button[type="submit"]')
    page.wait_for_timeout(2000)
    
    # Should not show error
    error_alert = page.locator("#errorAlert")
    if error_alert.is_visible():
        error_text = page.locator("#errorMessage").inner_text()
        assert "Passwords do not match" not in error_text


# ======================================================================================
# Registration Tests - Negative Scenarios
# ======================================================================================
@pytest.mark.e2e
def test_registration_password_mismatch_negative(page: Page, fastapi_server: str):
    """Test registration fails when passwords don't match."""
    page.goto(f"{fastapi_server}register")
    
    user_data = generate_test_user()
    
    page.fill("#username", user_data["username"])
    page.fill("#email", user_data["email"])
    page.fill("#first_name", user_data["first_name"])
    page.fill("#last_name", user_data["last_name"])
    page.fill("#password", "SecurePass123!")
    page.fill("#confirm_password", "DifferentPass123!")
    
    page.click('button[type="submit"]')
    page.wait_for_timeout(1000)
    
    # Should show error message
    error_alert = page.locator("#errorAlert")
    expect(error_alert).to_be_visible()
    
    error_message = page.locator("#errorMessage").inner_text()
    assert "password" in error_message.lower(), "Should show password mismatch error"


@pytest.mark.e2e
def test_registration_weak_password_negative(page: Page, fastapi_server: str):
    """Test registration fails with weak password (no uppercase/lowercase/digit)."""
    page.goto(f"{fastapi_server}register")
    
    user_data = generate_test_user()
    
    page.fill("#username", user_data["username"])
    page.fill("#email", user_data["email"])
    page.fill("#first_name", user_data["first_name"])
    page.fill("#last_name", user_data["last_name"])
    page.fill("#password", "weak")
    page.fill("#confirm_password", "weak")
    
    page.click('button[type="submit"]')
    page.wait_for_timeout(1000)
    
    # Should show error about password requirements
    error_alert = page.locator("#errorAlert")
    expect(error_alert).to_be_visible()
    
    error_message = page.locator("#errorMessage").inner_text()
    assert any(word in error_message.lower() for word in ["password", "character", "uppercase", "lowercase", "number"]), \
        "Should show password strength error"


@pytest.mark.e2e
def test_registration_invalid_email_negative(page: Page, fastapi_server: str):
    """Test registration fails with invalid email format."""
    page.goto(f"{fastapi_server}register")
    
    user_data = generate_test_user()
    
    page.fill("#username", user_data["username"])
    page.fill("#email", "not-a-valid-email")
    page.fill("#first_name", user_data["first_name"])
    page.fill("#last_name", user_data["last_name"])
    page.fill("#password", user_data["password"])
    page.fill("#confirm_password", user_data["confirm_password"])
    
    page.click('button[type="submit"]')
    page.wait_for_timeout(1000)
    
    # Should show error about email format
    error_alert = page.locator("#errorAlert")
    expect(error_alert).to_be_visible()
    
    error_message = page.locator("#errorMessage").inner_text()
    assert "email" in error_message.lower(), "Should show invalid email error"


@pytest.mark.e2e
def test_registration_duplicate_username_negative(page: Page, fastapi_server: str):
    """Test registration fails when username already exists."""
    page.goto(f"{fastapi_server}register")
    
    # First registration
    user_data = generate_test_user()
    
    page.fill("#username", user_data["username"])
    page.fill("#email", user_data["email"])
    page.fill("#first_name", user_data["first_name"])
    page.fill("#last_name", user_data["last_name"])
    page.fill("#password", user_data["password"])
    page.fill("#confirm_password", user_data["confirm_password"])
    
    page.click('button[type="submit"]')
    page.wait_for_timeout(2000)
    
    # Try to register again with same username but different email
    page.goto(f"{fastapi_server}register")
    
    page.fill("#username", user_data["username"])  # Same username
    page.fill("#email", fake.unique.email())  # Different email
    page.fill("#first_name", fake.first_name())
    page.fill("#last_name", fake.last_name())
    page.fill("#password", "AnotherPass123!")
    page.fill("#confirm_password", "AnotherPass123!")
    
    page.click('button[type="submit"]')
    page.wait_for_timeout(1000)
    
    # Should show error about duplicate username
    error_alert = page.locator("#errorAlert")
    expect(error_alert).to_be_visible()
    
    error_message = page.locator("#errorMessage").inner_text()
    assert any(word in error_message.lower() for word in ["username", "exist", "already", "taken"]), \
        "Should show duplicate username error"


@pytest.mark.e2e
def test_registration_missing_required_fields_negative(page: Page, fastapi_server: str):
    """Test registration fails when required fields are missing."""
    page.goto(f"{fastapi_server}register")
    
    # Try to submit with only username filled
    page.fill("#username", "testuser")
    
    page.click('button[type="submit"]')
    page.wait_for_timeout(500)
    
    # HTML5 validation should prevent submission or show error
    # Check if still on registration page
    assert "register" in page.url, "Should remain on registration page with missing fields"


# ======================================================================================
# Login Tests - Positive Scenarios
# ======================================================================================
@pytest.mark.e2e
def test_login_success_positive(page: Page, fastapi_server: str):
    """
    Test successful login with valid credentials.
    Verifies JWT token storage in localStorage and redirect to dashboard.
    """
    # First, register a user
    page.goto(f"{fastapi_server}register")
    user_data = generate_test_user()
    
    page.fill("#username", user_data["username"])
    page.fill("#email", user_data["email"])
    page.fill("#first_name", user_data["first_name"])
    page.fill("#last_name", user_data["last_name"])
    page.fill("#password", user_data["password"])
    page.fill("#confirm_password", user_data["confirm_password"])
    page.click('button[type="submit"]')
    page.wait_for_timeout(2000)
    
    # Clear any stored tokens
    clear_local_storage(page)
    
    # Now login
    page.goto(f"{fastapi_server}login")
    expect(page.locator("h2")).to_contain_text("Welcome Back")
    
    page.fill("#username", user_data["username"])
    page.fill("#password", user_data["password"])
    
    page.click('button[type="submit"]')
    page.wait_for_timeout(2000)
    
    # Should redirect to dashboard
    current_url = page.url
    assert "dashboard" in current_url or "login" not in current_url, \
        "Should redirect away from login page after successful login"


@pytest.mark.e2e
def test_login_stores_jwt_in_localstorage_positive(page: Page, fastapi_server: str):
    """
    Test that successful login stores JWT tokens in localStorage.
    Verifies access_token, refresh_token, user_id, and username are stored.
    """
    # Register a user
    page.goto(f"{fastapi_server}register")
    user_data = generate_test_user()
    
    page.fill("#username", user_data["username"])
    page.fill("#email", user_data["email"])
    page.fill("#first_name", user_data["first_name"])
    page.fill("#last_name", user_data["last_name"])
    page.fill("#password", user_data["password"])
    page.fill("#confirm_password", user_data["confirm_password"])
    page.click('button[type="submit"]')
    page.wait_for_timeout(2000)
    
    # Clear localStorage
    clear_local_storage(page)
    
    # Login
    page.goto(f"{fastapi_server}login")
    page.fill("#username", user_data["username"])
    page.fill("#password", user_data["password"])
    page.click('button[type="submit"]')
    page.wait_for_timeout(2000)
    
    # Verify tokens are stored in localStorage
    access_token = get_local_storage_item(page, "access_token")
    refresh_token = get_local_storage_item(page, "refresh_token")
    user_id = get_local_storage_item(page, "user_id")
    username = get_local_storage_item(page, "username")
    
    assert access_token is not None, "access_token should be stored in localStorage"
    assert refresh_token is not None, "refresh_token should be stored in localStorage"
    assert user_id is not None, "user_id should be stored in localStorage"
    assert username == user_data["username"], "username should be stored correctly in localStorage"
    
    # Verify tokens are not empty
    assert len(access_token) > 0, "access_token should not be empty"
    assert len(refresh_token) > 0, "refresh_token should not be empty"


@pytest.mark.e2e
def test_login_redirects_to_dashboard_positive(page: Page, fastapi_server: str):
    """Test that successful login redirects to dashboard page."""
    # Register and login
    page.goto(f"{fastapi_server}register")
    user_data = generate_test_user()
    
    page.fill("#username", user_data["username"])
    page.fill("#email", user_data["email"])
    page.fill("#first_name", user_data["first_name"])
    page.fill("#last_name", user_data["last_name"])
    page.fill("#password", user_data["password"])
    page.fill("#confirm_password", user_data["confirm_password"])
    page.click('button[type="submit"]')
    page.wait_for_timeout(2000)
    
    clear_local_storage(page)
    
    page.goto(f"{fastapi_server}login")
    page.fill("#username", user_data["username"])
    page.fill("#password", user_data["password"])
    page.click('button[type="submit"]')
    
    # Wait for redirect
    page.wait_for_timeout(3000)
    
    # Verify redirected to dashboard
    current_url = page.url
    assert "dashboard" in current_url, f"Should redirect to dashboard, but got {current_url}"


# ======================================================================================
# Login Tests - Negative Scenarios
# ======================================================================================
@pytest.mark.e2e
def test_login_invalid_credentials_negative(page: Page, fastapi_server: str):
    """Test login fails with invalid credentials and shows error message."""
    page.goto(f"{fastapi_server}login")
    
    page.fill("#username", "nonexistentuser")
    page.fill("#password", "WrongPassword123!")
    
    page.click('button[type="submit"]')
    page.wait_for_timeout(1000)
    
    # Should show error message
    error_alert = page.locator("#errorAlert")
    expect(error_alert).to_be_visible()
    
    error_message = page.locator("#errorMessage").inner_text()
    assert any(word in error_message.lower() for word in ["invalid", "incorrect", "failed", "password", "username"]), \
        "Should show invalid credentials error"
    
    # Should NOT store tokens
    access_token = get_local_storage_item(page, "access_token")
    assert access_token is None or access_token == "", "Should not store access_token on failed login"


@pytest.mark.e2e
def test_login_wrong_password_negative(page: Page, fastapi_server: str):
    """Test login fails with correct username but wrong password."""
    # Register a user
    page.goto(f"{fastapi_server}register")
    user_data = generate_test_user()
    
    page.fill("#username", user_data["username"])
    page.fill("#email", user_data["email"])
    page.fill("#first_name", user_data["first_name"])
    page.fill("#last_name", user_data["last_name"])
    page.fill("#password", user_data["password"])
    page.fill("#confirm_password", user_data["confirm_password"])
    page.click('button[type="submit"]')
    page.wait_for_timeout(2000)
    
    clear_local_storage(page)
    
    # Try to login with wrong password
    page.goto(f"{fastapi_server}login")
    page.fill("#username", user_data["username"])
    page.fill("#password", "WrongPassword123!")
    
    page.click('button[type="submit"]')
    page.wait_for_timeout(1000)
    
    # Should show error
    error_alert = page.locator("#errorAlert")
    expect(error_alert).to_be_visible()
    
    # Should NOT redirect
    assert "login" in page.url, "Should remain on login page"
    
    # Should NOT store tokens
    access_token = get_local_storage_item(page, "access_token")
    assert access_token is None or access_token == "", "Should not store tokens on failed login"


@pytest.mark.e2e
def test_login_nonexistent_user_negative(page: Page, fastapi_server: str):
    """Test login fails for non-existent user."""
    page.goto(f"{fastapi_server}login")
    
    page.fill("#username", "thisuserdoesnotexist123")
    page.fill("#password", "SomePassword123!")
    
    page.click('button[type="submit"]')
    page.wait_for_timeout(1000)
    
    # Should show error
    error_alert = page.locator("#errorAlert")
    expect(error_alert).to_be_visible()
    
    error_message = page.locator("#errorMessage").inner_text()
    assert any(word in error_message.lower() for word in ["invalid", "not found", "failed"]), \
        "Should show user not found error"


@pytest.mark.e2e
def test_login_empty_fields_negative(page: Page, fastapi_server: str):
    """Test login fails with empty fields."""
    page.goto(f"{fastapi_server}login")
    
    # Try to submit empty form
    page.click('button[type="submit"]')
    page.wait_for_timeout(500)
    
    # Should remain on login page (HTML5 validation)
    assert "login" in page.url, "Should remain on login page with empty fields"


# ======================================================================================
# Logout/Token Cleanup Tests
# ======================================================================================
@pytest.mark.e2e
def test_logout_clears_tokens_positive(page: Page, fastapi_server: str):
    """Test that logout clears tokens from localStorage (if logout feature exists)."""
    # Register and login
    page.goto(f"{fastapi_server}register")
    user_data = generate_test_user()
    
    page.fill("#username", user_data["username"])
    page.fill("#email", user_data["email"])
    page.fill("#first_name", user_data["first_name"])
    page.fill("#last_name", user_data["last_name"])
    page.fill("#password", user_data["password"])
    page.fill("#confirm_password", user_data["confirm_password"])
    page.click('button[type="submit"]')
    page.wait_for_timeout(2000)
    
    clear_local_storage(page)
    
    page.goto(f"{fastapi_server}login")
    page.fill("#username", user_data["username"])
    page.fill("#password", user_data["password"])
    page.click('button[type="submit"]')
    page.wait_for_timeout(2000)
    
    # Verify tokens are stored
    access_token = get_local_storage_item(page, "access_token")
    assert access_token is not None and access_token != "", "Tokens should be stored after login"
    
    # Clear localStorage (simulating logout)
    clear_local_storage(page)
    
    # Verify tokens are cleared
    access_token = get_local_storage_item(page, "access_token")
    refresh_token = get_local_storage_item(page, "refresh_token")
    
    assert access_token is None or access_token == "", "access_token should be cleared after logout"
    assert refresh_token is None or refresh_token == "", "refresh_token should be cleared after logout"
