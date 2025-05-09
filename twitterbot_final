from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from datetime import datetime
import os
import time
import json
import requests
import sys
import platform

# config
USERNAME = "user"  # Twitter handle (without the @)
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/................"  # Discord webhook URL for notifications
POLL_INTERVAL = 30  # Interval (in seconds) between checks for new tweets
SESSION_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "twitter_session.json") #run tsession file to conjure a twitter_session.json file (requires login)
# ---------------------

last_seen_id = None  # Tracks the most recent tweet to avoid duplicates


def validate_session_file():
    """
    Validates the existence and content of the Playwright Twitter session file.
    """
    if not os.path.exists(SESSION_FILE):
        print("❌ Session file missing.")
        return False
    try:
        with open(SESSION_FILE, "r") as f:
            data = json.load(f)
            if not data.get("cookies"):
                print("❌ Session file is corrupt or empty.")
                return False
        print("✅ Session file loaded successfully.")
        return True
    except Exception as e:
        print(f"❌ Failed to read session file: {e}")
        return False


def alert_discord_session_expired():
    """
    Sends a Discord alert if the Twitter session is expired or missing.
    """
    if DISCORD_WEBHOOK_URL:
        try:
            requests.post(DISCORD_WEBHOOK_URL, json={
                "content": (
                    "⚠️ **Twitter session expired or invalid.**\n"
                    "Please run `save_twitter_session.py` **from inside the VM**, then restart the bot."
                ) #posts into discord
            })
            print("📣 Sent session expired alert to Discord.")
        except Exception as e:
            print(f"❌ Failed to send Discord alert: {e}")


def get_latest_tweet(page):
    """
    Navigates to the user's main Twitter profile page and scrapes the most recent original tweet.
    Excludes replies by avoiding the /with_replies page.
    """
    try:
        print(f"🔗 Loading: https://twitter.com/{USERNAME}")
        page.goto(f"https://twitter.com/{USERNAME}", wait_until="domcontentloaded", timeout=60000)
        #replace above line with the following to include all tweets (replies, etc).
        #print(f"🔗 Loading: https://twitter.com/search?q=from%3A{USERNAME}&f=live")
        #page.goto(f"https://twitter.com/search?q=from%3A{USERNAME}&f=live", wait_until="domcontentloaded", timeout=60000)

        time.sleep(5)  # Allow full rendering of dynamic content
        page.wait_for_selector("article", timeout=15000)

        tweets = page.query_selector_all("article")

        for tweet in tweets:
            try:
                # Skip tweets that contain embedded tweets (e.g., quotes or replies)
                embedded = tweet.query_selector("article")
                if embedded:
                    print("↩️ Skipping quote/reply tweet with embedded tweet.")
                    continue

                # Get the main tweet content
                content_element = tweet.query_selector("div[lang]")
                if not content_element:
                    print("⚠️ No text content found, skipping.")
                    continue

                tweet_text = content_element.inner_text().strip()

                # Extract tweet URL and ID
                link_element = tweet.query_selector("a[href*='/status/']")
                permalink = link_element.get_attribute("href") if link_element else ""
                tweet_id = permalink.split("/")[-1] if permalink else None
                tweet_url = f"https://twitter.com{permalink}" if permalink else None

                # Extract tweet timestamp
                time_element = tweet.query_selector("time")
                if time_element:
                    iso_timestamp = time_element.get_attribute("datetime")
                    dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
                    formatted_time = dt.strftime("%Y-%m-%d %H:%M UTC")
                else:
                    formatted_time = "Unknown time"

                return tweet_text, tweet_url, formatted_time, tweet_id

            except Exception as e:
                print(f"⚠️ Error while processing tweet: {e}")
                continue

    except PlaywrightTimeoutError:
        print("⚠️ Tweets failed to load. Likely expired or invalid session.")
        raise

    return None, None, None, None


def main():
    """
    Main loop that monitors the specified Twitter account and posts new tweets to Discord.
    """
    global last_seen_id

    if not validate_session_file():
        alert_discord_session_expired()
        return

    with sync_playwright() as p:
        #browser launch configuration
        launch_args = {
            "headless": True,
            "args": [
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-blink-features=AutomationControlled"
            ]
        }

        #use system Chrome if on Linux
        if platform.system() == "Linux":
            launch_args["executable_path"] = "/usr/bin/google-chrome-stable"

        browser = p.chromium.launch(**launch_args)

        while True:
            try:
                context = browser.new_context(storage_state=SESSION_FILE)
                page = context.new_page()

                print(f"\n🔍 Checking @{USERNAME}...")
                content, link, timestamp, tweet_id = get_latest_tweet(page)

                # Post to Discord if new tweet is found
                if tweet_id and tweet_id != last_seen_id:
                    last_seen_id = tweet_id
                    print(f"🆕 New tweet: {tweet_id}")

                    if DISCORD_WEBHOOK_URL:
                        message = {
                            "content": (
                                f"🕊️ **New tweet from @{USERNAME}**\n"
                                f"> {content}\n\n"
                                f"🕓 {timestamp}\n"
                                f"🔗 {link}"
                            )
                        }
                        r = requests.post(DISCORD_WEBHOOK_URL, json=message)
                        if r.status_code == 204:
                            print("✅ Sent to Discord.")
                        else:
                            print(f"⚠️ Discord error: {r.status_code}")
                else:
                    print("ℹ️ No new tweet.")

                context.close()

            except PlaywrightTimeoutError:
                print("🛑 Session invalid or expired.")
                alert_discord_session_expired()
                break

            except Exception as e:
                print(f"❌ Unexpected error: {e}")

            time.sleep(POLL_INTERVAL)

        browser.close()

if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding='utf-8')  #ensure proper UTF-8 output for emojis/logs
        main()
    except KeyboardInterrupt:
        print("🛑 Bot stopped by user.")

#upload to VM 
