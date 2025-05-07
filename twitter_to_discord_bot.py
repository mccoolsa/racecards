from playwright.sync_api import sync_playwright
from datetime import datetime
import requests
import time

# configuration
PRIVATE_USERNAME = "user12345"  #twitter handle without @
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/56789" #discord webhook url
SESSION_FILE = "twitter_session.json" # note this is stored in C:\Users\yourname
POLL_INTERVAL = 15  # 15 seconds
# ======================

last_seen_id = None

def get_latest_tweet(page):
    page.goto(f"https://twitter.com/{PRIVATE_USERNAME}", wait_until="domcontentloaded", timeout=60000) #Load faster (only wait for the HTML DOM), Avoid full-page timeouts (which expect images/scripts/fonts) and waits for 60 seconds rather than 303

    page.wait_for_selector("article")

    tweet = page.query_selector("article")
    if tweet:
        #tweet ID from URL
        link_element = tweet.query_selector("a[href*='/status/']")
        permalink = link_element.get_attribute("href") if link_element else ""
        tweet_id = permalink.split("/")[-1] if permalink else None

        #tweet content
        content_element = tweet.query_selector("div[lang]")
        tweet_text = content_element.inner_text().strip() if content_element else "[No text]"

        #timestamp
        time_element = tweet.query_selector("time")
        if time_element:
            iso_timestamp = time_element.get_attribute("datetime")
            dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
            formatted_time = dt.strftime("%Y-%m-%d %H:%M UTC") #prints year, month, date and time UTC (GMT-1) 
        else:
            formatted_time = "Unknown time"

        return tweet_text, f"https://twitter.com{permalink}", formatted_time, tweet_id #timestamp added for price context - prices can change quickly

    return None, None, None, None

def main():
    global last_seen_id

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True) #Emulate a real browser (avoiding bot detection)
        context = browser.new_context(
        storage_state=SESSION_FILE,
        viewport={"width": 1280, "height": 720},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    ) 
        #Ensure article elements load correctly
        page = context.new_page()

        while True: #while loop to check new tweets
            print(f"🔍 Checking @{PRIVATE_USERNAME}...")

            try:
                content, link, timestamp, tweet_id = get_latest_tweet(page)

                if tweet_id and tweet_id != last_seen_id:
                    last_seen_id = tweet_id
                    print("🆕 New tweet detected!")

                    if DISCORD_WEBHOOK_URL:
                        message = {
                            "content": (
                                f"🕊️ **New tweet from @{PRIVATE_USERNAME}**\n"
                                f"> {content}\n\n"
                                f"🕓 {timestamp}\n"
                                f"🔗 {link}"
                            )
                        }
                        response = requests.post(DISCORD_WEBHOOK_URL, json=message)
                        if response.status_code == 204:
                            print("✅ Sent to Discord.")
                        else:
                            print(f"⚠️ Discord error: {response.status_code}")

                else:
                    print("ℹ️ No new tweet.")

            except Exception as e:
                print(f"❌ Error: {e}")

            time.sleep(POLL_INTERVAL) #pauses the loop for a set amount of time (POLL_INTERVAL in seconds)

        browser.close()#closes the Playwright browser after the loop ends.

if __name__ == "__main__": #main() function only runs when this is the entry point.
    main()

print(page.url)

#note script fully works in VSCode - some adjustments made to make work in VM Google cloud
