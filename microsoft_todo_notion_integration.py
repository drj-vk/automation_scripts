import requests
from msal import ConfidentialClientApplication
from todoist_api_python.api import TodoistAPI
import json
import os

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Build the full path to config.json
config_path = os.path.join(script_dir, 'config.json')


with open(config_path) as f:
    config = json.load(f)

# # Microsoft Authentication Config
# TENANT_ID = 'YOUR_TENANT_ID'
# CLIENT_ID = 'YOUR_CLIENT_ID'
# CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
# AUTHORITY = f'https://login.microsoftonline.com/{TENANT_ID}'
# SCOPE = ['https://graph.microsoft.com/.default']

# Todoist API Key
TODOIST_API_KEY = config['TODOIST_API_KEY']
ACCESS_TOKEN = config['MICROSOFT_ACCESS_TOKEN']

# # MSAL Confidential Client
# app = ConfidentialClientApplication(
#     client_id=CLIENT_ID,
#     client_credential=CLIENT_SECRET,
#     authority=AUTHORITY
# )

# Fetch access token for Microsoft Graph API
# token_response = app.acquire_token_for_client(scopes=SCOPE)
access_token = ACCESS_TOKEN

# Fetch tasks from Microsoft To-Do
todo_tasks_url = 'https://graph.microsoft.com/v1.0/me/todo/lists'
headers = {'Authorization': 'Bearer ' + access_token}
response = requests.get(todo_tasks_url, headers=headers)
tasks_lists = response.json().get('value', [])

# Initialize Todoist API
todoist_api = TodoistAPI(TODOIST_API_KEY)

for task_list in tasks_lists:
    tasks_url = f"https://graph.microsoft.com/v1.0/me/todo/lists/{task_list['id']}/tasks"
    tasks_response = requests.get(tasks_url, headers=headers)
    tasks = tasks_response.json().get('value', [])

    for task in tasks:
        # Define the task to add to Todoist
        todoist_task = {
            'content': task['title'],
            'description': task.get('body', {}).get('content', ''),
            # Add more fields as needed
        }
        # Create task in Todoist
        try:
            todoist_api.add_task(**todoist_task)
        except Exception as e:
            print(f'Error adding task to Todoist: {e}')

print("Migration completed.")


https://graph.microsoft.com/v1.0/me/todo/lists/{taskListId}/tasks