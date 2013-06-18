#Message object Abstraction for CHRONOS application
import pickle
from hash_util import *

#this is an abstract parent class
#you could use it, but it would be boring

def deserialize(in_string):
    return pickle.loads(in_string)
    #there are soo many exceptions I should be catching here

class Message(object):
    def __init__(self):
        self.contents = {}
        self.service = None
        self.destination_key = 0
        self.origin_node = None
        self.return_node = None

    def serialize(self):
        #it would be great if this was encrypted
        #would could also fix this with using a public-key algorithim for p2p communication
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

class Find_Successor_Message(Message):
    def __init__(self, origin_node, dest, requester):
        Message.__init__(self)
        self.one_hop_origin_node = origin_node  # node that just sent this message
        self.destination_key = dest    # node we're asking to do the finding
        self.return_node = requester
        self.add_content("type","FIND")
        self.service = "INTERNAL"



class Update_Message(Message):
    def __init__(self, origin_node, key,node):
        Message.__init__(self)
        self.origin_node = origin_node
        self.destination_key = key
        self.return_node = node   # the node to connect to
        self.add_content("type","UPDATE")
        self.service = "INTERNAL"

class Stablize_Message(Message):
    """docstring for Stablize_Message"""
    def __init__(self, origin_node):
        Message.__init__(self)
        self.origin_node = origin_node
        self.destination_key = add_keys(origin.key, generate_key_with_index(0))
        self.service = "INTERNAL"
        self.add_content("type","STABILIZE")

class Stablize_Reply_Message(Message):
    """docstring for Stablize_Message"""
    def __init__(self, origin_node, destination_key):
        Message.__init__(self)
        self.origin_node = origin_node
        self.destination_key = destination_key
        self.service = "INTERNAL"
        self.add_content("type","STABILIZE_REPLY")
        self. add_content("predecessor", predecessor)

class Notify_Message(Message):
    """docstring for Notify_Message"""
    def __init__(self, origin_node,destination_node):
        Message.__init__(self)
        self.origin_node = origin_node
        self.destination_node = destination_node
        self.service = "INTERNAL"
        self.add_content("type","NOTIFY")
        

class Database_Message(Message):
    def __init__(self, origin_node, dest, file_type):
        Message.__init__(self)
        self.origin_node = origin_node
        self.destination_key = dest
        self.service = "DATABASE"
        self.add_content("type",file_type)