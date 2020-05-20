import tornado.ioloop
import tornado.websocket
import tornado
# import redis
import asyncio
from message import Message
import aioredis
import asyncpg
import uuid
# from optify.settings import DATABASES
DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'd30pv3n8cs014v',
            'USER': 'tmkqpymlyrvjoj',
            'PASSWORD': '84e52983d0b8219a68e2a0f62b50f24e83d699344c805a44408b062aa6ef67a0',
            'HOST': 'ec2-54-247-89-181.eu-west-1.compute.amazonaws.com',
            'PORT': '5432',
        }
}
redis = None
pool = None
loop = None
class MainHandler(tornado.websocket.WebSocketHandler):
    def __init__(self,*args,**kwargs):
        super(MainHandler,self).__init__(*args,**kwargs)        
        self.loop = loop
        self.redis = None
    def check_origin(self, origin):
        return True        
    async def open(self,room,**kwargs):   
        try:   
            uuid.UUID(room)
            self.room_id = room      
            token = self.get_argument("token")   
            async with pool.acquire() as connection:                
                user_token =await connection.fetchrow("SELECT * FROM authtoken_token WHERE key=($1)",token)                
                if not user_token or len(user_token)==0:
                    raise Exception("No User Found")
                room = await connection.fetchrow("SELECT * FROM chat_room WHERE id=($1)",room)
                if not room or len(room)==0:
                    raise Exception("No Room Found")
                self.user_id = user_token['user_id']
                roommembers = await connection.fetchrow("SELECT id FROM chat_roommembers WHERE room_id=($1) AND user_id=($2)",self.room_id,self.user_id)
                if not roommembers or len(roommembers)==0:
                    raise Exception("You are not a member of the room")
                max_id = await connection.fetchrow("SELECT max(id) AS max_id FROM chat_message WHERE room_id=($1) AND sender_id=($2)",self.room_id,self.user_id)
                if not max_id or not max_id['max_id']:
                    self.session_id = 1 
                else:
                    self.session_id = max_id["max_id"] + 1

                            
            print("Starting Client with room %s and user token of %s"%(self.room_id,self.user_id))
            self.redis = await connectRedis()
            self.name = "room_%s"%(self.room_id)
            self.channel, = await self.redis.subscribe(self.name)      
            self.loop.asyncio_loop.create_task(self.waitForMessages())
        
        except ValueError:
            self.close(404,"Wrong Room ID Format")        
        except tornado.web.MissingArgumentError:
            self.close(405,"No User Token") 
        except Exception as e:            
            self.close(406,str(e))  
        

    async def on_message(self,message): 
        message = Message(message,self.user_id,self.room_id,self.session_id)
        self.session_id +=1
        await self.redis.publish(self.name,message.frameForRedis())    
        async with pool.acquire() as connection:             
            await connection.execute("INSERT INTO chat_message (date_created,date_modified,text,room_id,sender_id) VALUES (($1),($2),($3),($4),($5))",*message.save_params())       

    async def waitForMessages(self):
        while await self.channel.wait_message():
            try:
                msg = await self.channel.get_json()
                message = Message(msg,self.user_id,self.room_id,is_json=True)
                
                self.write_message(message.frameForuser())
            except:
                continue                
            

        print("Closing")                
    def on_close(self,**kwargs):
        if not self.redis:
            return
        self.redis.unsubscribe(self.name) 
        self.redis.close()        

def make_app():
    return tornado.web.Application([
        (r"/chat/(?P<room>[-0-9a-zA-Z]*)/", MainHandler),
    ])

async def connectRedis():
    return await aioredis.create_redis_pool("redis://h:p1f43f3f10c7cd21d5880d6d588117d330a225f8e4acc84f5e60814389a682a69@ec2-54-246-240-59.eu-west-1.compute.amazonaws.com:26719",minsize=2,maxsize=2)
async def connectPostgresq():
    import ssl
    ctx = ssl.create_default_context(cafile='')
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return await asyncpg.create_pool(ssl=ctx,user=DATABASES['default']['USER'],port=5432,password = DATABASES['default']['PASSWORD'],database= DATABASES['default']['NAME'],host=DATABASES['default']['HOST'])    
async def releaseAll():
    await pool.close()
    
if __name__ == "__main__": 
    import atexit
    import os
    atexit.register(lambda : loop.run_sync(releaseAll)) #Close pg Connection on closing the application
    pool = tornado.ioloop.IOLoop.current().run_sync(connectPostgresq)
    print("Redis Server Connection Established -----")
    loop = tornado.ioloop.IOLoop.current()    
    app = make_app()
    port = 8888
    try:
        port = os.environ["PORT"]
    except:
        pass
    print(port)
    app.listen(port)           

    tornado.ioloop.IOLoop.current().start()    
    
   
    
    
