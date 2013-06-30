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
        super(Shelver, self).__init__()
        self.service_id = DATABASE
        self.write_lock = Lock()
        self.db = db

    def __lookup_record(self, hash_name):
        records = shelve.open(self.db)
        content = None
        try:
            print "looking up:"+hash_name
            content = records[hash_name]    #this retrieved COPY OF CONTENT
        except KeyError: 
            content =  "404 Error"
        finally:
            records.close()
            return content

    def __write_record(self, hash_name,content):
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
        self.send_message(newmsg)

    def get_record(self,name):
        hash_loc = hash_util.hash_str(name)
        newmsg = Database_Message(self.owner,hash_loc,ECHO,GET)
        self.send_message(newmsg)

    def attach_to_console(self):
        ### return a dict of command-strings
        return ["put","get"]

    def handle_command(self, comand_st, arg_str):
        ### one of your commands got typed in
        if comand_st == "put":
            args = arg_str.split(" ",1)
            key = args[0]
            value = args[1]
            self.put_record(key,value)
        elif comand_st == "get":
            self.get_record(arg_str)


    def handle_message(self, msg):
        if not msg.service == self.service_id:
            return False
        if msg.type == "GET":
            filename = str(msg.destination_key)
            content = self.__lookup_record(str(filename))
            #this add other instances of database messages are borked
            return_service = msg.get_content("service")
            newmsg = Database_Message(self.owner, msg.reply_to.key, return_service, "RESP")
            newmsg.add_content("file_contents",content)
            self.send_message(newmsg, msg.reply_to)
        if msg.type == "PUT":
            filename = str(msg.destination_key)
            self.__write_record(filename,msg.get_content("file_contents"))
        if msg.type == "RESP":
            print msg.get_content("file_contents")
