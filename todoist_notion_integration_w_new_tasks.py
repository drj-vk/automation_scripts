from datetime import datetime
from todoist_api_python.api import TodoistAPI
from notion_client import Client

import json

with open('config.json') as f:
    config = json.load(f)

TODOIST_API_KEY = config['TODOIST_API_KEY']
NOTION_API_KEY = config['NOTION_API_KEY']

database_id = config["database_id"]

# Initialize Todoist and Notion APIs
todoist_api = TodoistAPI(TODOIST_API_KEY)
notion_api = Client(auth=NOTION_API_KEY)

# Fetch tasks from Todoist
try:
    tasks = todoist_api.get_tasks()
except Exception as error:
    print(error)  # Print errors if any

# Fetch the specified Notion database
try:
    notion_db = notion_api.databases.retrieve(database_id)
except Exception as error:
    print(error)  # Print errors if any

# Function to add a task from Todoist to Notion
def add_task_to_notion(task):
    # Extract task details
    task_name = task.content
    task_due = task.due.date if task.due is not None else None
    task_description = task.description 
    # Handle task creation date, labels, and priority
    task_created = task.created_at
    task_labels = [label for label in task.labels]
    task_priority = task.priority
    task_created_date = datetime.strptime(task_created, '%Y-%m-%dT%H:%M:%S.%fZ').date().isoformat()


    if task.comment_count > 0:
        comments = todoist_api.get_comments(task_id=task.id)
        file_url = comments[0].attachment.file_url if comments[0].attachment.file_url is not None else None
        for comment in comments:
            task_description += "\nComment: " + comment.content
        if file_url:
            task_description += "\nComment: " + file_url

    # Construct new Notion page properties
    new_page = {
        "Task name": {"title": [{"text": {"content": task_name}}]},
        "Status": {"status": {"name": "Backlog"}},
        "Date Created": {"date": {"start": task_created_date}},
        "Priority": {"select": {"name": "Low"}},
        "Description": {"rich_text": [{"text": {"content": task_description}}]},  # Add description field
    }

    # Set priority if different from default
    if task_priority != 1:
        new_page["Priority"] = {"select": {"name": "High"}}

    # Set due date if present
    if task_due:
        task_due_date = datetime.strptime(task_due, '%Y-%m-%d').date().isoformat()
        new_page["Due date"] = {"date": {"start": task_due_date}}

    # Set labels/tags if present
    if task_labels:
        new_page["Tags"] = {"multi_select": [{"name": label} for label in task_labels]}

    # Create the new page in Notion and close the task in Todoist
    try:
        notion_api.pages.create(parent={"database_id": database_id}, properties=new_page)
        task_id = task.id
        todoist_api.close_task(task_id)
    except Exception as error:
        print(error)  # Print errors if any

# Loop through each task in Todoist to add it to Notion
for task in tasks:
    add_task_to_notion(task)