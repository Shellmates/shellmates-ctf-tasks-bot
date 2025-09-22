"""

This file is dedicated for testing now

"""

from api.tasks import create_task, get_task, list_tasks, assign_task, mark_task_done, cancel_task
from api.users import users

if __name__ == "__main__":
   task = create_task("123456", "Write report", "Finish backend report", "high", "2025-09-20")
   print("Created Task:", task)
   task = assign_task(task["_id"], "00766647")
   fetched = get_task(task["_id"])
   print("Task is", fetched)
   task = mark_task_done(task["_id"], "00766647")
   fetched = get_task(task["_id"])
   print("Fetched Task:", fetched)
   task = cancel_task(task["_id"], "00766647")
   fetched = get_task(task["_id"])
   print("Fetched Task:", fetched)