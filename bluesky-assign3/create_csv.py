import os
import csv
import re
import time
from dotenv import load_dotenv
from atproto import Client

load_dotenv()
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PW")

client = Client()
client.login(USERNAME, PASSWORD)

PANIC_KEYWORDS = [
    "threat", "emergency", "evacuate", "shelter", "crisis",
    "urgent", "alert", "warning", "danger", "disaster",
    "breaking", "act now", "wake up"
]

# Panic-inducing regex patterns
PANIC_PATTERNS = [
    r"act\s+now", r"breaking\s+news", r"emergency", r"evacuate",
    r"shelter\s+in\s+place", r"immediate\s+threat", r"danger\s+to\s+life",
    r"urgent\s+action", r"massive\s+explosion", r"public\s+alert",
    r"they\s+don\u2019t\s+want\s+you\s+to\s+know"
]
PANIC_REGEX = re.compile("|".join(PANIC_PATTERNS), re.IGNORECASE)

def search_and_collect_posts(keywords, max_posts=500, per_keyword_limit=50):
    collected = []
    matched_count = 1
    seen_texts = set()

    for kw in keywords:
        print(f"\nSearching for: '{kw}'")
        cursor = None
        keyword_post_count = 0

        while keyword_post_count < per_keyword_limit and len(collected) < max_posts:
            try:
                res = client.app.bsky.feed.search_posts({
                    "q": kw,
                    "limit": 25,
                    "cursor": cursor,
                    "sort": "latest",
                    "lang": "en"
                })
            except Exception as e:
                print(f"Error while searching '{kw}': {e}")
                break

            for p in res.posts or []:
                if keyword_post_count >= per_keyword_limit or len(collected) >= max_posts:
                    break

                rec = getattr(p, "record", None)
                if not rec or not hasattr(rec, "text"):
                    continue

                # unsure only unique posts
                text = rec.text.strip()
                if text in seen_texts:
                    continue
                seen_texts.add(text)
                if kw.lower() not in text.lower():
                    continue
                if not PANIC_REGEX.search(text):
                    continue

                print(f"{matched_count}. Matched post: {text[:80]}...")
                matched_count += 1

                collected.append({
                    "text": text,
                    "keyword": kw,
                    "creator": p.author.handle,
                    "rkey": p.uri.split("/")[-1],
                    "likes": getattr(p, "like_count", 0),
                    "reposts": getattr(p, "repost_count", 0),
                    "responses": getattr(p, "reply_count", 0),
                })

                keyword_post_count += 1

            cursor = getattr(res, "cursor", None)
            if not cursor:
                break

            time.sleep(1)

    return collected

if __name__ == "__main__":
    output_path = "./bluesky-assign3/test-data/input-posts-panic.csv"
    posts = search_and_collect_posts(PANIC_KEYWORDS, max_posts=100, per_keyword_limit=10)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "keyword", "creator", "likes", "reposts", "responses"])
        writer.writeheader()
        writer.writerows(posts)
    print(f"\nSaved {len(posts)} posts to {output_path}")