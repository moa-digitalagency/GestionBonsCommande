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
        page.screenshot(path=f"{SCREENSHOT_DIR}/01_login_new_design.png")

        browser.close()
        print("Login screenshot captured.")

if __name__ == "__main__":
    run()
