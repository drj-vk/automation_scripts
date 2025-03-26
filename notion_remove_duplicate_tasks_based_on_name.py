from notion_client import Client
from collections import defaultdict
import os
import json

# Load config
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, 'config.json')

with open(config_path) as f:
    config = json.load(f)

NOTION_API_KEY = config['NOTION_API_KEY']
database_id = "7ac9feae88754c2b9331bf34a71b5564"

# Initialize Notion API
notion = Client(auth=NOTION_API_KEY)

# Helper to fetch all pages
def fetch_all_pages(database_id):
    results = []
    start_cursor = None
    while True:
        response = notion.databases.query(
            database_id=database_id,
            start_cursor=start_cursor
        )
        results.extend(response["results"])
        if not response.get("has_more"):
            break
        start_cursor = response["next_cursor"]
    return results

# Step 1: Fetch all tasks
pages = fetch_all_pages(database_id)

# Step 2: Track duplicates
seen_names = set()
duplicate_pages = []

for page in pages:
    props = page.get("properties", {})
    title_data = props.get("Task name", {}).get("title", [])
    if not title_data:
        continue
    task_name = title_data[0]["text"]["content"].strip()

    if task_name.lower() in seen_names:
        duplicate_pages.append(page["id"])
    else:
        seen_names.add(task_name.lower())

# Step 3: Archive duplicates
for page_id in duplicate_pages:
    notion.pages.update(page_id=page_id, archived=True)
    print(f"Archived duplicate task: {page_id}")

print(f"\n✅ Archived {len(duplicate_pages)} duplicates based on task name.")
