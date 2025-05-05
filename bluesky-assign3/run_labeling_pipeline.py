import os
import time
from dotenv import load_dotenv
from atproto import Client

from create_csv import search_and_collect_posts
from policy_proposal_labeler import PanicLanguageLabeler
from pylabel.label import label_post, did_from_handle

# Load login credentials
load_dotenv()
USERNAME = os.getenv("USERNAME", "")
PASSWORD = os.getenv("PW")

# Step 1: Set up clients
client = Client()
client.login(USERNAME, PASSWORD)
labeler_did = did_from_handle(USERNAME)
labeler_client = client.with_proxy("atproto_labeler", labeler_did)

# Step 2: Initialize labeler logic
labeler = PanicLanguageLabeler(keyword_threshold=2)

# Step 3: Scrape panic-related posts (real-time)
PANIC_KEYWORDS = [
    "emergency", "breaking", "alert", "urgent", "evacuate", "crisis",
    "do not ignore", "act now", "warning", "immediately", "catastrophe",
    "panic", "danger", "critical", "disaster"
]

posts = search_and_collect_posts(PANIC_KEYWORDS, max_posts=500, per_keyword_limit=50)

# Step 4: Apply rule-based labeler and emit if matched
for post in posts:
    text = post['text']
    creator = post['creator']
    rkey = post.get('rkey')  # scraping code should include this
    if not rkey:
        print(f"⚠️ Skipping post from {creator} — missing rkey.")
        continue


    label = labeler.moderate_post(text)

    if label:
        post_url = f"https://bsky.app/profile/{creator}/post/{rkey}"
        print(f"\n🚨 Emitting label for post: {post_url}")
        try:
            result = label_post(client, labeler_client, post_url, [label])
            print("✅ Label emitted:", result)
        except Exception as e:
            print("❌ Failed to emit label:", e)
        time.sleep(1)  # to be polite to the API