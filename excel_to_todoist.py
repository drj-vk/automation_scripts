import pandas as pd
from datetime import datetime
from todoist_api_python.api import TodoistAPI
import os
import json

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Build the full path to config.json
config_path = os.path.join(script_dir, 'config.json')

# Load config.json for API keys
with open(config_path) as f:
    config = json.load(f)

TODOIST_API_KEY = config['TODOIST_API_KEY']

# Initialize Todoist API
todoist_api = TodoistAPI(TODOIST_API_KEY)

# Path to the Excel file (adjust this to the location of your Excel file)
excel_file_path = './excel_only_todos_to_todoist.xlsx'

# Load the tasks from the Excel file
tasks_df = pd.read_excel(excel_file_path)

# Helper function to get the project ID by matching the project name (status)
def get_project_id_by_name(project_name):
    try:
        projects = todoist_api.get_projects()
        for project in projects:
            if project.name.lower() == project_name.lower():
                return project.id
        print(f"Project '{project_name}' not found, task will be added to the default project.")
        return None  # Return None if the project is not found
    except Exception as error:
        print(f"Error fetching projects: {error}")
        return None

# Helper function to get the label IDs by matching the label names (tags)
def get_label_ids_by_names(label_names):
    label_ids = []
    try:
        labels = todoist_api.get_labels()
        for label_name in label_names.split(','):
            for label in labels:
                if label.name.lower().strip() == label_name.lower().strip():
                    label_ids.append(label.id)
        return label_ids
    except Exception as error:
        print(f"Error fetching labels: {error}")
        return []

# Function to add tasks to Todoist
def add_task_to_todoist(task_details):
    try:
        # Extract task details
        task_name = task_details['Task Name']
        due_date = task_details['Due Date'] if pd.notna(task_details['Due Date']) else None
        description = task_details['Description'] if pd.notna(task_details['Description']) else ""
        priority = 1  # Default priority
        
        # Map the priority from input data to Todoist priority levels (Todoist: 1-4)
        if pd.notna(task_details['Priority']):
            priority_level = task_details['Priority'].lower()
            if priority_level == 'high':
                priority = 4
            elif priority_level == 'medium':
                priority = 3
            elif priority_level == 'low':
                priority = 1

        # Get the project ID by status
        project_name = task_details['Status']
        project_id = get_project_id_by_name(project_name)

        # Get the label IDs by tags
        tags = task_details['Tags'] if pd.notna(task_details['Tags']) else ""
        label_ids = get_label_ids_by_names(tags) if tags else []

        # Create the task in Todoist
        task = todoist_api.add_task(
            content=task_name,
            description=description,
            due_date=due_date,
            priority=priority,
            project_id=project_id,  # Add to the relevant project
            label_ids=label_ids    # Add tags as labels
        )
        print(f"Task '{task.content}' added successfully with project '{project_name}' and labels {tags}.")

        # Handle sub-tasks if they exist (you need to create the main task first)
        sub_tasks = task_details['Sub-tasks'] if pd.notna(task_details['Sub-tasks']) else ""
        if sub_tasks:
            sub_task_list = sub_tasks.split(",")  # Assuming sub-tasks are comma-separated
            for sub_task_name in sub_task_list:
                todoist_api.add_task(
                    content=sub_task_name.strip(),
                    parent_id=task.id,  # Set the parent task ID
                    description=f"Sub-task of {task_name}"
                )
                print(f"Sub-task '{sub_task_name.strip()}' added under '{task_name}'.")

    except Exception as error:
        print(f"Error adding task '{task_details['Task Name']}': {error}")

# Main function to iterate through the tasks in Excel and add them to Todoist
def main():
    # Iterate over each task in the Excel DataFrame and add it to Todoist
    for index, row in tasks_df.iterrows():
        task_details = {
            'Task Name': row['Task Name'],
            'Status': row['Status'],
            'Date Created': row['Date Created'],
            'Priority': row['Priority'],
            'Description': row['Description'],
            'Due Date': row['Due Date'],
            'Tags': row['Tags'],
            'Assignee': row['Assignee'],
            'Sub-tasks': row['Sub-tasks'],
            'Summary': row['Summary'],
            'Parent-task': row['Parent-task']
        }
        # add_task_to_todoist(task_details)
        print (task_details)

if __name__ == "__main__":
    main()
