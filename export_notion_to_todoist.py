from datetime import datetime
from notion_client import Client
from todoist_api_python.api import TodoistAPI
import os
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Build the full path to config.json
config_path = os.path.join(script_dir, 'config.json')

# Load the config file
try:
    with open(config_path) as f:
        config = json.load(f)
except Exception as e:
    logging.error(f"Error loading config.json: {e}")
    raise

NOTION_API_KEY = config.get('NOTION_API_KEY')
TODOIST_API_KEY = config.get('TODOIST_API_KEY')
database_id = config.get("database_id")

# Validate configuration
if not NOTION_API_KEY or not database_id or not TODOIST_API_KEY:
    logging.error("Missing NOTION_API_KEY, TODOIST_API_KEY or database_id in config.json")
    raise ValueError("NOTION_API_KEY, TODOIST_API_KEY, and database_id must be specified in config.json")

# Initialize Notion and Todoist APIs
notion_api = Client(auth=NOTION_API_KEY)
todoist_api = TodoistAPI(TODOIST_API_KEY)

# Fetch tasks from Notion database
def get_tasks_from_notion():
    try:
        response = notion_api.databases.query(database_id=database_id)
        return response.get('results', [])
    except Exception as error:
        logging.error(f"Error fetching tasks from Notion: {error}")
        return []

# Extract task details from the response
def extract_task_details(task):
    properties = task.get('properties', {})
    
    # Extract Task Name
    task_name = ''
    if 'Task name' in properties:
        titles = properties['Task name'].get('title', [])
        if titles:
            task_name = titles[0].get('text', {}).get('content', '')
    
    # Extract Status
    status = ''
    if 'Status' in properties:
        status = properties['Status'].get('status', {}).get('name', '')
    
    # Extract Date Created
    date_created = ''
    if 'Date Created' in properties:
        date_property = properties['Date Created'].get('date')
        if date_property:  # Check if 'date' is not None
            date_created = date_property.get('start', '')
    
    # Extract Priority
    priority = ''
    if 'Priority' in properties:
        priority_property = properties['Priority'].get('select')
        if priority_property:  # Check if 'select' is not None
            priority = priority_property.get('name', '')

    # Extract Description with all rich text entries
    description = ''
    if 'Description' in properties:
        rich_text = properties['Description'].get('rich_text', [])
        description = ' '.join([text.get('text', {}).get('content', '') for text in rich_text])
    
    # Extract Due Date
    due_date = ''
    if 'Due date' in properties:
        due_date_property = properties['Due date'].get('date')
        if due_date_property:  # Check if 'date' is not None
            due_date = due_date_property.get('start', '')
    
    # Extract Tags
    tags = []
    if 'Tags' in properties:
        multi_select = properties['Tags'].get('multi_select', [])
        tags = [tag.get('name', '') for tag in multi_select if 'name' in tag]

    # Extract Assignee
    assignee = []
    if 'Assignee' in properties:
        people = properties['Assignee'].get('people', [])
        assignee = [person.get('name', '') for person in people]

    # Extract Sub-tasks
    sub_tasks = []
    if 'Sub-tasks' in properties:
        sub_tasks_relation = properties['Sub-tasks'].get('relation', [])
        sub_tasks = [sub_task.get('id', '') for sub_task in sub_tasks_relation]

    # Extract Summary
    summary = ''
    if 'Summary' in properties:
        rich_text = properties['Summary'].get('rich_text', [])
        summary = ' '.join([text.get('text', {}).get('content', '') for text in rich_text])

    # Extract Parent-task
    parent_task = ''
    if 'Parent-task' in properties:
        parent_task_relation = properties['Parent-task'].get('relation', [])
        if parent_task_relation:
            parent_task = parent_task_relation[0].get('id', '')

    # Extract Project
    project = ''
    if 'Project' in properties:
        project_relation = properties['Project'].get('relation', [])
        if project_relation:
            project = project_relation[0].get('id', '')  # Assuming you want the project ID

    return {
        'task_name': task_name,
        'status': status,
        'date_created': date_created,
        'priority': priority,
        'description': description,
        'due_date': due_date,
        'tags': ', '.join(tags),
        'assignee': ', '.join(assignee),
        'sub_tasks': ', '.join(sub_tasks),
        'summary': summary,
        'parent_task': parent_task,
        'project': project,  # Adding the project to the output
    }

# Create a task in Todoist
def create_todoist_task(task_details):
    try:
        task = todoist_api.add_task(
            content=task_details['task_name'],
            description=task_details['description'],
            due_date=task_details['due_date'],
            priority=4 if task_details['priority'].lower() == 'high' else 1  # Todoist priorities: 4=urgent, 1=low
        )
        logging.info(f"Task '{task.content}' created in Todoist.")
    except Exception as error:
        logging.error(f"Error creating task in Todoist: {error}")

# Main function
def main():
    tasks = get_tasks_from_notion()
    if tasks:
        for task in tasks:
            task_details = extract_task_details(task)
            create_todoist_task(task_details)
    else:
        logging.info("No tasks found in the Notion database.")

if __name__ == "__main__":
    main()
