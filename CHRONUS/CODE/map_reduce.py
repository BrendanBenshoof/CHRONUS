from service import *
from message import *
from hash_util import *
import node

MAP_REDUCE = "MAP_REDUCE"
MAP = "MAP"
REDUCE = "REDUCE"
DISSEMINATE = "DISSEMINATE" 

class Disseminate_Message(Message):
    pass

class Map_Message(Message):
    """docstring for Map_Message"""
    def __init__(self, origin_node, destination_key, key_range, map_function, reduce_function, job_id):
        Message.__init__(self)
        self.origin_node = origin_node
        self.destination_key = destination_key
        self.service  = MAP_REDUCE
        self.add_content = ("key_range", key_range)
        self.add_content = ("map_function", map_function)
        self.add_content = ("reduce_function", reduce_function)
        self.add_content = ("job_id", job_id)

class Reduce_Message(Message):
    def __init__(self, origin_node, destination_key, key_range, reduce_function, job_id):
        Message.__init__(self)
        self.origin_node = origin_node
        self.destination_key = destination_key
        self.service  = MAP_REDUCE
        self.add_content = ("key_range", key_range)
        self.add_content = ("reduce_function", reduce_function)
        self.add_content = ("job_id", job_id)

def disseminate_data(data, job_id):
    pass

def map_reduce(data, map_function, reduce_function, job_id):
    pairs  = assignKeys()
    send_map_reduce()

def handle_map():
    pass

def handle_reduce():
    pass

def emit():
    pass



#########Brendan's work starts

class Map_Reduce(Service):
    def __init__(self):
        super(Service, self).__init__()
        self.service_id = MAP_REDUCE
        self.responsible_start = self.owner.key
        self.responsible_end = self.owner.key

    def change_in_responsibility(new_pred_key, my_key):
        self.responsible_start = new_pred_key
        self.responsible_end = my_key 

    def handle_message(self, msg):
        if node.TEST_MODE:
            print("Got Map-Reduce")
        if msg.service != self.service_id
            cry()
            return False
        msgtype = msg.get_content("type")
        if msgtype == DISSEMINATE:
            pass
        elif msgtype == MAP:
            pass
        elif msgtype == REDUCE:
            pass
        else:
            cry()
            return False
        return True



##########Brendan's work ends

def cry():
    print("Your code is bad, and you should feel bad. https://www.youtube.com/watch?v=BSKVEkMiTMI")