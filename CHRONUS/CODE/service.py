from message import *
from hash_util import *
class Service(object):
	"""This object is intented to act as a parent/promise for Service Objects"""
	def __init__(self):
		self.service_id = None
		self.owner = None
	def attach(self, owner):
		"""Called when the service is attached to the node"""
		"""Should return the ID that the node will see on messages to pass it"""
		self.owner = owner
		return self.service_id

	def handle_message(self, msg):
		"""This function is called whenever the node recives a message bound for this service"""
		"""Return True if message is handled correctly
		Return False if things go horribly wrong
		"""
		return msg.service == self.service_id
		