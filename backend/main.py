"""
This file is dedicated for testing now
"""

from api.tasks import create_task, get_task, list_tasks, assign_task, mark_task_done, cancel_task
from api.users import getorcreateuser, assignmanager, haspermission
from bson import ObjectId
#test notice use the userid provided or another hex 24 chars string to avoid duplicates instead of None in the following functions
# userid = "517f1f77bcf86cd799439011"
if __name__ == "__main__": 
    dbuser = getorcreateuser(None, "tedjeddine")
    task = create_task(dbuser, None, "Write report", "Finish backend report", "high", "2025-09-20")
    cancelledtask= cancel_task(task.get("_id"), dbuser)
   # print("Task:", task)
    #print("cancelledtask:", cancelledtask)
