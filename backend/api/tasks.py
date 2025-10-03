from datetime import datetime, timezone
from bson import ObjectId
from database.mongo_config import connection
from typing import Optional, Dict, List, Any
from .users import haspermission, getorcreateuser

db = connection()
tasks = db["tasks"]
class TaskModel:

#The function is used to initialize a register of fields   

    def __init__(self, title: str,  task_creator: str, 
                  description: Optional[str]=None,
                  assignees: Optional[List[str]]=None,
                  deadline: Optional[datetime]=None,
                  taskid: Optional[str]=None,
                  status: str = "Pending",
                  priority: str = "Normal",
                  date_of_creation: Optional[datetime]=None):
        self._id= ObjectId(taskid) if taskid else ObjectId()
        self.title= title
        self.createdby= task_creator
        self.description = description
        self.assignees = assignees or []
        self.status = status
        self.priority = priority
        self.deadline = deadline
        self.date_of_creation= date_of_creation or datetime.now(timezone.utc)

#The function is used for transfering the register to a dictionary for MongoDB

    def todict (self) -> Dict[str, Any]:
        return {
            "_id": self._id,
            "title": self.title,
            "createdby": self.createdby,
            "description": self.description,
            "assignees": self.assignees,
            "status": self.status,
            "priority": self.priority,
            "deadline": self.deadline,
            "date_of_creation": self.date_of_creation
        }       
   
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskModel": #This function is used for converting an object from JSON, BSON format to python object
      return cls(       
        title= data.get("title"),
        created_by= data.get("createdby"),
        description= data.get("description"),
        assignees= data.get("assignees", []),
        taskid= str(data.get("_id")) if data.get("_id") else None,
        status= data.get("status","Pending" ),    
        priority= data.get("priority", "Normal"),
        deadline= data.get("deadline"),
        date_of_creation= data.get("date_of_creation", datetime.now(timezone.utc))
      )
      
    """
    
    This function will create a task and adds it to the database
    
    """ 

def create_task(ifalloweduser: dict , userid, title, description, priority, deadline ):
         token = ifalloweduser.get("_id")
         if token:
             task = TaskModel(
                 title= title,
                 task_creator=ifalloweduser.get("username"),
                 description= description,
                 assignees= [userid],
                 deadline= deadline,
                 priority= priority
            )
             tasks.insert_one(task.todict())
             return task.todict()
         else:
              print("permission isn't granted!")
              return None

  
"""

    This function will get the wanted task and return it 
    
"""

def get_task(taskid, ifalloweduser: dict ):
       task= tasks.find_one({"_id": taskid})
       token = haspermission("get_task", ifalloweduser, task)
       if token:
            return task
       else:
            return None
"""

This function will list all the tasks availabe in the database
:param filters : Used for the purpose of filtering the list of
tasks that the user wants to list
types of filters: {} : lists all the tasks that exist in the db
                  {object: "something"} : lists all the tasks that include the object
                  {object: "something"}, {field: 1} : lists all the tasks that include the object but only the field alongside the _id field
                  {object: "something"}, {field: 0} : lists all the tasks that include the object but excludes the field
"""

def list_tasks(filters=None):
       if filters is None:
          filters = {} 
       return list(tasks.find(filters))  

"""

    This function will assign a task to a user and adds their id
    in the assignee field in the database and return the updated task.
 
"""

def assign_task(taskid, assigneeid, ifalloweduser: dict):
    task = tasks.find_one({"_id": taskid})
    token = haspermission("assign_task", ifalloweduser, task)
    if token:
        tasks.update_one(
             {"_id" :ObjectId(taskid)},
             {"$addToSet": {"assignees": assigneeid}} 
        )
        return tasks.find_one(ObjectId(taskid))
    else:
         return None
"""
   
     This function will mark a task as done by  and adds their id
    in the assignee field in the database and return the updated task.
    :param donebyid : The ID of the person who has done the 

"""
  
def mark_task_done (taskid, ifalloweduser: dict, donebyid=None): 
       task = tasks.find_one(ObjectId(taskid))     
       token = haspermission("mark_task_done", ifalloweduser, task)
       if token: 
        tasks.update_one(
              {"_id" :ObjectId(taskid)},
              {"$set": {"status": "Done"}, "$pull": {"assignees": donebyid}}
            )
        return tasks.find_one(ObjectId(taskid))
       else:
            return None
"""   

    This function will mark a task cancelled and register who cancelled it
    and the time of cancellation in the database
    :param cancelledbyid : The ID of the user who cancelled the task

"""

def cancel_task(taskid, ifalloweduser: dict):
      task = tasks.find_one(ObjectId(taskid))
      token = haspermission("cancel_task", ifalloweduser, task)
      if token:
        cancelledbyid= ifalloweduser.get("_id")
        tasks.update_one(
               {"_id": ObjectId(taskid)},
               {"$set": {"status": "Cancelled", "cancelled by": cancelledbyid, "cancelled at": datetime.now(tz=timezone.utc)}}
        )
        return tasks.find_one(ObjectId(taskid))
      else:  
           return None
        
      

   