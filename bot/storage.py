import json
from datetime import datetime

TASKS_FILE = "tasks.json"

def load_tasks():
    try:
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

def add_task(title, assignee, due_date):
    tasks = load_tasks()
    task_id = len(tasks) + 1
    task = {
        "id": task_id,
        "title": title,
        "assignee": assignee,
        "due_date": str(due_date),
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "reminded": False
    }
    tasks.append(task)
    save_tasks(tasks)
    return task

def get_user_tasks(user_id):
    return [t for t in load_tasks() if t["assignee"] == user_id and t["status"] == "pending"]

def get_all_tasks():
    return load_tasks()

def mark_task_done(task_id, user_id, is_manager=False):
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            if t["assignee"] != user_id and not is_manager:
                return False, "You can only complete your own tasks."
            if t["status"] == "done":
                return False, "This task is already done."
            t["status"] = "done"
            save_tasks(tasks)
            return True, f"✅ Task **{t['title']}** marked done."
    return False, "Task not found."
