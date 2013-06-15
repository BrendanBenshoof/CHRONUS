#dummy network object untill we get a real one working
import socket
import getIP

class Dumy_Network():
	def __init__(self):
		self.message_handle_callback = None

	def send_message(self, msg, dest):
		pass

myip = None
def getHostIP():
	global myip
	if myip == None:
		myip = getIP.get_lan_ip()
	return myip