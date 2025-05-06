import praw
import requests
import time

# ========== CONFIGURATION ==========
REDDIT_CLIENT_ID = 'U7k6K-16jvhwFwON59zMYw'
REDDIT_CLIENT_SECRET = 'GKJUXi89AfFbPtSKNbGzivBAbXTU0w'
REDDIT_USER_AGENT = 'script:reddit.discord.bot:v1.0'
TARGET_USERNAME = 'J_HorseRacing'

DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1369408072753221764/J9k2rSd7jhTFkXB7CBdBENvYgyaVUaTzaIEh6AsurNuo-l3ecD4waVrTpU6IHMPg7v3h'
POLL_INTERVAL = 60  # in seconds
# ====================================

# Initialize Reddit client
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

seen_ids = set()

print(f"🔍 Monitoring posts and comments by u/{TARGET_USERNAME}...")

while True:
    try:
        user = reddit.redditor(TARGET_USERNAME)

        # Check latest post
        for post in user.submissions.new(limit=1):
            if post.id not in seen_ids:
                seen_ids.add(post.id)
                message = {
                    "content": f"🆕 u/{TARGET_USERNAME} just posted:\n**{post.title}**\n{post.url}"
                }
                response = requests.post(DISCORD_WEBHOOK_URL, json=message)
                if response.status_code == 204:
                    print(f"✅ Posted notification for new post: {post.title}")
                else:
                    print(f"⚠️ Discord post failed: {response.status_code}")

        # Check latest comment
        for comment in user.comments.new(limit=1):
            if comment.id not in seen_ids:
                seen_ids.add(comment.id)
                message = {
                    "content": f"💬 u/{TARGET_USERNAME} commented:\n> {comment.body[:300]}...\n🔗 https://www.reddit.com{comment.permalink}"
                }
                response = requests.post(DISCORD_WEBHOOK_URL, json=message)
                if response.status_code == 204:
                    print(f"✅ Posted notification for new comment.")
                else:
                    print(f"⚠️ Discord comment failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {e}")

    time.sleep(POLL_INTERVAL)