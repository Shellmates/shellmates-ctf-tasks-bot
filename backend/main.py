"""

This file is dedicated for testing now

"""

from api.tasks import create_task, get_task, list_tasks, assign_task, mark_task_done, cancel_task
from api.users import users

if __name__ == "__main__":
   task = create_task("123456", "Write report", "Finish backend report", "2025-09-20", "high")
   print("Created Task:", task)
   task1 = assign_task(task["_id"], "00766647")
   fetched = get_task(task1["_id"])
   print("Task is", fetched)
   task2 = mark_task_done(task1["_id"], "00766647")
   fetched = get_task(task["_id"])
   print("Fetched Task:", fetched)
   task3 = cancel_task(task2["_id"], "00766647")
   fetched = get_task(task["_id"])
   print("Fetched Task:", fetched)