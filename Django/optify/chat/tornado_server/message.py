import json
from datetime import datetime
class Message:
    def __init__(self,message,user_id,room_id,session_id=0,is_json=False):
        if is_json:
            self.json_message = message
        else:
            self.message = message
        self.session_id = session_id    
        self.user_id = user_id
        self.room_id = room_id
    def frameForRedis(self):        
        return json.dumps({
            "sender":self.user_id,
            "room_id":self.room_id,
            "message":self.message,
            "session_id":self.session_id
        })
    def save_params(self):
        """ return parameters according to (date_created,date_modified,text,room,user) """ 
        return [datetime.utcnow(),datetime.utcnow(),self.message,self.room_id,self.user_id]        
    def frameForuser(self):
        return json.dumps(self.json_message)