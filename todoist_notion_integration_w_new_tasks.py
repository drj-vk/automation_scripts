from datetime import datetime, time as dtime
from todoist_api_python.api import TodoistAPI
from notion_client import Client

import os
import json
from typing import Optional

# Todoist -> Notion sync script
# Updated 2026-02-13 to match new Notion task database schema:
# - Priority: P1-P4 scale (was Low/Medium/High)
# - Energy: High/Medium/Low (new property)
# - Waiting on: text field (new property)
# - Status: defaults to Backlog for triage

script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "config.json")

with open(config_path) as f:
    config = json.load(f)

TODOIST_API_KEY = config["TODOIST_API_KEY"]
NOTION_API_KEY = config["NOTION_API_KEY"]
DATABASE_ID = config["database_id"]
DATA_SOURCE_NAME: Optional[str] = config.get("data_source_name")

todoist_api = TodoistAPI(TODOIST_API_KEY)
notion_api = Client(auth=NOTION_API_KEY, notion_version="2025-09-03")

# --- Priority mapping ---
# Todoist priority: 1 = lowest, 2 = low, 3 = high, 4 = urgent
# Notion priority: P1 (must do today), P2 (must do this week), P3 (should do this week), P4 (can wait)
PRIORITY_MAP = {
    1: "P4 - Can wait",
    2: "P3 - Should do this week",
    3: "P2 - Must do this week",
    4: "P1 - Must do today",
}

# --- Label-to-energy mapping ---
# If a Todoist label matches one of these, set the Energy property and remove it from Tags.
ENERGY_LABELS = {
    "deep_work": "High - Deep work",
    "deep": "High - Deep work",
    "structured": "Medium - Structured work",
    "admin": "Low - Admin/routine",
    "routine": "Low - Admin/routine",
    "quick": "Low - Admin/routine",
}

# --- Labels to exclude from Tags ---
# These are redundant with the Project relation or other properties.
# Add any Todoist labels here that should not become Notion Tags.
EXCLUDE_LABELS = set(ENERGY_LABELS.keys())


def get_data_source_id(database_id: str, preferred_name: Optional[str]) -> str:
    """Resolve the target data source ID for page creation."""
    try:
        db = notion_api.databases.retrieve(database_id)
    except Exception as error:
        raise RuntimeError(
            f"[notion] failed to retrieve database {database_id}: {error}"
        )

    data_sources = db.get("data_sources") or []

    if not data_sources:
        return database_id

    if preferred_name:
        for ds in data_sources:
            if (ds.get("name") or "").strip().lower() == preferred_name.strip().lower():
                return ds["id"]

    return data_sources[0]["id"]


def build_description(task) -> str:
    """Build the description string including any Todoist comments and attachments."""
    parts = []

    if task.description:
        parts.append(task.description)

    try:
        if getattr(task, "comment_count", 0) > 0:
            comments = todoist_api.get_comments(task_id=task.id)
            for comment in comments:
                if comment.content:
                    parts.append(f"Comment: {comment.content}")
                file_url = getattr(
                    getattr(comment, "attachment", None), "file_url", None
                )
                if file_url:
                    parts.append(f"Attachment: {file_url}")
    except Exception as e:
        print(f"[todoist] warning: could not fetch comments for task {task.id}: {e}")

    return "\n".join(parts)[:2000]


def resolve_energy(labels: list[str]) -> Optional[str]:
    """Check if any label maps to an energy level. Returns the first match or None."""
    for label in labels:
        normalized = label.strip().lower()
        if normalized in ENERGY_LABELS:
            return ENERGY_LABELS[normalized]
    return None


def filter_labels(labels: list[str]) -> list[str]:
    """Remove labels that are mapped to energy or otherwise excluded."""
    return [
        label
        for label in labels
        if label.strip().lower() not in EXCLUDE_LABELS
    ]


def add_task_to_notion(task, data_source_id: str) -> None:
    """Create a Notion page from a Todoist task, then close the Todoist task."""
    task_name = task.content
    task_due = task.due.date if task.due is not None else None
    task_created = task.created_at
    task_labels = list(task.labels or [])
    task_priority = task.priority or 1

    task_created_date = (
        task_created.date().isoformat()
        if isinstance(task_created, datetime)
        else datetime.strptime(task_created, "%Y-%m-%dT%H:%M:%S.%fZ").date().isoformat()
    )

    description = build_description(task)
    energy = resolve_energy(task_labels)
    clean_labels = filter_labels(task_labels)
    priority_name = PRIORITY_MAP.get(task_priority, "P4 - Can wait")

    # Build Notion page properties
    properties = {
        "Task name": {"title": [{"text": {"content": task_name}}]},
        "Status": {"status": {"name": "Backlog"}},
        "Date Created": {"date": {"start": task_created_date}},
        "Priority": {"select": {"name": priority_name}},
    }

    if description:
        properties["Description"] = {
            "rich_text": [{"text": {"content": description}}]
        }

    if energy:
        properties["Energy"] = {"select": {"name": energy}}

    if task_due:
        if isinstance(task_due, str):
            due_date_obj = datetime.strptime(task_due, "%Y-%m-%d").date()
        elif isinstance(task_due, datetime):
            due_date_obj = task_due.date()
        else:
            due_date_obj = task_due  # already a date object
        due_dt = datetime.combine(due_date_obj, dtime(hour=9, minute=0))
        properties["Due date"] = {"date": {"start": due_dt.isoformat()}}

    if clean_labels:
        properties["Tags"] = {
            "multi_select": [{"name": label} for label in clean_labels]
        }

    try:
        notion_api.pages.create(
            parent={"data_source_id": data_source_id},
            properties=properties,
        )
        todoist_api.complete_task(task_id=task.id)
        print(f"[ok] {task_name}")
    except Exception as error:
        print(f"[notion] error creating page for task '{task_name}' ({task.id}): {error}")


def main():
    # Resolve data source
    try:
        data_source_id = get_data_source_id(DATABASE_ID, DATA_SOURCE_NAME)
    except Exception as e:
        raise SystemExit(e)

    # Fetch Todoist tasks (API returns paginated results; flatten all pages)
    try:
        tasks = [
            task
            for page in todoist_api.get_tasks()
            for task in (page if isinstance(page, list) else [page])
        ]
    except Exception as error:
        print(f"[todoist] error fetching tasks: {error}")
        return

    if not tasks:
        print("[todoist] no tasks to sync")
        return

    print(f"[todoist] found {len(tasks)} tasks to sync")

    for task in tasks:
        add_task_to_notion(task, data_source_id)

    print("[done]")


if __name__ == "__main__":
    main()