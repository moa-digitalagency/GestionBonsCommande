from playwright.sync_api import sync_playwright, expect
import time

def verify_sidebar():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()

        # Login
        print("Navigating to login page...")
        try:
            page.goto("http://localhost:5000/auth/login", timeout=10000)
        except Exception as e:
            print(f"Failed to load page: {e}")
            return

        # Check if we are already logged in or need to log in
        if "login" in page.url:
            print("Logging in...")
            page.fill("input[name='email']", "admin@btpcommande.ma")
            page.fill("input[name='password']", "admin123")
            # Submit form
            page.click("button[type='submit']")
            page.wait_for_load_state("networkidle")

        print(f"Current URL: {page.url}")

        # Verify Sidebar exists
        print("Verifying Sidebar...")
        # The desktop sidebar is the <aside> element
        sidebar = page.locator("aside")
        expect(sidebar).to_be_visible()

        # Verify Links
        print("Verifying Links...")
        # Check for text in sidebar
        expect(sidebar).to_contain_text("BTP Commande")
        expect(sidebar).to_contain_text("Tableau de bord")

        # Take Screenshot Desktop
        print("Taking Desktop Screenshot...")
        page.screenshot(path="verification/sidebar_desktop.png")

        # Test Mobile
        print("Testing Mobile View...")
        page.set_viewport_size({'width': 375, 'height': 667})
        time.sleep(1) # wait for resize

        # Sidebar (aside) should be hidden because of 'hidden md:flex'
        expect(sidebar).not_to_be_visible()

        # Click Toggle button
        print("Clicking Toggle...")
        # The toggle button is visible on mobile
        toggle = page.locator("button").filter(has=page.locator("i.fa-bars"))
        expect(toggle).to_be_visible()
        toggle.click()

        # Wait for sidebar to open
        time.sleep(1)

        print("Taking Mobile Screenshot...")
        page.screenshot(path="verification/sidebar_mobile.png")

        print("Verification Done.")
        browser.close()

if __name__ == "__main__":
    verify_sidebar()
