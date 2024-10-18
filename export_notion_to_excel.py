from datetime import datetime
from notion_client import Client
import pandas as pd
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
database_id = config.get("database_id")

# Validate configuration
if not NOTION_API_KEY or not database_id:
    logging.error("Missing NOTION_API_KEY or database_id in config.json")
    raise ValueError("NOTION_API_KEY and database_id must be specified in config.json")

# Initialize Notion API
notion_api = Client(auth=NOTION_API_KEY)

# Fetch tasks from Notion database
def get_tasks_from_notion():
    try:
        response = notion_api.databases.query(database_id=database_id)
        return response.get('results', [])
    except Exception as error:
        logging.error(f"Error fetching tasks from Notion: {error}")
        return []

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

    # Extract Project
    project = ''
    if 'Project' in properties:
        project_relation = properties['Project'].get('relation', [])
        if project_relation:
            project = project_relation[0].get('id', '')  # Assuming you want the project ID


    # Extract Parent-task
    parent_task = ''
    if 'Parent-task' in properties:
        parent_task_relation = properties['Parent-task'].get('relation', [])
        if parent_task_relation:
            parent_task = parent_task_relation[0].get('id', '')

    return {
        'Task Name': task_name,
        'Status': status,
        'Date Created': date_created,
        'Priority': priority,
        'Description': description,
        'Due Date': due_date,
        'Tags': ', '.join(tags),
        'Assignee': ', '.join(assignee),
        'Sub-tasks': ', '.join(sub_tasks),
        'Summary': summary,
        'Parent-task': parent_task,
    }

# Write tasks to Excel
def write_tasks_to_excel(tasks, filename='tasks_from_notion.xlsx'):
    try:
        df = pd.DataFrame(tasks)
        df.to_excel(filename, index=False)
        logging.info(f'Tasks have been written to {filename}')
    except Exception as e:
        logging.error(f"Error writing tasks to Excel: {e}")
        raise

# Main function
def main():
    tasks = get_tasks_from_notion()
    if tasks:
        task_details = [extract_task_details(task) for task in tasks]
        write_tasks_to_excel(task_details)
    else:
        logging.info("No tasks found in the Notion database.")

if __name__ == "__main__":
    main()
