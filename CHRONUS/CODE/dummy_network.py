#dummy network object untill we get a real one working
import socket
import getIP
import urllib2
import NATPMP
LAN_mode = True

class Dummy_Network():
	def __init__(self):
		self.message_handle_callback = None

	def send_message(self, msg, dest):
		pass

	def add_node(self, callback):
		self.message_handle_callback = callback

myip = None
def getHostIP():
	global myip
	if myip == None:
		if LAN_mode:
			myip = getIP.get_lan_ip()
		else:
			myip = NATPMP.get_public_address()
	return myip