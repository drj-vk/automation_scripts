from datetime import datetime
from todoist_api_python.api import TodoistAPI
from notion_client import Client

import json

with open('config.json') as f:
    config = json.load(f)

TODOIST_API_KEY = config['TODOIST_API_KEY']
NOTION_API_KEY = config['NOTION_API_KEY']

database_id = config["database_id"]

# Initialize the APIs
todoist_api = TodoistAPI(TODOIST_API_KEY)
notion_api = Client(auth=NOTION_API_KEY)

# Get tasks from Todoist
try:
    tasks = todoist_api.get_tasks()
except Exception as error:
    print(error)

# Get the Notion database
try:
    notion_db = notion_api.databases.retrieve(database_id)
except Exception as error:
    print(error)

def add_task_to_notion(task):  
    task_name = task.content
    task_due = task.due.date if task.due is not None else None
    if task.comment_count == 1:
        comment = todoist_api.get_comments(task_id = task.id)
        file_url = comment[0].attachment.file_url if comment[0].attachment.file_url is not None else None
        if file_url:
            task_name = task_name + " " + file_url

    # task_url = task.url if task.url is not None else None
    # if task_url:
    #     task_name = task_name + " " + task_url 
    task_created = task.created_at
    task_labels = [label for label in task.labels]
    task_priority = task.priority
    task_created_date = datetime.strptime(task_created, '%Y-%m-%dT%H:%M:%S.%fZ').date().isoformat()
    if task_due:
        task_due_date = datetime.strptime(task_due, '%Y-%m-%d').date().isoformat()
    new_page = {
        "Task name": {"title": [{"text": {"content": task_name}}]},
        "Status": {"status": {"name": "Backlog"}},
        "Date Created": {"date": {"start": task_created_date }},
        "Priority":{"select": {"name": "Low"}},
        } 
    if task_priority != 1:
        new_page["Priority"] = {"select": {"name": "High"}}
    if task_due:
        new_page["Due date"] = {"date": {"start": task_due_date}} #"end": task_due_date, 
    if task_labels:
        # labels = [todoist_api.labels.get_by_id(label_id)["name"] for label_id in task["labels"]]
        new_page["Tags"] = {"multi_select": [{"name": label} for label in task_labels]}
    # Import tasks from Todoist to the Notion database
    try:
        # print(new_page)
        notion_api.pages.create(parent={"database_id": database_id}, properties=new_page)
        task_id = task.id
        todoist_api.close_task(task_id)
    except Exception as error:
        print(error)

# For each task in the list of tasks fetched from Todoist, add it to Notion and mark it as closed in Todoist
for task in tasks:
    add_task_to_notion(task)


