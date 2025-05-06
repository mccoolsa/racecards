import praw
import requests
import time

# CONFIGURATION
REDDIT_CLIENT_ID = '12345' #under personal use script on reddit api
REDDIT_CLIENT_SECRET = '3456' #secret encrypted key on reddit api
REDDIT_USER_AGENT = 'script:reddit.discord.bot:v1.0' #bot client
TARGET_USERNAME = 'J_HorseRacing' #target username J_horseracing - goat!

DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/12345' #take from webhook integration - copy url here
POLL_INTERVAL = 60  #ping in seconds
# _______

# Initialize Reddit client
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
) #use praw to assign and initialize

seen_ids = set()

print(f"🔍 New post by u/{TARGET_USERNAME}...") #printed message into the discord channel

while True:
    try: #ping loop each 60 seconds for target_username (checks posts and comments) 
        user = reddit.redditor(TARGET_USERNAME)

        #check latest post
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
                    "content": f"💬 u/{TARGET_USERNAME} commented:\n> {comment.body[:300]}...\n🔗 https://www.reddit.com{comment.permalink}" #supply post URL 
                }
                response = requests.post(DISCORD_WEBHOOK_URL, json=message)
                if response.status_code == 204:
                    print(f"✅ Posted notification for new comment.")
                else:
                    print(f"⚠️ Discord comment failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {e}")

    time.sleep(POLL_INTERVAL)
