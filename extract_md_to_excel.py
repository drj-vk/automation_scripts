import os
import pandas as pd
import re

# Define the folder where the .md files are located
folder_path = './Tasks/'

# Regular expressions to extract the relevant information
status_pattern = re.compile(r'Status:\s*(.*)')
due_date_pattern = re.compile(r'Due date:\s*(.*)')
project_pattern = re.compile(r'Project:\s*\-\s*(.*)')
priority_pattern = re.compile(r'Priority:\s*(.*)')
tags_pattern = re.compile(r'tags:\s*\-\s*(.*)')
date_created_pattern = re.compile(r'Date Created:\s*(.*)')

# List to store each task's information
tasks = []

# Loop over all files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith('.md'):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Extract the relevant information using regular expressions
        status = re.search(status_pattern, content)
        due_date = re.search(due_date_pattern, content)
        project = re.search(project_pattern, content)
        priority = re.search(priority_pattern, content)
        tags = re.findall(tags_pattern, content)
        date_created = re.search(date_created_pattern, content)

        # Store the information in a dictionary
        task_info = {
            'Task': filename.replace('.md', ''),
            'Status': status.group(1).strip() if status else None,
            'Due Date': due_date.group(1).strip() if due_date else None,
            'Project': project.group(1).strip() if project else None,
            'Priority': priority.group(1).strip() if priority else None,
            'Tags': ', '.join(tags) if tags else None,
            'Date Created': date_created.group(1).strip() if date_created else None
        }

        tasks.append(task_info)

# Create a DataFrame from the tasks list
df = pd.DataFrame(tasks)

# Save the DataFrame to an Excel file
output_file = 'tasks.xlsx'
df.to_excel(output_file, index=False)

print(f'Tasks exported to {output_file}')
