"""Simple Service that acts as a flatfile database"""
from service import Service
from message import Database_Message
class Database(Service):
    """docstring for Database"""
    def __init__(self, root_directory):
        super(Database, self).__init__()
        self.root_directory = root_directory
        self.service_id = "DATABASE"

    def lookup_record(self,hash_name):
        try:
            path = self.root_directory+"/"+hash_name
            ##figure out what exceptions can go horribly wrong here
            record_file = file(path,"r") 
            content = record_file.read()
            record_file.close()
            return content
        except IOError:
            return "404 Error"

    def write_record(self,hash_name, file_contents):
        print "writing record"
        path = self.root_directory+"/"+hash_name
        record_file= file(path,"w+")
        record_file.write(file_contents)
        record_file.close()

    def handle_message(self, msg):
        if not msg.service == self.service_id:
            return False
        if msg.get_content("type") == "GET":
            filename = msg.destination_node
            content = self.lookup_record(str(filename))
            #this add other instances of database messages are borked
            newmsg = Database_Message(msg.origin_node, self.owner.ID, msg.destination_node)
            newmsg.add_content("file_contents",content)
            self.callback(newmsg)
        if msg.get_content("type") == "PUT":
            filename = str(msg.destination_node.key)
            self.write_record(filename, msg.get_content("file_contents"))
            

