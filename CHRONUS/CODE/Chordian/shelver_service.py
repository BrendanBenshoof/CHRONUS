from threading import Lock
import threading
import time
import shelve

from super_service import Service
import hash_util
from service_message import *
from constants import *
from rwlock import RWLock



class Node_Db_Context(object):
    def __init__(self, node_info):
        self.sync = RWLock()
        self.db = "db/" + str(node_info.key) + ".db"
        self.node_info = node_info
        self.own_start = None
        self.own_end = None

        #self.back_thread = threading.Thread(target=lambda:  self.backup_loop(self))
        #self.back_thread.daemon = True
        #self.back_thread.start()

    def write(self, hash_name, content):
        self.sync.writer_acquire()
        try:
            records = shelve.open(self.db)
            records[hash_name] = content
            records.close()
            print str(self.node_info) + " write block: " + hash_name
        finally:
            self.sync.writer_release()


    def read(self, hash_name):
        content = None
        self.sync.reader_acquire()
        try:
            records = shelve.open(self.db)
            if not records.has_key(hash_name):
                print str(self.node_info) + " read block: " + hash_name + " FAILED!!"
                content = "404 Error"
            else:
                print str(self.node_info) + " read block: " + hash_name
                content = records[hash_name]    #this retrieved COPY OF CONTENT
            records.close()
        finally:
            self.sync.reader_release()
        return content

    #def backup_loop(self):
    #    while True:
    #        self.periodic_backup()

class Shelver_Service(Service):

    """docstring for Database"""
    def __init__(self, message_router):
        super(Shelver_Service,self).__init__(service_id=SERVICE_SHELVER, message_router=message_router, cl_name="sh")
        self.databases = {}
        self.sync = Lock( )

    def handle_message(self, msg):
        if not msg.dest_service == self.service_id:
            return False
        if msg.type == Message_Console_Command.Type():
            self.handle_command(msg.command,msg.args)
        elif msg.type == Database_Get_Message.Type():
            filename = str(msg.destination_key)
            db_context = self.__get_database_context(msg.storage_node)
            content = db_context.read(str(filename))
            self.send_message(Database_Get_Message_Response(msg.origin_node,msg.storage_node, msg.destination_key, content),
                              msg.origin_node if msg.origin_node != msg.storage_node else None)
        elif msg.type == Database_Put_Message.Type():
            filename = str(msg.destination_key)
            db_context = self.__get_database_context(msg.storage_node)
            db_context.write(filename, msg.file_contents)
            self.send_message(Database_Put_Message_Response(msg.origin_node, msg.storage_node, msg.destination_key, msg.keyfile_hash),
                              msg.origin_node if msg.origin_node != msg.storage_node else None)
        # TO DO: Properly implement these messages and their accompanying functionality in the new model
        elif msg.type == "BACKUP":
            self.integrate(msg.get_content("backup"))
        elif msg.type == "CHANGE_IN_RESPONSIBILITY":
            self.change_in_responsibility(msg.new_pred_key, msg.my_key)
        elif msg.type == Message_Console_Command.Type():
            self.handle_command(msg)
        return True


    def __get_database_context(self, node_info):
        self.sync.acquire()
        try:
            context = None
            if node_info.key in self.databases.keys():
                context = self.databases[node_info.key]
            else:
                context = Node_Db_Context(node_info)
                self.databases[node_info.key] = context
            return context
        finally:
            self.sync.release()

    def put_record(self,node_info, name,data):
        hash_loc = hash_util.hash_str(name)
        newmsg = Database_Put_Message(node_info,hash_loc, data)
        self.send_message(newmsg)

    def get_record(self,node_info, name):
        hash_loc = hash_util.hash_str(name)
        newmsg = Database_Get_Message(node_info,hash_loc,SERVICE_ECHO,GET)
        self.send_message(newmsg)

    def attach_to_console(self):
        ### return a dict of command-strings
        return ["put","get","test_store","test_get"]

    def handle_command(self, msg):
        command_st = msg.command
        args = msg.args

        ### one of your commands got typed in
        if command_st == "put" and len(args) == 2:
            key = args[0]
            value = args[1]
            self.put_record(key,value)
        elif command_st == "get" and len(args) == 1:
            self.get_record(args[1])
        elif command_st == "test_store":
            newfile = file("shelver.py","r")
            counter=0
            for l in newfile:
                self.put_record("book:"+str(counter),l)
                counter+=1
                print counter
            newfile.close()
        elif command_st == "test_get" and len(args) == 1:
            line = args[0]
            self.get_record("book:"+line)

    def integrate(self, new_data): #take a backup dump and integrate with my own data
        #WARNING THIS CODE TRUSTS PEERS
        for k in new_data.keys():
            self.__write_record(k,new_data[k])


    #this doesnt work in new architecture...would have to be updated
    def change_in_responsibility(self,new_pred_key, my_key):
        self.own_start = new_pred_key
        self.own_end = my_key
        backup = {}
        self.write_lock.acquire()
        records = shelve.open(self.db)
        for k in records.keys():
            k_key = hash_util.Key(k)
            if not hash_util.hash_between_right_inclusive(k_key,self.own_start, self.own_end):
                backup[k] = records[k]
        size = len(backup.keys())
        if size > 0:
            newmsg = Database_Backup_Message(self.owner, backup)
            self.send_message(newmsg, node.predecessor)
        records.close()
        self.write_lock.release()

    #this doesnt work in new architecture...would have to be updated
    def periodic_backup(self, node):
        time.sleep(60)
        if not self.own_start is None:
            backup = {}
            self.write_lock.acquire()
            records = shelve.open(self.db)
            for k in records.keys():
                k_key = hash_util.Key(k)
                if hash_util.hash_between_right_inclusive(k_key,self.own_start, self.own_end):
                    backup[k] = records[k]
            size = len(backup.keys())
            if size > 0:
                newmsg = Database_Backup_Message(self.owner, backup)
                self.send_message(newmsg, node.predecessor)
            records.close()
            self.write_lock.release()


