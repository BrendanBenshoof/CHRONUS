"""Simple Service that acts as a flatfile database"""
from service import Service

class Database(Service):
	"""docstring for Database"""
	def __init__(self, root_directory):
		super(Database, self).__init__()
		self.root_directory = root_directory

