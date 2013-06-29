from service import *
from message import *
from hash_util import *

MAP_REDUCE = "MAP_REDUCE"

class Disseminate_Message(Message):
    pass

class Map_Message(Message):
    """docstring for Map_Message"""
    def __init__(self, origin_node, destination_key, key_range, map_function, reduce_function, job_id):
        Message.__init__(self)
        self.origin_node = origin_node
        self.destination_key = destination_key
        self.service  = "MAP_REDUCE"
        self.key_range =  key_range
        self.map_function = map_function
        self.reduce_function = reduce_function
        self.job_id = job_id
        

def map_reduce(data, map_function, reduce_function):
    pairs  = assignKeys()
    send_map_reduce()

