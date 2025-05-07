from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    # Open login page
    page.goto("https://twitter.com/login")
    print("🔐 Log in manually in the opened browser window.")
    input("✅ After logging in and closing the browser, press Enter here...")

    # Save session
    context.storage_state(path="twitter_session.json")
    print("💾 Session saved to twitter_session.json")
    browser.close()