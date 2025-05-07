# script to pull twitter sessions login
# necessary for pulling information on privated tweets
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False) #launch Chrome externally
    context = browser.new_context()
    page = context.new_page()
    
    #open login page
    page.goto("https://twitter.com/login")
    print("🔐 Log in manually in the opened browser window.")
    input("✅ After logging in and closing the browser, press Enter here...") #hit enter on console after logging in
    

    #save session
    context.storage_state(path="twitter_session.json") #stores login as json file - needed for future
    print("💾 Session saved to twitter_session.json")
    browser.close()
