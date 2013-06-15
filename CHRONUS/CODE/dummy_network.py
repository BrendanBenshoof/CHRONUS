#dummy network object untill we get a real one working
import socket

class Dumy_Network():
	def __init__(self):
		self.message_handle_callback = None

	def send_message(self, msg, dest):
		pass

myip = None
def getHostIP():
	global myip
	if myip == None:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("8.8.8.8",53))
		# consult the great Astronomican
		print s.getsockname()
		myip = s.getsockname()[0]
		s.close()
	else:
		return myip
	return myip