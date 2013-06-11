#Message object Abstraction for CHRONOS application
import pickle

#this is an abstract parent class
#you could use it, but it would be boring

def deserialize(in_string):
	return pickle.loads(in_string)
	#there are soo many exceptions I should be catching here

class Message(object):
	def __init__(self):
		self.contents = {}
		self.service = "null"
		self.messagetype = 0
		self.destination_node = 0
		self.origin_node = 0

	def serialize(self):
		return pickle.dumps(self)

	def add_content(self, key, data):
		self.contents[key] = data

	def get_content(self, key):
		to_return = None
		try:
			to_return = self.contents[key]
		except IndexError:
			print "get_content was asked to look for a non-existant key"
		return to_return



