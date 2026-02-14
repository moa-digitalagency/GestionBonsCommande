import os
import time
import subprocess
import requests
from playwright.sync_api import sync_playwright

def run_verification():
    # Start the Flask app in a separate process
    env = os.environ.copy()
    env['FLASK_ENV'] = 'development'
    env['FLASK_APP'] = 'app.py'

    print("Starting Flask server...")
    process = subprocess.Popen(['python', 'app.py'], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Wait for server to start
    print("Waiting for server to start...")
    server_up = False
    for _ in range(30):
        try:
            requests.get('http://localhost:5000/auth/login')
            server_up = True
            break
        except requests.exceptions.ConnectionError:
            time.sleep(1)

    if not server_up:
        print("Server failed to start")
        # Kill strictly
        process.kill()
        out, err = process.communicate()
        print("Stdout:", out.decode())
        print("Stderr:", err.decode())
        return

    print("Server started. Capturing screenshots...")

    if not os.path.exists('screenshots'):
        os.makedirs('screenshots')

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Define the error codes to test
            error_codes = [400, 403, 404, 451]

            for code in error_codes:
                url = f"http://localhost:5000/error-preview/{code}"
                print(f"Navigating to {url}")
                try:
                    # Note: goto might throw error for 404/500 if not handled by playwright cleanly,
                    # but flask returns 404/etc which is a valid HTTP response, so goto should succeed.
                    response = page.goto(url)
                    print(f"Status: {response.status}")
                except Exception as e:
                    print(f"Error navigating to {url}: {e}")

                # Wait a bit for Lottie/animations
                time.sleep(2)

                # Take screenshot
                screenshot_path = f"screenshots/error_{code}.png"
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"Saved {screenshot_path}")

            browser.close()
    except Exception as e:
        print(f"Playwright error: {e}")
    finally:
        print("Killing server...")
        process.terminate()
        process.wait()

if __name__ == "__main__":
    run_verification()
