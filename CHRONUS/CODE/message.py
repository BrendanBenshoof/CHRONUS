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
        self.service = None
        self.messagetype = 0
        self.destination_node = 0
        self.origin_node = 0

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
    def __init__(self, dest, origin_node, requester, key):
        Message.__init__(self)
        self.origin_node = origin_node  # node that just sent this message
        self.requester = requester      # node we need to reply back with an update
        self.destination_node = dest    # node we're asking to do the finding
        self.add_content("key", key)
        self.add_content("requester", requester)
        self.service = "FIND"



class Update_Message(Message):
    def __init__(self, dest, origin_node,key,node):
        Message.__init__(self)
        self.origin_node = origin_node
        self.destination_node = dest
        self.add_content("key",key)
        self.add_content("node",node)   # the node to connect to
        self.service = UPDATE

class Database_Message(Message):
    def __init__(self, dest, origin_node, file_type):
        Message.__init__(self)
        self.origin_node = origin_node
        self.destination_node = dest
        self.service = "DATABASE"
        self.add_content("type",file_type)


class Sucessor_Message(Message):
    def __init__(self, dest, origin_node,key):
        Message.__init__(self)
        self.origin_node = origin_node
        self.destination_node = dest
        self.service = "JOIN"