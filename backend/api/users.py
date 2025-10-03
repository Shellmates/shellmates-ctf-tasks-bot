from datetime import datetime, timezone
from bson import ObjectId
from database.mongo_config import connection
from typing import Optional, Any, List,  Dict
db= connection()
users= db["users"]

#The function is used to initialize a register of fields 
class UserModel:
    
    def __init__(self, username: Optional[str] , roles: Optional[str], 
                 defaultremindertime: Optional[datetime]= None,
                 userid: Optional[str]=None):
        self._id= ObjectId(userid) if userid else ObjectId()
        self.username= username
        self.roles= roles
        self.defeaultremindertime= defaultremindertime        

#The function is used for transfering the register to a dictionary for MongoDB    
   
    def todict(self) -> Dict[str, Any]:
        return {
            "_id": self._id,
            "username": self.username,
            "roles": self.roles,
            "deafultremindertime": self.defeaultremindertime
        }
    @classmethod
    def fromdict(cls, data: Dict[str, Any]):
        return cls(
            username= data.get("username"),
            userid= str(data.get("_id")) if data.get("_id") else None,
            roles= data.get("roles"),
            defaultremindertime= data.get("defaultremindertime")
        )
'''

    This function will check if the task requesters has
    has permission to perform a task
    :param action : expresses the desired task
    :param requester : a dictionary for the query performer
    :param task : the task that is being created or updated

'''
def haspermission(action: str, requester: dict, task: dict = None) -> bool:
    role = requester.get("roles")
    if role == "manager":
        return True

    if role == "member":
        if action == "assign_task":
            return False
        
        if action in { "get_task", "list_tasks", "mark_task_done", "assign_manager"}:
            if task is None:
                return False
            else:
                return requester.get("_id") in task.get("assignees", [])
        
        if action == "cancel_task":
            if task is None:
                return False
            else: 
                return requester.get("username") == task.get("createdby")
'''

    This function is used to check if the user has access
    to manage users

'''
def managingusers( userid ) -> bool:
    user= users.find_one({"_id": userid})  
    role = user["roles"] 
    if role == "manager":
        return True
    else:
        return False
'''

    This function will check if there is a user with the provided ID
    and create one if there isn't 
    :param username : used for naming the user if they don't exist in the db

'''

def getorcreateuser(userid, username) -> dict:
    user = users.find_one({"_id": userid})
    if user: return user
    
    new_user = UserModel(
        username= username,
        roles = "member",
        defaultremindertime= None,
        userid=userid
    )      
    users.insert_one(new_user.todict())
    return new_user.todict()

'''

    This function is used to assign users as managers with 
    more privileges 
    :param ifalloweduser : a dictionary of the user to check their permission
   
'''

def assignmanager(ifalloweduser: dict, newmanagerid: str, username: str):
    
    token = managingusers(ifalloweduser.get("_id") )
    if token:
         user = getorcreateuser(newmanagerid, username)
         idd  = user.get("_id")
         updateduser = users.update_one(
             {"_id": idd},
             {"$set": {"roles": "admin"}}
            )  
         print(f"user {username} has been promoted to manager")
         return updateduser
    else:
         print("Permission isn't granted!")
         return None

    
