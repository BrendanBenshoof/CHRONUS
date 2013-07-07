#Message object Abstraction for CHRONOS application
import pickle
from globals import *
from hash_util import *

#this is an abstract parent class
#you could use it, but it would be boring

FIND = "FIND"
UPDATE =  "UPDATE"
STABILIZE = "STABILIZE"
STABILIZE_REPLY = "STABILIZE_REPLY"
NOTIFY = "NOTIFY"
CHECK_PREDECESSOR = "CHECK_PREDECESSOR"
POLITE_QUIT = "POLITE_QUIT"
FAILURE = "FAILURE"

class Message(object):
    def __init__(self, service, type, success_callback_msg = None, failed_callback_msg = None):
        self.origin_node = None     # One hop origin
        self.destination_key = generate_random_key()    # 160 number or hash object
        self.reply_to = None        # Node to reply to
        self.contents = {}          # All other data
        self.service = service      # What service handles this
        self.type = type
        self.success_callback_msg = success_callback_msg
        self.failed_callback_msg = failed_callback_msg
        self.finger = None          # int -1 to 160


    @staticmethod
    def deserialize(in_string):
        try:
            return pickle.loads(in_string)
        except EOFError:
            fail_message = Message()
            fail_message.service = FAILURE
            return fail_message
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
        Message.__init__(self, SERVICE_INTERNAL, FIND)
        self.origin_node = origin_node  # node that just sent this message
        self.destination_key = destination_key  # the key we're trying to find the node responsible for
        self.reply_to = requester
        self.finger = finger

class Update_Message(Message):
    def __init__(self, origin_node, destination_key, finger):
        Message.__init__(self,SERVICE_INTERNAL, UPDATE)
        self.origin_node = origin_node
        self.destination_key = destination_key  #key we are sending it back to
        self.finger = finger        # entry in the finger table to update.
        self.reply_to = origin_node     # the node to connect to


class Stablize_Message(Message):
    """docstring for Stablize_Message"""
    def __init__(self, origin_node, successor):
        Message.__init__(self, SERVICE_INTERNAL, STABILIZE)
        self.origin_node = origin_node
        self.destination_key = successor.key
        self.reply_to = origin_node

class Stablize_Reply_Message(Message):
    """docstring for Stablize_Reply_Message"""
    def __init__(self, origin_node, destination_key, predecessor):
        Message.__init__(self, SERVICE_INTERNAL, STABILIZE_REPLY)
        self.origin_node = origin_node
        self.destination_key = destination_key
        self.add_content("predecessor", predecessor)
        self.reply_to = origin_node

class Notify_Message(Message):
    """docstring for Notify_Message"""
    def __init__(self, origin_node,destination_key):
        Message.__init__(self, SERVICE_INTERNAL, NOTIFY)
        self.origin_node = origin_node
        self.destination_key = destination_key
        self.reply_to = origin_node

class Check_Predecessor_Message(Message):
    def __init__(self, origin_node,destination_key):
        Message.__init__(self, SERVICE_INTERNAL, CHECK_PREDECESSOR)
        self.origin_node = origin_node
        self.destination_key = destination_key
        self.reply_to = origin_node

class Exit_Message(Message):
    """docstring for Notify_Message"""
    def __init__(self, origin_node, destination_key):
        Message.__init__(self, SERVICE_INTERNAL, POLITE_QUIT)
        self.origin_node = origin_node
        self.destination_key = destination_key
        self.reply_to = origin_node



# Messages specific to Network_Service

class Message_Start_Server(Message):
    def __init__(self, host_ip, host_port, success_callback_msg=None, failed_callback_msg=None):
        Message.__init__(self, SERVICE_NETWORK, MESSAGE_START_SERVER, success_callback_msg, failed_callback_msg)
        self.host_ip = host_ip
        self.host_port = host_port


class Message_Stop_Server(Message):
    def __init__(self, success_callback_msg=None, failed_callback_msg=None):
        Message.__init__(self, SERVICE_NETWORK, MESSAGE_STOP_SERVER, success_callback_msg, failed_callback_msg)


class Message_Send_Peer_Data(Message):
    def __init__(self, remote_ip, remote_port, raw_data, success_callback_msg=None, failed_callback_msg=None):
        Message.__init__(self, SERVICE_NETWORK, MESSAGE_SEND_PEER_DATA, success_callback_msg, failed_callback_msg)
        self.remote_ip = remote_ip
        self.remote_port = remote_port
        self.raw_data = raw_data

