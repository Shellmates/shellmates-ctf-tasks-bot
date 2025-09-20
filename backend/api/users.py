from datetime import datetime, timezone
from bson import ObjectId
from database.mongo_config import connection
from typing import Optional, Any, List,  Dict
db= connection()
users= db["users"]

class UserModel:
    def __init__(self, username: Optional[str] , roles: Optional[str], 
                 defaultremindertime: Optional[datetime]= None,
                 userid: Optional[str]=None):
        self._id= ObjectId(userid)
        self.username= username
        self.roles= roles
        self.defeaultremindertime= defaultremindertime        
    
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
    