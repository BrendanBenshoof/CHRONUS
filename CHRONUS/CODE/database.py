"""Simple Service that acts as a flatfile database"""
from service import Service
from message import Database_Message
import hash_util
from threading import Lock
class Database(Service):
    """docstring for Database"""
    def __init__(self, root_directory):
        super(Database, self).__init__()
        self.root_directory = root_directory
        self.service_id = "DATABASE"
        self.write_lock = Lock()

    def lookup_record(self,hash_name):
        try:
            print "looking up:"+hash_name
            path = self.root_directory+"/"+hash_name
            ##figure out what exceptions can go horribly wrong here
            record_file = file(path,"r") 
            content = record_file.read()
            record_file.close()
            return content
        except IOError:
            return "404 Error"

    def write_record(self,hash_name, file_contents):
        self.write_lock.acquire()
        print "writing record"
        path = self.root_directory+"/"+hash_name
        record_file= file(path,"w+")
        record_file.write(file_contents)
        record_file.close()
        self.write_lock.release()

    def handle_message(self, msg):
        if not msg.service == self.service_id:
            return False
        if msg.get_content("type") == "GET":
            filename = str(msg.destination_key)
            content = self.lookup_record(str(filename))
            #this add other instances of database messages are borked
            return_service = msg.get_content("service")
            newmsg = Database_Message(self.owner, msg.reply_to.key, return_service, "RESP")
            newmsg.add_content("file_contents",content)
            self.callback(newmsg, msg.reply_to)
        if msg.get_content("type") == "PUT":
            filename = str(msg.destination_key)
            self.write_record(filename, msg.get_content("file_contents"))
        if msg.get_content("type") == "RESP":
            print msg.get_content("file_contents")
            
    
    def put_record(self,name,data):
        hash_loc = hash_util.hash_str(name)
        newmsg = Database_Message(self.owner,hash_loc,"DATABASE","PUT")
        newmsg.add_content("file_contents",data)
        self.callback(newmsg)

    def get_record(self,name):
        hash_loc = hash_util.hash_str(name)
        newmsg = Database_Message(self.owner,hash_loc,"ECHO","GET")
        self.callback(newmsg)

