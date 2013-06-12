"""Simple Service that acts as a flatfile database"""
from service import Service

class Database(Service):
	"""docstring for Database"""
	def __init__(self, root_directory):
		super(Database, self).__init__()
		self.root_directory = root_directory
		self.service_id = "DATABASE"

	def lookup_record(self,hash_name):
		path = self.root_directory+"/"+hash_name
		##figure out what exceptions can go horribly wrong here
		record_file = file(path,"r") 
		content = record_file.read()
		record_file.close()
		return content

	def write record(self,hash_name, file_contents):
		path = self.root_directory+"/"+hash_name
		record_file(path,"w")
		record_file.write(file_contents)
		record_file.close()

	def handle_message(self, msg):
		if not msg.service == self.service_id:
			return false
		if msg.get_content("type") == "GET":
			filename = msg.self.destination_node
			content = lookup_record(self,filename)
			newmsg = Database_Message(msg.origin_node, self.owner.ID, msg.destination_node):)
			newmsg.add_content("file_contents",content)
			self.owner.send_msg(newmsg)
		if msg.get_content("type") == "PUSH":
			filename = msg.self.destination_node
			self.write_record(filename, msg.get_content("file_contents"))
			

