#currently just a test script
#eventually to be the startup scrip for CHRONUS

import database as db 
import network_handler as net
import hash_util as hash
from message import *
class DummyOwner:
	def __init__(self):
		self.ID = "BOB"
	def send_msg(self, msg):
		print msg.get_content("file_contents")

M = Database_Message(hash.Key("0x40bbbc5d957d85546cd78956788708c8"),hash.generate_random_key(),"GET")
M.add_content("file_contents",str(hash.generate_random_key())) 

D = db.Database("../DATABASE")
dummy = DummyOwner()

D.attach(dummy.send_msg,dummy)
D.handle_message(M)
