from playwright.sync_api import sync_playwright
from datetime import datetime
import requests
import time

# === CONFIGURATION ===
USERNAME = "mooshtipsbeware"  # Public Twitter handle
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1369830226221076631/Tn52UquCGT7d3TDmjlIwDYnMJLkW2jGBBnU3iH8EK2E8Bo3ruay4bPzRNQUIu7J944XQ"
POLL_INTERVAL = 15  # seconds
# ======================

last_seen_id = None

def get_latest_media_tweet(page):
    page.goto(f"https://twitter.com/{USERNAME}", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_selector("article")

    tweet = page.query_selector("article")
    if tweet:
        link_element = tweet.query_selector("a[href*='/status/']")
        permalink = link_element.get_attribute("href") if link_element else ""
        tweet_id = permalink.split("/")[-1] if permalink else None

        # Check for media (image or video)
        media_element = tweet.query_selector("img[src*='twimg.com/media'], video")
        if not media_element:
            return None, None, None, None  # No media in this tweet

        # Tweet text
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
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        while True:
            print(f"🔍 Checking @{USERNAME}...")

            try:
                content, link, timestamp, tweet_id = get_latest_media_tweet(page)

                if tweet_id and tweet_id != last_seen_id:
                    last_seen_id = tweet_id
                    print("🆕 New media tweet detected!")

                    if DISCORD_WEBHOOK_URL:
                        message = {
                            "content": (
                                f"📸 **New media tweet from @{USERNAME}**\n"
                                f"> {content}\n\n"
                                f"🕓 {timestamp}\n"
                                f"🔗 {link}"
                            )
                        }
                        response = requests.post(DISCORD_WEBHOOK_URL, json=message)
                        if response.status_code in (200, 204):
                            print("✅ Sent to Discord.")
                        else:
                            print(f"⚠️ Discord error: {response.status_code}")

                else:
                    print("ℹ️ No new media tweet.")

            except Exception as e:
                print(f"❌ Error: {e}")

            time.sleep(POLL_INTERVAL)

        browser.close()

if __name__ == "__main__":
    main()