from datetime import datetime, timezone
from bson import ObjectId
from database.mongo_config import connection
from typing import Optional, Dict, List, Any

db = connection()
tasks = db["tasks"]
class TaskModel:

#The function is used to initialize a register of fields   

    def __init__(self, title: str, description: Optional[str]=None, 
                  assignees: Optional[List[str]]=None,
                  deadline: Optional[datetime]=None,
                  taskid: Optional[str]=None,
                  status: str = "Pending",
                  priority: str = "Normal",
                  date_of_creation: Optional[datetime]=None):
        self._id= ObjectId(taskid) if taskid else ObjectId()
        self.title= title
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
        description= data.get("description"),
        assignees= data.get("assignees", []),
        taskid= str(data.get("_id")) if data.get("_id") else None,
        status= data["status","Pending" ],    
        priority= data.get("priority", "Normal"),
        deadline= data.get("deadline"),
        date_of_creation= data.get("date_of_creation", datetime.now(timezone.utc))
      )
      
    """
    
    This function will create a task and adds it to the database
    
    """ 

def create_task(userid, title, description, priority, deadline ):
         task = TaskModel(
              title= title,
              description= description,
              assignees= [userid],
              deadline= deadline,
              priority= priority
         )
         tasks.insert_one(task.todict())
         return task.todict()
    
  
"""

    This function will get the wanted task and return it 
    
"""

def get_task(taskid):
       return tasks.find_one(ObjectId(taskid))
    
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
       return list(tasks.find_one(filters))  

"""

    This function will assign a task to a user and adds their id
    in the assignee field in the database and return the updated task.
 
"""

def assign_task(taskid, assigneeid):
    tasks.update_one(
             {"_id" :ObjectId(taskid)},
             {"$addToSet": {"assignees": assigneeid}} 
        )
    return get_task(taskid)
"""
   
     This function will mark a task as done by  and adds their id
    in the assignee field in the database and return the updated task.
    :param donebyid : The ID of the person who has done the 

"""
  
def mark_task_done (taskid, donebyid):
       tasks.update_one(
          {"_id" :ObjectId(taskid)},
          {"$set": {"status": "Done"}, "$pull": {"assignees": donebyid}}
        )
       return get_task(taskid)
    
"""   

    This function will mark a task cancelled and register who cancelled it
    and the time of cancellation in the database
    :param cancelledbyid : The ID of the user who cancelled the task

"""

def cancel_task(taskid, cancelledbyid):
      tasks.update_one(
           {"_id": ObjectId(taskid)},
           {"$set": {"status": "Cancelled", "cancelled by": cancelledbyid, "cancelled at": datetime.now(tz=timezone.utc)}}
      )
      return get_task(taskid)
      

   