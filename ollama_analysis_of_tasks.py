import os
import json
import subprocess
from notion_client import Client

# Load config
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, 'config.json')
with open(config_path) as f:
    config = json.load(f)

NOTION_API_KEY = config['NOTION_API_KEY']
DATABASE_ID = config['database_id']

# Init Notion
notion = Client(auth=NOTION_API_KEY)
# Allowed statuses
ALLOWED_STATUSES = {"Backlog", "Next", "Waiting for", "Someday/Maybe"}
# Fetch tasks from Notion
response = notion.databases.query(database_id=DATABASE_ID)
task_lines = []

for page in response["results"]:
    props = page["properties"]
    try:
        task_name = props["Task name"]["title"][0]["text"]["content"]
        status = props["Status"]["status"]["name"] if "Status" in props else ""
        if status not in ALLOWED_STATUSES:
            continue

        project = props.get("Project", {}).get("select", {}).get("name", "No Project")
        priority = props.get("Priority", {}).get("select", {}).get("name", "None")
        created = props.get("Date Created", {}).get("date", {}).get("start", "Unknown")
        tags = [tag["name"] for tag in props.get("Tags", {}).get("multi_select", [])]
        tags_str = ", ".join(tags) if tags else "No tags"
        
        # Extract description safely
        description_raw = props.get("Description", {}).get("rich_text", [])
        description = ""
        if description_raw:
            description = " ".join(block.get("text", {}).get("content", "") for block in description_raw)

        line = (
            f"- **{task_name}**\n"
            f"  • Status: {status}\n"
            f"  • Project: {project}\n"
            f"  • Priority: {priority}\n"
            f"  • Tags: {tags_str}\n"
            f"  • Created: {created}\n"
            f"  • Description: {description.strip() or 'No description'}\n"
        )
        task_lines.append(line)
    except Exception as e:
        print(f"Skipping a task due to error: {e}")


# Build the final prompt
task_text = "\n".join(task_lines)
prompt = f"""
You are my personal task coach. Help me reflect and take action today.

Here are my current open tasks (Backlog, Next, Waiting for, and Someday/Maybe):

{task_text}

Instructions:
1. Group tasks into logical categories or domains (e.g. Personal, GIII, Fashion Futures).
2. Based on urgency and clarity, suggest 3 tasks I should focus on today.
3. Identify tasks that seem unclear, duplicated, or outdated.
4. Highlight any helpful patterns or improvements in how I write or organise tasks.
"""

# Run with Ollama (e.g., llama3)
print("🧠 Sending prompt to Ollama...")
ollama_command = f'ollama run gemma3 "{prompt}"'
result = subprocess.run(ollama_command, shell=True, capture_output=True, text=True)

if result.returncode == 0:
    print("\n🎯 LLM Suggestion:\n")
    print(result.stdout)
else:
    print("Error running Ollama:", result.stderr)

# # Optionally: write result to Notion as a new page
# notion.pages.create(
#     parent={"database_id": DATABASE_ID},
#     properties={
#         "Task name": {"title": [{"text": {"content": "LLM Summary Suggestion"}}]},
#         "Description": {"rich_text": [{"text": {"content": result.stdout}}]}
#     }
# )
