from playwright.sync_api import sync_playwright
from datetime import datetime
import requests
import time

# === CONFIGURATION ===
PRIVATE_USERNAME = "willhewitt1010"  # Twitter handle without @
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1369755732458602696/XAD-nWIHgo2Pu_riVnv0aJM_BH8RrClyfO-Iv2PkJRo57SeCGoA19DksmDTv_Sf-RcqY"
SESSION_FILE = "twitter_session.json"
POLL_INTERVAL = 15  # seconds
# ======================

last_seen_id = None

def get_latest_tweet(page):
    page.goto(f"https://twitter.com/{PRIVATE_USERNAME}", wait_until="domcontentloaded", timeout=60000)

    page.wait_for_selector("article")

    tweet = page.query_selector("article")
    if tweet:
        # Tweet ID from URL
        link_element = tweet.query_selector("a[href*='/status/']")
        permalink = link_element.get_attribute("href") if link_element else ""
        tweet_id = permalink.split("/")[-1] if permalink else None

        # Tweet content
        content_element = tweet.query_selector("div[lang]")
        tweet_text = content_element.inner_text().strip() if content_element else "[No text]"

        # Timestamp
        time_element = tweet.query_selector("time")
        if time_element:
            iso_timestamp = time_element.get_attribute("datetime")
            dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
            formatted_time = dt.strftime("%Y-%m-%d %H:%M UTC")
        else:
            formatted_time = "Unknown time"

        return tweet_text, f"https://twitter.com{permalink}", formatted_time, tweet_id

    return None, None, None, None

def main():
    global last_seen_id

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
        storage_state=SESSION_FILE,
        viewport={"width": 1280, "height": 720},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    )
        page = context.new_page()

        while True:
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

            time.sleep(POLL_INTERVAL)

        browser.close()

if __name__ == "__main__":
    main()

print(page.url)