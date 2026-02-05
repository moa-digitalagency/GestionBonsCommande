import os
from playwright.sync_api import sync_playwright, expect

def capture_lexicon():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Go to home page
        page.goto("http://localhost:5000/")

        # Login
        page.fill('input[name="email"]', 'admin@btpcommande.ma')
        page.fill('input[name="password"]', 'admin123')
        page.click('button[type="submit"]')

        # Wait for dashboard
        expect(page.get_by_text("Tableau de bord").first).to_be_visible()

        # Go directly to lexique page to avoid menu selector issues
        page.goto("http://localhost:5000/lexique/")

        # Wait for the table to load
        expect(page.locator('table')).to_be_visible()

        # Ensure we see some of the imported words (e.g., Ciment, Sable)
        # Using a relaxed check just to ensure content is there
        expect(page.locator('body')).to_contain_text("Ciment")

        # Screenshot
        page.screenshot(path="/home/jules/verification/lexicon_content.png", full_page=True)
        print("Screenshot taken: lexicon_content.png")

        browser.close()

if __name__ == "__main__":
    capture_lexicon()
