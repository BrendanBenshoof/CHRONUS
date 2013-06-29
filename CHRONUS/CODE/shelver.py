from service import Service
from message import Database_Message
from threading import Lock
import hash_util
import shelve

GET = "GET"
PUT = "PUT"
DATABASE = "DATABASE"
ECHO = "ECHO"
RESPONSE = "RESP"

class Shelver(Service):
    """docstring for Database"""
    def __init__(self, db):
        super(Database, self).__init__()
        self.service_id = DATABASE
        self.write_lock = Lock()
        self.db = db

    def lookup_record(self, hash_name):
        records = shelve.open(self.db)
        content None
        try:
            print "looking up:"+hash_name
            content = records[hash_name]    #this retrieved COPY OF CONTENT
        except KeyError: 
            content =  "404 Error"
        finally:
            records.close()
            return content

    def write_record(self, hash_name,content):
        self.write_lock.acquire()
        records = shelve.open(self.db)
        records[hash_name] = content
        records.close()
        self.write_lock.release()
        return True

    def put_record(self,name,data):
        hash_loc = hash_util.hash_str(name)
        newmsg = Database_Message(self.owner,hash_loc,DATABASE,PUT)
        newmsg.add_content("file_contents",data)
        self.callback(newmsg)

    def get_record(self,name):
        hash_loc = hash_util.hash_str(name)
        newmsg = Database_Message(self.owner,hash_loc,ECHO,GET)
        self.callback(newmsg)


    def handle_message(self, msg):
        if not msg.service == self.service_id:
            return False
        if msg.get_content("type")  == GET:
            name = str(msg.destination_key)
            content = self.lookup_record(name)  #str(index)
            sendDataBack()
        if msg.get_content("type")  == PUT:
            name = str(msg.destination_key)
            self.write_record(name,msg.get_content("file_contents"))
        if msg.get_content("type") == RESPONSE:
            print msg.get_content("file_contents")