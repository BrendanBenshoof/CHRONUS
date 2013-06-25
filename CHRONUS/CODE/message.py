#Message object Abstraction for CHRONOS application
import pickle
from hash_util import *

#this is an abstract parent class
#you could use it, but it would be boring

INTERNAL = "INTERNAL"
FIND = "FIND"
UPDATE =  "UPDATE"
STABILIZE = "STABILIZE"
STABILIZE_REPLY = "STABILIZE_REPLY"
NOTIFY = "NOTIFY"
CHECK_PREDECESSOR = "CHECK_PREDECESSOR"

class Message(object):
    def __init__(self):
        self.contents = {} #nasty collection
        self.service = None #string right now could be int
        self.destination_key = 0 #160 number or hash object
        self.finger = None# int -1 to 160
        self.origin_node = None #node object
        self.return_node = None #node object -> hash_location, IP, port

    @staticmethod
    def deserialize(in_string):
        return pickle.loads(in_string)
        #there are soo many exceptions I should be catching here

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
    def __init__(self, origin_node, destination_key, requester, finger = 1):
        Message.__init__(self)
        self.one_hop_origin_node = origin_node  # node that just sent this message
        self.destination_key = destination_key  # the key we're trying to find the node responsible for
        self.return_node = requester
        self.finger = finger
        self.add_content("type",FIND)
        self.service = INTERNAL

class Update_Message(Message):
    def __init__(self, origin_node, destination_key, node, finger):
        Message.__init__(self)
        self.origin_node = origin_node
        self.destination_key = destination_key
        self.finger = finger        # entry in the finger table to update.
        self.return_node = node     # the node to connect to
        self.add_content("type",UPDATE)
        self.service = INTERNAL

class Stablize_Message(Message):
    """docstring for Stablize_Message"""
    def __init__(self, origin_node):
        Message.__init__(self)
        self.origin_node = origin_node
        self.destination_key = add_keys(self.origin_node.key, generate_key_with_index(0))
        self.return_node = origin_node
        self.service = INTERNAL
        self.add_content("type",STABILIZE)

class Stablize_Reply_Message(Message):
    """docstring for Stablize_Message"""
    def __init__(self, origin_node, destination_key, predecessor):
        Message.__init__(self)
        self.origin_node = origin_node
        self.destination_key = destination_key
        self.service = INTERNAL
        self.add_content("type",STABILIZE_REPLY)
        self. add_content("predecessor", predecessor)
        self.return_node = origin_node

class Notify_Message(Message):
    """docstring for Notify_Message"""
    def __init__(self, origin_node,destination_key):
        Message.__init__(self)
        self.origin_node = origin_node
        self.destination_key = destination_key
        self.service = INTERNAL
        self.add_content("type",NOTIFY)
        self.return_node = origin_node

class Check_Predecessor_Message(Message):
    def __init__(self, origin_node,destination_key):
        Message.__init__(self)
        self.origin_node = origin_node
        self.destination_key = destination_key
        self.service = INTERNAL
        self.add_content("type",CHECK_PREDECESSOR)
        self.return_node = origin_node

class Database_Message(Message):
    def __init__(self, origin_node, destination_key, file_type):
        Message.__init__(self)
        self.origin_node = origin_node
        self.destination_key = destination_key
        self.service = "DATABASE"
        self.add_content("type",file_type)
        self.return_node = origin_node
