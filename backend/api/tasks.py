from datetime import datetime, timezone
from bson import ObjectId
from database.mongo_config import tasks



def create_task(userid, title, description=None, deadline=None,priority="Normal" ):
     task = {
        "title": title,
        "description": description,
        "assignees": [userid],
        "status": "pending",
        "priority": priority,
        "deadline": deadline,
        "date of creation": datetime.now(tz=timezone.utc)
    }
     createdtask = tasks.insert_one(task)
     task["_id"] = createdtask.inserted_id
     return task
  
"""
    This function will create a task and adds it to the database.
    :param userid : The ID of the user that the task was assigned to.

"""

def get_task(taskid):
       return tasks.find_one(ObjectId(taskid))
    
"""
    
    This function will get the wanted task and return it 
    
"""

def list_tasks(filters=None):
       if filters is None:
          filters = {} 
       return list(tasks.find_one(filters))  

"""

This function will list all the tasks availabe in the database
:param filters : Used for the  

"""
def assign_task(taskid, assigneeid):
         updatedtask = tasks.update_one(
             {"_id" :ObjectId(taskid)},
             {"$push": {"assignees": assigneeid}} 
        )
         return tasks.find_one(ObjectId(taskid))
   
"""

    This function will assign a task to a user and adds their id
    in the assignee field in the database and return the updated task.
 
"""
  
def mark_task_done (taskid, donebyid):
       updatedtask = tasks.update_one(
          {"_id" :ObjectId(taskid)},
          {"$set": {"status": "Done"}, "$pull": {"assignees": donebyid}}
        )
       return tasks.find_one(ObjectId(taskid))
    
"""
   
     This function will mark a task as done by  and adds their id
    in the assignee field in the database and return the updated task.
    :param donebyid : The ID of the person who has done the 

"""

def cancel_task(taskid, cancelledbyid):
      cancelledtask = tasks.update_one(
           {"_id": ObjectId(taskid)},
           {"$set": {"status": "Cancelled", "cancelled by": cancelledbyid, "canceled at": datetime.now(tz=timezone.utc)}}
      )
      return tasks.find_one(ObjectId(taskid))
"""   

    This function will mark a task cancelled and register who cancelled it
    and the time of cancellation in the database
    :param cancelledbyid : The ID of the user who cancelled the task

"""      

   