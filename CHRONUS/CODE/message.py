#Message object Abstraction for CHRONOS application


#this is an abstract parent class
#you could use it, but it would be boring
class Message(object):
	def __init__(self):
		self.content = {}
		self.service = "null"
		self.messagetype = 0
		self.destintation_node = 0
		self.origin_node = 0


	def 