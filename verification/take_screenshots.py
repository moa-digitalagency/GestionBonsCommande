import os
import time
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:5000"
SCREENSHOT_DIR = "screenshots"

if not os.path.exists(SCREENSHOT_DIR):
    os.makedirs(SCREENSHOT_DIR)

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        print("1. Login Page")
        page.goto(f"{BASE_URL}/auth/login")
        page.screenshot(path=f"{SCREENSHOT_DIR}/01_login.png")

        print("2. Login as Tenant Admin")
        page.fill('input[name="email"]', 'admin@btp.ma')
        page.fill('input[name="password"]', 'password123')
        page.click('button[type="submit"]')

        # Wait for dashboard
        page.wait_for_url(f"{BASE_URL}/dashboard")
        page.wait_for_load_state('networkidle')

        print("3. Dashboard")
        page.screenshot(path=f"{SCREENSHOT_DIR}/02_dashboard.png")

        print("4. Company Settings")
        page.goto(f"{BASE_URL}/company/settings")
        page.wait_for_load_state('networkidle')
        try:
            page.click("text=Numérotation")
            page.wait_for_timeout(500)
        except:
            print("Could not click Numérotation tab, taking screenshot anyway")

        page.screenshot(path=f"{SCREENSHOT_DIR}/03_settings_numbering.png")

        print("5. Sites List")
        page.goto(f"{BASE_URL}/projects/")
        page.wait_for_load_state('networkidle')
        page.screenshot(path=f"{SCREENSHOT_DIR}/04_sites_list.png")

        print("6. Products List")
        page.goto(f"{BASE_URL}/products/")
        page.wait_for_load_state('networkidle')
        page.screenshot(path=f"{SCREENSHOT_DIR}/05_products_list.png")

        print("7. Orders List")
        page.goto(f"{BASE_URL}/orders/")
        page.wait_for_load_state('networkidle')
        page.screenshot(path=f"{SCREENSHOT_DIR}/06_orders_list.png")

        print("8. Create Order")
        page.goto(f"{BASE_URL}/orders/create")
        page.wait_for_load_state('networkidle')
        page.screenshot(path=f"{SCREENSHOT_DIR}/07_create_order_step1.png")

        # Fill Order Init
        page.select_option('select[name="project_id"]', index=1)
        page.fill('input[name="supplier_name"]', 'Bricolage Maroc')
        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle')

        print("9. Edit Order (Add Items)")
        # We should be on edit page now
        page.screenshot(path=f"{SCREENSHOT_DIR}/08_edit_order.png")

        # Add a line
        page.fill('input[name="description"]', 'Briques Rouges 8 trous')
        page.fill('input[name="quantity"]', '1000')
        page.fill('input[name="unit_price"]', '2.50')

        # Try to find the button more robustly
        try:
            page.click('button[title="Ajouter la ligne"]')
        except:
            print("Could not find button by title, trying generic submit inside form")
            page.click('i.fa-plus-circle')

        page.wait_for_load_state('networkidle')

        page.screenshot(path=f"{SCREENSHOT_DIR}/09_edit_order_with_items.png")

        # Submit
        page.click('button:has-text("Soumettre pour validation")')
        page.wait_for_load_state('networkidle')

        print("10. Order Detail (View)")
        page.screenshot(path=f"{SCREENSHOT_DIR}/10_order_view_submitted.png")

        # Validate
        # Using force=True to bypass overlapping elements (often tooltips or sticky headers)
        page.click('button:has-text("Valider")', force=True)
        page.wait_for_load_state('networkidle')
        page.screenshot(path=f"{SCREENSHOT_DIR}/11_order_view_validated.png")

        print("11. Dictionary (Admin)")
        page.goto(f"{BASE_URL}/auth/logout")
        page.wait_for_load_state('networkidle')

        page.fill('input[name="email"]', 'admin@btpcommande.ma')
        page.fill('input[name="password"]', 'admin123')
        page.click('button[type="submit"]')
        page.wait_for_url(f"{BASE_URL}/dashboard")

        page.goto(f"{BASE_URL}/lexique/admin")
        page.screenshot(path=f"{SCREENSHOT_DIR}/12_dictionary_admin.png")

        browser.close()
        print("Screenshots captured successfully.")

if __name__ == "__main__":
    run()
