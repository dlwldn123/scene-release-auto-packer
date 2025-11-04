"""E2E tests for complete application flows using Playwright Browser MCP."""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
def test_login_flow_e2e(page: Page) -> None:
    """Test complete login flow E2E."""
    # Navigate to login page
    page.goto("http://localhost:8080/login")
    
    # Wait for login form
    expect(page.locator('input[name="username"]')).toBeVisible()
    expect(page.locator('input[name="password"]')).toBeVisible()
    
    # Fill login form
    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "password")
    
    # Submit form
    page.click('button[type="submit"]')
    
    # Wait for redirect to dashboard
    expect(page).toHaveURL("http://localhost:8080/dashboard")
    
    # Verify dashboard is visible
    expect(page.locator("h1")).toContainText("Dashboard")


@pytest.mark.e2e
def test_dashboard_access_e2e(page: Page) -> None:
    """Test dashboard access after login."""
    # Login first
    page.goto("http://localhost:8080/login")
    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "password")
    page.click('button[type="submit"]')
    
    # Wait for dashboard
    expect(page).toHaveURL("http://localhost:8080/dashboard")
    
    # Verify statistics are displayed
    expect(page.locator(".stat-card")).toHaveCount(4, timeout=5000)


@pytest.mark.e2e
def test_wizard_complete_flow_e2e(page: Page) -> None:
    """Test complete wizard flow (9 steps) E2E."""
    # Login first
    page.goto("http://localhost:8080/login")
    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "password")
    page.click('button[type="submit"]')
    
    # Navigate to new release wizard
    page.goto("http://localhost:8080/releases/new")
    
    # Step 1: Group
    expect(page.locator("h3")).toContainText("Étape 1")
    page.fill('input[name="group"]', "TestGroup")
    page.click('button:has-text("Next")')
    
    # Step 2: Release Type
    expect(page.locator("h3")).toContainText("Étape 2")
    page.click('button:has-text("EBOOK")')
    page.click('button:has-text("Next")')
    
    # Step 3: Rules
    expect(page.locator("h3")).toContainText("Étape 3")
    # Select first rule
    page.click('input[type="radio"]:first-of-type')
    page.click('button:has-text("Next")')
    
    # Step 4: File Upload
    expect(page.locator("h3")).toContainText("Étape 4")
    # Use URL for testing
    page.click('label:has-text("URL Distante")')
    page.fill('input[type="url"]', "https://example.com/test.epub")
    page.click('button:has-text("Next")')
    
    # Step 5: Analysis
    expect(page.locator("h3")).toContainText("Étape 5")
    # Wait for analysis to complete
    expect(page.locator(".card-header")).toContainText("Résultats", timeout=10000)
    page.click('button:has-text("Next")')
    
    # Step 6: Metadata
    expect(page.locator("h3")).toContainText("Étape 6")
    page.click('button:has-text("Next")')
    
    # Step 7: Templates
    expect(page.locator("h3")).toContainText("Étape 7")
    page.click('button:has-text("Next")')
    
    # Step 8: Options
    expect(page.locator("h3")).toContainText("Étape 8")
    page.click('button:has-text("Next")')
    
    # Step 9: Destination
    expect(page.locator("h3")).toContainText("Étape 9")
    page.click('button:has-text("Finaliser")')
    
    # Verify redirect to releases list
    expect(page).toHaveURL("http://localhost:8080/releases", timeout=10000)


@pytest.mark.e2e
def test_releases_list_and_filter_e2e(page: Page) -> None:
    """Test releases list and filtering E2E."""
    # Login first
    page.goto("http://localhost:8080/login")
    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "password")
    page.click('button[type="submit"]')
    
    # Navigate to releases list
    page.goto("http://localhost:8080/releases")
    
    # Verify releases table is visible
    expect(page.locator("table")).toBeVisible()
    
    # Test filter by release type
    page.select_option('select[name="release_type"]', "EBOOK")
    page.click('button:has-text("Filtrer")')
    
    # Verify filtered results
    expect(page.locator("table tbody tr")).toHaveCount(1, timeout=5000)


@pytest.mark.e2e
def test_rules_management_e2e(page: Page) -> None:
    """Test rules management (list, create, edit, delete) E2E."""
    # Login first
    page.goto("http://localhost:8080/login")
    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "password")
    page.click('button[type="submit"]')
    
    # Navigate to rules
    page.goto("http://localhost:8080/rules")
    
    # Verify rules table is visible
    expect(page.locator("table")).toBeVisible()
    
    # Test search
    page.fill('input[name="search"]', "eBOOK")
    page.click('button:has-text("Rechercher")')
    
    # Verify search results
    expect(page.locator("table tbody tr")).toHaveCount(1, timeout=5000)


@pytest.mark.e2e
def test_logout_flow_e2e(page: Page) -> None:
    """Test logout flow E2E."""
    # Login first
    page.goto("http://localhost:8080/login")
    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "password")
    page.click('button[type="submit"]')
    
    # Wait for dashboard
    expect(page).toHaveURL("http://localhost:8080/dashboard")
    
    # Click logout
    page.click('button:has-text("Logout")')
    
    # Verify redirect to login
    expect(page).toHaveURL("http://localhost:8080/login")
    
    # Verify user is logged out (cannot access dashboard)
    page.goto("http://localhost:8080/dashboard")
    expect(page).toHaveURL("http://localhost:8080/login")
